from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(slots=True)
class Subscription:
    id: int
    umo: str
    keyword: str
    interval_sec: int
    pages: int
    recommend_max_price: float | None
    drop_abs: float
    drop_pct: float
    new_window_sec: int
    cooldown_sec: int
    enabled: bool
    paused_reason: str | None
    last_run_at: int | None
    next_run_at: int | None
    consecutive_failures: int


@dataclass(slots=True)
class ExistingItem:
    sub_id: int
    item_id: str
    title: str
    url: str
    publish_time: int | None
    first_seen_at: int
    last_seen_at: int
    last_price: float | None


@dataclass(slots=True)
class NormalizedItem:
    item_id: str
    title: str
    price: float
    url: str
    publish_time: int | None = None
    raw: dict[str, Any] | None = None


@dataclass(slots=True)
class RecommendationCandidate:
    event_type: str
    keyword: str
    item_id: str
    title: str
    price: float
    url: str
    publish_time: int | None
    observed_at: int
    last_price: float | None = None
    drop_abs: float | None = None
    drop_pct: float | None = None
    payload_hash: str | None = None
    notification_meta: dict[str, Any] | None = None


@dataclass(slots=True)
class RecommendationItem:
    item_id: str
    score: float
    reason: str
    risk: str
    title: str
    price: float
    url: str


@dataclass(slots=True)
class RecommendationResult:
    keyword: str
    summary: str
    top: list[RecommendationItem]
    total_candidates: int
    used_llm: bool
    fallback_reason: str | None = None


@dataclass(slots=True)
class FavoriteItemResult:
    status: str
    url: str
    item_id: str | None = None
    title: str | None = None


class ProviderErrorCode(str, Enum):
    DEPENDENCY_MISSING = "DEPENDENCY_MISSING"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CAPTCHA = "CAPTCHA"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    PARSE_ERROR = "PARSE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN = "UNKNOWN"


class ProviderError(Exception):
    def __init__(
        self,
        code: ProviderErrorCode,
        message: str,
        retry_after_sec: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retry_after_sec = retry_after_sec

    def __str__(self) -> str:
        if self.retry_after_sec is None:
            return f"{self.code}: {self.message}"
        return f"{self.code}: {self.message} (retry_after={self.retry_after_sec}s)"
