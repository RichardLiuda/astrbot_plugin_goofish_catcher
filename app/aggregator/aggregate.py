"""聚合层：多平台候选的去重、风险打标、启发式评分与 LLM 重排。

数据流：
    NormalizedItem（各平台原始结果）
    → dedupe_items 去重 → risk_tags_for 打标 → score_heuristic 评分
    → DecisionItem → rank_items（LLM 优先，失败回退启发式排序）
    → (排序后 Top-K, 总结文本, used_llm)。
全部被 purchase.PurchaseDecisionService 串起；本模块不触网、不依赖 AstrBot。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from ..intent.engine import PurchaseIntent
from ..platforms.registry import PLATFORM_TAOBAO
from ..types import NormalizedItem

logger = logging.getLogger("astrbot_plugin_goofish_catcher")

_SYSTEM_PROMPT = "你是采购决策助手，宁缺毋滥，只输出 JSON"

# 标题风险词：命中一个追加一个标签；评分时每个 -8（上限 -24）。
_GOOFISH_TITLE_RISK_WORDS = (
    "坏", "故障", "拆修", "不退不换", "仅自提", "矿", "瑕疵", "暗病", "无票",
)
_TAOBAO_TITLE_RISK_WORDS = ("工包", "拆机", "矿", "翻新", "水洗")

_GOOFISH_BASE_TAG = "二手/无发票风险"
_TAOBAO_OFFICIAL_TAG = "品牌/官方店铺"
_TAOBAO_C_SHOP_TAG = "淘宝C店/注意验货与评价"
# 平台级基础标签（信息性，不参与评分扣分）。
_BASE_TAGS = (_GOOFISH_BASE_TAG, _TAOBAO_OFFICIAL_TAG, _TAOBAO_C_SHOP_TAG)


@dataclass(slots=True)
class DecisionItem:
    item: NormalizedItem
    risk_tags: list[str]
    price_note: str | None             # "低于参考价 26%" / "高于参考价 8%"
    score: float = 0.0
    reason: str = ""
    risk: str = ""


def dedupe_items(items: list[NormalizedItem]) -> list[NormalizedItem]:
    """先按 (platform, item_id) 精确去重，再按 (platform, 标题前20字, price) 近似去重。

    保序：同一商品在不同平台不算重复（同平台跨店铺同标题同价才算近似重复）。
    """
    seen_exact: set[tuple[str, str]] = set()
    seen_fuzzy: set[tuple[str, str, float]] = set()
    out: list[NormalizedItem] = []
    for item in items:
        exact = (item.platform, item.item_id)
        if exact in seen_exact:
            continue
        seen_exact.add(exact)
        fuzzy = (item.platform, (item.title or "")[:20], round(float(item.price), 2))
        if fuzzy in seen_fuzzy:
            continue
        seen_fuzzy.add(fuzzy)
        out.append(item)
    return out


def risk_tags_for(item: NormalizedItem) -> list[str]:
    """平台基础标签 + 标题风险词。未知平台按闲鱼（二手）口径处理。"""
    title = item.title or ""
    if item.platform == PLATFORM_TAOBAO:
        shop = str((item.raw or {}).get("shopName") or "")
        if "旗舰" in shop or "官方" in shop:
            tags = [_TAOBAO_OFFICIAL_TAG]
        else:
            tags = [_TAOBAO_C_SHOP_TAG]
        tags.extend(word for word in _TAOBAO_TITLE_RISK_WORDS if word in title)
        return tags
    tags = [_GOOFISH_BASE_TAG]
    tags.extend(word for word in _GOOFISH_TITLE_RISK_WORDS if word in title)
    return tags


def score_heuristic(
    item: NormalizedItem,
    *,
    ema: float | None,
    intent: PurchaseIntent,
) -> float:
    """基线 60 的加减分：EMA 偏离 ±20 封顶、标题风险词每个 -8（-24 封顶）、
    品牌/官方店 +6、标题"全新/未拆封"且需求要全新 +8；最终 clamp 到 0-100。"""
    score = 60.0
    if ema is not None and ema > 0:
        delta_pct = (ema - float(item.price)) / ema * 100.0
        score += max(-20.0, min(20.0, delta_pct))

    tags = risk_tags_for(item)
    title_hits = [tag for tag in tags if tag not in _BASE_TAGS]
    score -= min(24.0, 8.0 * len(title_hits))
    if _TAOBAO_OFFICIAL_TAG in tags:
        score += 6.0

    title = item.title or ""
    if intent.condition == "全新" and ("全新" in title or "未拆封" in title):
        score += 8.0
    return max(0.0, min(100.0, score))


async def rank_items(
    candidates: list[DecisionItem],
    *,
    requirement: str,
    llm_call=None,
    top_k: int = 5,
    timeout_sec: int = 20,
) -> tuple[list[DecisionItem], str, bool]:
    """候选排序：LLM 重排优先，失败回退按 score 启发式排序。

    返回 (排序后列表, 总结文本, used_llm)。LLM 路径会回填 score/reason/risk；
    回退路径保留调用方已算好的启发式 score。
    """
    if not candidates:
        return [], "本次无候选商品。", False
    if llm_call is not None:
        ranked = await _rank_with_llm(
            candidates,
            requirement=requirement,
            llm_call=llm_call,
            top_k=top_k,
            timeout_sec=timeout_sec,
        )
        if ranked is not None:
            return ranked
    return _rank_heuristic(candidates, top_k=top_k)


# ── LLM 重排 ─────────────────────────────────────────────────────────────────

async def _rank_with_llm(
    candidates: list[DecisionItem],
    *,
    requirement: str,
    llm_call,
    top_k: int,
    timeout_sec: int,
) -> tuple[list[DecisionItem], str, bool] | None:
    serialized = [
        {
            "platform": c.item.platform,
            "item_id": c.item.item_id,
            "title": c.item.title,
            "price": round(float(c.item.price), 2),
            "ema_note": c.price_note,
            "risk_tags": list(c.risk_tags),
            "score_hint": round(float(c.score), 1),
        }
        for c in candidates
    ]
    prompt = (
        f"采购需求：{requirement}\n"
        f"候选商品（最多推荐 {top_k} 条）：\n"
        f"{json.dumps(serialized, ensure_ascii=False)}\n\n"
        f"请优先保证结果真正符合需求，宁缺毋滥，不要为了凑满 {top_k} 而强行推荐；"
        "不符合需求的可以一条都不推。"
        '请输出 JSON：{"summary": "总体风险与建议", '
        '"top": [{"item_id": "...", "score": 0-100, "reason": "推荐理由", "risk": "风险提示"}]}。'
        "只输出 JSON，不要输出任何其他内容。"
    )
    try:
        resp = await asyncio.wait_for(
            llm_call(prompt, _SYSTEM_PROMPT),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        logger.warning("[goofish_catcher] rank llm timeout")
        return None
    except Exception as exc:
        logger.warning("[goofish_catcher] rank llm failed: %s", exc)
        return None

    parsed = _extract_json_object(str(resp or ""))
    top_raw = parsed.get("top")
    if not isinstance(top_raw, list):
        return None

    by_id = {c.item.item_id: c for c in candidates}
    ranked: list[DecisionItem] = []
    for row in top_raw:
        if not isinstance(row, dict):
            continue
        item_id = str(row.get("item_id") or "").strip()
        cand = by_id.get(item_id)
        if cand is None:
            continue
        cand.score = _clamp_score(row.get("score"), default=cand.score)
        cand.reason = str(row.get("reason") or "").strip()
        cand.risk = str(row.get("risk") or "").strip()
        ranked.append(cand)
        if len(ranked) >= top_k:
            break
    if not ranked:
        return None

    summary = str(parsed.get("summary") or "").strip()
    if not summary:
        summary = f"共 {len(candidates)} 个候选，模型推荐前 {len(ranked)} 个。"
    return ranked, summary, True


def _rank_heuristic(
    candidates: list[DecisionItem],
    *,
    top_k: int,
) -> tuple[list[DecisionItem], str, bool]:
    ordered = sorted(
        candidates,
        key=lambda c: (-float(c.score), float(c.item.price)),
    )[:top_k]
    summary = (
        f"共 {len(candidates)} 个候选，按价格偏离、风险标签启发式评分，"
        f"取前 {len(ordered)} 条；请优先关注风险标签。"
    )
    return ordered, summary, False


def _clamp_score(value: Any, *, default: float) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(100.0, score))


def _extract_json_object(text: str) -> dict[str, Any]:
    """鲁棒 JSON 提取：去 markdown fence，取首尾花括号（对齐 provider_agent）。"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
