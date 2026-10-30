"""Group/conversation allow and deny lists for inbound plugin requests."""

from __future__ import annotations

import logging
import re
from typing import Any

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

# Longer prefixes first so "群聊:" is not partially consumed by "群:".
_ENTRY_PREFIXES = (
    "unified_msg_origin:",
    "umo:",
    "group:",
    "group_",
    "群聊:",
    "群:",
    "session:",
    "对话:",
    "私聊:",
    "friend:",
    "user:",
)
_ENTRY_SPLIT = re.compile(r"[\s,，;；]+")

CHAT_BLOCKED_TOOL_MESSAGE = (
    "当前会话不在闲鱼助手可用范围内，未执行任何操作。"
    "请告诉用户此对话未启用该功能，不要编造搜索或订阅结果。"
)

_active_whitelist: tuple[str, ...] = ()
_active_blacklist: tuple[str, ...] = ()


def parse_chat_entries(raw: Any) -> tuple[str, ...]:
    """Normalize config values into comparable chat tokens.

    Accepts a list or a string split by whitespace, commas, or newlines.
    Each token may be a group id, a private-chat user id, a unified message
    origin, or the same values with a ``group:`` / ``umo:`` style prefix.
    """
    if raw is None:
        return ()
    if isinstance(raw, str):
        pieces = _ENTRY_SPLIT.split(raw)
    elif isinstance(raw, (list, tuple, set)):
        pieces = []
        for item in raw:
            pieces.extend(_ENTRY_SPLIT.split(str(item)))
    else:
        pieces = _ENTRY_SPLIT.split(str(raw))

    seen: list[str] = []
    found: set[str] = set()
    for piece in pieces:
        token = _normalize_entry(piece)
        if not token or token in found:
            continue
        found.add(token)
        seen.append(token)
    return tuple(seen)


def chat_match_keys(
    *,
    group_id: str = "",
    unified_msg_origin: str = "",
    sender_id: str = "",
    is_private: bool = False,
) -> frozenset[str]:
    """Identifiers that can match a configured allow/deny entry."""
    keys: set[str] = set()

    def add(value: str) -> None:
        token = _normalize_entry(value)
        if token:
            keys.add(token)

    add(group_id)
    umo = str(unified_msg_origin or "").strip()
    add(umo)
    parts = umo.split(":")
    if len(parts) >= 3:
        session_id = parts[-1].strip()
        message_type = parts[-2].strip()
        add(session_id)
        if message_type and session_id:
            add(f"{message_type}:{session_id}")
    if is_private:
        add(sender_id)
    return frozenset(keys)


def is_chat_allowed(
    whitelist: Any,
    blacklist: Any,
    *,
    group_id: str = "",
    unified_msg_origin: str = "",
    sender_id: str = "",
    is_private: bool = False,
) -> bool:
    """Return whether this chat may use the plugin.

    Empty lists do not restrict. A blacklist hit always denies. When the
    whitelist is non-empty, the chat must also match it.
    """
    allowed_entries = parse_chat_entries(whitelist)
    denied_entries = parse_chat_entries(blacklist)
    if not allowed_entries and not denied_entries:
        return True
    keys = chat_match_keys(
        group_id=group_id,
        unified_msg_origin=unified_msg_origin,
        sender_id=sender_id,
        is_private=is_private,
    )
    if keys & set(denied_entries):
        return False
    if allowed_entries and not (keys & set(allowed_entries)):
        return False
    return True


def subscription_chat_allowed(
    subscription: Any,
    *,
    unified_msg_origin: str = "",
    group_id: str = "",
    sender_id: str = "",
    is_private: bool = False,
) -> bool:
    """Whether this chat may act on a single subscription or receive its pushes.

    Uses the subscription's own ``allow_umos`` / ``deny_umos``; both empty means
    the subscription inherits the global rules only.
    """
    allow = getattr(subscription, "allow_umos", ()) or ()
    deny = getattr(subscription, "deny_umos", ()) or ()
    if not allow and not deny:
        return True
    return is_chat_allowed(
        allow,
        deny,
        group_id=group_id,
        unified_msg_origin=unified_msg_origin,
        sender_id=sender_id,
        is_private=is_private,
    )


def event_allowed_for_subscription(event: Any, subscription: Any) -> bool:
    """Apply a subscription's own chat lists to an incoming message event."""
    group_id = _event_text(event, "get_group_id")
    private = _event_is_private(event, group_id)
    return subscription_chat_allowed(
        subscription,
        group_id=group_id,
        unified_msg_origin=str(getattr(event, "unified_msg_origin", "") or ""),
        sender_id=_event_text(event, "get_sender_id") if private else "",
        is_private=private,
    )


def set_active_chat_rules(whitelist: Any, blacklist: Any) -> None:
    """Publish the lists used by message filters and outbound checks."""
    global _active_whitelist, _active_blacklist
    _active_whitelist = parse_chat_entries(whitelist)
    _active_blacklist = parse_chat_entries(blacklist)


def active_chat_allowed(event: Any) -> bool:
    """Apply the current lists to an AstrBot message event."""
    if not _active_whitelist and not _active_blacklist:
        return True
    group_id = _event_text(event, "get_group_id")
    private = _event_is_private(event, group_id)
    allowed = is_chat_allowed(
        _active_whitelist,
        _active_blacklist,
        group_id=group_id,
        unified_msg_origin=str(getattr(event, "unified_msg_origin", "") or ""),
        sender_id=_event_text(event, "get_sender_id") if private else "",
        is_private=private,
    )
    if not allowed:
        logger.debug(
            "[goofish_catcher] skip chat outside access list group_id=%s umo=%s",
            group_id,
            getattr(event, "unified_msg_origin", ""),
        )
    return allowed


def _normalize_entry(raw: str) -> str:
    text = str(raw or "").strip().casefold()
    if not text:
        return ""
    for prefix in _ENTRY_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :].strip()
            break
    return text


def _event_text(event: Any, method_name: str) -> str:
    method = getattr(event, method_name, None)
    if not callable(method):
        return ""
    try:
        return str(method() or "").strip()
    except Exception:
        return ""


def _event_is_private(event: Any, group_id: str) -> bool:
    method = getattr(event, "is_private_chat", None)
    if callable(method):
        try:
            return bool(method())
        except Exception:
            pass
    return not group_id
