from __future__ import annotations

import time
from pathlib import Path

import pytest

from data.plugins.astrbot_plugin_goofish_catcher.app.storage import SubscriptionStorage
from data.plugins.astrbot_plugin_goofish_catcher.app.types import NormalizedItem


@pytest.mark.asyncio
async def test_subscription_crud_and_schedule(tmp_path: Path):
    db_path = tmp_path / "test.db"
    storage = SubscriptionStorage(db_path)
    await storage.initialize()

    sub, created = await storage.upsert_subscription(
        umo="qq:group:123",
        keyword="显卡",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=1800,
        cooldown_sec=3600,
    )
    assert created
    assert sub.keyword == "显卡"

    sub2, created2 = await storage.upsert_subscription(
        umo="qq:group:123",
        keyword="显卡",
        interval_sec=300,
        pages=2,
        drop_abs=30.0,
        drop_pct=0.03,
        new_window_sec=1200,
        cooldown_sec=7200,
    )
    assert not created2
    assert sub2.interval_sec == 300
    assert sub2.pages == 2

    listed = await storage.list_subscriptions_by_umo("qq:group:123")
    assert len(listed) == 1

    now_ts = int(time.time())
    due = await storage.get_due_subscriptions(now_ts, limit=10)
    assert len(due) >= 1

    await storage.update_schedule_success(sub2.id, now_ts, sub2.interval_sec)
    updated = await storage.get_subscription_by_id(sub2.id)
    assert updated is not None
    assert updated.consecutive_failures == 0
    assert updated.next_run_at is not None

    await storage.update_schedule_failure(sub2.id, now_ts, 120)
    failed = await storage.get_subscription_by_id(sub2.id)
    assert failed is not None
    assert failed.consecutive_failures >= 1

    await storage.delete_subscription("qq:group:123", "显卡")
    listed_after = await storage.list_subscriptions_by_umo("qq:group:123")
    assert listed_after == []
    await storage.close()


@pytest.mark.asyncio
async def test_item_and_notification(tmp_path: Path):
    db_path = tmp_path / "test.db"
    storage = SubscriptionStorage(db_path)
    await storage.initialize()

    sub, _ = await storage.upsert_subscription(
        umo="qq:group:123",
        keyword="switch",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=1800,
        cooldown_sec=3600,
    )
    now_ts = int(time.time())
    item = NormalizedItem(
        item_id="1001",
        title="Switch OLED",
        price=1500.0,
        url="https://www.goofish.com/item?id=1001",
        publish_time=now_ts,
    )
    await storage.insert_item(sub.id, item, now_ts)
    got = await storage.get_item(sub.id, "1001")
    assert got is not None
    assert got.last_price == 1500.0

    await storage.insert_notification(
        sub_id=sub.id,
        item_id=item.item_id,
        event_type="NEW",
        payload_hash="abc123",
        sent_at=now_ts,
        meta={"x": 1},
    )
    exists = await storage.notification_hash_exists(
        sub.id, item.item_id, "NEW", "abc123"
    )
    assert exists

    sent_at = await storage.get_last_notification_sent_at(sub.id, item.item_id, "NEW")
    assert sent_at == now_ts

    snapshot_items, snapshot_total = await storage.list_items_by_snapshot(
        sub_id=sub.id,
        snapshot_ts=now_ts,
        limit=10,
    )
    assert snapshot_total == 1
    assert len(snapshot_items) == 1
    assert snapshot_items[0].item_id == "1001"
    await storage.close()


@pytest.mark.asyncio
async def test_snapshot_items_sorted_by_price_asc(tmp_path: Path):
    db_path = tmp_path / "test.db"
    storage = SubscriptionStorage(db_path)
    await storage.initialize()

    sub, _ = await storage.upsert_subscription(
        umo="qq:group:123",
        keyword="镜头",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=1800,
        cooldown_sec=3600,
    )
    now_ts = int(time.time())
    high = NormalizedItem(
        item_id="2001",
        title="高价镜头",
        price=6800.0,
        url="https://www.goofish.com/item?id=2001",
        publish_time=now_ts,
    )
    low = NormalizedItem(
        item_id="2002",
        title="低价镜头",
        price=5200.0,
        url="https://www.goofish.com/item?id=2002",
        publish_time=now_ts,
    )

    await storage.insert_item(sub.id, high, now_ts)
    await storage.insert_item(sub.id, low, now_ts)

    snapshot_items, snapshot_total = await storage.list_items_by_snapshot(
        sub_id=sub.id,
        snapshot_ts=now_ts,
        limit=10,
    )
    assert snapshot_total == 2
    assert [item.item_id for item in snapshot_items] == ["2002", "2001"]
    await storage.close()


@pytest.mark.asyncio
async def test_filtered_items_roundtrip(tmp_path: Path):
    db_path = tmp_path / "test.db"
    storage = SubscriptionStorage(db_path)
    await storage.initialize()

    sub, _ = await storage.upsert_subscription(
        umo="qq:group:123",
        keyword="camera",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=1800,
        cooldown_sec=3600,
    )
    now_ts = int(time.time())
    item = NormalizedItem(
        item_id="3001",
        title="Camera Body",
        price=5000.0,
        url="https://www.goofish.com/item?id=3001",
        publish_time=now_ts,
    )

    await storage.upsert_filtered_items_bulk(sub.id, [item], now_ts)
    filtered_ids = await storage.get_filtered_item_ids(sub.id, ["3001", "9999"])

    assert filtered_ids == {"3001"}
    await storage.close()
