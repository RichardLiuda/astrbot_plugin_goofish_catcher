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

# 预算解析：任何形式（含万形式）都必须带上下文锚点，否则 "RTX 5090"/
# "850W电源"/"5000万像素" 里的型号、参数数字会被误吞。锚点分两类：
# ① 前置引导词（预算2万 / ￥2000）；② 后置单位或限定词（2万以内 / 8000元）。
# 万形式数值体："1万5 / 1.5万 / 1w5"，万后面跟的数字按千位补足。
# 尾数必须紧贴 万/w：允许空格会把 "预算2万 850W电源" 的 850 吞进预算。
_WAN_BODY = r"(\d+(?:\.\d+)?)\s*[万wW](\d+)?"
_PLAIN_BODY = r"(\d{3,}(?:\.\d+)?)"
_LEAD_ANCHOR = (
    r"(?:预算|限价|不超过|至多|最多|小于|低于|≤|大概|约|￥|¥)"
    r"\s*(?:是|为|等于|:|：)?\s*"
)
_TAIL_ANCHOR = r"\s*(?:元|块|以内|之内|以下|左右|上下|封顶)"
_BUDGET_WAN_LEAD_RE = re.compile(_LEAD_ANCHOR + _WAN_BODY)
_BUDGET_WAN_TAIL_RE = re.compile(_WAN_BODY + _TAIL_ANCHOR)
_BUDGET_PLAIN_LEAD_RE = re.compile(_LEAD_ANCHOR + _PLAIN_BODY)
_BUDGET_PLAIN_TAIL_RE = re.compile(_PLAIN_BODY + _TAIL_ANCHOR)

# 启发式属性词表：目前只收颜色（示例需求的主轴），命中即进 require_terms。
_COLOR_WORDS = (
    "红色",
    "黑色",
    "白色",
    "蓝色",
    "绿色",
    "黄色",
    "粉色",
    "紫色",
    "灰色",
    "银色",
    "金色",
    "橙色",
    "棕色",
    "青色",
)

_NEW_WORDS = ("全新", "未拆封")
_USED_WORDS = ("二手",)

# ── 平台限定词预提取 ─────────────────────────────────────────────────────────
# 在 LLM/启发式解析之前从原文剥离：平台名不是商品词，留在关键词里会污染
# 各平台搜索（实证：「RTX 5060 Ti 显卡，淘宝平台」整句被打进闲鱼搜索框）。
_PLATFORM_ALIASES: dict[str, str] = {
    "淘宝": "taobao",
    "taobao": "taobao",
    "闲鱼": "goofish",
    "咸鱼": "goofish",  # 常见别写
    "goofish": "goofish",
}
# 匹配形态：「，淘宝平台」「在淘宝搜」「闲鱼上的」「帮我在淘宝找」等。
# 平台名前必须是句首/分隔符 + 可选引导短语，后必须走完可选后缀链后到达
# 分隔符或句尾——「闲鱼玩偶」这类把平台字当商品词一部分的输入不会命中。
# 覆盖是 best-effort：漏匹配 = 维持现状（平台词进关键词、搜全平台），不致错。
# 前导分隔符是消耗式匹配（非 lookbehind）：剥离中段平台词时把它前面的
# 逗号/空格一并吃掉，避免留下「显卡，，全新」式的重复/悬空分隔符。
_PLATFORM_RE = re.compile(
    r"(?:^|[,，、;；\s])"
    r"(?:请|麻烦)?(?:帮我|帮忙|替我)?"
    r"(?:想?在|去|上|订阅|监控|蹲)?"
    r"(淘宝|闲鱼|咸鱼|taobao|goofish)"
    r"(?:平台|网)?"
    r"(?:"
    r"(?:上面|上|里)?(?:搜索|搜|找找|找|买|逛逛|看看)?的"
    r"|"
    r"(?:上面|上|里)?(?:搜索|搜|找找|找|买|逛逛|看看)?(?=[,，、;；\s]|$)"
    r")",
    re.IGNORECASE,
)


def extract_platforms(text: str) -> tuple[str, tuple[str, ...]]:
    """从需求原文剥离平台限定词，返回 (清理后文本, 平台约束)。

    约束为空元组 = 未指定平台（下游搜全部启用平台）。整句只剩平台词时
    保留原文作兜底关键词（搜索本身已无意义，但不至于空关键词报错）。
    """
    raw = str(text or "")
    platforms: list[str] = []

    def _record(match: re.Match[str]) -> str:
        name = _PLATFORM_ALIASES.get(match.group(1).lower())
        if name and name not in platforms:
            platforms.append(name)
        return ""

    cleaned = _PLATFORM_RE.sub(_record, raw)
    cleaned = " ".join(cleaned.split()).strip(" ，,、;；").strip()
    if not cleaned:
        cleaned = raw.strip()
    return cleaned, tuple(platforms)


