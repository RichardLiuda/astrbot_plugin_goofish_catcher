from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TrendBucket:
    day: str
    new_count: int
    price_drop_count: int


@dataclass(slots=True)
class OverviewAlert:
    level: str
    keyword: str
    message: str
    occurred_at: int | None
    subscription_id: int | None = None


@dataclass(slots=True)
class AdminOverview:
    provider_mode: str
    provider_available: bool
    provider_error: str | None
    scheduler_running: bool
    queue_size: int
    inflight: int
    workers: int
    enabled_subscriptions: int
    paused_subscriptions: int
    total_subscriptions: int
    success_runs_24h: int
    failed_runs_24h: int
    success_rate_24h: float
    recent_alerts: list[OverviewAlert] = field(default_factory=list)
    trends: list[TrendBucket] = field(default_factory=list)
    provider_health: dict[str, Any] | None = None
    provider_health_checked_at: int | None = None


@dataclass(slots=True)
class SubscriptionSummary:
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
class SubscriptionOption:
    id: int
    umo: str
    keyword: str
    enabled: bool
    paused_reason: str | None


@dataclass(slots=True)
class NotificationRecord:
    sub_id: int
    keyword: str
    umo: str
    item_id: str
    event_type: str
    sent_at: int
    meta: dict[str, Any] | None


@dataclass(slots=True)
class PriceHistoryPoint:
    sub_id: int
    keyword: str
    umo: str
    item_id: str
    price: float
    observed_at: int
    source: str


@dataclass(slots=True)
class FetchRunSummary:
    id: int
    sub_id: int
    keyword: str
    umo: str
    started_at: int
    finished_at: int | None
    status: str
    err_type: str | None
    err_msg: str | None
    items_count: int


@dataclass(slots=True)
class ItemSummary:
    item_id: str
    title: str
    url: str
    price: float
    publish_time: int | None
    first_seen_at: int
    last_seen_at: int
    subscription_count: int
    latest_event_type: str | None


@dataclass(slots=True)
class SubscriptionItemSummary:
    sub_id: int
    keyword: str
    umo: str
    enabled: bool
    paused_reason: str | None
    item_id: str
    title: str
    url: str
    price: float
    publish_time: int | None
    first_seen_at: int
    last_seen_at: int
    latest_event_type: str | None


@dataclass(slots=True)
class RelatedSubscription:
    sub_id: int
    keyword: str
    umo: str
    enabled: bool
    paused_reason: str | None
    last_seen_at: int
    last_price: float | None


@dataclass(slots=True)
class ItemDetail:
    item: ItemSummary
    subscriptions: list[RelatedSubscription] = field(default_factory=list)
    price_history: list[PriceHistoryPoint] = field(default_factory=list)
    notifications: list[NotificationRecord] = field(default_factory=list)
    fetch_runs: list[FetchRunSummary] = field(default_factory=list)


@dataclass(slots=True)
class ProviderHealthSnapshot:
    ok: bool
    provider: str
    auth: str | None
    storage_state: bool | None
    checked_at: int | None
    details: dict[str, Any] | None = None


@dataclass(slots=True)
class EditablePluginConfig:
    values: dict[str, Any]
    groups: list[dict[str, Any]]
    schema: dict[str, Any]
    overlay_path: str


@dataclass(slots=True)
class QueryPreviewItem:
    item_id: str
    title: str
    price: float
    url: str
    score: float
    reason: str
    risk: str


@dataclass(slots=True)
class QueryPreview:
    keyword: str
    page_count: int
    raw_total: int
    filtered_total: int
    filter_mode: str
    summary: str
    used_llm: bool
    fallback_reason: str | None
    items: list[QueryPreviewItem] = field(default_factory=list)
