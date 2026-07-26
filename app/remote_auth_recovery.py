from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from astrbot.api.event import MessageChain
from astrbot.api.star import Context

from .auth_session import AUTH_SESSION_TIMEOUT_SEC
from .config import PluginSettings
from .platforms.registry import (
    PLATFORM_GOOFISH,
    PLATFORM_TAOBAO,
    platform_display_name,
)

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

AUTH_PAUSE_REASONS = ("AUTH_REQUIRED", "CAPTCHA")
# Returned by handle_provider_auth_failure / start_login when quick login
# succeeded automatically (no QR scan needed).  The caller in main.py detects
# this and runs the subscription-resume logic directly.
AUTO_LOGIN_DONE_SENTINEL = "AUTO_LOGIN_DONE"
REMOTE_AUTH_COMMAND_PREFIXES = (
    "/闲鱼",
    "/goofish",
)
# 重启登录的消息标记：基础形态 = goofish；带平台后缀（如「… 淘宝」）路由到
# 对应平台。与 /闲鱼 登录 [平台] 命令的参数形态保持一致。
_LOGIN_RESTART_BASES = (
    "闲鱼 登录",
    "/闲鱼 登录",
    "goofish login",
    "/goofish login",
    "goofish auth",
    "/goofish auth",
)
_RESTART_PLATFORM_SUFFIXES: dict[str, str] = {
    "": PLATFORM_GOOFISH,
    " 淘宝": PLATFORM_TAOBAO,
    " taobao": PLATFORM_TAOBAO,
}
LOGIN_RESTART_MARKERS = tuple(
    base + suffix
    for base in _LOGIN_RESTART_BASES
    for suffix in _RESTART_PLATFORM_SUFFIXES
)
CANCEL_MARKERS = (
    "闲鱼 登录取消",
    "/闲鱼 登录取消",
    "goofish login_cancel",
    "/goofish login_cancel",
    "goofish auth_cancel",
    "/goofish auth_cancel",
)


@dataclass(slots=True)
class ActiveRemoteAuthFlow:
    session_id: str
    owner_umo: str
    started_at: int
    expires_at: float
    page_url: str
    affected_subscription_ids: set[int] = field(default_factory=set)
    # 该 flow 所属平台：决定使用哪个 auth controller、登录成功后恢复哪些
    # 平台的订阅，以及通知文案的平台显示名。缺省 goofish（向后兼容）。
    platform: str = PLATFORM_GOOFISH


