from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Callable

from astrbot.api import logger
from astrbot.api.star import Context

from .config import PluginSettings
from .detector import (
    EventPayload,
    build_payload_hash,
    evaluate_price_drop,
    in_cooldown,
    within_new_window,
)
from .notifier import Notifier
from .provider import SearchProvider
from .recommender import GoofishRecommender
from .storage import SubscriptionStorage
from .types import (
    ProviderError,
    ProviderErrorCode,
    RecommendationCandidate,
    Subscription,
)

EVENT_NEW = "NEW"
EVENT_PRICE_DROP = "PRICE_DROP"


def calculate_retry_delay(
    *,
    failure_count: int,
    base_sec: int,
    max_sec: int,
    jitter_ratio: float = 0.2,
    rng: Callable[[], float] | None = None,
) -> int:
    if failure_count <= 0:
        return max(1, base_sec)

    no_jitter = base_sec * (2 ** (failure_count - 1))
    no_jitter = min(no_jitter, max_sec)
    generator = rng or random.random
    jitter = int(no_jitter * jitter_ratio * generator())
    return max(1, min(max_sec, no_jitter + jitter))


class MonitoringScheduler:
    def __init__(
        self,
        *,
        context: Context,
        settings: PluginSettings,
        storage: SubscriptionStorage,
        provider: SearchProvider,
        notifier: Notifier,
        recommender: GoofishRecommender,
    ) -> None:
        self.context = context
        self.settings = settings
        self.storage = storage
        self.provider = provider
        self.notifier = notifier
        self.recommender = recommender

        self._running = False
        self._queue: asyncio.Queue[int] = asyncio.Queue(maxsize=settings.queue_max_size)
        self._poll_task: asyncio.Task | None = None
        self._worker_tasks: list[asyncio.Task] = []
        self._inflight_sub_ids: set[int] = set()
        self._inflight_lock = asyncio.Lock()

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        if self._running:
            return
        self._running = True

        self._poll_task = asyncio.create_task(
            self._poll_loop(),
            name="goofish-catcher-poll",
        )
        worker_count = max(1, self.settings.max_concurrency)
        for idx in range(worker_count):
            self._worker_tasks.append(
                asyncio.create_task(
                    self._worker_loop(idx),
                    name=f"goofish-catcher-worker-{idx}",
                )
            )
        logger.info(
            "[goofish_catcher] scheduler started, workers=%s, tick=%ss",
            worker_count,
            self.settings.scheduler_tick_sec,
        )

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False

        tasks = [task for task in [self._poll_task, *self._worker_tasks] if task]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._poll_task = None
        self._worker_tasks.clear()
        self._inflight_sub_ids.clear()
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break
        logger.info("[goofish_catcher] scheduler stopped")

    async def enqueue_manual_check(self, sub_id: int) -> bool:
        return await self._enqueue_sub_id(sub_id)

    async def try_acquire_subscription(self, sub_id: int) -> bool:
        async with self._inflight_lock:
            if sub_id in self._inflight_sub_ids:
                return False
            self._inflight_sub_ids.add(sub_id)
            return True

    async def release_subscription(self, sub_id: int) -> None:
        await self._release_sub_id(sub_id)

    async def get_status(self) -> dict[str, int | bool]:
        enabled_count = await self.storage.count_enabled_subscriptions()
        return {
            "running": self._running,
            "queue_size": self._queue.qsize(),
            "inflight": len(self._inflight_sub_ids),
            "enabled_subscriptions": enabled_count,
            "workers": len(self._worker_tasks),
        }

    async def process_manual_fetch(
        self,
        *,
        sub: Subscription,
        items: list,
        now_ts: int,
    ) -> list[RecommendationCandidate]:
        """Process externally fetched items and keep storage/state consistent."""
        filtered_items, filter_mode = await self.recommender.prefilter_items(
            umo=sub.umo,
            keyword=sub.keyword,
            items=items,
        )
        logger.info(
            "[goofish_catcher] sub=%s manual prefilter %s -> %s (%s)",
            sub.id,
            len(items),
            len(filtered_items),
            filter_mode,
        )
        candidates = await self._process_items(sub, filtered_items, now_ts)
        await self.storage.update_schedule_success(sub.id, now_ts, sub.interval_sec)
        return candidates

    async def _enqueue_sub_id(self, sub_id: int) -> bool:
        async with self._inflight_lock:
            if sub_id in self._inflight_sub_ids:
                return False
            if self._queue.full():
                return False
            self._inflight_sub_ids.add(sub_id)

        try:
            self._queue.put_nowait(sub_id)
            return True
        except asyncio.QueueFull:
            async with self._inflight_lock:
                self._inflight_sub_ids.discard(sub_id)
            return False

    async def _release_sub_id(self, sub_id: int) -> None:
        async with self._inflight_lock:
            self._inflight_sub_ids.discard(sub_id)

    async def _poll_loop(self) -> None:
        while self._running:
            try:
                now_ts = int(time.time())
                due_subs = await self.storage.get_due_subscriptions(
                    now_ts,
                    limit=max(20, self.settings.max_concurrency * 20),
                )
                for sub in due_subs:
                    await self._enqueue_sub_id(sub.id)
                await asyncio.sleep(self.settings.scheduler_tick_sec)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(
                    "[goofish_catcher] poll loop crashed: %s",
                    exc,
                    exc_info=True,
                )
                await asyncio.sleep(min(5, self.settings.scheduler_tick_sec))

    async def _worker_loop(self, worker_idx: int) -> None:
        try:
            while self._running:
                try:
                    sub_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                try:
                    sub = await self.storage.get_subscription_by_id(sub_id)
                    if sub is None:
                        logger.info(
                            "[goofish_catcher] worker=%s skip missing sub_id=%s",
                            worker_idx,
                            sub_id,
                        )
                        continue
                    if not sub.enabled:
                        logger.info(
                            "[goofish_catcher] worker=%s skip disabled sub_id=%s keyword=%s paused_reason=%s",
                            worker_idx,
                            sub.id,
                            sub.keyword,
                            sub.paused_reason,
                        )
                        continue
                    await self._process_subscription(sub, worker_idx)
                except Exception as exc:
                    logger.error(
                        "[goofish_catcher] worker %s failed to process sub_id=%s: %s",
                        worker_idx,
                        sub_id,
                        exc,
                        exc_info=True,
                    )
                finally:
                    self._queue.task_done()
                    await self._release_sub_id(sub_id)
        except asyncio.CancelledError:
            raise

    async def _process_subscription(self, sub: Subscription, worker_idx: int) -> None:
        started_at = int(time.time())
        run_id = await self.storage.create_fetch_run(sub.id, started_at)
        logger.info(
            "[goofish_catcher] worker=%s sub=%s start keyword=%s",
            worker_idx,
            sub.id,
            sub.keyword,
        )

        try:
            raw_items = await asyncio.wait_for(
                self.provider.search(
                    keyword=sub.keyword,
                    pages=max(1, min(sub.pages, self.settings.max_pages)),
                    timeout_sec=self.settings.fetch_timeout_sec,
                ),
                # Add a global timeout wrapper to avoid hanging without logs.
                timeout=max(self.settings.fetch_timeout_sec + 30, 45),
            )
            items, filter_mode = await self.recommender.prefilter_items(
                umo=sub.umo,
                keyword=sub.keyword,
                items=raw_items,
            )
            now_ts = int(time.time())
            candidates = await self._process_items(sub, items, now_ts)
            await self.storage.finish_fetch_run(
                run_id,
                finished_at=now_ts,
                status="success",
                items_count=len(items),
            )
            await self.storage.update_schedule_success(sub.id, now_ts, sub.interval_sec)

            if candidates:
                recommendation = await self.recommender.analyze(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    candidates=candidates,
                    top_k=self.settings.llm_top_k,
                )
                sent = await self.notifier.send_recommendation_summary(
                    umo=sub.umo,
                    recommendation=recommendation,
                )
                if sent:
                    await self.persist_notifications(
                        sub_id=sub.id,
                        candidates=candidates,
                        sent_at=now_ts,
                    )
                else:
                    logger.warning(
                        "[goofish_catcher] sub=%s summary send failed, skip notification dedupe write",
                        sub.id,
                    )
            logger.info(
                "[goofish_catcher] worker=%s sub=%s success raw=%s filtered=%s candidates=%s prefilter=%s",
                worker_idx,
                sub.id,
                len(raw_items),
                len(items),
                len(candidates),
                filter_mode,
            )
            return
        except asyncio.TimeoutError:
            now_ts = int(time.time())
            await self.storage.finish_fetch_run(
                run_id,
                finished_at=now_ts,
                status="failed",
                err_type=ProviderErrorCode.TIMEOUT.value,
                err_msg="provider search timed out",
                items_count=0,
            )
            failure_count = sub.consecutive_failures + 1
            retry_sec = calculate_retry_delay(
                failure_count=failure_count,
                base_sec=self.settings.retry_base_sec,
                max_sec=self.settings.retry_max_sec,
            )
            await self.storage.update_schedule_failure(sub.id, now_ts, retry_sec)
            logger.warning(
                "[goofish_catcher] sub=%s timed out in scheduler wrapper, retry_in=%ss",
                sub.id,
                retry_sec,
            )
            return
        except ProviderError as exc:
            now_ts = int(time.time())
            await self.storage.finish_fetch_run(
                run_id,
                finished_at=now_ts,
                status="failed",
                err_type=exc.code.value,
                err_msg=exc.message,
                items_count=0,
            )

            if exc.code in {
                ProviderErrorCode.DEPENDENCY_MISSING,
                ProviderErrorCode.AUTH_REQUIRED,
                ProviderErrorCode.CAPTCHA,
            }:
                await self.storage.pause_subscription(sub.id, exc.code.value)
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code=exc.code.value,
                    message=exc.message,
                )
                retry_sec = exc.retry_after_sec or self.settings.retry_max_sec
                await self.storage.update_schedule_failure(sub.id, now_ts, retry_sec)
                logger.warning(
                    "[goofish_catcher] sub=%s paused due to %s",
                    sub.id,
                    exc.code.value,
                )
                return

            failure_count = sub.consecutive_failures + 1
            retry_sec = exc.retry_after_sec or calculate_retry_delay(
                failure_count=failure_count,
                base_sec=self.settings.retry_base_sec,
                max_sec=self.settings.retry_max_sec,
            )
            await self.storage.update_schedule_failure(sub.id, now_ts, retry_sec)
            logger.warning(
                "[goofish_catcher] sub=%s provider_error=%s retry_in=%ss",
                sub.id,
                exc.code.value,
                retry_sec,
            )
            return
        except Exception as exc:
            now_ts = int(time.time())
            await self.storage.finish_fetch_run(
                run_id,
                finished_at=now_ts,
                status="failed",
                err_type=ProviderErrorCode.UNKNOWN.value,
                err_msg=str(exc),
                items_count=0,
            )
            failure_count = sub.consecutive_failures + 1
            retry_sec = calculate_retry_delay(
                failure_count=failure_count,
                base_sec=self.settings.retry_base_sec,
                max_sec=self.settings.retry_max_sec,
            )
            await self.storage.update_schedule_failure(sub.id, now_ts, retry_sec)
            logger.error(
                "[goofish_catcher] sub=%s unknown_error retry_in=%ss: %s",
                sub.id,
                retry_sec,
                exc,
                exc_info=True,
            )

    async def _process_items(
        self,
        sub: Subscription,
        items: list,
        now_ts: int,
    ) -> list[RecommendationCandidate]:
        candidates: list[RecommendationCandidate] = []
        for item in items:
            if item.price < 0:
                continue

            existing = await self.storage.get_item(sub.id, item.item_id)
            if existing is None:
                await self.storage.insert_item(sub.id, item, now_ts)
                await self.storage.insert_price_history(
                    sub.id,
                    item.item_id,
                    item.price,
                    now_ts,
                    self.settings.provider_mode,
                )

                if not within_new_window(item.publish_time, now_ts, sub.new_window_sec):
                    continue

                payload = EventPayload(
                    event_type=EVENT_NEW,
                    keyword=sub.keyword,
                    item_id=item.item_id,
                    title=item.title,
                    price=item.price,
                    url=item.url,
                    publish_time=item.publish_time,
                    observed_at=now_ts,
                )
                payload_hash = build_payload_hash(payload)
                existed = await self.storage.notification_hash_exists(
                    sub.id,
                    item.item_id,
                    EVENT_NEW,
                    payload_hash,
                )
                if existed:
                    continue
                candidates.append(
                    RecommendationCandidate(
                        event_type=EVENT_NEW,
                        keyword=sub.keyword,
                        item_id=item.item_id,
                        title=item.title,
                        price=item.price,
                        url=item.url,
                        publish_time=item.publish_time,
                        observed_at=now_ts,
                        payload_hash=payload_hash,
                    )
                )
                continue

            old_price = existing.last_price
            await self.storage.update_item(sub.id, item, now_ts)

            if old_price is None or float(old_price) == float(item.price):
                continue

            await self.storage.insert_price_history(
                sub.id,
                item.item_id,
                item.price,
                now_ts,
                self.settings.provider_mode,
            )

            decision = evaluate_price_drop(
                old_price,
                item.price,
                sub.drop_abs,
                sub.drop_pct,
            )
            if not decision.triggered:
                continue

            last_sent = await self.storage.get_last_notification_sent_at(
                sub.id,
                item.item_id,
                EVENT_PRICE_DROP,
            )
            if in_cooldown(last_sent, now_ts, sub.cooldown_sec):
                continue

            payload = EventPayload(
                event_type=EVENT_PRICE_DROP,
                keyword=sub.keyword,
                item_id=item.item_id,
                title=item.title,
                price=item.price,
                url=item.url,
                publish_time=item.publish_time,
                observed_at=now_ts,
                drop_abs=decision.drop_abs,
                drop_pct=decision.drop_pct,
                last_price=float(old_price),
            )
            payload_hash = build_payload_hash(payload)
            existed = await self.storage.notification_hash_exists(
                sub.id,
                item.item_id,
                EVENT_PRICE_DROP,
                payload_hash,
            )
            if existed:
                continue

            candidates.append(
                RecommendationCandidate(
                    event_type=EVENT_PRICE_DROP,
                    keyword=sub.keyword,
                    item_id=item.item_id,
                    title=item.title,
                    price=item.price,
                    url=item.url,
                    publish_time=item.publish_time,
                    observed_at=now_ts,
                    last_price=float(old_price),
                    drop_abs=decision.drop_abs,
                    drop_pct=decision.drop_pct,
                    payload_hash=payload_hash,
                    notification_meta={
                        "drop_abs": decision.drop_abs,
                        "drop_pct": decision.drop_pct,
                        "last_price": old_price,
                        "new_price": item.price,
                    },
                )
            )
        return candidates

    async def persist_notifications(
        self,
        *,
        sub_id: int,
        candidates: list[RecommendationCandidate],
        sent_at: int,
    ) -> None:
        for candidate in candidates:
            if not candidate.payload_hash:
                continue
            await self.storage.insert_notification(
                sub_id=sub_id,
                item_id=candidate.item_id,
                event_type=candidate.event_type,
                payload_hash=candidate.payload_hash,
                sent_at=sent_at,
                meta=candidate.notification_meta,
            )
