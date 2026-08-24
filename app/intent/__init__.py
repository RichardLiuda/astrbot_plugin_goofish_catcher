"""意图层（阶段 2.x）：自然语言需求 → PurchaseIntent 降级链。"""

from .engine import DegradationLevel, PurchaseIntent, parse_intent
from .subscribe import (
    KIND_KNOWN_COMMAND,
    KIND_NONE,
    KIND_SUBSCRIBE,
    KIND_UNKNOWN_PREFIX,
    ClassifiedMessage,
    SubscribeIntent,
    classify_goofish_message,
    parse_subscribe_command,
    parse_subscribe_text,
)

__all__ = [
    "ClassifiedMessage",
    "DegradationLevel",
    "KIND_KNOWN_COMMAND",
    "KIND_NONE",
    "KIND_SUBSCRIBE",
    "KIND_UNKNOWN_PREFIX",
    "PurchaseIntent",
    "SubscribeIntent",
    "classify_goofish_message",
    "parse_intent",
    "parse_subscribe_command",
    "parse_subscribe_text",
]
