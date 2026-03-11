from __future__ import annotations

import time
from pathlib import Path

import pytest

from data.plugins.astrbot_plugin_goofish_catcher.app.config import PluginSettings
from data.plugins.astrbot_plugin_goofish_catcher.app.scheduler import (
    MonitoringScheduler,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.types import (
    ExistingItem,
    NormalizedItem,
    RecommendationItem,
    RecommendationResult,
    Subscription,
)


def _make_settings(tmp_path: Path) -> PluginSettings:
    return PluginSettings(
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path,
        db_path=tmp_path / "test.db",
        provider_mode="playwright_local",
        default_interval_sec=600,
        default_pages=1,
        max_pages=2,
        scheduler_tick_sec=15,
        max_concurrency=1,
        fetch_timeout_sec=20,
        max_retries=3,
        retry_base_sec=30,
        retry_max_sec=900,
        default_new_window_sec=1800,
        default_drop_abs=50.0,
        default_drop_pct=0.05,
        default_cooldown_sec=3600,
        playwright_storage_state_path=None,
        playwright_headless=True,
        playwright_block_assets=True,
        playwright_force_direct=True,
        webhook_url=None,
        remote_base_url=None,
        remote_api_key=None,
        remote_headers_json=None,
        remote_timeout_sec=20,
        remote_healthcheck_on_init=True,
        remote_healthcheck_timeout_sec=10,
        queue_max_size=256,
        llm_enabled=True,
        llm_provider_id=None,
        llm_prefilter_provider_id=None,
        llm_timeout_sec=25,
        llm_top_k=3,
        llm_max_candidates=20,
        llm_recommend_prompt=(
            "关键词: $keyword\n候选条目（最多推荐 $top_k 条）:\n$candidates_json\n\n"
            "请输出 JSON，字段必须包含 summary 和 top。"
        ),
        llm_prefilter_enabled=True,
        llm_prefilter_timeout_sec=6,
        llm_prefilter_max_items=30,
        llm_prefilter_prompt=(
            "关键词: $keyword\n商品列表: $items_json\n"
            "请只做“商品相关性筛选”，忽略价格、功能优劣、成色。\n"
            '输出 JSON: {"keep_item_ids": ["..."]}'
        ),
    )


class _FakeStorage:
    def __init__(self):
        self.items: dict[tuple[int, str], ExistingItem] = {}
        self.filtered_items: set[tuple[int, str]] = set()
        self.notifications: set[tuple[int, str, str, str]] = set()
        self.recommendations_written = 0

    async def create_fetch_run(self, sub_id: int, started_at: int) -> int:
        return 1

    async def finish_fetch_run(self, *args, **kwargs) -> None:
        return None

    async def update_schedule_success(self, *args, **kwargs) -> None:
        return None

    async def update_schedule_failure(self, *args, **kwargs) -> None:
        return None

    async def pause_subscription(self, *args, **kwargs) -> None:
        return None

    async def get_item(self, sub_id: int, item_id: str) -> ExistingItem | None:
        return self.items.get((sub_id, item_id))

    async def get_items_by_ids(
        self, sub_id: int, item_ids: list[str]
    ) -> dict[str, ExistingItem]:
        return {
            item_id: self.items[(sub_id, item_id)]
            for item_id in item_ids
            if (sub_id, item_id) in self.items
        }

    async def get_filtered_item_ids(self, sub_id: int, item_ids: list[str]) -> set[str]:
        return {
            item_id
            for item_id in item_ids
            if (sub_id, item_id) in self.filtered_items
        }

    async def insert_item(self, sub_id: int, item: NormalizedItem, now_ts: int) -> None:
        self.items[(sub_id, item.item_id)] = ExistingItem(
            sub_id=sub_id,
            item_id=item.item_id,
            title=item.title,
            url=item.url,
            publish_time=item.publish_time,
            first_seen_at=now_ts,
            last_seen_at=now_ts,
            last_price=item.price,
        )

    async def upsert_items_bulk(
        self, sub_id: int, items: list[NormalizedItem], now_ts: int
    ) -> None:
        for item in items:
            if (sub_id, item.item_id) in self.items:
                await self.update_item(sub_id, item, now_ts)
            else:
                await self.insert_item(sub_id, item, now_ts)

    async def upsert_filtered_items_bulk(
        self, sub_id: int, items: list[NormalizedItem], now_ts: int
    ) -> None:
        for item in items:
            self.filtered_items.add((sub_id, item.item_id))

    async def update_item(self, sub_id: int, item: NormalizedItem, now_ts: int) -> None:
        old = self.items[(sub_id, item.item_id)]
        self.items[(sub_id, item.item_id)] = ExistingItem(
            sub_id=sub_id,
            item_id=item.item_id,
            title=item.title,
            url=item.url,
            publish_time=item.publish_time or old.publish_time,
            first_seen_at=old.first_seen_at,
            last_seen_at=now_ts,
            last_price=item.price,
        )

    async def insert_price_history(self, *args, **kwargs) -> None:
        return None

    async def insert_price_history_bulk(self, *args, **kwargs) -> None:
        return None

    async def notification_hash_exists(
        self,
        sub_id: int,
        item_id: str,
        event_type: str,
        payload_hash: str,
    ) -> bool:
        return (sub_id, item_id, event_type, payload_hash) in self.notifications

    async def get_last_notification_sent_at(
        self, sub_id: int, item_id: str, event_type: str
    ) -> int | None:
        return None

    async def get_last_notification_sent_map(
        self, sub_id: int, item_ids: list[str], event_type: str
    ) -> dict[str, int]:
        return {}

    async def insert_notification(
        self,
        *,
        sub_id: int,
        item_id: str,
        event_type: str,
        payload_hash: str,
        sent_at: int,
        meta: dict | None = None,
    ) -> None:
        self.notifications.add((sub_id, item_id, event_type, payload_hash))

    async def insert_notifications_bulk(
        self,
        rows: list[tuple[int, str, str, str, int, dict | None]],
    ) -> None:
        for sub_id, item_id, event_type, payload_hash, _, _ in rows:
            self.notifications.add((sub_id, item_id, event_type, payload_hash))


class _FakeProvider:
    async def search(self, *, keyword: str, pages: int, timeout_sec: int):
        now_ts = int(time.time())
        return [
            NormalizedItem(
                item_id="1001",
                title=f"{keyword} 新上架",
                price=6800.0,
                url="https://www.goofish.com/item?id=1001",
                publish_time=now_ts,
            )
        ]


class _FakeNotifier:
    def __init__(self, *, send_success: bool = True):
        self.summary_calls = 0
        self.send_success = send_success

    async def send_recommendation_summary(self, *, umo: str, recommendation):
        self.summary_calls += 1
        return self.send_success

    async def send_alert(self, *args, **kwargs):
        return True

    async def send_new(self, *args, **kwargs):
        raise AssertionError("send_new should not be called in summary mode")

    async def send_price_drop(self, *args, **kwargs):
        raise AssertionError("send_price_drop should not be called in summary mode")


class _FakeRecommender:
    def __init__(self):
        self.prefilter_calls = 0

    async def prefilter_items(self, *, umo: str, keyword: str, items: list):
        self.prefilter_calls += 1
        return items, "TEST"

    async def analyze(self, *, umo: str, keyword: str, candidates: list, top_k: int):
        assert len(candidates) >= 1
        return RecommendationResult(
            keyword=keyword,
            summary="推荐关注降价幅度更高的条目。",
            top=[
                RecommendationItem(
                    item_id=candidates[0].item_id,
                    score=88.0,
                    reason="降价幅度可观",
                    risk="注意验货",
                    title=candidates[0].title,
                    price=candidates[0].price,
                    url=candidates[0].url,
                )
            ],
            total_candidates=len(candidates),
            used_llm=False,
            fallback_reason="TEST",
        )


class _RejectingRecommender:
    def __init__(self):
        self.prefilter_calls = 0

    async def prefilter_items(self, *, umo: str, keyword: str, items: list):
        self.prefilter_calls += 1
        return [], "REJECT_ALL"

    async def analyze(self, *, umo: str, keyword: str, candidates: list, top_k: int):
        raise AssertionError("analyze should not be called when all items are filtered")


@pytest.mark.asyncio
async def test_scheduler_sends_summary_only(tmp_path: Path):
    storage = _FakeStorage()
    provider = _FakeProvider()
    notifier = _FakeNotifier()
    recommender = _FakeRecommender()
    scheduler = MonitoringScheduler(
        context=object(),
        settings=_make_settings(tmp_path),
        storage=storage,
        provider=provider,
        notifier=notifier,
        recommender=recommender,
    )
    sub = Subscription(
        id=1,
        umo="webchat:test",
        keyword="适马60-600",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=3600,
        cooldown_sec=3600,
        enabled=True,
        paused_reason=None,
        last_run_at=None,
        next_run_at=None,
        consecutive_failures=0,
    )

    await scheduler._process_subscription(sub, worker_idx=0)

    assert notifier.summary_calls == 1
    assert len(storage.notifications) >= 1


@pytest.mark.asyncio
async def test_scheduler_does_not_write_notifications_when_summary_send_fails(
    tmp_path: Path,
):
    storage = _FakeStorage()
    provider = _FakeProvider()
    notifier = _FakeNotifier(send_success=False)
    recommender = _FakeRecommender()
    scheduler = MonitoringScheduler(
        context=object(),
        settings=_make_settings(tmp_path),
        storage=storage,
        provider=provider,
        notifier=notifier,
        recommender=recommender,
    )
    sub = Subscription(
        id=1,
        umo="webchat:test",
        keyword="适马60-600",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=3600,
        cooldown_sec=3600,
        enabled=True,
        paused_reason=None,
        last_run_at=None,
        next_run_at=None,
        consecutive_failures=0,
    )

    await scheduler._process_subscription(sub, worker_idx=0)

    assert notifier.summary_calls == 1
    assert len(storage.notifications) == 0


@pytest.mark.asyncio
async def test_scheduler_skips_prefilter_for_previously_rejected_new_items(
    tmp_path: Path,
):
    storage = _FakeStorage()
    provider = _FakeProvider()
    notifier = _FakeNotifier()
    recommender = _RejectingRecommender()
    scheduler = MonitoringScheduler(
        context=object(),
        settings=_make_settings(tmp_path),
        storage=storage,
        provider=provider,
        notifier=notifier,
        recommender=recommender,
    )
    sub = Subscription(
        id=1,
        umo="webchat:test",
        keyword="camera",
        interval_sec=600,
        pages=1,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=3600,
        cooldown_sec=3600,
        enabled=True,
        paused_reason=None,
        last_run_at=None,
        next_run_at=None,
        consecutive_failures=0,
    )

    await scheduler._process_subscription(sub, worker_idx=0)
    await scheduler._process_subscription(sub, worker_idx=0)

    assert recommender.prefilter_calls == 1
    assert notifier.summary_calls == 0
    assert (sub.id, "1001") in storage.filtered_items
