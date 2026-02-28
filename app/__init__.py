"""Application modules for the Goofish catcher plugin."""

from .config import PluginSettings, load_plugin_settings
from .detector import (
    EventPayload,
    PriceDropDecision,
    build_payload_hash,
    evaluate_price_drop,
    in_cooldown,
    within_new_window,
)
from .types import (
    ExistingItem,
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
    RecommendationCandidate,
    RecommendationItem,
    RecommendationResult,
    Subscription,
)

__all__ = [
    "EventPayload",
    "ExistingItem",
    "NormalizedItem",
    "PluginSettings",
    "PriceDropDecision",
    "ProviderError",
    "ProviderErrorCode",
    "RecommendationCandidate",
    "RecommendationItem",
    "RecommendationResult",
    "Subscription",
    "build_payload_hash",
    "evaluate_price_drop",
    "in_cooldown",
    "load_plugin_settings",
    "within_new_window",
]
