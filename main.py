from __future__ import annotations

import asyncio
import re
import time
from datetime import datetime
from sys import maxsize
from typing import Any

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, StarTools
from astrbot.core.star.filter.command import GreedyStr

from .app.activity_monitor import ActivityMonitor
from .app.admin_server import AdminWebuiServer
from .app.auth_session import LocalAuthSessionController
from .app.config import (
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
    PluginSettings,
    load_plugin_settings,
)
from .app.notifier import Notifier
from .app.provider import (
    ProviderConfigurationError,
    ProviderDependencyError,
    SearchProvider,
    build_provider,
)
from .app.provider_retry import (
    estimate_captcha_retry_timeout_sec,
    search_with_captcha_retry,
)
from .app.reply_favorite import (
    extract_non_reply_text,
    extract_reply_context_from_outline,
    extract_reply_text,
    map_reply_selection,
    parse_reply_selection,
    parse_reply_target,
    recommendation_reply_hint,
)
from .app.remote_auth_recovery import RemoteAuthRecoveryCoordinator
from .app.recommender import GoofishRecommender
from .app.scheduler import MonitoringScheduler
from .app.storage import SubscriptionStorage
from .app.types import (
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
    RecommendationCandidate,
    RecommendationResult,
)

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"


class GoofishCatcherPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | dict | None = None):
        super().__init__(context)
        self.context = context
        self.config = dict(config or {})
        self.settings = load_plugin_settings(
            self.config,
            PLUGIN_NAME,
            plugin_data_dir=StarTools.get_data_dir(PLUGIN_NAME),
        )

        self.storage: SubscriptionStorage | None = None
        self.provider: SearchProvider | None = None
        self.notifier: Notifier | None = None
        self.recommender: GoofishRecommender | None = None
        self.scheduler: MonitoringScheduler | None = None
        self.remote_auth_coordinator: RemoteAuthRecoveryCoordinator | None = None
        self._provider_error: str | None = None
        self._provider_health: dict[str, Any] | None = None
        self._provider_health_checked_at: int | None = None
        self.activity_monitor = ActivityMonitor()
        self._ready = False
        self._loaded = False
        self._admin_webui = AdminWebuiServer(self)
        self._start_lock = asyncio.Lock()
        self._reload_lock = asyncio.Lock()
        # Heartbeat: periodic login-state probe for playwright_local mode.
        self._heartbeat_task: asyncio.Task | None = None
        # Interval in seconds; 0 means disabled.
        _HEARTBEAT_INTERVAL_SEC = 1800  # 30 minutes
        self._heartbeat_interval_sec: int = _HEARTBEAT_INTERVAL_SEC

    async def initialize(self) -> None:
        async with self._reload_lock:
            self.settings = load_plugin_settings(
                self.config,
                PLUGIN_NAME,
                plugin_data_dir=StarTools.get_data_dir(PLUGIN_NAME),
            )
            self.storage = SubscriptionStorage(self.settings.db_path)
            await self.storage.initialize()
            await self._configure_runtime()
        await self._ensure_admin_webui_started()

    @filter.on_astrbot_loaded()
    async def on_astrbot_loaded(self) -> None:
        self._loaded = True
        async with self._start_lock:
            if not self._ready:
                logger.warning("[goofish_catcher] skip start, plugin not ready")
                return
            if self._provider_error:
                logger.warning(
                    "[goofish_catcher] skip scheduler start, provider unavailable: %s",
                    self._provider_error,
                )
                return
            if self.scheduler is None:
                logger.warning("[goofish_catcher] skip start, scheduler is missing")
                return
            await self.scheduler.start()
            self._ensure_heartbeat_started()

    async def terminate(self) -> None:
        await self._safe_close("admin_webui", self._admin_webui.stop)
        await self._close_runtime(close_storage=True)
        self._ready = False
        self._loaded = False

    async def reload_runtime(self) -> dict[str, Any]:
        async with self._reload_lock:
            previous_admin = (
                self.settings.admin_webui_enabled,
                self.settings.admin_webui_host,
                self.settings.admin_webui_port,
            )
            await self._close_runtime(close_storage=False)
            self.settings = load_plugin_settings(
                self.config,
                PLUGIN_NAME,
                plugin_data_dir=StarTools.get_data_dir(PLUGIN_NAME),
            )
            if self.storage is None:
                self.storage = SubscriptionStorage(self.settings.db_path)
                await self.storage.initialize()
            await self._configure_runtime()
            await self._ensure_admin_webui_started(allow_stop=False)
            current_admin = (
                self.settings.admin_webui_enabled,
                self.settings.admin_webui_host,
                self.settings.admin_webui_port,
            )
            return {
                "reloaded": True,
                "provider_mode": self.settings.provider_mode,
                "provider_error": self._provider_error,
                "admin_server_restart_required": previous_admin != current_admin,
                "admin_url": self.admin_webui_url,
            }

    async def refresh_provider_health(
        self,
        *,
        force: bool = False,
    ) -> tuple[dict[str, Any] | None, int | None]:
        if self.provider is None:
            if force:
                self._provider_health = None
                self._provider_health_checked_at = int(time.time())
            return self._provider_health, self._provider_health_checked_at
        if self.settings.provider_mode != PROVIDER_MODE_REMOTE_REST:
            if force:
                self._provider_health = None
                self._provider_health_checked_at = int(time.time())
            return self._provider_health, self._provider_health_checked_at
        try:
            (
                self._provider_health,
                self._provider_health_checked_at,
            ) = await _run_remote_provider_healthcheck(
                self.provider,
                self.settings,
                ignore_disabled=force,
            )
        except ProviderError as exc:
            self._provider_health = {
                "ok": False,
                "provider": self.settings.provider_mode,
                "provider_error": exc.message,
            }
            self._provider_health_checked_at = int(time.time())
            raise
        return self._provider_health, self._provider_health_checked_at

    @property
    def admin_webui_url(self) -> str | None:
        if not self.settings.admin_webui_enabled:
            return None
        return (
            f"http://{self.settings.admin_webui_host}:"
            f"{self.settings.admin_webui_port}"
        )

    async def _configure_runtime(self) -> None:
        self._provider_error = None
        self._provider_health = None
        self._provider_health_checked_at = None
        self.provider = None
        self.scheduler = None
        self.remote_auth_coordinator = None
        self.notifier = Notifier(
            context=self.context,
            webhook_url=self.settings.webhook_url,
            timeout_sec=self.settings.fetch_timeout_sec,
        )
        self.recommender = GoofishRecommender(
            context=self.context,
            settings=self.settings,
        )
        try:
            self.provider = build_provider(
                self.settings,
                llm_call=self._make_llm_call() if self.settings.llm_enabled else None,
            )
            (
                self._provider_health,
                self._provider_health_checked_at,
            ) = await _run_remote_provider_healthcheck(
                self.provider,
                self.settings,
            )
        except (ProviderDependencyError, ProviderConfigurationError, ProviderError) as exc:
            self._provider_error = str(exc)
            if self.provider is not None:
                await self._safe_close("provider", self.provider.close)
                self.provider = None
            self._ready = True
            logger.error(
                "[goofish_catcher] provider initialization failed: %s",
                self._provider_error,
            )
            return
        except Exception as exc:
            self._provider_error = str(exc)
            if self.provider is not None:
                await self._safe_close("provider", self.provider.close)
                self.provider = None
            self._ready = True
            logger.error(
                "[goofish_catcher] unexpected provider initialization failure: %s",
                self._provider_error,
                exc_info=True,
            )
            return

        if self.storage is None:
            raise RuntimeError("storage is not initialized")
        auth_controller: Any | None = None
        if self.settings.provider_mode == PROVIDER_MODE_REMOTE_REST:
            auth_controller = self.provider
        elif self.settings.provider_mode == PROVIDER_MODE_PLAYWRIGHT_LOCAL:
            auth_controller = LocalAuthSessionController(
                self.settings,
                on_before_start=self._recycle_local_provider_browser,
                on_after_confirm=self._adopt_local_login_session,
            )
        self.remote_auth_coordinator = RemoteAuthRecoveryCoordinator(
            context=self.context,
            settings=self.settings,
            auth_controller=auth_controller,
        )
        self.scheduler = MonitoringScheduler(
            context=self.context,
            settings=self.settings,
            storage=self.storage,
            provider=self.provider,
            notifier=self.notifier,
            recommender=self.recommender,
            activity_monitor=self.activity_monitor,
            remote_auth_coordinator=self.remote_auth_coordinator,
        )
        self._ready = True
        logger.info(
            "[goofish_catcher] initialized, provider=%s, db=%s",
            self.settings.provider_mode,
            self.settings.db_path,
        )
        if self._loaded:
            await self._ensure_scheduler_started()
            self._ensure_heartbeat_started()

    async def _close_runtime(self, *, close_storage: bool) -> None:
        self._cancel_heartbeat()
        if self.scheduler is not None:
            await self._safe_close("scheduler", self.scheduler.stop)
        if self.remote_auth_coordinator is not None:
            await self._safe_close("auth_recovery", self.remote_auth_coordinator.close)
        if self.notifier is not None:
            await self._safe_close("notifier", self.notifier.close)
        if self.provider is not None:
            await self._safe_close("provider", self.provider.close)
        if close_storage and self.storage is not None:
            await self._safe_close("storage", self.storage.close)
            self.storage = None
        self.scheduler = None
        self.notifier = None
        self.provider = None
        self.recommender = None
        self.remote_auth_coordinator = None
        self._ready = False

    async def _ensure_admin_webui_started(self, *, allow_stop: bool = True) -> None:
        if self.settings.admin_webui_enabled:
            await self._admin_webui.start()
            return
        if allow_stop and self._admin_webui.running:
            await self._admin_webui.stop()

    async def _run_immediate_subscription_check(
        self,
        *,
        umo: str,
        sub,
    ) -> RecommendationResult:
        if self.scheduler is None:
            raise RuntimeError("调度器未启动。")

        acquired = await self.scheduler.try_acquire_subscription(sub.id)
        if not acquired:
            raise RuntimeError("该订阅当前正在执行，请稍后重试。")

        try:
            items = await asyncio.wait_for(
                self._search_with_captcha_retry(
                    keyword=sub.keyword,
                    pages=max(1, min(sub.pages, self.settings.max_pages)),
                ),
                timeout=self._search_operation_timeout_sec(),
            )
            now_ts = int(time.time())
            candidates, _ = await self.scheduler.process_manual_fetch(
                sub=sub,
                items=items,
                now_ts=now_ts,
            )
            recommendation = await self.recommender.analyze(
                umo=umo,
                keyword=sub.keyword,
                candidates=candidates,
                top_k=self.settings.llm_top_k,
                recommend_max_price=sub.recommend_max_price,
            )
            if recommendation.top:
                await self.scheduler.persist_notifications(
                    sub_id=sub.id,
                    candidates=candidates,
                    sent_at=now_ts,
                )
            return recommendation
        finally:
            await self.scheduler.release_subscription(sub.id)

    async def _safe_close(self, name: str, closer) -> None:
        try:
            await closer()
        except Exception as exc:
            logger.error(
                "[goofish_catcher] failed to close %s: %s",
                name,
                exc,
                exc_info=True,
            )

    def _make_llm_call(self):
        """Return an async callable(prompt, system_prompt) -> str backed by
        the configured AstrBot LLM provider, for use as the agent fallback
        inside PlaywrightSearchProvider.  Returns None when no provider is
        available so callers can skip the LLM path gracefully."""
        context = self.context
        settings = self.settings

        async def _llm_call(prompt: str, system_prompt: str) -> str:
            provider_id: str | None = None
            if settings.llm_provider_id:
                provider_id = settings.llm_provider_id
            else:
                provider = context.get_all_providers()
                if provider:
                    try:
                        provider_id = str(provider[0].meta().id)
                    except Exception:
                        pass
            if not provider_id:
                return ""
            try:
                resp = await context.llm_generate(
                    chat_provider_id=provider_id,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.0,
                    max_tokens=1200,
                )
                return (getattr(resp, "completion_text", "") or "").strip()
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher][agent] llm_call failed: %s", exc
                )
                return ""

        return _llm_call

    # ── Heartbeat ────────────────────────────────────────────────────────────

    def _ensure_heartbeat_started(self) -> None:
        """Start the heartbeat task if not already running.

        Only active for playwright_local mode — remote mode has its own
        health-check mechanism via RemoteAuthRecoveryCoordinator.
        """
        if self.settings.provider_mode != PROVIDER_MODE_PLAYWRIGHT_LOCAL:
            return
        if self._heartbeat_interval_sec <= 0:
            return
        if self._heartbeat_task is not None and not self._heartbeat_task.done():
            return
        self._heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(),
            name="goofish-catcher-heartbeat",
        )
        logger.info(
            "[goofish_catcher] heartbeat started, interval=%ss",
            self._heartbeat_interval_sec,
        )

    def _cancel_heartbeat(self) -> None:
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def _heartbeat_loop(self) -> None:
        """Periodically probe Goofish to detect session expiry early.

        On auth failure, mirrors exactly what the scheduler does:
        pause all subscriptions + trigger auth recovery + notify users.
        """
        try:
            # Initial delay: wait one full interval before the first probe
            # so we don't hammer Goofish right after startup.
            await asyncio.sleep(self._heartbeat_interval_sec)

            while True:
                await self._run_heartbeat_probe()
                await asyncio.sleep(self._heartbeat_interval_sec)
        except asyncio.CancelledError:
            raise

    async def _run_heartbeat_probe(self) -> None:
        provider = self.provider
        if provider is None:
            return

        check_login = getattr(provider, "check_login_state", None)
        if not callable(check_login):
            return  # only PlaywrightSearchProvider has this method

        logger.info("[goofish_catcher] heartbeat: probing login state")
        try:
            state: str = await asyncio.wait_for(
                check_login(timeout_sec=15),
                timeout=25,
            )
        except asyncio.TimeoutError:
            logger.warning("[goofish_catcher] heartbeat: probe timed out, skip")
            return
        except Exception as exc:
            logger.warning("[goofish_catcher] heartbeat: probe error: %s", exc)
            return

        logger.info("[goofish_catcher] heartbeat: login state = %s", state)

        if state == "ok":
            return  # all good, nothing to do

        if state not in ("auth_required", "captcha"):
            # "error" = browser not ready yet, skip silently
            return

        # Session expired or captcha wall — mirror the scheduler's auth-failure
        # path: pause all subscriptions and trigger recovery.
        if self.storage is None or self.remote_auth_coordinator is None:
            return

        paused = await self.storage.pause_all_enabled_subscriptions(state.upper())
        logger.warning(
            "[goofish_catcher] heartbeat: detected %s, paused %d subscriptions",
            state,
            paused,
        )

        if state == "auth_required":
            try:
                # Use a synthetic umo=None so the coordinator broadcasts to the
                # first available user, same as it does for remote mode.
                await self.remote_auth_coordinator.handle_provider_auth_failure(
                    umo=None,
                    sub_id=None,
                )
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher] heartbeat: auth recovery trigger failed: %s",
                    exc,
                )
            if self.notifier is not None:
                try:
                    umos: list[str] = []
                    if self.storage is not None:
                        umos = await self.storage.get_all_subscriber_umos()
                    await self.notifier.broadcast_alert(
                        code="AUTH_REQUIRED",
                        message=(
                            "登录态已过期（心跳检测），"
                            "所有订阅已暂停。请发送 /闲鱼 登录 重新扫码。"
                        ),
                        umos=umos,
                    )
                except Exception as exc:
                    logger.warning(
                        "[goofish_catcher] heartbeat: broadcast_alert failed: %s", exc
                    )

    async def _recycle_local_provider_browser(self) -> None:
        provider = self.provider
        if provider is None:
            return
        closer = getattr(provider, "close", None)
        if not callable(closer):
            return
        try:
            await closer()
            logger.info("[goofish_catcher] recycled local playwright browser session")
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to recycle local playwright browser session: %s",
                exc,
                exc_info=True,
            )

    async def _adopt_local_login_session(self, session) -> bool:
        provider = self.provider
        if provider is None:
            return False
        adopter = getattr(provider, "adopt_login_session", None)
        if not callable(adopter):
            await self._recycle_local_provider_browser()
            return False
        try:
            await adopter(session)
            return True
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to adopt local login session: %s",
                exc,
                exc_info=True,
            )
            return False

    async def _trigger_remote_auth_recovery(
        self,
        *,
        umo: str,
        sub_id: int | None = None,
    ) -> str | None:
        if self.remote_auth_coordinator is None:
            return None
        try:
            return await self.remote_auth_coordinator.handle_provider_auth_failure(
                umo=umo,
                sub_id=sub_id,
            )
        except ProviderError as exc:
            logger.warning(
                "[goofish_catcher] failed to trigger auth recovery: %s",
                exc,
                exc_info=True,
            )
            return (
                "自动启动登录恢复失败。\n"
                f"{exc.code.value}: {exc.message}\n"
                "可稍后发送 /闲鱼 登录 重试。"
            )
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to trigger auth recovery: %s",
                exc,
                exc_info=True,
            )
            return (
                "自动启动登录恢复失败。\n"
                f"{exc}\n"
                "可稍后发送 /闲鱼 登录 重试。"
            )

    async def _search_with_captcha_retry(
        self,
        *,
        keyword: str,
        pages: int,
    ) -> list[NormalizedItem]:
        if self.provider is None:
            raise RuntimeError("抓取组件不可用")
        return await search_with_captcha_retry(
            self.provider,
            keyword=keyword,
            pages=pages,
            timeout_sec=self.settings.fetch_timeout_sec,
        )

    def _search_operation_timeout_sec(self) -> int:
        return estimate_captcha_retry_timeout_sec(
            timeout_sec=self.settings.fetch_timeout_sec,
        )

    @filter.event_message_type(filter.EventMessageType.ALL, priority=maxsize - 20)
    async def auto_complete_remote_auth_flow(self, event: AstrMessageEvent):
        if not await self._check_ready(event):
            return
        reply_favorite_result = await self._build_reply_favorite_result(event)
        if reply_favorite_result is not None:
            yield reply_favorite_result.stop_event()
            return
        if self.remote_auth_coordinator is None or self.storage is None:
            return
        message_text = event.get_message_str()
        try:
            should_restart = await (
                self.remote_auth_coordinator.should_restart_login_from_message(
                    umo=event.unified_msg_origin,
                    message_text=message_text,
                )
            )
            if should_restart:
                message = await self.remote_auth_coordinator.start_login(
                    umo=event.unified_msg_origin
                )
                yield event.plain_result(message).stop_event()
                return
            should_complete = await (
                self.remote_auth_coordinator.should_auto_complete_from_message(
                    umo=event.unified_msg_origin,
                    message_text=message_text,
                )
            )
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to inspect auth recovery auto-complete message: %s",
                exc,
                exc_info=True,
            )
            return
        if not should_complete:
            return

        await self._ensure_scheduler_started()
        try:
            message = await self.remote_auth_coordinator.complete_login(
                umo=event.unified_msg_origin,
                storage=self.storage,
                scheduler=self.scheduler,
            )
            yield event.plain_result(message).stop_event()
            return
        except ProviderError as exc:
            yield event.plain_result(
                f"保存登录态失败：{exc.code.value}\n{exc.message}"
            ).stop_event()
            return
        except Exception as exc:
            yield event.plain_result(f"保存登录态失败：{exc}").stop_event()
            return

    async def _build_reply_favorite_result(
        self,
        event: AstrMessageEvent,
    ):
        messages = event.get_messages()
        raw_message_text = event.get_message_str()
        outline_text = event.get_message_outline()
        outline_reply_text, outline_selection_text = extract_reply_context_from_outline(
            outline_text
        )
        selection_candidates = [
            extract_non_reply_text(messages),
            outline_selection_text,
            raw_message_text,
        ]
        selection_text = next(
            (candidate for candidate in selection_candidates if candidate),
            None,
        )
        reply_candidates = [
            extract_reply_text(messages),
            outline_reply_text,
        ]
        reply_text = next((candidate for candidate in reply_candidates if candidate), None)
        if reply_text:
            logger.debug(
                "[goofish_catcher] inspect reply favorite candidate: selection_candidates=%r raw_message_str=%r outline_selection_text=%r component_types=%s",
                selection_candidates,
                raw_message_text,
                outline_selection_text,
                [type(component).__name__ for component in messages],
            )
        selections = None
        for candidate in selection_candidates:
            parsed = parse_reply_selection(candidate or "")
            if parsed is not None:
                selections = parsed
                selection_text = candidate
                break
        if selections is None:
            if reply_text:
                logger.debug(
                    "[goofish_catcher] reply favorite skipped: selection parse failed, selection_candidates=%r raw_message_str=%r outline_selection_text=%r outline=%r",
                    selection_candidates,
                    raw_message_text,
                    outline_selection_text,
                    outline_text,
                )
            return None

        if not reply_text:
            if outline_text:
                logger.debug(
                    "[goofish_catcher] reply favorite skipped: reply text missing, raw_message_str=%r outline=%r",
                    raw_message_text,
                    outline_text,
                )
            return None

        target = parse_reply_target(reply_text)
        if target is None:
            logger.debug(
                "[goofish_catcher] reply favorite skipped: quoted text did not match recommendation format, preview=%r",
                reply_text[:200],
            )
            return None
        logger.info(
            "[goofish_catcher] matched reply favorite request: source=%s selections=%s",
            target.source,
            selections,
        )

        if target.error_message:
            return event.plain_result(target.error_message)

        selected_items, invalid = map_reply_selection(target, selections)
        if invalid:
            max_index = max((item.index for item in target.items), default=0)
            invalid_text = "、".join(str(value) for value in invalid)
            return event.plain_result(
                f"序号超出范围：{invalid_text}\n"
                f"当前可选范围：1-{max_index}"
            )
        if not selected_items:
            return event.plain_result("未识别到可收藏的商品序号，请重新引用推荐消息后再试。")
        if self._provider_error:
            return event.plain_result(
                f"Provider 当前不可用，暂时无法执行收藏。\n原因：{self._provider_error}"
            )
        if self.provider is None:
            return event.plain_result("插件内部错误：抓取组件不可用，请重启后重试。")

        lines = ["收藏结果："]
        auth_hint: str | None = None
        interrupted = False
        for item in selected_items:
            title = item.title
            try:
                result = await self.provider.favorite_item(
                    url=item.url,
                    item_id=item.item_id,
                    timeout_sec=self.settings.fetch_timeout_sec,
                )
                display_title = result.title or title
                if result.status == "already_favorited":
                    lines.append(f"{item.index}. 已在收藏夹：{display_title}")
                else:
                    lines.append(f"{item.index}. 已收藏：{display_title}")
            except ProviderError as exc:
                logger.warning(
                    "[goofish_catcher] favorite item failed: index=%s url=%s code=%s message=%s",
                    item.index,
                    item.url,
                    exc.code.value,
                    exc.message,
                )
                lines.append(
                    f"{item.index}. 收藏失败：{title}（{exc.code.value}: {exc.message}）"
                )
                if exc.code in {
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    auth_hint = await self._trigger_remote_auth_recovery(
                        umo=event.unified_msg_origin
                    )
                    interrupted = True
                    break
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher] favorite item failed unexpectedly: index=%s url=%s error=%s",
                    item.index,
                    item.url,
                    exc,
                    exc_info=True,
                )
                lines.append(f"{item.index}. 收藏失败：{title}（{exc}）")

        if interrupted:
            remaining_count = len(selected_items) - (len(lines) - 1)
            if remaining_count > 0:
                lines.append(
                    f"后续 {remaining_count} 个商品未继续处理，请先完成登录恢复后重试。"
                )
        if auth_hint:
            lines.append(auth_hint)
        return event.plain_result("\n".join(lines))

    @filter.event_message_type(filter.EventMessageType.ALL, priority=maxsize - 21)
    async def favorite_recommendation_by_reply(self, event: AstrMessageEvent):
        if not await self._check_ready(event):
            return
        result = await self._build_reply_favorite_result(event)
        if result is None:
            return
        yield result.stop_event()
        return

    @filter.on_llm_request(priority=10000)
    async def intercept_reply_favorite_before_llm(
        self,
        event: AstrMessageEvent,
        req: ProviderRequest,
    ) -> None:
        del req
        if not self._ready:
            return
        result = await self._build_reply_favorite_result(event)
        if result is None:
            return
        logger.info("[goofish_catcher] intercept reply favorite before llm request")
        await event.send(result)
        event.should_call_llm(False)
        event.stop_event()
        return

    @filter.command_group("闲鱼", alias={"goofish"})
    async def goofish(self, event: AstrMessageEvent):
        """闲鱼监控指令入口，查看命令总览。"""
        yield event.plain_result(
            "用法：\n"
            "/闲鱼 订阅 <关键词> [interval_sec] [pages]\n"
            "/闲鱼 退订 <关键词>\n"
            "/闲鱼 列表\n"
            "/闲鱼 暂停 <关键词>\n"
            "/闲鱼 恢复 <关键词>\n"
            "/闲鱼 立即检查 [关键词]\n"
            "/闲鱼 查询 <关键词...> [--pages N]\n"
            "/闲鱼 登录\n"
            "/闲鱼 登录取消\n"
            "/闲鱼 明细 <关键词> [limit]\n"
            "/闲鱼 状态"
        )

    @goofish.command("订阅", alias={"subscribe", "watch"})
    async def subscribe(
        self,
        event: AstrMessageEvent,
        keyword: str,
        interval_sec: int = 0,
        pages: int = 0,
    ):
        """创建或更新关键词订阅，并立即触发一次检查。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        interval = (
            interval_sec if interval_sec > 0 else self.settings.default_interval_sec
        )
        page_count = pages if pages > 0 else self.settings.default_pages
        page_count = max(1, min(page_count, self.settings.max_pages))
        interval = max(30, interval)
        umo = event.unified_msg_origin
        current = await self.storage.get_subscription(umo, keyword)

        subscription, created = await self.storage.upsert_subscription(
            umo=umo,
            keyword=keyword,
            interval_sec=interval,
            pages=page_count,
            recommend_max_price=(
                current.recommend_max_price if current is not None else None
            ),
            drop_abs=self.settings.default_drop_abs,
            drop_pct=self.settings.default_drop_pct,
            new_window_sec=self.settings.default_new_window_sec,
            cooldown_sec=self.settings.default_cooldown_sec,
        )
        await self._ensure_scheduler_started()
        if self.scheduler is not None:
            await self.scheduler.enqueue_manual_check(subscription.id)

        action = "已创建" if created else "已更新"
        message = (
            f"{action}订阅：{keyword}\n"
            f"间隔：{interval}s，页数：{page_count}\n"
            f"降价阈值：￥{subscription.drop_abs:.2f} 或 {subscription.drop_pct:.1%}"
        )
        if subscription.recommend_max_price is not None:
            message += f"\n推荐价格阈值：≤￥{subscription.recommend_max_price:.2f}"
        if self._provider_error:
            message += (
                "\n⚠️ 当前 Provider 不可用，任务不会执行。"
                f"\n原因：{self._provider_error}"
            )
        yield event.plain_result(message)

    @goofish.command("退订", alias={"unsubscribe", "unwatch"})
    async def unsubscribe(self, event: AstrMessageEvent, keyword: GreedyStr):
        """删除当前会话下指定关键词的订阅。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        deleted = await self.storage.delete_subscription(
            event.unified_msg_origin, keyword
        )
        if not deleted:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        yield event.plain_result(f"已退订：{keyword}")

    @goofish.command("列表", alias={"list"})
    async def list_subscriptions(self, event: AstrMessageEvent):
        """查看当前会话的订阅列表与运行状态。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        if not subscriptions:
            yield event.plain_result("当前会话暂无订阅。")
            return

        lines = ["当前订阅："]
        for sub in subscriptions:
            status = "启用" if sub.enabled else f"暂停({sub.paused_reason or 'manual'})"
            next_run = _format_ts(sub.next_run_at)
            lines.append(
                f"- {sub.keyword} | {status} | 每{sub.interval_sec}s | pages={sub.pages} | "
                f"推荐价≤{f'￥{sub.recommend_max_price:.2f}' if sub.recommend_max_price is not None else '不限'} | "
                f"下次={next_run}"
            )
        yield event.plain_result("\n".join(lines))

    @goofish.command("暂停", alias={"pause"})
    async def pause(self, event: AstrMessageEvent, keyword: GreedyStr):
        """暂停指定关键词订阅，不再参与自动轮询。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        await self.storage.pause_subscription(sub.id, "MANUAL_PAUSE")
        yield event.plain_result(f"已暂停订阅：{keyword}")

    @goofish.command("恢复", alias={"resume"})
    async def resume(self, event: AstrMessageEvent, keyword: GreedyStr):
        """恢复已暂停订阅，并立即入队一次检查。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        now_ts = int(time.time())
        await self.storage.resume_subscription(sub.id, now_ts)
        await self._ensure_scheduler_started()
        if self.scheduler is not None:
            await self.scheduler.enqueue_manual_check(sub.id)
        yield event.plain_result(f"已恢复订阅：{keyword}")

    @goofish.command("立即检查", alias={"checknow", "run"})
    async def check_now(self, event: AstrMessageEvent, keyword: GreedyStr = ""):
        """对订阅执行立即检查并返回推荐；不填关键词则批量入队当前会话全部订阅。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self._provider_error:
            yield event.plain_result(
                f"Provider 当前不可用，无法执行立即检查。\n原因：{self._provider_error}"
            )
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return
        if self.provider is None:
            yield event.plain_result("插件内部错误：抓取组件不可用，请重启后重试。")
            return
        if self.recommender is None:
            yield event.plain_result("插件内部错误：推荐组件不可用，请重启后重试。")
            return
        await self._ensure_scheduler_started()
        if self.scheduler is None:
            yield event.plain_result("调度器未启动。")
            return

        if keyword:
            sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
            if sub is None:
                yield event.plain_result(f"未找到订阅：{keyword}")
                return
            if not sub.enabled:
                yield event.plain_result(
                    f"订阅 {keyword} 当前处于暂停状态（{sub.paused_reason or 'manual'}），请先执行 /闲鱼 恢复 {keyword}"
                )
                return
            try:
                recommendation = await self._run_immediate_subscription_check(
                    umo=event.unified_msg_origin,
                    sub=sub,
                )
                yield event.plain_result(_render_recommendation_preview(recommendation))
                return
            except asyncio.TimeoutError:
                yield event.plain_result(
                    f"立即检查超时（>{self._search_operation_timeout_sec()}s），请稍后重试。"
                )
                return
            except ProviderError as exc:
                if exc.code in {
                    ProviderErrorCode.DEPENDENCY_MISSING,
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    await self.storage.pause_subscription(sub.id, exc.code.value)
                extra_hint = ""
                if exc.code in {
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    login_hint = await self._trigger_remote_auth_recovery(
                        umo=event.unified_msg_origin,
                        sub_id=sub.id,
                    )
                    if login_hint:
                        extra_hint = f"\n{login_hint}"
                yield event.plain_result(
                    f"立即检查失败：{exc.code.value}\n{exc.message}{extra_hint}"
                )
                return
            except Exception as exc:
                yield event.plain_result(f"立即检查失败：{exc}")
                return

        checked_count = 0
        result_sections: list[str] = []
        subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        for sub in subscriptions:
            if not sub.enabled:
                continue
            checked_count += 1
            try:
                recommendation = await self._run_immediate_subscription_check(
                    umo=event.unified_msg_origin,
                    sub=sub,
                )
                result_sections.append(_render_recommendation_preview(recommendation))
            except asyncio.TimeoutError:
                result_sections.append(
                    _render_manual_check_error(
                        keyword=sub.keyword,
                        message=(
                            f"立即检查超时（>{self._search_operation_timeout_sec()}s），请稍后重试。"
                        ),
                    )
                )
            except ProviderError as exc:
                if exc.code in {
                    ProviderErrorCode.DEPENDENCY_MISSING,
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    await self.storage.pause_subscription(sub.id, exc.code.value)
                extra_hint = ""
                if exc.code in {
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    login_hint = await self._trigger_remote_auth_recovery(
                        umo=event.unified_msg_origin,
                        sub_id=sub.id,
                    )
                    if login_hint:
                        extra_hint = f"\n{login_hint}"
                result_sections.append(
                    _render_manual_check_error(
                        keyword=sub.keyword,
                        message=f"立即检查失败：{exc.code.value}\n{exc.message}{extra_hint}",
                    )
                )
            except Exception as exc:
                result_sections.append(
                    _render_manual_check_error(
                        keyword=sub.keyword,
                        message=f"立即检查失败：{exc}",
                    )
                )

        if checked_count == 0:
            yield event.plain_result("没有可执行的订阅，请先创建并启用订阅。")
            return
        yield event.plain_result(
            _render_batch_manual_check_results(
                total_subscriptions=checked_count,
                sections=result_sections,
            )
        )

    @goofish.command("查询", alias={"query", "search", "inspect"})
    async def query_once(
        self,
        event: AstrMessageEvent,
        keyword: GreedyStr = "",
    ):
        """免订阅查询：整段关键词可包含空格，可选 --pages/-p 指定页数，--min-price/--max-price 过滤价格区间。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self._provider_error:
            yield event.plain_result(
                f"Provider 当前不可用，无法执行查询。\n原因：{self._provider_error}"
            )
            return
        if self.provider is None:
            yield event.plain_result("插件内部错误：抓取组件不可用，请重启后重试。")
            return
        if self.recommender is None:
            yield event.plain_result("插件内部错误：推荐组件不可用，请重启后重试。")
            return

        raw_query_args = _merge_query_args(
            message_query_args=_extract_subcommand_args(event.get_message_str()),
            parsed_keyword=str(keyword).strip(),
        )
        keyword_text, page_count, price_min, price_max = _parse_query_input(
            raw_keyword=raw_query_args,
            default_pages=self.settings.default_pages,
            max_pages=self.settings.max_pages,
        )
        if not keyword_text:
            yield event.plain_result(
                "关键词不能为空。示例：/闲鱼 查询 适马 60-600 --pages 2"
            )
            return
        timeout_sec = self._search_operation_timeout_sec()
        try:
            raw_items = await asyncio.wait_for(
                self._search_with_captcha_retry(
                    keyword=keyword_text,
                    pages=page_count,
                ),
                timeout=timeout_sec,
            )
            filtered_items, filter_mode = await self.recommender.prefilter_items(
                umo=event.unified_msg_origin,
                keyword=keyword_text,
                items=raw_items,
            )
            if price_min is not None or price_max is not None:
                filtered_items = [
                    item for item in filtered_items
                    if (price_min is None or item.price >= price_min)
                    and (price_max is None or item.price <= price_max)
                ]
            candidates = _build_query_candidates(
                keyword=keyword_text,
                items=filtered_items,
                observed_at=int(time.time()),
            )
            recommendation = await self.recommender.analyze(
                umo=event.unified_msg_origin,
                keyword=keyword_text,
                candidates=candidates,
                top_k=self.settings.llm_top_k,
            )
            yield event.plain_result(
                _render_query_recommendation_preview(
                    recommendation=recommendation,
                    page_count=page_count,
                    raw_total=len(raw_items),
                    filtered_total=len(filtered_items),
                    filter_mode=filter_mode,
                    price_min=price_min,
                    price_max=price_max,
                )
            )
            return
        except asyncio.TimeoutError:
            yield event.plain_result(f"查询超时（>{timeout_sec}s），请稍后重试。")
            return
        except ProviderError as exc:
            extra_hint = ""
            if exc.code in {
                ProviderErrorCode.AUTH_REQUIRED,
                ProviderErrorCode.CAPTCHA,
            }:
                login_hint = await self._trigger_remote_auth_recovery(
                    umo=event.unified_msg_origin
                )
                if login_hint:
                    extra_hint = f"\n{login_hint}"
            yield event.plain_result(
                f"查询失败：{exc.code.value}\n{exc.message}{extra_hint}"
            )
            return
        except Exception as exc:
            yield event.plain_result(f"查询失败：{exc}")
            return

    @goofish.command("登录", alias={"login", "auth"})
    async def remote_login(self, event: AstrMessageEvent):
        """手动拉起登录流程并回传二维码截图。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.remote_auth_coordinator is None:
            yield event.plain_result("当前 Provider 未启用登录恢复流程。")
            return

        try:
            message = await self.remote_auth_coordinator.start_login(
                umo=event.unified_msg_origin
            )
            yield event.plain_result(message)
            return
        except ProviderError as exc:
            yield event.plain_result(f"启动登录失败：{exc.code.value}\n{exc.message}")
            return
        except Exception as exc:
            yield event.plain_result(f"启动登录失败：{exc}")
            return

    @goofish.command("登录完成", alias={"login_done", "auth_done"})
    async def remote_login_done(self, event: AstrMessageEvent):
        """确认扫码已完成，保存登录态并自动恢复订阅。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.remote_auth_coordinator is None:
            yield event.plain_result("当前 Provider 未启用登录恢复流程。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        await self._ensure_scheduler_started()
        try:
            message = await self.remote_auth_coordinator.complete_login(
                umo=event.unified_msg_origin,
                storage=self.storage,
                scheduler=self.scheduler,
            )
            yield event.plain_result(message)
            return
        except ProviderError as exc:
            yield event.plain_result(f"保存登录态失败：{exc.code.value}\n{exc.message}")
            return
        except Exception as exc:
            yield event.plain_result(f"保存登录态失败：{exc}")
            return

    @goofish.command("登录取消", alias={"login_cancel", "auth_cancel"})
    async def remote_login_cancel(self, event: AstrMessageEvent):
        """取消当前登录恢复流程。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.remote_auth_coordinator is None:
            yield event.plain_result("当前 Provider 未启用登录恢复流程。")
            return

        try:
            message = await self.remote_auth_coordinator.cancel_login(
                umo=event.unified_msg_origin
            )
            yield event.plain_result(message)
            return
        except ProviderError as exc:
            yield event.plain_result(f"取消登录恢复失败：{exc.code.value}\n{exc.message}")
            return
        except Exception as exc:
            yield event.plain_result(f"取消登录恢复失败：{exc}")
            return

    @goofish.command("明细", alias={"detail", "items"})
    async def detail(
        self,
        event: AstrMessageEvent,
        keyword: str,
        limit: int = 10,
    ):
        """查看订阅最近一次缓存快照，不触发新抓取。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return

        limit = max(1, min(limit, 30))
        if sub.last_run_at is None:
            yield event.plain_result(
                f"订阅 {keyword} 暂无缓存结果。先执行 /闲鱼 立即检查 {keyword}"
            )
            return

        snapshot_ts = int(sub.last_run_at)
        items, total = await self.storage.list_items_by_snapshot(
            sub_id=sub.id,
            snapshot_ts=snapshot_ts,
            limit=limit,
        )
        yield event.plain_result(
            _render_items_detail(
                sub.keyword,
                items,
                limit=limit,
                total=total,
                snapshot_ts=snapshot_ts,
            )
        )

    @goofish.command("状态", alias={"status"})
    async def status(self, event: AstrMessageEvent):
        """查看调度器、Provider 与当前会话订阅的运行状态。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self.storage is None:
            yield event.plain_result("插件内部错误：存储组件不可用，请重启后重试。")
            return

        await self._ensure_scheduler_started()
        scheduler_status = (
            await self.scheduler.get_status() if self.scheduler is not None else {}
        )
        umo_subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        enabled_local = sum(1 for sub in umo_subscriptions if sub.enabled)
        paused_local = len(umo_subscriptions) - enabled_local

        lines = [
            "闲鱼监控状态：",
            f"- 运行中：{scheduler_status.get('running', False)}",
            f"- 队列长度：{scheduler_status.get('queue_size', 0)}",
            f"- 执行中：{scheduler_status.get('inflight', 0)}",
            f"- Worker 数：{scheduler_status.get('workers', 0)}",
            f"- 当前会话订阅：{len(umo_subscriptions)}（启用 {enabled_local} / 暂停 {paused_local}）",
            f"- 全局启用订阅：{scheduler_status.get('enabled_subscriptions', 0)}",
            f"- Provider：{self.settings.provider_mode}",
            f"- Provider 可用：{self._provider_error is None}",
            f"- Provider 错误：{self._provider_error or '-'}",
            f"- DB：{self.settings.db_path}",
            f"- Admin WebUI：{self.admin_webui_url or '-'}",
        ]
        lines.extend(
            _render_remote_status_lines(
                settings=self.settings,
                provider_health=self._provider_health,
                provider_health_checked_at=self._provider_health_checked_at,
            )
        )
        yield event.plain_result("\n".join(lines))

    async def _ensure_scheduler_started(self) -> None:
        if self.scheduler is None:
            return
        if self._provider_error:
            return
        if self.scheduler.running:
            return
        async with self._start_lock:
            if not self.scheduler.running:
                await self.scheduler.start()

    async def _check_ready(self, event: AstrMessageEvent) -> bool:
        if self._ready and self.storage is not None:
            return True
        logger.warning("[goofish_catcher] command called before ready")
        return False


def _format_ts(ts: int | None) -> str:
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


async def _run_remote_provider_healthcheck(
    provider: SearchProvider,
    settings: PluginSettings,
    *,
    ignore_disabled: bool = False,
) -> tuple[dict[str, Any] | None, int | None]:
    if settings.provider_mode != PROVIDER_MODE_REMOTE_REST:
        return None, None
    if not ignore_disabled and not settings.remote_healthcheck_on_init:
        return None, None

    healthcheck = getattr(provider, "healthcheck", None)
    if not callable(healthcheck):
        raise ProviderError(
            ProviderErrorCode.NETWORK_ERROR,
            "remote provider does not support healthcheck",
        )

    checked_at = int(time.time())
    result = await healthcheck(timeout_sec=settings.remote_healthcheck_timeout_sec)
    if not isinstance(result, dict):
        raise ProviderError(
            ProviderErrorCode.PARSE_ERROR,
            "remote healthcheck payload is not an object",
        )
    if result.get("ok") is not True:
        raise ProviderError(
            ProviderErrorCode.NETWORK_ERROR,
            "remote healthcheck did not return ok=true",
        )
    return result, checked_at


def _render_remote_status_lines(
    *,
    settings: PluginSettings,
    provider_health: dict[str, Any] | None,
    provider_health_checked_at: int | None,
) -> list[str]:
    if settings.provider_mode != PROVIDER_MODE_REMOTE_REST:
        return []

    lines = [
        f"- 远程地址：{settings.remote_base_url or '-'}",
        f"- 启动健康检查：{settings.remote_healthcheck_on_init}",
        f"- 最近健康检查：{_format_ts(provider_health_checked_at) if provider_health_checked_at else '未执行'}",
    ]
    if not provider_health:
        lines.append("- 远程健康详情：-")
        return lines

    lines.append(
        "- 远程健康详情："
        f"ok={provider_health.get('ok', False)}, "
        f"provider={provider_health.get('provider', '-')}, "
        f"auth={provider_health.get('auth', '-')}, "
        "storage_state="
        f"{'yes' if provider_health.get('storage_state') else 'no'}"
    )
    provider_error = provider_health.get("provider_error")
    if provider_error:
        lines.append(f"- 远程 Worker 错误：{provider_error}")
    return lines


def _render_recommendation_preview(recommendation: RecommendationResult) -> str:
    lines = [
        f"【立即检查】关键词：{recommendation.keyword}",
        f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
        f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
        f"总体建议：{recommendation.summary}",
    ]
    if recommendation.fallback_reason:
        lines.append(f"回退原因：{recommendation.fallback_reason}")

    if not recommendation.top:
        lines.append("本次检查已完成，未命中可推荐条目。")
        lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
        return "\n".join(lines)

    for idx, item in enumerate(recommendation.top, start=1):
        lines.append(f"{idx}. [{item.score:.1f}] {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   理由：{item.reason}")
        lines.append(f"   风险：{item.risk}")
        lines.append(f"   链接：{item.url}")
    lines.append(recommendation_reply_hint())
    lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
    return "\n".join(lines)


def _render_manual_check_error(keyword: str, message: str) -> str:
    return f"【立即检查】关键词：{keyword}\n{message}"


def _render_batch_manual_check_results(
    *,
    total_subscriptions: int,
    sections: list[str],
) -> str:
    if not sections:
        return "没有可展示的立即检查结果。"
    if len(sections) == 1:
        return sections[0]
    return "\n\n".join(
        [
            f"【立即检查】共执行 {total_subscriptions} 个订阅，结果如下：",
            *sections,
        ]
    )


def _build_query_candidates(
    keyword: str,
    items: list[NormalizedItem],
    observed_at: int,
) -> list[RecommendationCandidate]:
    return [
        RecommendationCandidate(
            event_type="NEW",
            keyword=keyword,
            item_id=item.item_id,
            title=item.title,
            price=item.price,
            url=item.url,
            publish_time=item.publish_time,
            observed_at=observed_at,
        )
        for item in items
    ]


def _extract_subcommand_args(message: str) -> str:
    normalized = re.sub(r"\s+", " ", message.strip())
    if not normalized:
        return ""
    # Prefer explicit command extraction first.
    patterns = (
        r"^/?(?:闲鱼|goofish)\s+(?:查询|query|search|inspect)\s*(.*)$",
        r"^(?:查询|query|search|inspect)\s*(.*)$",
    )
    for pattern in patterns:
        matched = re.match(pattern, normalized, flags=re.IGNORECASE)
        if matched:
            return (matched.group(1) or "").strip()
    parts = normalized.split(" ", 2)
    if len(parts) < 3:
        return ""
    return parts[2].strip()


def _merge_query_args(*, message_query_args: str, parsed_keyword: str) -> str:
    from_message = message_query_args.strip()
    from_param = parsed_keyword.strip()
    if from_message and from_param and from_param not in from_message:
        return f"{from_param} {from_message}".strip()
    return from_message or from_param


def _parse_query_input(
    raw_keyword: str,
    *,
    default_pages: int,
    max_pages: int,
) -> tuple[str, int, float | None, float | None]:
    text = raw_keyword.strip()
    page_count = max(1, min(default_pages, max_pages))
    price_min: float | None = None
    price_max: float | None = None
    if not text:
        return "", page_count, price_min, price_max

    matches = list(
        re.finditer(
            r"(?<!\S)(?:--pages|-p)(?:\s*=\s*|\s+)?(\d+)\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    if matches:
        matched = matches[-1]
        page_count = max(1, min(int(matched.group(1)), max_pages))
        text = f"{text[: matched.start()]} {text[matched.end() :]}"
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"^[，,。.!?]+|[，,。.!?]+$", "", text).strip()

    for flag_re, is_min in [
        (r"(?<!\S)(?:--min-price|--min)(?:\s*=\s*|\s+)?(\d+(?:\.\d+)?)\b", True),
        (r"(?<!\S)(?:--max-price|--max)(?:\s*=\s*|\s+)?(\d+(?:\.\d+)?)\b", False),
    ]:
        flag_matches = list(re.finditer(flag_re, text, flags=re.IGNORECASE))
        if flag_matches:
            m = flag_matches[-1]
            val = float(m.group(1))
            if is_min:
                price_min = val
            else:
                price_max = val
            text = f"{text[: m.start()]} {text[m.end() :]}"
            text = re.sub(r"\s+", " ", text).strip()
            text = re.sub(r"^[，,。.!?]+|[，,。.!?]+$", "", text).strip()

    return text, page_count, price_min, price_max


def _render_query_recommendation_preview(
    recommendation: RecommendationResult,
    *,
    page_count: int,
    raw_total: int,
    filtered_total: int,
    filter_mode: str,
    price_min: float | None = None,
    price_max: float | None = None,
) -> str:
    lines = [
        f"【查询推荐】关键词：{recommendation.keyword}",
        f"抓取页数：{page_count} | 原始结果：{raw_total} | 初筛后：{filtered_total}",
        f"初筛模式：{filter_mode}",
    ]
    if price_min is not None or price_max is not None:
        parts = []
        if price_min is not None:
            parts.append(f"≥￥{price_min:.0f}")
        if price_max is not None:
            parts.append(f"≤￥{price_max:.0f}")
        lines.append(f"价格区间：{' '.join(parts)}")
    lines += [
        f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
        f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
        f"总体建议：{recommendation.summary}",
    ]
    if recommendation.fallback_reason:
        lines.append(f"回退原因：{recommendation.fallback_reason}")

    if not recommendation.top:
        lines.append("未产出可推荐条目，请尝试更精确的关键词后重试。")
        return "\n".join(lines)

    for idx, item in enumerate(recommendation.top, start=1):
        lines.append(f"{idx}. [{item.score:.1f}] {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   理由：{item.reason}")
        lines.append(f"   风险：{item.risk}")
        lines.append(f"   链接：{item.url}")
    lines.append(recommendation_reply_hint())
    re_execute = f"/闲鱼 查询 {recommendation.keyword}"
    if price_min is not None:
        re_execute += f" --min-price {price_min:.0f}"
    if price_max is not None:
        re_execute += f" --max-price {price_max:.0f}"
    lines.append(f"可再次执行 {re_execute}")
    return "\n".join(lines)


def _render_items_detail(
    keyword: str,
    items: list[NormalizedItem],
    limit: int = 10,
    total: int | None = None,
    snapshot_ts: int | None = None,
) -> str:
    total_count = total if total is not None else len(items)
    if not items:
        if snapshot_ts is None:
            return f"【明细】关键词：{keyword}\n暂无缓存商品。"
        return (
            f"【明细】关键词：{keyword}\n"
            f"最近一次缓存时间：{_format_ts(snapshot_ts)}\n"
            "该次结果为 0 条商品。"
        )

    top = items[:limit]
    lines = [
        f"【明细】关键词：{keyword}",
        f"最近一次缓存时间：{_format_ts(snapshot_ts) if snapshot_ts else '-'}",
        f"该次缓存共 {total_count} 条，展示前 {len(top)} 条：",
    ]
    for idx, item in enumerate(top, start=1):
        lines.append(f"{idx}. {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   链接：{item.url}")
    return "\n".join(lines)
