from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Callable
from typing import Any

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
from .activity_monitor import ActivityMonitor
from .provider import SearchProvider
from .provider_retry import (
    estimate_captcha_retry_timeout_sec,
    search_with_captcha_retry,
)
from .recommender import GoofishRecommender
from .storage import SubscriptionStorage
from .types import (
    DeepAnalysisResult,
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
    RecommendationCandidate,
    Subscription,
)

# 价格异常检测：当前价格超过上次价格的此倍数时，记录警告但不触发降价事件
_PRICE_SPIKE_FACTOR = 10.0

EVENT_NEW = "NEW"
EVENT_PRICE_DROP = "PRICE_DROP"
DEEP_ANALYSIS_MAX_CANDIDATES = 10
DEEP_ANALYSIS_CACHE_TTL_SEC = 6 * 3600


def _matches_price_range(item: NormalizedItem, sub: Subscription) -> bool:
    price = item.price
    if sub.price_min is not None and price < sub.price_min:
        return False
    if sub.price_max is not None and price > sub.price_max:
        return False
    return True


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
        activity_monitor: ActivityMonitor,
        remote_auth_coordinator: Any | None = None,
    ) -> None:
        self.context = context
        self.settings = settings
        self.storage = storage
        self.provider = provider
        self.notifier = notifier
        self.recommender = recommender
        self.activity_monitor = activity_monitor
        self.remote_auth_coordinator = remote_auth_coordinator

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
    ) -> tuple[list[RecommendationCandidate], int]:
        """Process externally fetched items and keep storage/state consistent."""
        price_scoped = [item for item in items if _matches_price_range(item, sub)]
        kept_items, filter_mode = await self.recommender.prefilter_items(
            umo=sub.umo,
            keyword=sub.keyword,
            items=price_scoped,
        )
        # 被关键词预筛拒绝的价格合规商品也写入 items 表，供后续分析使用
        kept_ids = {item.item_id for item in kept_items}
        rejected_items = [item for item in price_scoped if item.item_id not in kept_ids]
        if rejected_items:
            await self.storage.upsert_items_bulk(sub.id, rejected_items, now_ts)
        logger.info(
            "[goofish_catcher] sub=%s manual prefilter %s -> %s (%s), rejected_stored=%s",
            sub.id,
            len(items),
            len(kept_items),
            filter_mode,
            len(rejected_items),
        )
        candidates = await self._process_items(sub, kept_items, now_ts)
        candidates = await self.deep_analyze_candidates(candidates)
        await self.storage.update_schedule_success(sub.id, now_ts, sub.interval_sec)
        return candidates, len(kept_items)

    async def deep_analyze_candidates(
        self,
        candidates: list[RecommendationCandidate],
    ) -> list[RecommendationCandidate]:
        if not candidates:
            return candidates
        now_ts = int(time.time())
        selected = candidates[:DEEP_ANALYSIS_MAX_CANDIDATES]
        cached = await self.storage.get_deep_analysis_bulk(
            [candidate.item_id for candidate in selected]
        )
        kept: list[RecommendationCandidate] = []
        for candidate in candidates:
            if candidate not in selected:
                kept.append(candidate)
                continue
            analysis = cached.get(candidate.item_id)
            if analysis is None or now_ts - analysis.analyzed_at > DEEP_ANALYSIS_CACHE_TTL_SEC:
                analysis = await self._fetch_candidate_deep_analysis(candidate, now_ts)
            candidate.deep_analysis = analysis
            if analysis and analysis.rejected:
                logger.info(
                    "[goofish_catcher] deep analysis rejected item_id=%s reason=%s",
                    candidate.item_id,
                    analysis.credit_reason,
                )
                continue
            kept.append(candidate)
        return kept

    async def _fetch_candidate_deep_analysis(
        self,
        candidate: RecommendationCandidate,
        now_ts: int,
    ) -> DeepAnalysisResult | None:
        analyze = getattr(self.provider, "analyze_item_detail", None)
        if not callable(analyze):
            return None
        try:
            item = NormalizedItem(
                item_id=candidate.item_id,
                title=candidate.title,
                price=candidate.price,
                url=candidate.url,
                publish_time=candidate.publish_time,
            )
            analysis = await asyncio.wait_for(
                analyze(item=item, timeout_sec=max(8, self.settings.fetch_timeout_sec)),
                timeout=max(12, self.settings.fetch_timeout_sec + 8),
            )
            await self.storage.upsert_deep_analysis(analysis)
            return analysis
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] deep analysis failed item_id=%s: %s",
                candidate.item_id,
                exc,
            )
            fallback = DeepAnalysisResult(
                item_id=candidate.item_id,
                analyzed_at=now_ts,
                status="passed",
                credit_status="unknown",
                credit_reason="深度分析失败，按保守规则不过滤",
                summary="深度分析失败，已保守放行",
                risk=str(exc),
                image_urls=[],
                raw={"error": str(exc)},
            )
            await self.storage.upsert_deep_analysis(fallback)
            return fallback

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
                    if self.remote_auth_coordinator is not None:
                        await self.remote_auth_coordinator.wait_until_idle()
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
        activity_id = await self.activity_monitor.start_task(
            source="subscription",
            keyword=sub.keyword,
            umo=sub.umo,
            provider_mode=self.settings.provider_mode,
            page_count=max(1, min(sub.pages, self.settings.max_pages)),
            sub_id=sub.id,
            worker_idx=worker_idx,
            message="正在抓取闲鱼结果",
        )
        logger.info(
            "[goofish_catcher] worker=%s sub=%s start keyword=%s",
            worker_idx,
            sub.id,
            sub.keyword,
        )

        try:
            raw_items = await asyncio.wait_for(
                search_with_captcha_retry(
                    self.provider,
                    keyword=sub.keyword,
                    pages=max(1, min(sub.pages, self.settings.max_pages)),
                    timeout_sec=self.settings.fetch_timeout_sec,
                    filters=sub.search_filters(),
                ),
                timeout=estimate_captcha_retry_timeout_sec(
                    timeout_sec=self.settings.fetch_timeout_sec,
                ),
            )
            now_ts = int(time.time())
            await self.activity_monitor.update_task(
                activity_id,
                phase="prefiltering",
                raw_total=len(raw_items),
                message=f"已抓取 {len(raw_items)} 条，正在预筛",
            )
            items, filter_mode, skipped_filtered = await self._prefilter_subscription_items(
                sub=sub,
                raw_items=raw_items,
                now_ts=now_ts,
            )

            # 用本批原始价格（未过滤）更新市场 EMA，并读取最新均价供评分使用
            market_snapshot: float | None = None
            if raw_items:
                raw_prices = [item.price for item in raw_items if item.price > 0]
                try:
                    mp = await self.storage.upsert_market_price(
                        sub.keyword, raw_prices, now_ts
                    )
                    market_snapshot = mp.ema_price
                    logger.debug(
                        "[goofish_catcher] sub=%s keyword=%r market_ema=%.2f samples=%d",
                        sub.id,
                        sub.keyword,
                        mp.ema_price,
                        mp.sample_count,
                    )
                except Exception as exc:
                    logger.warning(
                        "[goofish_catcher] sub=%s failed to update market_price: %s",
                        sub.id,
                        exc,
                    )

            candidates = await self._process_items(sub, items, now_ts, market_price=market_snapshot)
            candidates = await self.deep_analyze_candidates(candidates)
            await self.storage.finish_fetch_run(
                run_id,
                finished_at=now_ts,
                status="success",
                items_count=len(items),
            )
            await self.storage.update_schedule_success(sub.id, now_ts, sub.interval_sec)

            await self.activity_monitor.update_task(
                activity_id,
                phase="analyzing",
                filtered_total=len(items),
                candidate_total=len(candidates),
                message=(
                    f"已筛出 {len(candidates)} 个候选，正在分析推荐"
                    if candidates
                    else "没有候选商品，正在生成分析结果"
                ),
            )
            if candidates:
                recommendation = await self.recommender.analyze(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    candidates=candidates,
                    top_k=self.settings.llm_top_k,
                    recommend_max_price=sub.recommend_max_price,
                )
                if recommendation.top:
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
                else:
                    logger.info(
                        "[goofish_catcher] sub=%s no recommendation above min_score=%s, skip push",
                        sub.id,
                        self.settings.llm_min_score,
                    )
            logger.info(
                "[goofish_catcher] worker=%s sub=%s success raw=%s filtered=%s cached_skip=%s candidates=%s prefilter=%s",
                worker_idx,
                sub.id,
                len(raw_items),
                len(items),
                skipped_filtered,
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
                action_hint = None
                if exc.code in {
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                } and self.remote_auth_coordinator is not None:
                    try:
                        await self.remote_auth_coordinator.handle_provider_auth_failure(
                            umo=sub.umo,
                            sub_id=sub.id,
                        )
                        action_hint = (
                            "已暂停该订阅，并已尝试启动登录恢复流程。"
                            "扫码完成后会自动恢复；如未收到二维码，可发送 /闲鱼 登录。"
                        )
                    except ProviderError as recovery_exc:
                        action_hint = (
                            "已暂停该订阅，但自动启动登录恢复失败。"
                            f"{recovery_exc.code.value}: {recovery_exc.message}。"
                            "可稍后发送 /闲鱼 登录 重试。"
                        )
                        logger.warning(
                            "[goofish_catcher] failed to trigger auth recovery for sub=%s: %s",
                            sub.id,
                            recovery_exc,
                            exc_info=True,
                        )
                    except Exception as recovery_exc:
                        action_hint = (
                            "已暂停该订阅，但自动启动登录恢复失败。"
                            f"{recovery_exc}。可稍后发送 /闲鱼 登录 重试。"
                        )
                        logger.warning(
                            "[goofish_catcher] failed to trigger auth recovery for sub=%s: %s",
                            sub.id,
                            recovery_exc,
                            exc_info=True,
                        )
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code=exc.code.value,
                    message=exc.message,
                    action_hint=action_hint,
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
        finally:
            await self.activity_monitor.finish_task(activity_id)

    async def _prefilter_subscription_items(
        self,
        *,
        sub: Subscription,
        raw_items: list[NormalizedItem],
        now_ts: int,
    ) -> tuple[list[NormalizedItem], str, int]:
        if not raw_items:
            return [], "EMPTY", 0

        raw_items = [item for item in raw_items if _matches_price_range(item, sub)]
        if not raw_items:
            return [], "PRICE_RANGE_FILTER", 0

        raw_item_ids = [item.item_id for item in raw_items]
        filtered_ids = await self.storage.get_filtered_item_ids(sub.id, raw_item_ids)
        pending_items = [item for item in raw_items if item.item_id not in filtered_ids]
        if not pending_items:
            return [], "FILTERED_CACHE_HIT", len(filtered_ids)

        existing_map = await self.storage.get_items_by_ids(
            sub.id,
            [item.item_id for item in pending_items],
        )
        kept_items, filter_mode = await self.recommender.prefilter_items(
            umo=sub.umo,
            keyword=sub.keyword,
            items=pending_items,
        )
        kept_ids = {item.item_id for item in kept_items}
        # 关键词预筛拒绝的商品：新商品写入 items 表（价格合规，保留供分析），
        # 同时写 filtered_items 作为去重缓存，避免下轮重复进入预筛。
        rejected_new_items = [
            item
            for item in pending_items
            if item.item_id not in kept_ids and item.item_id not in existing_map
        ]
        if rejected_new_items:
            await self.storage.upsert_items_bulk(sub.id, rejected_new_items, now_ts)
        await self.storage.upsert_filtered_items_bulk(
            sub.id,
            rejected_new_items,
            now_ts,
        )
        return kept_items, filter_mode, len(filtered_ids)

    async def _process_items(
        self,
        sub: Subscription,
        items: list,
        now_ts: int,
        *,
        market_price: float | None = None,
    ) -> list[RecommendationCandidate]:
        normalized_items = [
            item
            for item in items
            if item.price >= 0 and _matches_price_range(item, sub)
        ]
        if not normalized_items:
            return []

        item_ids = [item.item_id for item in normalized_items]
        existing_map = await self.storage.get_items_by_ids(sub.id, item_ids)
        last_drop_sent_map = await self.storage.get_last_notification_sent_map(
            sub.id,
            item_ids,
            EVENT_PRICE_DROP,
        )
        # 批量拉取已有历史价格统计，用于：
        #   1. 判断是否突破历史最低价
        #   2. 异常价格检测（价格突涨超过 _PRICE_SPIKE_FACTOR 倍）
        #   3. 推荐评分时提供历史上下文
        price_stats_map = await self.storage.get_price_stats_bulk(item_ids)

        await self.storage.upsert_items_bulk(sub.id, normalized_items, now_ts)

        price_history_rows: list[tuple[int, str, float, int, str]] = []
        candidates: list[RecommendationCandidate] = []
        for item in normalized_items:
            existing = existing_map.get(item.item_id)
            stats = price_stats_map.get(item.item_id)

            if existing is None:
                price_history_rows.append(
                    (
                        sub.id,
                        item.item_id,
                        item.price,
                        now_ts,
                        self.settings.provider_mode,
                    )
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
                        hist_min=stats.hist_min if stats else None,
                        hist_avg=stats.hist_avg if stats else None,
                        market_price=market_price,
                    )
                )
                continue

            old_price = existing.last_price
            if old_price is None or float(old_price) == float(item.price):
                continue

            # 价格异常检测：价格暴涨（如卖家改错价再纠正）不触发降价，只记录警告
            if (
                old_price is not None
                and old_price > 0
                and item.price > float(old_price) * _PRICE_SPIKE_FACTOR
            ):
                logger.warning(
                    "[goofish_catcher] price spike detected for item %s "
                    "(keyword=%r): %.2f → %.2f (%.1fx), skipping drop check",
                    item.item_id,
                    sub.keyword,
                    old_price,
                    item.price,
                    item.price / float(old_price),
                )
                price_history_rows.append(
                    (sub.id, item.item_id, item.price, now_ts, self.settings.provider_mode)
                )
                continue

            price_history_rows.append(
                (
                    sub.id,
                    item.item_id,
                    item.price,
                    now_ts,
                    self.settings.provider_mode,
                )
            )

            # 传入历史最低价，让 evaluate_price_drop 标记是否突破历史底部
            hist_min = stats.hist_min if stats and stats.hist_count >= 2 else None
            decision = evaluate_price_drop(
                old_price,
                item.price,
                sub.drop_abs,
                sub.drop_pct,
                hist_min=hist_min,
            )
            if not decision.triggered:
                continue

            last_sent = last_drop_sent_map.get(item.item_id)
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
                        "hist_min": stats.hist_min if stats else None,
                        "hist_avg": stats.hist_avg if stats else None,
                        "below_hist_min": decision.below_hist_min,
                        "market_price": market_price,
                    },
                    hist_min=stats.hist_min if stats else None,
                    hist_avg=stats.hist_avg if stats else None,
                    market_price=market_price,
                )
            )
        await self.storage.insert_price_history_bulk(price_history_rows)
        return candidates

    async def persist_notifications(
        self,
        *,
        sub_id: int,
        candidates: list[RecommendationCandidate],
        sent_at: int,
    ) -> None:
        rows: list[tuple[int, str, str, str, int, dict | None]] = []
        for candidate in candidates:
            if not candidate.payload_hash:
                continue
            rows.append(
                (
                    sub_id,
                    candidate.item_id,
                    candidate.event_type,
                    candidate.payload_hash,
                    sent_at,
                    candidate.notification_meta,
                )
            )
        await self.storage.insert_notifications_bulk(rows)
