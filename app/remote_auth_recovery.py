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
LOGIN_RESTART_MARKERS = (
    "闲鱼 登录",
    "/闲鱼 登录",
    "goofish login",
    "/goofish login",
    "goofish auth",
    "/goofish auth",
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
        self.auth_controller = auth_controller or provider
        self.auth_timeout_sec = max(1.0, float(auth_timeout_sec))
        self._lock = asyncio.Lock()
        self._active_flow: ActiveRemoteAuthFlow | None = None
        self._timeout_task: asyncio.Task | None = None
        self._idle_event = asyncio.Event()
        self._idle_event.set()

    async def handle_provider_auth_failure(
        self,
        *,
        umo: str,
        sub_id: int | None = None,
    ) -> str | None:
        if not self._supports_auth_recovery():
            return None

        notify_umo: str | None = None
        notify_chain: MessageChain | None = None
        async with self._lock:
            if self._active_flow is not None:
                if sub_id is not None:
                    self._active_flow.affected_subscription_ids.add(sub_id)
                return None

            payload = await self.auth_controller.start_auth_session(force_restart=False)
            if payload.get("auto_login_done"):
                return AUTO_LOGIN_DONE_SENTINEL
            started_at = _safe_int(payload.get("started_at")) or int(time.time())
            self._set_active_flow(
                ActiveRemoteAuthFlow(
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
                )
            )
            notify_umo = umo
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=self._active_flow.page_url,
                timeout_sec=int(self._timeout_seconds_for_flow(self._active_flow)),
                owner_only=False,
            )

        if notify_umo and notify_chain is not None:
            await self._send_chain(notify_umo, notify_chain)
            return "已向当前会话发送登录二维码，扫码登录后回复任意消息即可继续。"
        return None

    async def start_login(self, *, umo: str) -> str:
        if not self._supports_auth_recovery():
            return "当前 Provider 未启用登录恢复流程。"

        notify_chain: MessageChain | None = None
        async with self._lock:
            if self._active_flow is not None and self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能接管。"
            force_restart = self._active_flow is not None

            payload = await self.auth_controller.start_auth_session(
                force_restart=force_restart
            )
            if payload.get("auto_login_done"):
                await self._clear_active_flow_locked()
                return AUTO_LOGIN_DONE_SENTINEL
            existing_ids = (
                set(self._active_flow.affected_subscription_ids)
                if self._active_flow is not None
                else set()
            )
            started_at = _safe_int(payload.get("started_at")) or int(time.time())
            self._set_active_flow(
                ActiveRemoteAuthFlow(
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
                )
            )
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=self._active_flow.page_url,
                timeout_sec=int(self._timeout_seconds_for_flow(self._active_flow)),
                owner_only=True,
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
        if not self._supports_auth_recovery():
            return "当前 Provider 未启用登录恢复流程。"

        async with self._lock:
            if self._active_flow is None:
                return "当前没有进行中的登录恢复流程，请先发送 /闲鱼 登录。"
            if self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能确认。"
            if self._is_flow_expired(self._active_flow):
                await self._clear_active_flow_locked()
                return (
                    f"登录二维码已超时（>{int(self.auth_timeout_sec)}s），"
                    "请重新发送 /闲鱼 登录。"
                )
            session_id = self._active_flow.session_id
            self._cancel_timeout_task_locked()

        result = await self.auth_controller.confirm_auth_session(session_id=session_id)

        async with self._lock:
            await self._clear_active_flow_locked()

        now_ts = int(time.time())
        resumed = await storage.resume_subscriptions_by_pause_reasons(
            AUTH_PAUSE_REASONS,
            now_ts=now_ts,
        )
        enqueued = 0
        for sub in resumed:
            if scheduler is None:
                continue
            if await scheduler.enqueue_manual_check(sub.id):
                enqueued += 1

        saved_path = str(result.get("saved_path", "")).strip() or "-"
        mirrored_paths = [
            str(path).strip()
            for path in (result.get("mirrored_paths") or [])
            if str(path).strip()
        ]
        lines = [
            "登录态已保存。",
            f"保存位置：{saved_path}",
        ]
        if mirrored_paths:
            lines.append(f"同步位置：{', '.join(mirrored_paths)}")
        lines.extend(
            [
                f"已恢复订阅：{len(resumed)}",
                f"已重新入队：{enqueued}",
            ]
        )
        return "\n".join(lines)

    async def cancel_login(self, *, umo: str) -> str:
        if not self._supports_auth_recovery():
            return "当前 Provider 未启用登录恢复流程。"

        async with self._lock:
            if self._active_flow is None:
                return "当前没有进行中的登录恢复流程。"
            if self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能取消。"
            session_id = self._active_flow.session_id
            self._cancel_timeout_task_locked()

        await self.auth_controller.cancel_auth_session(session_id=session_id)

        async with self._lock:
            await self._clear_active_flow_locked()
        return "已取消当前登录恢复流程。"

    def has_active_flow(self) -> bool:
        return self._active_flow is not None

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

        async with self._lock:
            if self._active_flow is None:
                return False
            if self._is_flow_expired(self._active_flow):
                return False
            if self._active_flow.owner_umo != umo:
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
            if self._active_flow is None:
                return False
            if self._is_flow_expired(self._active_flow):
                return False
            if self._active_flow.owner_umo != umo:
                return False

        return self._is_restart_message(normalized.lower())

    async def close(self) -> None:
        async with self._lock:
            self._cancel_timeout_task_locked()
            await self._clear_active_flow_locked()
        if callable(getattr(self.auth_controller, "close", None)):
            await self.auth_controller.close()

    def _supports_auth_recovery(self) -> bool:
        return bool(
            self.auth_controller is not None
            and callable(getattr(self.auth_controller, "start_auth_session", None))
            and callable(getattr(self.auth_controller, "confirm_auth_session", None))
            and callable(getattr(self.auth_controller, "cancel_auth_session", None))
        )

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
        self._active_flow = flow
        self._idle_event.clear()
        self._cancel_timeout_task_locked()
        self._timeout_task = asyncio.create_task(
            self._expire_flow_after_timeout(flow.session_id)
        )

    async def _clear_active_flow_locked(self) -> None:
        self._active_flow = None
        self._idle_event.set()
        self._cancel_timeout_task_locked()

    def _cancel_timeout_task_locked(self) -> None:
        if self._timeout_task is None:
            return
        if self._timeout_task is asyncio.current_task():
            self._timeout_task = None
            return
        self._timeout_task.cancel()
        self._timeout_task = None

    async def _expire_flow_after_timeout(self, session_id: str) -> None:
        notify_umo: str | None = None
        try:
            async with self._lock:
                active_flow = self._active_flow
                if active_flow is None or active_flow.session_id != session_id:
                    return
                sleep_sec = max(0.0, active_flow.expires_at - time.time())
            await asyncio.sleep(sleep_sec)

            async with self._lock:
                active_flow = self._active_flow
                if active_flow is None or active_flow.session_id != session_id:
                    return
                notify_umo = active_flow.owner_umo
                await self._clear_active_flow_locked()

            try:
                await self.auth_controller.cancel_auth_session(session_id=session_id)
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
                        "如需继续请重新发送 /闲鱼 登录。"
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
) -> MessageChain:
    lines = [
        "检测到需要重新登录闲鱼。",
        "请直接在当前对话里扫码登录。",
        f"二维码有效期约 {timeout_sec} 秒，超时后请重新发送 /闲鱼 登录。",
        "扫码登录后回复任意消息即可继续任务。",
        "如需取消请发送 /闲鱼 登录取消",
    ]
    if owner_only:
        lines.append("如需刷新截图，可再次发送 /闲鱼 登录")
    if page_url:
        lines.append(f"当前页面：{page_url}")

    chain = MessageChain().message("\n".join(lines))
    if screenshot_base64:
        chain.base64_image(screenshot_base64)
    else:
        chain.message("\n未获取到截图，请稍后重试。")
    return chain


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