class RemoteAuthRecoveryCoordinator:
    def __init__(
        self,
        *,
        context: Context,
        settings: PluginSettings,
        provider: Any | None = None,
        auth_controller: Any | None = None,
        auth_timeout_sec: float = AUTH_SESSION_TIMEOUT_SEC,
    ) -> None:
        self.context = context
        self.settings = settings
        self.auth_timeout_sec = max(1.0, float(auth_timeout_sec))
        # 按平台注册的 auth controller；构造时传入的单 controller 视为 goofish
        # （向后兼容既有调用方），其他平台经 set_auth_controller 注册。
        self._auth_controllers: dict[str, Any] = {}
        default_controller = auth_controller or provider
        if default_controller is not None:
            self._auth_controllers[PLATFORM_GOOFISH] = default_controller
        self._lock = asyncio.Lock()
        # 进行中的登录恢复 flow，按平台隔离（键 = platform），互不干扰。
        self._active_flows: dict[str, ActiveRemoteAuthFlow] = {}
        self._timeout_tasks: dict[str, asyncio.Task] = {}
        self._idle_event = asyncio.Event()
        self._idle_event.set()

    @property
    def auth_controller(self) -> Any | None:
        """缺省（goofish）平台的 auth controller；保留给既有调用方。"""
        return self._auth_controllers.get(PLATFORM_GOOFISH)

    @auth_controller.setter
    def auth_controller(self, controller: Any | None) -> None:
        if controller is None:
            self._auth_controllers.pop(PLATFORM_GOOFISH, None)
        else:
            self._auth_controllers[PLATFORM_GOOFISH] = controller

    @property
    def _active_flow(self) -> ActiveRemoteAuthFlow | None:
        """goofish 平台的活跃 flow；仅为兼容既有测试/调用方保留。"""
        return self._active_flows.get(PLATFORM_GOOFISH)

    @_active_flow.setter
    def _active_flow(self, flow: ActiveRemoteAuthFlow | None) -> None:
        if flow is None:
            self._active_flows.pop(PLATFORM_GOOFISH, None)
        else:
            self._active_flows[PLATFORM_GOOFISH] = flow

    def set_auth_controller(self, platform: str, controller: Any | None) -> None:
        """注册（或传 None 注销）指定平台的 auth controller。"""
        key = _normalize_platform(platform)
        if controller is None:
            self._auth_controllers.pop(key, None)
        else:
            self._auth_controllers[key] = controller

    def _controller_for(self, platform: str) -> Any | None:
        return self._auth_controllers.get(platform)

    async def handle_provider_auth_failure(
        self,
        *,
        umo: str,
        sub_id: int | None = None,
        platform: str = "goofish",
    ) -> str | None:
        platform = _normalize_platform(platform)
        controller = self._controller_for(platform)
        if not self._supports_auth_recovery(controller):
            return None

        notify_umo: str | None = None
        notify_chain: MessageChain | None = None
        async with self._lock:
            active_flow = self._active_flows.get(platform)
            if active_flow is not None:
                if sub_id is not None:
                    active_flow.affected_subscription_ids.add(sub_id)
                return None

            payload = await controller.start_auth_session(force_restart=False)
            if payload.get("auto_login_done"):
                return AUTO_LOGIN_DONE_SENTINEL
            started_at = _safe_int(payload.get("started_at")) or int(time.time())
            flow = ActiveRemoteAuthFlow(
                session_id=str(payload.get("session_id", "")).strip(),
                owner_umo=umo,
                started_at=started_at,
                expires_at=_resolve_flow_expires_at(
                    payload,
                    started_at=started_at,
                    default_timeout_sec=self.auth_timeout_sec,
                ),
                page_url=str(payload.get("page_url", "")).strip(),
                affected_subscription_ids=({sub_id} if sub_id is not None else set()),
                platform=platform,
            )
            self._set_active_flow(flow)
            notify_umo = umo
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=flow.page_url,
                timeout_sec=int(self._timeout_seconds_for_flow(flow)),
                owner_only=False,
                platform=platform,
            )

        if notify_umo and notify_chain is not None:
            await self._send_chain(notify_umo, notify_chain)
            return _qr_sent_text(platform)
        return None

    async def start_login(self, *, umo: str, platform: str = "goofish") -> str:
        platform = _normalize_platform(platform)
        controller = self._controller_for(platform)
        if not self._supports_auth_recovery(controller):
            return "当前 Provider 未启用登录恢复流程。"

        notify_chain: MessageChain | None = None
        async with self._lock:
            active_flow = self._active_flows.get(platform)
            if active_flow is not None and active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能接管。"
            force_restart = active_flow is not None

            payload = await controller.start_auth_session(
                force_restart=force_restart
            )
            if payload.get("auto_login_done"):
                await self._clear_active_flow_locked(platform)
                return AUTO_LOGIN_DONE_SENTINEL
            existing_ids = (
                set(active_flow.affected_subscription_ids)
                if active_flow is not None
                else set()
            )
            started_at = _safe_int(payload.get("started_at")) or int(time.time())
            flow = ActiveRemoteAuthFlow(
                session_id=str(payload.get("session_id", "")).strip(),
                owner_umo=umo,
                started_at=started_at,
                expires_at=_resolve_flow_expires_at(
                    payload,
                    started_at=started_at,
                    default_timeout_sec=self.auth_timeout_sec,
                ),
                page_url=str(payload.get("page_url", "")).strip(),
                affected_subscription_ids=existing_ids,
                platform=platform,
            )
            self._set_active_flow(flow)
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=flow.page_url,
                timeout_sec=int(self._timeout_seconds_for_flow(flow)),
                owner_only=True,
                platform=platform,
            )

        if notify_chain is not None:
            await self._send_chain(umo, notify_chain)
        if force_restart:
            return "已重启登录流程并将新的二维码发送到当前会话。"
        return "已将登录二维码发送到当前会话，扫码登录后回复任意消息即可继续。"

    async def complete_login(
        self,
        *,
        umo: str,
        storage,
        scheduler,
    ) -> str:
        async with self._lock:
            owned = self._find_flows_for_umo_locked(umo)
            if not owned:
                if self._active_flows:
                    return "登录恢复已在其他会话进行中，当前会话不能确认。"
                if not self._supports_auth_recovery(
                    self._controller_for(PLATFORM_GOOFISH)
                ):
                    return "当前 Provider 未启用登录恢复流程。"
                return "当前没有进行中的登录恢复流程，请先发送 /闲鱼 登录。"
            live: list[tuple[str, str]] = []
            expired_platforms: list[str] = []
            for flow_platform, flow in owned:
                if self._is_flow_expired(flow):
                    await self._clear_active_flow_locked(flow_platform)
                    expired_platforms.append(flow_platform)
                    continue
                self._cancel_timeout_task_locked(flow_platform)
                live.append((flow_platform, flow.session_id))

        if not live:
            return (
                f"登录二维码已超时（>{int(self.auth_timeout_sec)}s），"
                f"请重新{_restart_action_hint(expired_platforms[0])}。"
            )

        # 逐平台确认。通常只有一个 flow；同一会话双平台并发扫码时逐个尝试，
        # 避免 dict 插入顺序决定确认哪个平台（先插入的失败会卡死后插入的）。
        # 确认失败的 flow 保持活跃并重新武装超时看门狗（上面已统一取消），
        # 用户可重扫后再回复确认；不重新武装会留下永不超时的僵尸 flow
        # （不通知、不释放浏览器会话、卡住 scheduler 的 wait_until_idle）。
        successes: list[tuple[str, dict[str, Any]]] = []
        failures: list[tuple[str, Exception]] = []
        for flow_platform, session_id in live:
            try:
                result = await self._controller_for(flow_platform).confirm_auth_session(
                    session_id=session_id
                )
            except Exception as exc:
                failures.append((flow_platform, exc))
                async with self._lock:
                    retained = self._active_flows.get(flow_platform)
                    if retained is not None and retained.session_id == session_id:
                        self._set_active_flow(retained)
                continue
            successes.append((flow_platform, result))
            async with self._lock:
                await self._clear_active_flow_locked(flow_platform)

        if not successes:
            # 单 flow 语义不变：确认失败直接抛给调用方渲染错误。
            raise failures[0][1]

        now_ts = int(time.time())
        message_blocks: list[str] = []
        for flow_platform, result in successes:
            # 只恢复与本次登录同平台的 AUTH 暂停订阅，其他平台保持原样。
            resumed = await storage.resume_subscriptions_by_pause_reasons(
                AUTH_PAUSE_REASONS,
                now_ts=now_ts,
                platform=flow_platform,
            )
            enqueued = 0
            for sub in resumed:
                if scheduler is None:
                    continue
                if await scheduler.enqueue_manual_check(sub.id):
                    enqueued += 1
            message_blocks.append(
                _build_complete_message(
                    flow_platform,
                    result=result,
                    resumed_count=len(resumed),
                    enqueued_count=enqueued,
                )
            )
        for flow_platform, exc in failures:
            message_blocks.append(
                f"{platform_display_name(flow_platform)}登录确认失败：{exc}。"
                "可重新扫码后回复任意消息再次确认。"
            )
        return "\n".join(message_blocks)

    async def cancel_login(self, *, umo: str) -> str:
        async with self._lock:
            owned = self._find_flows_for_umo_locked(umo)
            if not owned:
                if self._active_flows:
                    return "登录恢复已在其他会话进行中，当前会话不能取消。"
                if not self._supports_auth_recovery(
                    self._controller_for(PLATFORM_GOOFISH)
                ):
                    return "当前 Provider 未启用登录恢复流程。"
                return "当前没有进行中的登录恢复流程。"
            targets = [(platform, flow.session_id) for platform, flow in owned]
            for flow_platform, _ in targets:
                self._cancel_timeout_task_locked(flow_platform)

        # 逐平台取消并隔离异常：某个 controller 取消失败不能拦住其余平台，
        # 也不能让 flow 留在 _active_flows 里（看门狗已取消，留下即僵尸——
        # 用户已明确要取消，coordinator 状态一律清除，controller 侧会话
        # 由其自身的过期逻辑兜底）。全部失败时抛出首个异常保持原有报错语义。
        cancel_errors: list[Exception] = []
        for flow_platform, session_id in targets:
            try:
                await self._controller_for(flow_platform).cancel_auth_session(
                    session_id=session_id
                )
            except Exception as exc:
                cancel_errors.append(exc)
                logger.warning(
                    "[goofish_catcher] failed to cancel auth session"
                    " (platform=%s, session_id=%s): %s",
                    flow_platform,
                    session_id,
                    exc,
                )

        async with self._lock:
            for flow_platform, _ in targets:
                await self._clear_active_flow_locked(flow_platform)
        if len(cancel_errors) == len(targets) and cancel_errors:
            raise cancel_errors[0]
        return "已取消当前登录恢复流程。"

    def has_active_flow(self) -> bool:
        return bool(self._active_flows)

    async def wait_until_idle(self) -> None:
        await self._idle_event.wait()

    async def should_auto_complete_from_message(
        self,
        *,
        umo: str,
        message_text: str,
    ) -> bool:
        normalized = str(message_text or "").strip()
        if not normalized:
            return False

        # 检查该 umo 拥有的全部 flow：只要有任意一个未过期就放行
        # （残留的过期 flow 不能挡住另一平台仍有效的确认，complete_login
        # 自己会清理过期项）。
        async with self._lock:
            owned = self._find_flows_for_umo_locked(umo)
            if not owned:
                return False
            if all(self._is_flow_expired(flow) for _platform, flow in owned):
                return False

        lowered = normalized.lower()
        if self._is_restart_message(lowered) or self._is_cancel_message(lowered):
            return False
        if any(lowered.startswith(prefix.lower()) for prefix in REMOTE_AUTH_COMMAND_PREFIXES):
            return False
        return True

    async def should_restart_login_from_message(
        self,
        *,
        umo: str,
        message_text: str,
    ) -> bool:
        normalized = str(message_text or "").strip()
        if not normalized:
            return False

        async with self._lock:
            owned = self._find_flows_for_umo_locked(umo)
            if not owned:
                return False
            if all(self._is_flow_expired(flow) for _platform, flow in owned):
                return False

        return self._is_restart_message(normalized.lower())

    @staticmethod
    def resolve_restart_platform(message_text: str) -> str:
        """restart 消息标记 → 目标平台；非标记消息返回 goofish（缺省平台）。

        仅在 should_restart_login_from_message 为 True 后调用，用于把
        「闲鱼 登录 淘宝」这类带平台后缀的重启消息路由到对应平台。
        """
        lowered = str(message_text or "").strip().lower()
        return _LOGIN_RESTART_PLATFORMS_LOWER.get(lowered, PLATFORM_GOOFISH)

    async def close(self) -> None:
        async with self._lock:
            platforms = list(self._active_flows) + [
                platform
                for platform in self._timeout_tasks
                if platform not in self._active_flows
            ]
            for platform in platforms:
                await self._clear_active_flow_locked(platform)
        closed_controller_ids: set[int] = set()
        for controller in self._auth_controllers.values():
            if id(controller) in closed_controller_ids:
                continue
            closed_controller_ids.add(id(controller))
            if callable(getattr(controller, "close", None)):
                await controller.close()

    def _supports_auth_recovery(self, controller: Any | None) -> bool:
        return bool(
            controller is not None
            and callable(getattr(controller, "start_auth_session", None))
            and callable(getattr(controller, "confirm_auth_session", None))
            and callable(getattr(controller, "cancel_auth_session", None))
        )

    def _find_flows_for_umo_locked(
        self,
        umo: str,
    ) -> list[tuple[str, ActiveRemoteAuthFlow]]:
        """返回该 umo 拥有的全部 (platform, flow)。须持锁调用。"""
        return [
            (platform, flow)
            for platform, flow in self._active_flows.items()
            if flow.owner_umo == umo
        ]

    async def _send_chain(self, umo: str, chain: MessageChain) -> None:
        try:
            await self.context.send_message(umo, chain)
        except Exception as exc:
            logger.error(
                "[goofish_catcher] failed to send auth recovery message: %s",
                exc,
                exc_info=True,
            )

    def _set_active_flow(self, flow: ActiveRemoteAuthFlow) -> None:
        platform = _normalize_platform(flow.platform)
        self._active_flows[platform] = flow
        self._idle_event.clear()
        self._cancel_timeout_task_locked(platform)
        self._timeout_tasks[platform] = asyncio.create_task(
            self._expire_flow_after_timeout(platform, flow.session_id)
        )

    async def _clear_active_flow_locked(self, platform: str) -> None:
        self._active_flows.pop(platform, None)
        self._cancel_timeout_task_locked(platform)
        if not self._active_flows:
            self._idle_event.set()

    def _cancel_timeout_task_locked(self, platform: str) -> None:
        task = self._timeout_tasks.pop(platform, None)
        if task is None:
            return
        if task is asyncio.current_task():
            return
        task.cancel()

    async def _expire_flow_after_timeout(self, platform: str, session_id: str) -> None:
        notify_umo: str | None = None
        try:
            async with self._lock:
                active_flow = self._active_flows.get(platform)
                if active_flow is None or active_flow.session_id != session_id:
                    return
                sleep_sec = max(0.0, active_flow.expires_at - time.time())
            await asyncio.sleep(sleep_sec)

            async with self._lock:
                active_flow = self._active_flows.get(platform)
                if active_flow is None or active_flow.session_id != session_id:
                    return
                notify_umo = active_flow.owner_umo
                await self._clear_active_flow_locked(platform)

            controller = self._controller_for(platform)
            if controller is not None:
                try:
                    await controller.cancel_auth_session(session_id=session_id)
                except Exception as exc:
                    logger.warning(
                        "[goofish_catcher] failed to cancel timed out auth session %s: %s",
                        session_id,
                        exc,
                    )

            if notify_umo:
                await self._send_chain(
                    notify_umo,
                    MessageChain().message(
                        f"本次登录二维码已超时（{int(self.auth_timeout_sec)}s），"
                        f"如需继续请重新{_restart_action_hint(platform)}。"
                    ),
                )
        except asyncio.CancelledError:
            raise

    def _is_flow_expired(self, flow: ActiveRemoteAuthFlow) -> bool:
        return time.time() >= flow.expires_at

    def _timeout_seconds_for_flow(self, flow: ActiveRemoteAuthFlow) -> float:
        return max(1.0, flow.expires_at - flow.started_at)

    def _is_restart_message(self, lowered_message: str) -> bool:
        return lowered_message in _LOGIN_RESTART_MARKERS_LOWER

    def _is_cancel_message(self, lowered_message: str) -> bool:
        return lowered_message in _CANCEL_MARKERS_LOWER


