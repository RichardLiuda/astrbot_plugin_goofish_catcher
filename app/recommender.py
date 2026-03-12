from __future__ import annotations

import asyncio
import json
import re
import time
from string import Template
from typing import Any

from astrbot.api import logger
from astrbot.api.star import Context

from .config import PluginSettings
from .types import (
    NormalizedItem,
    RecommendationCandidate,
    RecommendationItem,
    RecommendationResult,
)

_RISK_KEYWORDS = (
    "配件",
    "坏",
    "故障",
    "不退不换",
    "仅自提",
    "拆修",
    "瑕疵",
    "暗病",
)


class GoofishRecommender:
    def __init__(self, *, context: Context, settings: PluginSettings) -> None:
        self.context = context
        self.settings = settings

    async def prefilter_items(
        self,
        *,
        umo: str,
        keyword: str,
        items: list[NormalizedItem],
    ) -> tuple[list[NormalizedItem], str]:
        if not items:
            return [], "EMPTY"

        max_llm_items = max(1, self.settings.llm_prefilter_max_items)
        head = items[:max_llm_items]
        tail = items[max_llm_items:]

        if self.settings.llm_prefilter_enabled:
            provider_id = self._resolve_provider_id(
                umo,
                configured_provider_id=(
                    self.settings.llm_prefilter_provider_id
                    or self.settings.llm_provider_id
                ),
                config_key=(
                    "llm_prefilter_provider_id"
                    if self.settings.llm_prefilter_provider_id
                    else "llm_provider_id"
                ),
            )
            if provider_id:
                keep_ids, reason = await self._prefilter_with_llm(
                    provider_id=provider_id,
                    keyword=keyword,
                    items=head,
                )
                if keep_ids is not None:
                    keep_set = set(keep_ids)
                    kept_head = [item for item in head if item.item_id in keep_set]
                    # Keep filtering for overflow with cheap local rules.
                    kept_tail = _prefilter_with_keyword(keyword, tail)
                    filtered = kept_head + kept_tail
                    if filtered:
                        return filtered, "LLM_PREFILTER"
                    # LLM can be too strict; fallback to local keyword filtering.
                    local = _prefilter_with_keyword(keyword, items)
                    return (local if local else items), "LLM_EMPTY_FALLBACK"
                logger.warning("[goofish_catcher] llm prefilter failed: %s", reason)

        local = _prefilter_with_keyword(keyword, items)
        if local:
            return local, "HEURISTIC_PREFILTER"
        return items, "HEURISTIC_KEEP_ALL"

    async def analyze(
        self,
        *,
        umo: str,
        keyword: str,
        candidates: list[RecommendationCandidate],
        top_k: int | None = None,
    ) -> RecommendationResult:
        if not candidates:
            return RecommendationResult(
                keyword=keyword,
                summary="本轮没有上新或降价候选。",
                top=[],
                total_candidates=0,
                used_llm=False,
                fallback_reason="NO_CANDIDATE",
            )

        picked_top_k = max(1, top_k or self.settings.llm_top_k)
        limited_candidates = candidates[: self.settings.llm_max_candidates]
        llm_result: RecommendationResult | None = None
        fallback_reason: str | None = None

        if self.settings.llm_enabled:
            provider_id = self._resolve_provider_id(
                umo,
                configured_provider_id=self.settings.llm_provider_id,
                config_key="llm_provider_id",
            )
            if provider_id:
                llm_result, fallback_reason = await self._analyze_with_llm(
                    provider_id=provider_id,
                    keyword=keyword,
                    candidates=limited_candidates,
                    top_k=picked_top_k,
                )
            else:
                fallback_reason = "NO_PROVIDER"
        else:
            fallback_reason = "LLM_DISABLED"

        if llm_result is not None:
            llm_result.total_candidates = len(candidates)
            return llm_result

        return self._analyze_with_heuristic(
            keyword=keyword,
            candidates=limited_candidates,
            top_k=picked_top_k,
            fallback_reason=fallback_reason or "LLM_FAILED",
            total_candidates=len(candidates),
        )

    def _resolve_provider_id(
        self,
        umo: str,
        *,
        configured_provider_id: str | None,
        config_key: str,
    ) -> str | None:
        configured_provider_id = (configured_provider_id or "").strip()
        if configured_provider_id:
            configured_provider = self.context.get_provider_by_id(
                configured_provider_id
            )
            if configured_provider is not None:
                return configured_provider_id
            logger.warning(
                "[goofish_catcher] configured %s not found: %s",
                config_key,
                configured_provider_id,
            )

        provider = self.context.get_using_provider(umo)
        if provider is None:
            providers = self.context.get_all_providers()
            provider = providers[0] if providers else None
        if provider is None:
            return None
        try:
            return str(provider.meta().id)
        except Exception:
            return None

    async def _prefilter_with_llm(
        self,
        *,
        provider_id: str,
        keyword: str,
        items: list[NormalizedItem],
    ) -> tuple[list[str] | None, str]:
        payload = [
            {
                "item_id": item.item_id,
                "title": item.title,
                "url": item.url,
                "snippet": _item_snippet(item),
            }
            for item in items
        ]
        prompt = _render_prompt_template(
            self.settings.llm_prefilter_prompt,
            keyword=keyword,
            items_json=json.dumps(payload, ensure_ascii=False),
        )
        try:
            llm_resp = await asyncio.wait_for(
                self.context.llm_generate(
                    chat_provider_id=provider_id,
                    prompt=prompt,
                    system_prompt=_prefilter_system_prompt(),
                    temperature=0.0,
                    max_tokens=280,
                ),
                timeout=self.settings.llm_prefilter_timeout_sec,
            )
        except asyncio.TimeoutError:
            return None, "LLM_TIMEOUT"
        except Exception as exc:
            return None, f"LLM_EXCEPTION:{exc}"

        text = (getattr(llm_resp, "completion_text", "") or "").strip()
        if not text:
            return None, "LLM_EMPTY"
        try:
            parsed = _parse_json_maybe_fenced(text)
        except Exception:
            return None, "LLM_JSON_INVALID"

        keep_ids: list[str] = []
        keep_raw = parsed.get("keep_item_ids")
        if isinstance(keep_raw, list):
            for val in keep_raw:
                item_id = str(val).strip()
                if item_id:
                    keep_ids.append(item_id)

        if not keep_ids:
            return [], "LLM_EMPTY_KEEP"
        return keep_ids, "OK"

    async def _analyze_with_llm(
        self,
        *,
        provider_id: str,
        keyword: str,
        candidates: list[RecommendationCandidate],
        top_k: int,
    ) -> tuple[RecommendationResult | None, str | None]:
        prompt = self._build_prompt(keyword=keyword, candidates=candidates, top_k=top_k)
        try:
            llm_resp = await asyncio.wait_for(
                self.context.llm_generate(
                    chat_provider_id=provider_id,
                    prompt=prompt,
                    system_prompt=_recommend_system_prompt(),
                    temperature=0.2,
                    max_tokens=900,
                ),
                timeout=self.settings.llm_timeout_sec,
            )
        except asyncio.TimeoutError:
            logger.warning("[goofish_catcher] llm analysis timeout")
            return None, "LLM_TIMEOUT"
        except Exception as exc:
            logger.warning("[goofish_catcher] llm analysis failed: %s", exc)
            return None, "LLM_EXCEPTION"

        text = (getattr(llm_resp, "completion_text", "") or "").strip()
        if not text:
            return None, "LLM_EMPTY"
        try:
            parsed = _parse_json_maybe_fenced(text)
        except Exception:
            logger.warning(
                "[goofish_catcher] llm output is not valid json: %s", text[:200]
            )
            return None, "LLM_JSON_INVALID"

        result = self._build_result_from_llm(
            keyword=keyword,
            candidates=candidates,
            top_k=top_k,
            parsed=parsed,
        )
        if result is None:
            return None, "LLM_JSON_UNUSABLE"
        return result, None

    def _build_result_from_llm(
        self,
        *,
        keyword: str,
        candidates: list[RecommendationCandidate],
        top_k: int,
        parsed: dict[str, Any],
    ) -> RecommendationResult | None:
        by_id = {c.item_id: c for c in candidates}
        top_raw = parsed.get("top")
        if not isinstance(top_raw, list):
            return None

        top: list[RecommendationItem] = []
        for row in top_raw:
            if not isinstance(row, dict):
                continue
            item_id = str(row.get("item_id", "")).strip()
            if not item_id or item_id not in by_id:
                continue
            cand = by_id[item_id]
            score = _safe_float(row.get("score"), default=0.0)
            score = max(0.0, min(100.0, score))
            if score < self.settings.llm_min_score:
                continue
            reason = str(row.get("reason", "")).strip() or "模型未提供理由。"
            risk = str(row.get("risk", "")).strip() or "未提供风险提示。"
            top.append(
                RecommendationItem(
                    item_id=item_id,
                    score=score,
                    reason=reason,
                    risk=risk,
                    title=cand.title,
                    price=cand.price,
                    url=cand.url,
                )
            )
            if len(top) >= top_k:
                break

        if not top:
            return None

        summary = str(parsed.get("summary", "")).strip()
        if not summary:
            summary = f"共 {len(candidates)} 个候选，模型推荐前 {len(top)} 个。"
        return RecommendationResult(
            keyword=keyword,
            summary=summary,
            top=top,
            total_candidates=len(candidates),
            used_llm=True,
            fallback_reason=None,
        )

    def _analyze_with_heuristic(
        self,
        *,
        keyword: str,
        candidates: list[RecommendationCandidate],
        top_k: int,
        fallback_reason: str,
        total_candidates: int,
    ) -> RecommendationResult:
        now_ts = int(time.time())
        scored: list[tuple[RecommendationCandidate, float, str, str]] = []
        for cand in candidates:
            score, reason, risk = _heuristic_score(cand, now_ts)
            scored.append((cand, score, reason, risk))
        scored.sort(key=lambda row: row[1], reverse=True)

        top: list[RecommendationItem] = []
        for cand, score, reason, risk in scored[:top_k]:
            if score < self.settings.llm_min_score:
                continue
            top.append(
                RecommendationItem(
                    item_id=cand.item_id,
                    score=score,
                    reason=reason,
                    risk=risk,
                    title=cand.title,
                    price=cand.price,
                    url=cand.url,
                )
            )

        summary = f"使用启发式评分完成分析，共 {total_candidates} 个候选。"
        return RecommendationResult(
            keyword=keyword,
            summary=summary,
            top=top,
            total_candidates=total_candidates,
            used_llm=False,
            fallback_reason=fallback_reason,
        )

    def _build_prompt(
        self,
        *,
        keyword: str,
        candidates: list[RecommendationCandidate],
        top_k: int,
    ) -> str:
        serialized = [
            {
                "event_type": c.event_type,
                "title": c.title,
                "item_id": c.item_id,
                "price": round(float(c.price), 2),
                "url": c.url,
                "publish_time": c.publish_time,
                "last_price": c.last_price,
                "drop_abs": c.drop_abs,
                "drop_pct": c.drop_pct,
            }
            for c in candidates
        ]
        return (
            _render_prompt_template(
                self.settings.llm_recommend_prompt,
                keyword=keyword,
                top_k=top_k,
                candidates_json=json.dumps(serialized, ensure_ascii=False),
            )
        )


