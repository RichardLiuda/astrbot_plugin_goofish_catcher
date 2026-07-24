"""决策卡片渲染：DecisionReport → Markdown 纯文本（聊天软件直接发送）。

数据流：
    purchase.DecisionReport → render_decision_card → 多行 Markdown 字符串。
结构：标题 → 需求理解行 → 降级提示（level_used>0 必有）→ 按平台分节的商品列表
→ 风险与建议（summary）→ 失败平台节（errors 非空时）。
仅 TYPE_CHECKING 引用 purchase，避免运行时环依赖。
"""

from __future__ import annotations

import statistics
from typing import TYPE_CHECKING

from ..platforms.registry import platform_display_name

if TYPE_CHECKING:
    from ..purchase import DecisionReport


def render_decision_card(report: "DecisionReport") -> str:
    """把采购决策报告渲染成 Markdown 卡片。"""
    intent = report.intent
    lines: list[str] = [f"🛒 采购决策：{intent.raw_query}", ""]

    lines.append(_render_intent_line(report))

    degradation_note = _render_degradation(report)
    if degradation_note:
        lines.extend(["", *degradation_note])

    lines.extend(["", *_render_platform_sections(report)])

    lines.extend(["", f"🛡️ 风险与建议：{report.summary}"])

    if report.errors:
        lines.append("")
        lines.append("⚠️ 失败平台：")
        for platform, message in report.errors.items():
            lines.append(f"- ⚠️ {platform_display_name(platform)}：{message}")

    return "\n".join(lines)


def _render_intent_line(report: "DecisionReport") -> str:
    """需求理解行：关键词｜属性｜预算（缺失项省略）。"""
    intent = report.intent
    parts = [f"🔍 关键词：{intent.keyword}"]
    if intent.attributes:
        attrs = "、".join(f"{key}={value}" for key, value in intent.attributes.items())
        parts.append(f"🎨 属性：{attrs}")
    if intent.budget_max is not None:
        parts.append(f"💰 预算：≤{_fmt_price(intent.budget_max)} 元")
    if intent.condition:
        parts.append(f"📦 成色：{intent.condition}")
    return " ｜ ".join(parts)


def _render_degradation(report: "DecisionReport") -> list[str]:
    """降级提示：level_used>0 时必有；带 hint 时追加 💡 行。"""
    if report.level_used <= 0:
        return []
    l0 = report.intent.degradation[0] if report.intent.degradation else None
    if l0 is not None:
        head = f"⚠️ 精确匹配（L0 {l0.keyword}）无结果，已降级到 L{report.level_used}"
    else:
        head = f"⚠️ 精确匹配无结果，已降级到 L{report.level_used}"
    if report.level_note:
        head += f"：{report.level_note}"
    lines = [head]
    if report.level_hint:
        lines.append(f"💡 {report.level_hint}")
    return lines


def _render_platform_sections(report: "DecisionReport") -> list[str]:
    """按平台分节列出商品；无商品时给出明确提示。"""
    if not report.items:
        return ["本次各平台均无符合条件的商品。"]

    # 保持 searched_platforms 的顺序，未登记的平台排最后。
    order = {name: idx for idx, name in enumerate(report.searched_platforms)}
    by_platform: dict[str, list] = {}
    for decision in report.items:
        by_platform.setdefault(decision.item.platform, []).append(decision)

    lines: list[str] = []
    for platform in sorted(by_platform, key=lambda p: order.get(p, len(order))):
        decisions = by_platform[platform]
        header = f"【{platform_display_name(platform)}】{len(decisions)} 条"
        ref = _render_price_ref(report, platform, decisions)
        if ref:
            header += f" · {ref}"
        lines.append(header)
        for idx, decision in enumerate(decisions, start=1):
            lines.extend(_render_item_lines(idx, decision))
    # 有结果但全部未进推荐的平台也要露个面，避免用户误以为该平台没搜到
    for platform in report.searched_platforms:
        if platform in by_platform:
            continue
        count = report.platform_counts.get(platform, 0)
        if count > 0:
            lines.append(
                f"【{platform_display_name(platform)}】另有 {count} 条结果，"
                "综合评分未进本次推荐"
            )
    return lines


def _render_price_ref(report: "DecisionReport", platform: str, decisions: list) -> str:
    """参考价：EMA 优先；无 EMA 用本批中位数；两者皆无不显示。"""
    ema = report.market_refs.get(platform)
    if ema is not None and ema > 0:
        return f"参考价 {_fmt_price(ema)} 元（EMA）"
    prices = [float(d.item.price) for d in decisions if d.item.price is not None]
    if prices:
        return f"参考价 {_fmt_price(statistics.median(prices))} 元（本批中位数）"
    return ""


def _render_item_lines(idx: int, decision) -> list[str]:
    item = decision.item
    raw = item.raw or {}
    title = item.title
    cluster_count = _safe_int(raw.get("cluster_count"))
    if cluster_count > 1:
        title = f"{title}（同店同款 ×{cluster_count}）"
    lines = [f"{idx}. [{decision.score:.0f}] {title}"]

    price_text = f"💰 {_fmt_price(item.price)} 元"
    cluster_min = _safe_float(raw.get("cluster_price_min"))
    if cluster_min is not None and cluster_min < float(item.price):
        price_text += f"（同店最低 ¥{_fmt_price(cluster_min)}）"
    meta = [price_text]
    if decision.price_note:
        meta.append(decision.price_note)
    shop = str(raw.get("shopName") or "").strip()
    if shop:
        meta.append(f"🏪 {shop}")
    sales = str(raw.get("salesText") or "").strip()
    if sales:
        meta.append(f"📦 {sales}")
    lines.append("   " + " ｜ ".join(meta))

    tail: list[str] = []
    if decision.risk_tags:
        tail.append("⚠️ " + "、".join(decision.risk_tags))
    if decision.reason:
        tail.append(f"理由：{decision.reason}")
    if decision.risk:
        tail.append(f"风险：{decision.risk}")
    if tail:
        lines.append("   " + " ｜ ".join(tail))

    if item.url:
        lines.append(f"   🔗 {item.url}")
    return lines


def _safe_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt_price(value: float) -> str:
    """价格显示：整数不带小数点，否则保留两位。"""
    num = float(value)
    if num == int(num):
        return str(int(num))
    return f"{num:.2f}"
