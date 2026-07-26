"""意图层（阶段 2.x）：自然语言需求 → PurchaseIntent 降级链。"""

from .engine import DegradationLevel, PurchaseIntent, parse_intent

__all__ = [
    "DegradationLevel",
    "PurchaseIntent",
    "parse_intent",
]