def _build_login_chain(
    *,
    screenshot_base64: str,
    page_url: str,
    timeout_sec: int,
    owner_only: bool,
    platform: str = PLATFORM_GOOFISH,
) -> MessageChain:
    if platform == PLATFORM_GOOFISH:
        lines = [
            "检测到需要重新登录闲鱼。",
            "请直接在当前对话里扫码登录。",
            f"二维码有效期约 {timeout_sec} 秒，超时后请重新发送 /闲鱼 登录。",
            "扫码登录后回复任意消息即可继续任务。",
            "如需取消请发送 /闲鱼 登录取消",
        ]
        if owner_only:
            lines.append("如需刷新截图，可再次发送 /闲鱼 登录")
    else:
        display_name = platform_display_name(platform)
        lines = [
            f"检测到需要重新登录{display_name}。",
            "请直接在当前对话里扫码登录。",
            f"二维码有效期约 {timeout_sec} 秒，超时后请重新{_restart_action_hint(platform)}。",
            "扫码登录后回复任意消息即可继续任务。",
            "如需取消请发送 /闲鱼 登录取消",
        ]
        if owner_only:
            lines.append(f"如需刷新截图，可再次发送 /闲鱼 登录 {display_name}")
    if page_url:
        lines.append(f"当前页面：{page_url}")

    chain = MessageChain().message("\n".join(lines))
    if screenshot_base64:
        chain.base64_image(screenshot_base64)
    else:
        chain.message("\n未获取到截图，请稍后重试。")
    return chain