def _render_prompt_template(template: str, **values: Any) -> str:
    prepared = {key: str(value) for key, value in values.items()}
    return Template(template).safe_substitute(prepared)


def _safe_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_json_maybe_fenced(raw_text: str) -> dict[str, Any]:
    cleaned = raw_text.strip()
    if not cleaned:
        raise ValueError("empty llm output")

    candidates: list[str] = [cleaned]
    candidates.extend(_extract_fenced_json_candidates(cleaned))
    candidates.extend(_extract_balanced_json_objects(cleaned))

    seen: set[str] = set()
    for candidate in candidates:
        payload_text = candidate.strip()
        if not payload_text or payload_text in seen:
            continue
        seen.add(payload_text)
        try:
            payload = json.loads(payload_text)
        except (TypeError, ValueError):
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError("llm payload must be a dict")


def _extract_fenced_json_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for match in re.finditer(
        r"```(?:json|JSON)?\s*([\s\S]*?)```",
        text,
        flags=re.IGNORECASE,
    ):
        block = match.group(1).strip()
        if block:
            candidates.append(block)

    if text.startswith("```"):
        stripped = re.sub(r"^```(?:json|JSON)?\s*", "", text, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped).strip()
        if stripped:
            candidates.append(stripped)
    return candidates


def _extract_balanced_json_objects(text: str) -> list[str]:
    blocks: list[str] = []
    depth = 0
    start = -1
    in_string = False
    escape = False

    for idx, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
            continue

        if ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                blocks.append(text[start : idx + 1])
                start = -1

    return blocks


