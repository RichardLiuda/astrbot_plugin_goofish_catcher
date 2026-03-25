from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from astrbot.api.event import MessageChain
from astrbot.api.star import Context

from .config import PROVIDER_MODE_REMOTE_REST, PluginSettings

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

AUTH_PAUSE_REASONS = ("AUTH_REQUIRED", "CAPTCHA")


@dataclass(slots=True)
class ActiveRemoteAuthFlow:
    session_id: str
    owner_umo: str
    started_at: int
    page_url: str
    affected_subscription_ids: set[int] = field(default_factory=set)


class RemoteAuthRecoveryCoordinator:
    def __init__(
        self,
        *,
        context: Context,
        settings: PluginSettings,
        provider: Any | None,
    ) -> None:
        self.context = context
        self.settings = settings
        self.provider = provider
        self._lock = asyncio.Lock()
        self._active_flow: ActiveRemoteAuthFlow | None = None

    async def handle_provider_auth_failure(
        self,
        *,
        umo: str,
        sub_id: int | None = None,
    ) -> str | None:
        if not self._supports_remote_auth():
            return None

        notify_umo: str | None = None
        notify_chain: MessageChain | None = None
        async with self._lock:
            if self._active_flow is not None:
                if sub_id is not None:
                    self._active_flow.affected_subscription_ids.add(sub_id)
                return None

            payload = await self.provider.start_auth_session(force_restart=False)
            self._active_flow = ActiveRemoteAuthFlow(
                session_id=str(payload.get("session_id", "")).strip(),
                owner_umo=umo,
                started_at=_safe_int(payload.get("started_at")) or int(time.time()),
                page_url=str(payload.get("page_url", "")).strip(),
                affected_subscription_ids=({sub_id} if sub_id is not None else set()),
            )
            notify_umo = umo
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=self._active_flow.page_url,
                owner_only=False,
            )

        if notify_umo and notify_chain is not None:
            await self._send_chain(notify_umo, notify_chain)
            return "已向当前会话发送远端登录二维码，请扫码后发送 /闲鱼 登录完成。"
        return None

    async def start_login(self, *, umo: str) -> str:
        if not self._supports_remote_auth():
            return "当前 Provider 不是 remote_rest，远端登录流程不可用。"

        notify_chain: MessageChain | None = None
        async with self._lock:
            if self._active_flow is not None and self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能接管。"

            payload = await self.provider.start_auth_session(force_restart=False)
            existing_ids = (
                set(self._active_flow.affected_subscription_ids)
                if self._active_flow is not None
                else set()
            )
            self._active_flow = ActiveRemoteAuthFlow(
                session_id=str(payload.get("session_id", "")).strip(),
                owner_umo=umo,
                started_at=_safe_int(payload.get("started_at")) or int(time.time()),
                page_url=str(payload.get("page_url", "")).strip(),
                affected_subscription_ids=existing_ids,
            )
            notify_chain = _build_login_chain(
                screenshot_base64=str(payload.get("screenshot_base64", "")).strip(),
                page_url=self._active_flow.page_url,
                owner_only=True,
            )

        if notify_chain is not None:
            await self._send_chain(umo, notify_chain)
        return "已将远端登录二维码发送到当前会话，请扫码后发送 /闲鱼 登录完成。"

    async def complete_login(
        self,
        *,
        umo: str,
        storage,
        scheduler,
    ) -> str:
        if not self._supports_remote_auth():
            return "当前 Provider 不是 remote_rest，远端登录流程不可用。"

        async with self._lock:
            if self._active_flow is None:
                return "当前没有进行中的远端登录恢复流程，请先发送 /闲鱼 登录。"
            if self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能确认。"
            session_id = self._active_flow.session_id

        result = await self.provider.confirm_auth_session(session_id=session_id)

        async with self._lock:
            self._active_flow = None

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
        return (
            "远端登录态已保存。\n"
            f"保存位置：{saved_path}\n"
            f"已恢复订阅：{len(resumed)}\n"
            f"已重新入队：{enqueued}"
        )

    async def cancel_login(self, *, umo: str) -> str:
        if not self._supports_remote_auth():
            return "当前 Provider 不是 remote_rest，远端登录流程不可用。"

        async with self._lock:
            if self._active_flow is None:
                return "当前没有进行中的远端登录恢复流程。"
            if self._active_flow.owner_umo != umo:
                return "登录恢复已在其他会话进行中，当前会话不能取消。"
            session_id = self._active_flow.session_id

        await self.provider.cancel_auth_session(session_id=session_id)

        async with self._lock:
            self._active_flow = None
        return "已取消当前远端登录恢复流程。"

    def _supports_remote_auth(self) -> bool:
        return bool(
            self.settings.provider_mode == PROVIDER_MODE_REMOTE_REST
            and self.provider is not None
            and callable(getattr(self.provider, "start_auth_session", None))
            and callable(getattr(self.provider, "confirm_auth_session", None))
            and callable(getattr(self.provider, "cancel_auth_session", None))
        )

    async def _send_chain(self, umo: str, chain: MessageChain) -> None:
        try:
            await self.context.send_message(umo, chain)
        except Exception as exc:
            logger.error(
                "[goofish_catcher] failed to send remote auth recovery message: %s",
                exc,
                exc_info=True,
            )


def _build_login_chain(
    *,
    screenshot_base64: str,
    page_url: str,
    owner_only: bool,
) -> MessageChain:
    lines = [
        "检测到远端 worker 需要重新登录闲鱼。",
        "请直接在当前对话里扫码登录。",
        "登录完成后发送 /闲鱼 登录完成",
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
