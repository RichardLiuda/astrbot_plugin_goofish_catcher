from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# 平台标识。现有数据全部属于闲鱼；多平台改造（阶段 0 起）逐步引入 "taobao" 等。
DEFAULT_PLATFORM = "goofish"


@dataclass(slots=True)
class SearchFilters:
    price_lower: float | None = None
    price_upper: float | None = None
    personal_only: bool = False
    free_shipping: bool = False
    new_publish_option: str | None = None
    region: str | None = None

    def normalized(self) -> "SearchFilters":
        new_publish = (self.new_publish_option or "").strip()
        region = (self.region or "").strip()
        return SearchFilters(
            price_lower=self.price_lower if self.price_lower and self.price_lower > 0 else None,
            price_upper=self.price_upper if self.price_upper and self.price_upper > 0 else None,
            personal_only=bool(self.personal_only),
            free_shipping=bool(self.free_shipping),
            new_publish_option=new_publish or None,
            region=region or None,
        )

    def to_dict(self) -> dict[str, Any]:
        filters = self.normalized()
        return {
            "price_lower": filters.price_lower,
            "price_upper": filters.price_upper,
            "personal_only": filters.personal_only,
            "free_shipping": filters.free_shipping,
            "new_publish_option": filters.new_publish_option,
            "region": filters.region,
        }


@dataclass(slots=True)
class DeepAnalysisResult:
    item_id: str
    analyzed_at: int
    status: str
    credit_status: str
    credit_reason: str
    summary: str
    risk: str
    image_urls: list[str]
    seller_name: str | None = None
    seller_id: str | None = None
    seller_credit: str | None = None
    want_count: int | None = None
    browse_count: int | None = None
    raw: dict[str, Any] | None = None

    @property
    def rejected(self) -> bool:
        return self.status == "rejected" or self.credit_status == "bad"

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "analyzed_at": self.analyzed_at,
            "status": self.status,
            "credit_status": self.credit_status,
            "credit_reason": self.credit_reason,
            "summary": self.summary,
            "risk": self.risk,
            "image_urls": list(self.image_urls),
            "seller_name": self.seller_name,
            "seller_id": self.seller_id,
            "seller_credit": self.seller_credit,
            "want_count": self.want_count,
            "browse_count": self.browse_count,
            "raw": self.raw,
        }


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
    price_min: float | None = None
    price_max: float | None = None
    personal_only: bool = False
    free_shipping: bool = False
    new_publish_option: str | None = None
    region: str | None = None
    platform: str = DEFAULT_PLATFORM

    def search_filters(self) -> SearchFilters:
        return SearchFilters(
            price_lower=self.price_min,
            price_upper=self.price_max,
            personal_only=self.personal_only,
            free_shipping=self.free_shipping,
            new_publish_option=self.new_publish_option,
            region=self.region,
        ).normalized()


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
    platform: str = DEFAULT_PLATFORM


@dataclass(slots=True)
class MarketPrice:
    """某关键词的市场均价快照，通过 EMA 滚动维护。"""

    keyword: str
    ema_price: float       # 指数移动均价（平滑后的市场参考价）
    sample_count: int      # 累计参与计算的样本数（价格点数）
    updated_at: int        # 最后一次更新的 Unix 时间戳
    platform: str = DEFAULT_PLATFORM


@dataclass(slots=True)
class PriceStats:
    """从 price_history 聚合出的历史价格统计。"""

    item_id: str
    hist_min: float
    hist_max: float
    hist_avg: float
    hist_count: int  # 历史记录点数


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
    # 历史价格统计（可选，有则在推荐评分中使用）
    hist_min: float | None = None
    hist_avg: float | None = None
    # 市场均价（EMA，跨商品、跨时间的关键词级别均价）
    market_price: float | None = None
    deep_analysis: DeepAnalysisResult | None = None


@dataclass(slots=True)
class RecommendationItem:
    item_id: str
    score: float
    reason: str
    risk: str
    title: str
    price: float
    url: str
    deep_analysis: DeepAnalysisResult | None = None


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