def _build_complete_message(
    flow_platform: str,
    *,
    result: dict[str, Any],
    resumed_count: int,
    enqueued_count: int,
) -> str:
    """单平台登录确认成功的回执文案（goofish 保持 master 原格式逐字节不变）。"""
    saved_path = str(result.get("saved_path", "")).strip() or "-"
    mirrored_paths = [
        str(path).strip()
        for path in (result.get("mirrored_paths") or [])
        if str(path).strip()
    ]
    name_prefix = (
        ""
        if flow_platform == PLATFORM_GOOFISH
        else platform_display_name(flow_platform)
    )
    lines = [
        f"{name_prefix}登录态已保存。",
        f"保存位置：{saved_path}",
    ]
    if mirrored_paths:
        lines.append(f"同步位置：{', '.join(mirrored_paths)}")
    lines.extend(
        [
            f"已恢复订阅：{resumed_count}",
            f"已重新入队：{enqueued_count}",
        ]
    )
    return "\n".join(lines)


def _normalize_platform(platform: str | None) -> str:
    return str(platform or "").strip() or PLATFORM_GOOFISH


def _restart_action_hint(platform: str) -> str:
    """超时/失效后重新发起登录的动作提示（/闲鱼 登录 [平台] 对全平台可用）。"""
    if platform == PLATFORM_GOOFISH:
        return "发送 /闲鱼 登录"
    return f"发送 /闲鱼 登录 {platform_display_name(platform)}"


