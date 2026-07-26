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
    should_recover_unsent_new_event,
    within_new_window,
)
from .notifier import Notifier
from .activity_monitor import ActivityMonitor
from .platforms.registry import platform_display_name, split_item_id
from .provider import SearchProvider
from .provider_retry import (
    estimate_captcha_retry_timeout_sec,
    search_with_captcha_retry,
)
from .recommender import GoofishRecommender
from .storage import SubscriptionStorage
from .types import (
    DEFAULT_PLATFORM,
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
DEEP_ANALYSIS_MAX_CANDIDATES = 3
DEEP_ANALYSIS_CACHE_TTL_SEC = 6 * 3600
DEEP_ANALYSIS_INCOMPLETE_RETRY_SEC = 10 * 60
DEEP_ANALYSIS_COOLDOWN_ON_GUARD_SEC = 30 * 60
DEEP_ANALYSIS_INTERVAL_RANGE_SEC = (8.0, 15.0)
NEW_EVENT_UNSENT_RECOVERY_SEC = 24 * 3600

# 连续失败多少次后向用户推送一次告警（针对 NETWORK_ERROR 等非暂停类错误）
_CONSECUTIVE_FAILURE_ALERT_THRESHOLD = 3


def _matches_price_range(item: NormalizedItem, sub: Subscription) -> bool:
    price = item.price
    if sub.price_min is not None and price < sub.price_min:
        return False
    if sub.price_max is not None and price > sub.price_max:
        return False
    return True


def _deep_analysis_incomplete(analysis: DeepAnalysisResult) -> bool:
    if analysis.credit_status != "unknown":
        return False
    if analysis.seller_credit:
        return False
    reason = analysis.credit_reason or ""
    return (
        "未获取到明确卖家信用信息" in reason
        or "深度分析失败" in reason
        or not analysis.seller_name
    )


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
        provider: SearchProvider | dict[str, SearchProvider],
        notifier: Notifier,
        recommender: GoofishRecommender,
        activity_monitor: ActivityMonitor,
        remote_auth_coordinator: Any | None = None,
    ) -> None:
        self.context = context
        self.settings = settings
        self.storage = storage
        # 平台路由表：单 provider（旧用法）归一成 {"goofish": provider}。
        if isinstance(provider, dict):
            self._providers: dict[str, SearchProvider] = dict(provider)
        else:
            self._providers = {DEFAULT_PLATFORM: provider}
        # 兼容旧访问点：self.provider 指向 goofish provider。
        self.provider = self._providers.get(DEFAULT_PLATFORM)
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
        self._deep_analysis_blocked_until = 0
        self._deep_analysis_block_reason = ""
        self._last_deep_analysis_at = 0.0

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
            provider = self._providers.get(split_item_id(candidate.item_id)[0])
            if not getattr(
                getattr(provider, "_profile", None), "supports_item_detail", True
            ):
                # 平台不支持详情分析：跳过节流 sleep 与占位缓存写入，候选保留
                candidate.deep_analysis = None
                kept.append(candidate)
                continue
            analysis = cached.get(candidate.item_id)
            analysis_age = now_ts - analysis.analyzed_at if analysis is not None else None
            incomplete_retry = (
                analysis is not None
                and _deep_analysis_incomplete(analysis)
                and analysis_age is not None
                and analysis_age > DEEP_ANALYSIS_INCOMPLETE_RETRY_SEC
            )
            if (
                analysis is None
                or analysis_age is not None
                and analysis_age > DEEP_ANALYSIS_CACHE_TTL_SEC
                or incomplete_retry
            ):
                if now_ts < self._deep_analysis_blocked_until:
                    logger.warning(
                        "[goofish_catcher] deep analysis skipped item_id=%s blocked_for=%ss reason=%s",
                        candidate.item_id,
                        self._deep_analysis_blocked_until - now_ts,
                        self._deep_analysis_block_reason or "-",
                    )
                    candidate.deep_analysis = analysis
                    kept.append(candidate)
                    continue
                if analysis is None:
                    logger.info(
                        "[goofish_catcher] deep analysis cache miss item_id=%s title=%r",
                        candidate.item_id,
                        candidate.title[:80],
                    )
                elif incomplete_retry:
                    logger.info(
                        "[goofish_catcher] deep analysis cache incomplete item_id=%s age=%ss retry_ttl=%ss old_credit=%s seller=%s seller_credit=%s reason=%s",
                        candidate.item_id,
                        analysis_age,
                        DEEP_ANALYSIS_INCOMPLETE_RETRY_SEC,
                        analysis.credit_status,
                        analysis.seller_name or "-",
                        analysis.seller_credit or "-",
                        analysis.credit_reason,
                    )
                else:
                    logger.info(
                        "[goofish_catcher] deep analysis cache stale item_id=%s age=%ss ttl=%ss old_credit=%s reason=%s",
                        candidate.item_id,
                        analysis_age,
                        DEEP_ANALYSIS_CACHE_TTL_SEC,
                        analysis.credit_status,
                        analysis.credit_reason,
                    )
                analysis = await self._fetch_candidate_deep_analysis(candidate, now_ts)
            else:
                logger.info(
                    "[goofish_catcher] deep analysis cache hit item_id=%s age=%ss credit=%s seller=%s reason=%s",
                    candidate.item_id,
                    analysis_age,
                    analysis.credit_status,
                    analysis.seller_name or "-",
                    analysis.credit_reason,
                )
            candidate.deep_analysis = analysis
            if analysis is not None:
                logger.info(
                    "[goofish_catcher] deep analysis result item_id=%s status=%s credit=%s seller=%s seller_credit=%s want=%s browse=%s reason=%s",
                    candidate.item_id,
                    analysis.status,
                    analysis.credit_status,
                    analysis.seller_name or "-",
                    analysis.seller_credit or "-",
                    analysis.want_count,
                    analysis.browse_count,
                    analysis.credit_reason,
                )
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
        platform = split_item_id(candidate.item_id)[0]
        provider = self._providers.get(platform)
        analyze = getattr(provider, "analyze_item_detail", None) if provider else None
        if not callable(analyze):
            if provider is None:
                logger.info(
                    "[goofish_catcher] deep analysis skipped item_id=%s: no provider for platform=%s",
                    candidate.item_id,
                    platform,
                )
            return None
        try:
            elapsed = time.monotonic() - self._last_deep_analysis_at
            target_interval = random.uniform(*DEEP_ANALYSIS_INTERVAL_RANGE_SEC)
            if elapsed < target_interval:
                delay = target_interval - elapsed
                logger.info(
                    "[goofish_catcher] deep analysis throttle sleep=%.1fs item_id=%s interval=%.1fs",
                    delay,
                    candidate.item_id,
                    target_interval,
                )
                await asyncio.sleep(delay)
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
            self._last_deep_analysis_at = time.monotonic()
            return analysis
        except ProviderError as exc:
            if exc.code in {
                ProviderErrorCode.CAPTCHA,
                ProviderErrorCode.RATE_LIMITED,
                ProviderErrorCode.AUTH_REQUIRED,
            }:
                self._deep_analysis_blocked_until = now_ts + (
                    exc.retry_after_sec or DEEP_ANALYSIS_COOLDOWN_ON_GUARD_SEC
                )
                self._deep_analysis_block_reason = f"{exc.code.value}: {exc.message}"
                logger.warning(
                    "[goofish_catcher] deep analysis guard blocked item_id=%s code=%s cooldown=%ss message=%s; skip remaining detail pages and do not cache unknown fallback",
                    candidate.item_id,
                    exc.code.value,
                    self._deep_analysis_blocked_until - now_ts,
                    exc.message,
                )
                return None
            logger.warning(
                "[goofish_catcher] deep analysis provider failed item_id=%s: %s",
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
            provider = self._providers.get(sub.platform)
            if provider is None:
                now_ts = int(time.time())
                await self.storage.finish_fetch_run(
                    run_id,
                    finished_at=now_ts,
                    status="failed",
                    err_type="PLATFORM_UNAVAILABLE",
                    err_msg=f"no provider available for platform {sub.platform}",
                    items_count=0,
                )
                await self.storage.pause_subscription(sub.id, "PLATFORM_UNAVAILABLE")
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code="PLATFORM_UNAVAILABLE",
                    message=(
                        f"平台「{platform_display_name(sub.platform)}」当前不可用"
                        "（未启用或当前运行模式不支持），该订阅已暂停。"
                    ),
                    action_hint=(
                        "如需监控该平台，请在插件配置中启用对应平台并重启插件后，"
                        "重新启用该订阅。"
                    ),
                )
                logger.warning(
                    "[goofish_catcher] sub=%s paused: no provider for platform=%s",
                    sub.id,
                    sub.platform,
                )
                return
            raw_items = await asyncio.wait_for(
                search_with_captcha_retry(
                    provider,
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
                        sub.keyword, raw_prices, now_ts, platform=sub.platform
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
            if failure_count % _CONSECUTIVE_FAILURE_ALERT_THRESHOLD == 0:
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code=ProviderErrorCode.TIMEOUT.value,
                    message="provider search timed out",
                    action_hint=(
                        f"已连续超时 {failure_count} 次，将在 {retry_sec}s 后自动重试。"
                        "订阅未暂停，无需手动操作；如持续告警请检查 Worker 状态。"
                    ),
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
                    if sub.platform == DEFAULT_PLATFORM:
                        start_hint = "已尝试启动登录恢复流程"
                        recovery_hint = "可发送 /闲鱼 登录"
                        retry_hint = "可稍后发送 /闲鱼 登录 重试"
                    else:
                        display_name = platform_display_name(sub.platform)
                        start_hint = f"已尝试启动{display_name}登录恢复流程"
                        recovery_hint = f"可发送 /闲鱼 登录 {display_name}"
                        retry_hint = f"可稍后发送 /闲鱼 登录 {display_name} 重试"
                    try:
                        await self.remote_auth_coordinator.handle_provider_auth_failure(
                            umo=sub.umo,
                            sub_id=sub.id,
                            platform=sub.platform,
                        )
                        action_hint = (
                            f"已暂停该订阅，并{start_hint}。"
                            f"扫码完成后会自动恢复；如未收到二维码，{recovery_hint}。"
                        )
                    except ProviderError as recovery_exc:
                        action_hint = (
                            "已暂停该订阅，但自动启动登录恢复失败。"
                            f"{recovery_exc.code.value}: {recovery_exc.message}。"
                            f"{retry_hint}。"
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
                            f"{recovery_exc}。{retry_hint}。"
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
            # 连续失败达到阈值时推送告警，避免 NETWORK_ERROR 等错误静默丢失
            if failure_count % _CONSECUTIVE_FAILURE_ALERT_THRESHOLD == 0:
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code=exc.code.value,
                    message=exc.message,
                    action_hint=(
                        f"已连续失败 {failure_count} 次，将在 {retry_sec}s 后自动重试。"
                        "订阅未暂停，无需手动操作；如持续告警请检查 Worker 状态。"
                    ),
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
            if failure_count % _CONSECUTIVE_FAILURE_ALERT_THRESHOLD == 0:
                await self.notifier.send_alert(
                    umo=sub.umo,
                    keyword=sub.keyword,
                    code=ProviderErrorCode.UNKNOWN.value,
                    message=str(exc),
                    action_hint=(
                        f"已连续失败 {failure_count} 次，将在 {retry_sec}s 后自动重试。"
                        "订阅未暂停，无需手动操作；如持续告警请检查日志。"
                    ),
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
        last_new_sent_map = await self.storage.get_last_notification_sent_map(
            sub.id,
            item_ids,
            EVENT_NEW,
        )
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
                if (
                    item.item_id not in last_new_sent_map
                    and should_recover_unsent_new_event(
                        first_seen_at=existing.first_seen_at,
                        publish_time=item.publish_time,
                        now_ts=now_ts,
                        new_window_sec=sub.new_window_sec,
                        recovery_sec=NEW_EVENT_UNSENT_RECOVERY_SEC,
                    )
                ):
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
                    if not existed:
                        logger.info(
                            "[goofish_catcher] recover unsent NEW candidate sub=%s item_id=%s first_seen_at=%s",
                            sub.id,
                            item.item_id,
                            existing.first_seen_at,
                        )
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
