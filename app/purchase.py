"""采购编排服务（阶段 2.x 核心管线）：需求 → 意图 → 逐级降级多平台搜索 → 决策报告。

数据流：
    requirement
    → intent.parse_intent（LLM 优先，启发式兜底）→ PurchaseIntent
    → 按 degradation 逐级：asyncio.gather 并发搜各平台
      （每个 provider 由 asyncio.wait_for 包 per_platform_timeout_sec，
       单平台超时/异常记入 errors、不影响其他平台）
    → require_terms 过滤 → 预算过滤 → dedupe，合并后非空即停止降级；
      全部级都空则 level_used=最后一级、items 空、summary 说明
    → storage.get_market_price 取各平台 EMA 参考价（异常静默为 None）
    → risk_tags / price_note / score_heuristic → cluster_same_shop 同店聚类
    → rank_items → DecisionReport
    → 下游 reporter.render_decision_card 渲染成 Markdown 卡片发送。
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aggregator.aggregate import (
    DecisionItem,
    cluster_same_shop,
    dedupe_items,
    rank_items,
    risk_tags_for,
    score_heuristic,
)
from .intent.engine import DegradationLevel, PurchaseIntent, parse_intent
from .types import NormalizedItem

if TYPE_CHECKING:
    from .provider import SearchProvider

logger = logging.getLogger("astrbot_plugin_goofish_catcher")


@dataclass(slots=True)
class DecisionReport:
    intent: PurchaseIntent
    level_used: int
    level_note: str | None
    level_hint: str | None
    items: list[DecisionItem]
    market_refs: dict[str, float | None]
    errors: dict[str, str]
    searched_platforms: list[str]
    used_llm: bool
    summary: str
    # 各平台在去重后的候选总数（含未进 top_k 的），卡片用来提示"N 条未进推荐"
    platform_counts: dict[str, int] = field(default_factory=dict)
    # 聚类+排序后未进 top_k 的候选（按分数降序）：给 LLM 回答用户追问用，
    # 卡片不展示（只提示数量）
    other_items: list[DecisionItem] = field(default_factory=list)


class PurchaseDecisionService:
    """采购决策编排：持有平台 provider 路由表，按需降级搜索并产出报告。"""

    def __init__(
        self,
        *,
        providers: dict[str, "SearchProvider"],
        storage=None,
        llm_call=None,
        top_k: int = 5,
        per_platform_timeout_sec: int = 20,
    ) -> None:
        self._providers = dict(providers)
        self._storage = storage
        self._llm_call = llm_call
        self._top_k = top_k
        self._per_platform_timeout_sec = per_platform_timeout_sec

    async def run(self, requirement: str) -> DecisionReport:
        intent = await parse_intent(requirement, llm_call=self._llm_call)
        levels = intent.degradation or [
            DegradationLevel(level=0, keyword=intent.keyword, note="精确匹配")
        ]
        searched = list(self._providers)
        errors: dict[str, str] = {}

        # 逐级降级：当前级合并结果非空即停；全空则停在最后一级。
        hit_level = levels[-1]
        merged: list[NormalizedItem] = []
        for level in levels:
            batch = await self._search_all(level.keyword, errors)
            batch = _filter_by_require_terms(batch, level.require_terms)
            batch = _filter_by_budget(batch, intent.budget_max)
            merged = dedupe_items(batch)
            if merged:
                hit_level = level
                break

        market_refs = await self._collect_market_refs(hit_level.keyword)

        if not merged:
            summary = (
                f"已沿降级链搜索至 L{hit_level.level}（{hit_level.keyword}），"
                "各平台均无符合条件的结果；可放宽预算或换个描述再试。"
            )
            return DecisionReport(
                intent=intent,
                level_used=hit_level.level,
                level_note=hit_level.note,
                level_hint=hit_level.hint,
                items=[],
                market_refs=market_refs,
                errors=errors,
                searched_platforms=searched,
                used_llm=False,
                summary=summary,
            )

        platform_counts: dict[str, int] = {}
        for item in merged:
            platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
        candidates = [
            DecisionItem(
                item=item,
                risk_tags=risk_tags_for(item),
                price_note=_price_note(item.price, market_refs.get(item.platform)),
                score=score_heuristic(
                    item, ema=market_refs.get(item.platform), intent=intent
                ),
            )
            for item in merged
        ]
        # 同店同款聚类：需在 DecisionItem 组装（拿到 shopName 与 score）之后、
        # rank_items 之前；platform_counts 保持聚类前的去重总数不变。
        clustered = cluster_same_shop(candidates)
        clustered_keys = {(d.item.platform, d.item.item_id) for d in clustered}
        # 被聚类归并的成员不参与排序，但不能凭空消失：留在未推荐池供追问。
        absorbed = [
            d
            for d in candidates
            if (d.item.platform, d.item.item_id) not in clustered_keys
        ]
        ranked, summary, used_llm = await rank_items(
            clustered,
            requirement=requirement,
            llm_call=self._llm_call,
            top_k=self._top_k,
        )
        ranked_ids = {d.item.item_id for d in ranked}
        other_items = sorted(
            (d for d in clustered + absorbed if d.item.item_id not in ranked_ids),
            key=lambda d: d.score,
            reverse=True,
        )
        return DecisionReport(
            intent=intent,
            level_used=hit_level.level,
            level_note=hit_level.note,
            level_hint=hit_level.hint,
            items=ranked,
            market_refs=market_refs,
            errors=errors,
            searched_platforms=searched,
            used_llm=used_llm,
            summary=summary,
            platform_counts=platform_counts,
            other_items=other_items,
        )

    # ── 内部 ─────────────────────────────────────────────────────────────────

    async def _search_all(
        self, keyword: str, errors: dict[str, str]
    ) -> list[NormalizedItem]:
        """并发搜所有平台；单平台失败记 errors 并返回空，不拖垮其他平台。"""

        async def _one(name: str, provider: "SearchProvider") -> list[NormalizedItem]:
            try:
                result = await asyncio.wait_for(
                    provider.search(
                        keyword=keyword,
                        pages=1,
                        timeout_sec=self._per_platform_timeout_sec,
                    ),
                    timeout=self._per_platform_timeout_sec,
                )
            except Exception as exc:
                errors[name] = _brief_error(exc, self._per_platform_timeout_sec)
                logger.warning(
                    "[goofish_catcher] purchase search failed on %s: %s",
                    name,
                    errors[name],
                )
                return []
            # errors 跨降级级别复用：本级成功须清掉该平台早前级别的失败记录，
            # 否则卡片会同时展示该平台商品和"失败平台"。
            errors.pop(name, None)
            return result

        results = await asyncio.gather(
            *(_one(name, provider) for name, provider in self._providers.items()),
            return_exceptions=True,
        )
        merged: list[NormalizedItem] = []
        for result in results:
            # _one 已吞掉所有异常；这里防御 gather 层面的意外。
            if isinstance(result, list):
                merged.extend(result)
        return merged

    async def _collect_market_refs(self, keyword: str) -> dict[str, float | None]:
        """各平台 EMA 参考价；storage 缺失或单平台异常都静默为 None。"""
        refs: dict[str, float | None] = {}
        if self._storage is None:
            return refs
        for platform in self._providers:
            refs[platform] = await self._market_ema(keyword, platform)
        return refs

    async def _market_ema(self, keyword: str, platform: str) -> float | None:
        try:
            result = self._storage.get_market_price(keyword, platform=platform)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] market price lookup failed (%s/%s): %s",
                platform,
                keyword,
                exc,
            )
            return None
        if result is None:
            return None
        ema = getattr(result, "ema_price", None)
        try:
            return float(ema) if ema is not None else None
        except (TypeError, ValueError):
            return None


def _filter_by_require_terms(
    items: list[NormalizedItem], require_terms: tuple[str, ...]
) -> list[NormalizedItem]:
    """精确级过滤：标题须包含全部 require_terms（大小写不敏感）。"""
    if not require_terms:
        return items
    lowered_terms = tuple(term.lower() for term in require_terms)
    return [
        item
        for item in items
        if all(term in (item.title or "").lower() for term in lowered_terms)
    ]


def _filter_by_budget(
    items: list[NormalizedItem], budget_max: float | None
) -> list[NormalizedItem]:
    if budget_max is None:
        return items
    return [item for item in items if float(item.price) <= budget_max]


def _price_note(price: float, ema: float | None) -> str | None:
    if ema is None or ema <= 0:
        return None
    pct = (ema - float(price)) / ema * 100.0
    if pct > 0:
        return f"低于参考价 {pct:.0f}%"
    if pct < 0:
        return f"高于参考价 {abs(pct):.0f}%"
    return "与参考价持平"


def _brief_error(exc: Exception, timeout_sec: int) -> str:
    if isinstance(exc, asyncio.TimeoutError):
        return f"搜索超时（>{timeout_sec}s）"
    message = str(exc).strip()
    return message or type(exc).__name__