def _item_snippet(item: NormalizedItem) -> str:
    if not item.raw:
        return ""
    try:
        text = json.dumps(item.raw, ensure_ascii=False)
    except Exception:
        return ""
    return text[:180]


def _normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    return re.sub(r"[\s\-_]+", "", lowered)


def _keyword_tokens(keyword: str) -> list[str]:
    raw = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", keyword.lower())
    tokens: list[str] = []
    for token in raw:
        normalized = _normalize_text(token)
        if not normalized:
            continue
        if len(normalized) <= 1:
            continue
        tokens.append(normalized)
    return tokens


def _is_relevant_by_keyword(keyword: str, item: NormalizedItem) -> bool:
    title_text = _normalize_text(item.title or "")
    keyword_text = _normalize_text(keyword)
    if not title_text:
        return False
    if keyword_text and keyword_text in title_text:
        return True

    tokens = _keyword_tokens(keyword)
    if not tokens:
        return True
    hit = sum(1 for token in tokens if token in title_text)
    threshold = max(1, (len(tokens) + 1) // 2)
    return hit >= threshold


def _prefilter_with_keyword(
    keyword: str,
    items: list[NormalizedItem],
) -> list[NormalizedItem]:
    return [item for item in items if _is_relevant_by_keyword(keyword, item)]


def _heuristic_score(
    candidate: RecommendationCandidate,
    now_ts: int,
) -> tuple[float, str, str]:
    score = 50.0
    reason_parts: list[str] = []
    lowered = candidate.title.lower()
    risk_hits = [kw for kw in _RISK_KEYWORDS if kw in lowered]

    if candidate.event_type == "PRICE_DROP":
        drop_abs = candidate.drop_abs
        if (
            drop_abs is None
            and candidate.last_price
            and candidate.last_price > candidate.price
        ):
            drop_abs = candidate.last_price - candidate.price
        drop_abs = max(0.0, float(drop_abs or 0.0))
        drop_pct = candidate.drop_pct
        if drop_pct is None and candidate.last_price and candidate.last_price > 0:
            drop_pct = drop_abs / candidate.last_price
        drop_pct = max(0.0, float(drop_pct or 0.0))
        score += min(25.0, drop_abs / 10.0)
        score += min(25.0, drop_pct * 100.0)
        reason_parts.append(f"降价 {drop_abs:.2f} 元 ({drop_pct:.1%})")
    else:
        if candidate.publish_time is not None and candidate.publish_time > 0:
            age_hours = max(0.0, (now_ts - candidate.publish_time) / 3600.0)
            freshness = max(0.0, 15.0 - age_hours)
            score += freshness
            reason_parts.append(f"上新约 {age_hours:.1f} 小时")
        else:
            score += 6.0
            reason_parts.append("上新时间未知，默认中等新鲜度")

    if risk_hits:
        score -= min(28.0, len(risk_hits) * 8.0)
        risk = "命中风险词: " + "、".join(risk_hits)
    else:
        risk = "暂无明显风险关键词"

    score = max(0.0, min(100.0, round(score, 1)))
    reason = "；".join(reason_parts) if reason_parts else "综合价格与新鲜度评分"
    return score, reason, risk


def _recommend_system_prompt() -> str:
    return (
        "你是二手交易投资建议助手。"
        "你会根据候选商品的降价幅度、发布时间和风险词进行排序。"
        "只输出 JSON，不要 Markdown，不要额外字段。"
        'JSON 结构: {"summary":"...", "top":[{"item_id":"...", "score":0-100, "reason":"...", "risk":"..."}]}。'
    )


def _prefilter_system_prompt() -> str:
    return (
        "你是二手商品相关性过滤器。"
        "只判断商品是否和关键词匹配。"
        "忽略价格高低、功能描述、成色、是否值得买。"
        '输出 JSON: {"keep_item_ids": ["..."]}。'
    )
