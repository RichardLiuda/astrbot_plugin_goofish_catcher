"""意图引擎：自然语言需求 → PurchaseIntent（含逐级降级链）。

数据流：
    用户原始文本 → parse_intent → PurchaseIntent
    - 有 llm_call：LLM 按固定 system prompt 输出
      {keyword, attributes, budget_max, condition, degradation:[...]}，
      超时（asyncio.wait_for）/ 异常 / JSON 不可解析一律回退启发式；
    - 无 llm_call（或 LLM 失败）：启发式兜底——整句作关键词、正则抓预算，
      degradation 固定为 [L0 整句（require_terms=属性词）, L1 去属性关键词]。
    任何输入保证 degradation ≥ 1 级。
下游 purchase.PurchaseDecisionService 按 degradation 逐级搜索，首个非空级停止。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("astrbot_plugin_goofish_catcher")

_SYSTEM_PROMPT = "你是购物意图解析器，只输出 JSON"

# 预算：1万5 / 1.5万 / 1w5 → 15000；万后面跟的数字按千位补足。
_BUDGET_WAN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[万wW]\s*(\d+)?")
# 预算必须有上下文锚点，否则 "RTX 5090" 里的 5090 会被误吞：
# ① 预算/以内/不超过 等引导词后跟数字；② 数字后跟 元/块。
_BUDGET_CONTEXT_RE = re.compile(
    r"(?:预算|限价|不超过|以内|之内|左右|上下|封顶|至多|最多|小于|低于|≤|大概|约)"
    r"\s*(?:是|为|等于|:|：)?\s*(\d{3,}(?:\.\d+)?)"
)
_BUDGET_UNIT_RE = re.compile(r"(\d{3,}(?:\.\d+)?)\s*(?:元|块)")

# 启发式属性词表：目前只收颜色（示例需求的主轴），命中即进 require_terms。
_COLOR_WORDS = (
    "红色", "黑色", "白色", "蓝色", "绿色", "黄色", "粉色", "紫色",
    "灰色", "银色", "金色", "橙色", "棕色", "青色",
)

_NEW_WORDS = ("全新", "未拆封")
_USED_WORDS = ("二手",)


@dataclass(slots=True)
class DegradationLevel:
    level: int
    keyword: str
    note: str                          # 这一级妥协了什么
    hint: str | None = None            # 给用户的替代建议（如"可考虑黑色+RGB调红"）
    require_terms: tuple[str, ...] = ()  # 标题必须包含的词（精确级过滤用）


@dataclass(slots=True)
class PurchaseIntent:
    raw_query: str
    keyword: str                       # 核心商品词（去修饰后）
    attributes: dict[str, str]         # {"颜色": "红色"}
    budget_max: float | None = None
    condition: str | None = None       # 全新/二手/不限
    degradation: list[DegradationLevel] = field(default_factory=list)


async def parse_intent(
    text: str,
    *,
    llm_call=None,
    timeout_sec: int = 12,
) -> PurchaseIntent:
    """解析购物需求。LLM 优先，任何失败回退启发式；保证 degradation 非空。"""
    raw = (text or "").strip()
    if llm_call is not None and raw:
        intent = await _parse_with_llm(raw, llm_call=llm_call, timeout_sec=timeout_sec)
        if intent is not None:
            return intent
    return _parse_heuristic(raw)


# ── LLM 路径 ─────────────────────────────────────────────────────────────────

async def _parse_with_llm(
    raw: str,
    *,
    llm_call,
    timeout_sec: int,
) -> PurchaseIntent | None:
    prompt = (
        f"需求：{raw}\n\n"
        "请把上面的购物需求解析成 JSON，字段：\n"
        '- keyword: 核心商品词（去掉颜色、成色等修饰）\n'
        '- attributes: 属性键值对，如 {"颜色": "红色"}，无则 {}\n'
        '- budget_max: 预算上限（元，数字），无则 null\n'
        '- condition: 全新 / 二手 / 不限\n'
        "- degradation: 降级链 2-4 级，逐级放松，每级 "
        '{"level": 0, "keyword": "...", "note": "这一级妥协了什么", '
        '"hint": "可选，给用户的替代建议", "require_terms": ["标题必须包含的词"]}\n'
        '  示例（红色RTX5090）：L0 精确匹配（require_terms 含 "红色"）→ L1 去掉颜色 '
        "→ L2 妥协成色 → L3 改色建议（hint 如 \"可考虑黑色+RGB调红\"）。\n"
        "只输出 JSON，不要输出任何其他内容。"
    )
    try:
        resp = await asyncio.wait_for(
            llm_call(prompt, _SYSTEM_PROMPT),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        logger.warning("[goofish_catcher] intent llm timeout")
        return None
    except Exception as exc:
        logger.warning("[goofish_catcher] intent llm failed: %s", exc)
        return None

    parsed = _extract_json_object(str(resp or ""))
    if not parsed:
        logger.warning("[goofish_catcher] intent llm output not usable json")
        return None
    return _intent_from_parsed(raw, parsed)


def _intent_from_parsed(raw: str, parsed: dict[str, Any]) -> PurchaseIntent | None:
    keyword = str(parsed.get("keyword") or "").strip() or raw
    if not keyword:
        return None

    attributes: dict[str, str] = {}
    raw_attrs = parsed.get("attributes")
    if isinstance(raw_attrs, dict):
        for key, value in raw_attrs.items():
            k, v = str(key).strip(), str(value).strip()
            if k and v:
                attributes[k] = v

    budget_max = _safe_positive_float(parsed.get("budget_max"))

    condition = str(parsed.get("condition") or "").strip() or None

    levels = _levels_from_parsed(parsed.get("degradation"))
    if not levels:
        levels = [DegradationLevel(level=0, keyword=keyword, note="精确匹配")]
    return PurchaseIntent(
        raw_query=raw,
        keyword=keyword,
        attributes=attributes,
        budget_max=budget_max,
        condition=condition,
        degradation=levels,
    )


def _levels_from_parsed(raw_levels: Any) -> list[DegradationLevel]:
    if not isinstance(raw_levels, list):
        return []
    levels: list[DegradationLevel] = []
    for idx, row in enumerate(raw_levels):
        if not isinstance(row, dict):
            continue
        keyword = str(row.get("keyword") or "").strip()
        if not keyword:
            continue
        note = str(row.get("note") or "").strip() or "放宽条件"
        hint = str(row.get("hint") or "").strip() or None
        require_terms = tuple(
            t for t in (str(x).strip() for x in row.get("require_terms") or []) if t
        )
        try:
            level_no = int(row.get("level", idx))
        except (TypeError, ValueError):
            level_no = idx
        levels.append(
            DegradationLevel(
                level=level_no,
                keyword=keyword,
                note=note,
                hint=hint,
                require_terms=require_terms,
            )
        )
    levels.sort(key=lambda lv: lv.level)
    return levels


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


def _safe_positive_float(value: Any) -> float | None:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    return num if num > 0 else None


# ── 启发式兜底 ───────────────────────────────────────────────────────────────

def _parse_heuristic(raw: str) -> PurchaseIntent:
    """无 LLM 时的保底解析：整句当 keyword，正则抓预算与成色，颜色词进属性。

    degradation = [L0 整句（require_terms=属性词）, L1 去属性纯关键词]；
    无属性词可去时只留 L0，保证任何输入 ≥1 级。
    """
    budget_max = _parse_budget(raw)
    attributes = _parse_attributes(raw)
    condition = _parse_condition(raw)

    attr_words = tuple(attributes.values())
    levels = [
        DegradationLevel(
            level=0,
            keyword=raw,
            note="精确匹配原始描述",
            require_terms=attr_words,
        )
    ]
    relaxed = _strip_attributes(raw, attr_words)
    if relaxed and relaxed != raw:
        levels.append(
            DegradationLevel(
                level=1,
                keyword=relaxed,
                note="放宽属性限制，仅按核心关键词搜索",
            )
        )
    return PurchaseIntent(
        raw_query=raw,
        keyword=raw,
        attributes=attributes,
        budget_max=budget_max,
        condition=condition,
        degradation=levels,
    )


def _parse_budget(text: str) -> float | None:
    match = _BUDGET_WAN_RE.search(text)
    if match:
        base = float(match.group(1)) * 10000.0
        tail = match.group(2)
        if tail:
            # "1万5" 的 5 是千位：值不足千时按千位补，否则原样加。
            tail_value = float(tail)
            base += tail_value * 1000.0 if tail_value < 1000 else tail_value
        return base
    for pattern in (_BUDGET_CONTEXT_RE, _BUDGET_UNIT_RE):
        match = pattern.search(text)
        if match:
            return float(match.group(1))
    return None


def _parse_attributes(text: str) -> dict[str, str]:
    for word in _COLOR_WORDS:
        if word in text:
            return {"颜色": word}
    return {}


def _parse_condition(text: str) -> str | None:
    if any(word in text for word in _NEW_WORDS):
        return "全新"
    if any(word in text for word in _USED_WORDS):
        return "二手"
    return None


def _strip_attributes(text: str, attr_words: tuple[str, ...]) -> str:
    relaxed = text
    for word in attr_words:
        relaxed = relaxed.replace(word, "")
    return " ".join(relaxed.split())