@dataclass(slots=True)
class DegradationLevel:
    level: int
    keyword: str
    note: str  # 这一级妥协了什么
    hint: str | None = None  # 给用户的替代建议（如"可考虑黑色+RGB调红"）
    require_terms: tuple[str, ...] = ()  # 标题必须包含的词（精确级过滤用）


@dataclass(slots=True)
class PurchaseIntent:
    raw_query: str
    keyword: str  # 核心商品词（去修饰后）
    attributes: dict[str, str]  # {"颜色": "红色"}
    budget_max: float | None = None
    condition: str | None = None  # 全新/二手/不限
    degradation: list[DegradationLevel] = field(default_factory=list)
    # 用户点名的平台约束（("taobao",) 等）；空元组 = 未指定，搜全部。
    platforms: tuple[str, ...] = ()


async def parse_intent(
    text: str,
    *,
    llm_call=None,
    timeout_sec: int = 12,
) -> PurchaseIntent:
    """解析购物需求。LLM 优先，任何失败回退启发式；保证 degradation 非空。

    平台限定词在进入任一解析路径前统一剥离（确定性正则，不依赖 LLM），
    平台约束记录在 intent.platforms，raw_query 保留真实原文。
    """
    raw = (text or "").strip()
    cleaned, platforms = extract_platforms(raw)
    intent: PurchaseIntent | None = None
    if llm_call is not None and cleaned:
        intent = await _parse_with_llm(
            cleaned, llm_call=llm_call, timeout_sec=timeout_sec
        )
    if intent is None:
        intent = _parse_heuristic(cleaned)
    intent.raw_query = raw
    intent.platforms = platforms
    return intent


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
        "- keyword: 核心商品词（去掉颜色、成色等修饰）\n"
        '- attributes: 属性键值对，如 {"颜色": "红色"}，无则 {}\n'
        "- budget_max: 预算上限（元，数字），无则 null\n"
        "- condition: 全新 / 二手 / 不限\n"
        "- degradation: 降级链 2-4 级，逐级放松，每级 "
        '{"level": 0, "keyword": "...", "note": "这一级妥协了什么", '
        '"hint": "可选，给用户的替代建议", "require_terms": ["标题必须包含的词"]}\n'
        '  示例（红色RTX5090）：L0 精确匹配（require_terms 含 "红色"）→ L1 去掉颜色 '
        '→ L2 妥协成色 → L3 改色建议（hint 如 "可考虑黑色+RGB调红"）。\n'
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

    try:
        parsed = _extract_json_object(str(resp or ""))
        if not parsed:
            logger.warning("[goofish_catcher] intent llm output not usable json")
            return None
        return _intent_from_parsed(raw, parsed)
    except Exception as exc:
        # LLM 输出结构不可控：解析期任何异常只回退启发式，不冒泡给用户。
        logger.warning("[goofish_catcher] intent llm output unusable: %s", exc)
        return None


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
        raw_terms = row.get("require_terms")
        if isinstance(raw_terms, str):
            # 整串是一个词，不能逐字符拆散。
            raw_terms = [raw_terms]
        elif not isinstance(raw_terms, (list, tuple)):
            # 其他标量（如 int）不是词表，忽略。
            raw_terms = []
        require_terms = tuple(t for t in (str(x).strip() for x in raw_terms) if t)
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


def _wan_value(match: re.Match[str]) -> float:
    base = float(match.group(1)) * 10000.0
    tail = match.group(2)
    if tail:
        # "1万5" 的 5 是千位：值不足千时按千位补，否则原样加。
        tail_value = float(tail)
        base += tail_value * 1000.0 if tail_value < 1000 else tail_value
    return base


def _parse_budget(text: str) -> float | None:
    # 前置引导词（预算X）先于后置限定（X以内）：瓦数 "850W以内" 会被万形式
    # 误读，同句真实预算 "预算400元" 必须赢。同级内万形式先于纯数字；
    # 无锚点的裸 "N万/NW" 一律不作预算。
    for pattern, is_wan in (
        (_BUDGET_WAN_LEAD_RE, True),
        (_BUDGET_PLAIN_LEAD_RE, False),
        (_BUDGET_WAN_TAIL_RE, True),
        (_BUDGET_PLAIN_TAIL_RE, False),
    ):
        match = pattern.search(text)
        if match:
            return _wan_value(match) if is_wan else float(match.group(1))
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
