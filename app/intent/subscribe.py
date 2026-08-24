"""Deterministic subscribe-intent parser.

Natural-language lines like 「订阅淘宝的 总统黄油」 used to fall through
to AstrBot's default LLM. This module classifies those messages and
extracts (platform, keyword) without calling a model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO

_PLATFORM_ALIASES: dict[str, str] = {
    "淘宝": PLATFORM_TAOBAO,
    "taobao": PLATFORM_TAOBAO,
    "闲鱼": PLATFORM_GOOFISH,
    "咸鱼": PLATFORM_GOOFISH,
    "goofish": PLATFORM_GOOFISH,
}

# After wake_prefix strip, command-group messages look like: 闲鱼 订阅 ...
_GROUP_PREFIX_RE = re.compile(
    r"^[／/!！]?\s*(?:闲鱼|goofish)\s+",
    re.IGNORECASE,
)

_QUESTION_RE = re.compile(r"^(如何|怎么|怎样|什么是|为啥|为什么|能否)")

# 订阅淘宝的 总统黄油 / 帮我监控一下闲鱼的 xxx
_NL_SUBSCRIBE_RE = re.compile(
    r"^(?:请|麻烦)?"
    r"(?:帮我|帮忙|替我|给我|为我)?"
    r"(?:我)?(?:想要|想)?"
    r"(?:把|给)?"
    r"(?:订阅|监控|蹲(?:一个|一下)?)"
    r"(?:一下|一个)?"
    r"(淘宝|闲鱼|咸鱼|taobao|goofish)?"
    r"(?:的|上的|上)?"
    r"\s*(.+)$",
    re.IGNORECASE,
)

# Platform as its own token or 「淘宝的xxx」; do not steal 「淘宝店」.
_LEAD_PLATFORM_RE = re.compile(
    r"^(淘宝|闲鱼|咸鱼|taobao|goofish)(?:的|上的|上|(?=\s)|$)\s*(.*)$",
    re.IGNORECASE,
)

_SUBSCRIBE_VERBS = frozenset({"订阅", "subscribe", "watch"})

KNOWN_COMMANDS = frozenset(
    {
        "订阅",
        "subscribe",
        "watch",
        "退订",
        "unsubscribe",
        "unwatch",
        "列表",
        "list",
        "暂停",
        "pause",
        "恢复",
        "resume",
        "立即检查",
        "checknow",
        "run",
        "查询",
        "query",
        "search",
        "inspect",
        "登录",
        "login",
        "auth",
        "登录完成",
        "login_done",
        "auth_done",
        "登录取消",
        "login_cancel",
        "auth_cancel",
        "明细",
        "detail",
        "items",
        "状态",
        "status",
    }
)

_MULTIWORD_COMMANDS = ("立即检查", "登录完成", "登录取消")

_KEYWORD_BLOCKLIST = frozenset(
    {
        "会员",
        "通知",
        "消息",
        "功能",
        "服务",
        "频道",
        "号",
        "一下",
        "这个",
        "那个",
    }
)

KIND_NONE = "none"
KIND_KNOWN_COMMAND = "known_command"
KIND_SUBSCRIBE = "subscribe"
KIND_UNKNOWN_PREFIX = "unknown_prefix"


@dataclass(slots=True, frozen=True)
class SubscribeIntent:
    keyword: str
    platform: str
    interval_sec: int = 0
    pages: int = 0


@dataclass(slots=True, frozen=True)
class ClassifiedMessage:
    kind: str
    intent: SubscribeIntent | None = None


def strip_wrappers(text: str) -> str:
    """Peel decorative quotes the README examples use, e.g. 「订阅淘宝的 xx」."""
    raw = str(text or "").strip()
    wrappers = (
        ("「", "」"),
        ("『", "』"),
        ("“", "”"),
        ("‘", "’"),
        ('"', '"'),
        ("'", "'"),
        ("（", "）"),
        ("(", ")"),
    )
    changed = True
    while changed and len(raw) >= 2:
        changed = False
        for left, right in wrappers:
            if raw.startswith(left) and raw.endswith(right):
                raw = raw[len(left) : -len(right)].strip()
                changed = True
                break
    return raw


def classify_goofish_message(text: str) -> ClassifiedMessage:
    """Classify a chat line into command / subscribe / unknown / ignore."""
    raw = strip_wrappers(text)
    if not raw:
        return ClassifiedMessage(KIND_NONE)
    if _QUESTION_RE.match(raw):
        return ClassifiedMessage(KIND_NONE)

    group_match = _GROUP_PREFIX_RE.match(raw)
    if group_match:
        rest = raw[group_match.end() :].strip()
        if not rest:
            return ClassifiedMessage(KIND_KNOWN_COMMAND)
        for cmd in _MULTIWORD_COMMANDS:
            if rest == cmd or rest.startswith(f"{cmd} "):
                return ClassifiedMessage(KIND_KNOWN_COMMAND)
        first = rest.split(None, 1)[0]
        if first.lower() in {item.lower() for item in KNOWN_COMMANDS}:
            return ClassifiedMessage(KIND_KNOWN_COMMAND)
        intent = parse_subscribe_text(rest)
        if intent is not None:
            return ClassifiedMessage(KIND_SUBSCRIBE, intent)
        return ClassifiedMessage(KIND_UNKNOWN_PREFIX)

    intent = parse_subscribe_text(raw)
    if intent is not None:
        return ClassifiedMessage(KIND_SUBSCRIBE, intent)
    return ClassifiedMessage(KIND_NONE)


def parse_subscribe_command(rest: str) -> SubscribeIntent | None:
    """Parse the remainder of `/闲鱼 订阅 ...`."""
    return parse_subscribe_text(rest, require_verb=False)


def parse_subscribe_text(
    text: str,
    *,
    require_verb: bool = True,
) -> SubscribeIntent | None:
    raw = strip_wrappers(text)
    if not raw:
        return None

    platform = ""
    if raw.split(None, 1)[0].lower() in _SUBSCRIBE_VERBS:
        raw = raw.split(None, 1)[1].strip() if " " in raw.strip() else ""
        require_verb = False
    elif require_verb:
        match = _NL_SUBSCRIBE_RE.match(raw)
        if match is None:
            return None
        platform = _PLATFORM_ALIASES.get((match.group(1) or "").lower(), "")
        raw = (match.group(2) or "").strip()

    if not raw:
        return None

    interval_sec, pages, raw = _peel_trailing_ints(raw)
    if not raw:
        return None

    if not platform:
        platform, raw = _split_platform_and_keyword(raw)
    if not raw or not _keyword_ok(raw):
        return None
    return SubscribeIntent(
        keyword=raw,
        platform=platform or PLATFORM_GOOFISH,
        interval_sec=interval_sec,
        pages=pages,
    )


def _peel_trailing_ints(text: str) -> tuple[int, int, str]:
    """Keep `/闲鱼 订阅 <kw> [interval_sec] [pages]` positional semantics."""
    parts = text.split()
    interval_sec = 0
    pages = 0
    if len(parts) >= 2 and parts[-1].isdigit() and parts[-2].isdigit():
        interval_sec = int(parts[-2])
        pages = int(parts[-1])
        parts = parts[:-2]
    elif parts and parts[-1].isdigit():
        interval_sec = int(parts[-1])
        parts = parts[:-1]
    return interval_sec, pages, " ".join(parts).strip()


def _split_platform_and_keyword(text: str) -> tuple[str, str]:
    match = _LEAD_PLATFORM_RE.match(text.strip())
    if match is None:
        return PLATFORM_GOOFISH, text.strip()
    platform = _PLATFORM_ALIASES[match.group(1).lower()]
    keyword = (match.group(2) or "").strip()
    if not keyword:
        return PLATFORM_GOOFISH, text.strip()
    return platform, keyword


def _keyword_ok(keyword: str) -> bool:
    value = keyword.strip()
    if not value or value.lower() in {item.lower() for item in KNOWN_COMMANDS}:
        return False
    if value in _KEYWORD_BLOCKLIST:
        return False
    return True
