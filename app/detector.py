from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PriceDropDecision:
    triggered: bool
    drop_abs: float
    drop_pct: float
    # 当前价格是否低于历史最低价（含本次降价前的所有记录）
    below_hist_min: bool = False


@dataclass(slots=True)
class EventPayload:
    event_type: str
    keyword: str
    item_id: str
    title: str
    price: float
    url: str
    publish_time: int | None
    observed_at: int
    drop_abs: float | None = None
    drop_pct: float | None = None
    last_price: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "event_type": self.event_type,
            "keyword": self.keyword,
            "item_id": self.item_id,
            "title": self.title,
            "price": round(float(self.price), 2),
            "url": self.url,
            "publish_time": self.publish_time,
            "observed_at": self.observed_at,
        }
        if self.drop_abs is not None:
            payload["drop_abs"] = round(float(self.drop_abs), 2)
        if self.drop_pct is not None:
            payload["drop_pct"] = round(float(self.drop_pct), 6)
        if self.last_price is not None:
            payload["last_price"] = round(float(self.last_price), 2)
        return payload


def within_new_window(
    publish_time: int | None,
    now_ts: int,
    window_sec: int,
) -> bool:
    if window_sec <= 0:
        return True
    if publish_time is None:
        return True
    return publish_time >= now_ts - window_sec


def evaluate_price_drop(
    last_price: float | None,
    current_price: float,
    abs_threshold: float,
    pct_threshold: float,
    hist_min: float | None = None,
) -> PriceDropDecision:
    if last_price is None or last_price <= 0:
        return PriceDropDecision(False, 0.0, 0.0)

    if current_price >= last_price:
        return PriceDropDecision(False, 0.0, 0.0)

    drop_abs = float(last_price - current_price)
    drop_pct = drop_abs / float(last_price)
    triggered = (drop_abs >= abs_threshold) or (drop_pct >= pct_threshold)
    # 判断当前价格是否突破历史最低价（排除 last_price 本身，看更早的记录）
    below_hist_min = hist_min is not None and hist_min > 0 and current_price < hist_min
    return PriceDropDecision(
        triggered=triggered,
        drop_abs=drop_abs,
        drop_pct=drop_pct,
        below_hist_min=below_hist_min,
    )


def in_cooldown(last_sent_at: int | None, now_ts: int, cooldown_sec: int) -> bool:
    if cooldown_sec <= 0:
        return False
    if last_sent_at is None:
        return False
    return (now_ts - last_sent_at) < cooldown_sec


def build_payload_hash(payload: EventPayload | dict[str, Any]) -> str:
    data = payload.to_dict() if isinstance(payload, EventPayload) else payload
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