def _qr_sent_text(platform: str) -> str:
    if platform == PLATFORM_GOOFISH:
        return "已向当前会话发送登录二维码，扫码登录后回复任意消息即可继续。"
    return (
        f"已向当前会话发送{platform_display_name(platform)}登录二维码，"
        "扫码登录后回复任意消息即可继续。"
    )


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_flow_expires_at(
    payload: dict[str, Any],
    *,
    started_at: int,
    default_timeout_sec: float,
) -> float:
    expires_at = _safe_float(payload.get("expires_at"))
    if expires_at is not None:
        return expires_at

    timeout_sec = _safe_float(payload.get("timeout_sec")) or default_timeout_sec
    return started_at + max(1.0, timeout_sec)


_LOGIN_RESTART_MARKERS_LOWER = {marker.lower() for marker in LOGIN_RESTART_MARKERS}
_CANCEL_MARKERS_LOWER = {marker.lower() for marker in CANCEL_MARKERS}
# 小写标记 → 目标平台，restart-by-message 按此路由（无后缀 = goofish）。
_LOGIN_RESTART_PLATFORMS_LOWER = {
    (base + suffix).lower(): platform
    for base in _LOGIN_RESTART_BASES
    for suffix, platform in _RESTART_PLATFORM_SUFFIXES.items()
}
