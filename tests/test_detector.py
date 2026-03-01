from __future__ import annotations

from data.plugins.astrbot_plugin_goofish_catcher.app.detector import (
    EventPayload,
    build_payload_hash,
    evaluate_price_drop,
    in_cooldown,
    within_new_window,
)


def test_within_new_window():
    now_ts = 1_700_000_000
    assert within_new_window(now_ts, now_ts, 60)
    assert within_new_window(now_ts - 30, now_ts, 60)
    assert not within_new_window(now_ts - 61, now_ts, 60)
    assert within_new_window(None, now_ts, 60)


def test_evaluate_price_drop_abs_and_pct():
    decision = evaluate_price_drop(100.0, 90.0, abs_threshold=5.0, pct_threshold=0.2)
    assert decision.triggered
    assert round(decision.drop_abs, 2) == 10.0
    assert round(decision.drop_pct, 2) == 0.1

    decision_pct = evaluate_price_drop(
        100.0, 70.0, abs_threshold=40.0, pct_threshold=0.2
    )
    assert decision_pct.triggered
    assert round(decision_pct.drop_pct, 2) == 0.3

    decision_no = evaluate_price_drop(100.0, 98.0, abs_threshold=5.0, pct_threshold=0.1)
    assert not decision_no.triggered


def test_in_cooldown():
    now_ts = 1_700_000_000
    assert in_cooldown(now_ts - 10, now_ts, 30)
    assert not in_cooldown(now_ts - 31, now_ts, 30)
    assert not in_cooldown(None, now_ts, 30)
    assert not in_cooldown(now_ts - 1, now_ts, 0)


def test_payload_hash_stable():
    payload = EventPayload(
        event_type="NEW",
        keyword="显卡",
        item_id="123",
        title="RTX 4070",
        price=3000.0,
        url="https://www.goofish.com/item?id=123",
        publish_time=1_700_000_000,
        observed_at=1_700_000_001,
    )
    h1 = build_payload_hash(payload)
    h2 = build_payload_hash(payload.to_dict())
    assert h1 == h2
