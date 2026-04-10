from __future__ import annotations

import re
from dataclasses import dataclass

from astrbot.api.message_components import Plain, Reply

_INDEX_LINE_RE = re.compile(r"^(\d+)\.\s+\[[^\]]+\]\s+(.+)$")
_LINK_LINE_RE = re.compile(r"^链接：\s*(https?://\S+)\s*$")
_SELECTION_RE = re.compile(r"^\s*\d+(?:[\s,，、]+\d+)*\s*$")
_RECOMMENDATION_HINT = "引用本消息回复序号可收藏，支持 1 或 1 3"
_SUPPORTED_HEADERS = ("【闲鱼建议】", "【查询推荐】", "【立即检查】")


@dataclass(slots=True)
class ReplyFavoriteItem:
    index: int
    title: str
    url: str
    item_id: str | None = None


@dataclass(slots=True)
class ReplyFavoriteTarget:
    source: str
    items: list[ReplyFavoriteItem]
    error_message: str | None = None


def recommendation_reply_hint() -> str:
    return _RECOMMENDATION_HINT


def extract_reply_text(messages: list[object]) -> str | None:
    for component in messages:
        if not isinstance(component, Reply):
            continue
        message_str = str(getattr(component, "message_str", "") or "").strip()
        if message_str:
            return message_str
        chain = getattr(component, "chain", None) or []
        parts: list[str] = []
        for item in chain:
            if isinstance(item, Plain):
                parts.append(item.text)
        text = "\n".join(part.strip() for part in parts if part.strip()).strip()
        if text:
            return text
    return None


def parse_reply_selection(text: str) -> list[int] | None:
    normalized = str(text or "").strip()
    if not normalized or not _SELECTION_RE.fullmatch(normalized):
        return None
    seen: set[int] = set()
    results: list[int] = []
    for raw in re.split(r"[\s,，、]+", normalized):
        if not raw:
            continue
        value = int(raw)
        if value <= 0 or value in seen:
            continue
        seen.add(value)
        results.append(value)
    return results or None


def parse_reply_target(text: str) -> ReplyFavoriteTarget | None:
    normalized = str(text or "").strip()
    if not normalized:
        return None

    lines = [line.rstrip() for line in normalized.splitlines()]
    first_line = next((line.strip() for line in lines if line.strip()), "")
    if not first_line:
        return None
    if first_line.startswith("【立即检查】共执行"):
        return ReplyFavoriteTarget(
            source="batch_manual_check",
            items=[],
            error_message="当前引用的是批量立即检查结果，暂不支持直接回复序号收藏，请引用单条推荐列表消息。",
        )
    if not first_line.startswith(_SUPPORTED_HEADERS):
        return None

    items: list[ReplyFavoriteItem] = []
    current_index: int | None = None
    current_title: str | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        item_match = _INDEX_LINE_RE.match(line)
        if item_match:
            current_index = int(item_match.group(1))
            current_title = item_match.group(2).strip()
            continue
        if current_index is None or current_title is None:
            continue
        link_match = _LINK_LINE_RE.match(line)
        if not link_match:
            continue
        url = link_match.group(1).strip()
        items.append(
            ReplyFavoriteItem(
                index=current_index,
                title=current_title,
                url=url,
                item_id=_extract_item_id_from_url(url),
            )
        )
        current_index = None
        current_title = None

    if not items:
        return ReplyFavoriteTarget(
            source="recommendation",
            items=[],
            error_message="引用的推荐消息里没有可解析的商品链接，暂时无法执行收藏。",
        )
    return ReplyFavoriteTarget(source="recommendation", items=items)


def map_reply_selection(
    target: ReplyFavoriteTarget,
    selections: list[int],
) -> tuple[list[ReplyFavoriteItem], list[int]]:
    mapping = {item.index: item for item in target.items}
    selected: list[ReplyFavoriteItem] = []
    invalid: list[int] = []
    for value in selections:
        item = mapping.get(value)
        if item is None:
            invalid.append(value)
            continue
        selected.append(item)
    return selected, invalid


def _extract_item_id_from_url(url: str) -> str | None:
    match = re.search(r"(?:[?&](?:id|item_id|itemId|auctionId)=|item(?:_id)?[=/])(\d+)", url)
    if match:
        return match.group(1)
    return None
