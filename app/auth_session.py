from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import PluginSettings
from .login_session import (
    PLUGIN_NAME,
    GoofishLoginSession,
    get_astrbot_root,
)
from .types import ProviderError, ProviderErrorCode

try:
    from astrbot.api import logger
    from astrbot.api.star import StarTools
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")
    StarTools = None

AUTH_SESSION_TIMEOUT_SEC = 60


@dataclass(slots=True)
class LocalAuthSession:
    session_id: str
    started_at: int
    expires_at_monotonic: float
    session: GoofishLoginSession


def resolve_local_storage_state_path() -> Path:
    plugin_data_dir: Path
    if StarTools is not None:
        try:
            plugin_data_dir = Path(StarTools.get_data_dir(PLUGIN_NAME))
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to resolve plugin data dir via StarTools: %s",
                exc,
            )
            plugin_data_dir = (
                get_astrbot_root()
                / "data"
                / "plugin_data"
                / PLUGIN_NAME
            )
    else:
        plugin_data_dir = (
            get_astrbot_root()
            / "data"
            / "plugin_data"
            / PLUGIN_NAME
        )
    plugin_data_dir.mkdir(parents=True, exist_ok=True)
    return plugin_data_dir / "storage_state.json"


async def save_login_session_state(
    session: GoofishLoginSession,
    *,
    stable_path: Path | str,
) -> dict[str, Any]:
    stable_target = Path(stable_path).expanduser()
    saved_path = await session.save_storage_state(stable_target)
    return {
        "saved_path": saved_path,
        "mirrored_paths": [],
    }


class LocalAuthSessionController:
    def __init__(
        self,
        settings: PluginSettings,
        *,
        auth_timeout_sec: float = AUTH_SESSION_TIMEOUT_SEC,
    ) -> None:
        self.settings = settings
        self.auth_timeout_sec = max(1.0, float(auth_timeout_sec))
        self._lock = asyncio.Lock()
        self._active_session: LocalAuthSession | None = None

    async def start_auth_session(self, *, force_restart: bool = False) -> dict[str, Any]:
        async with self._lock:
            await self._expire_active_session_if_needed(raise_on_timeout=False)
            if self._active_session is not None and not force_restart:
                return await self._serialize_active_session(self._active_session)

            if self._active_session is not None:
                await self._active_session.session.close()
                self._active_session = None

            session = GoofishLoginSession(
                executable_path=self.settings.playwright_executable_path,
                force_direct=self.settings.playwright_force_direct,
            )
            try:
                await session.start_login_session()
                active_session = LocalAuthSession(
                    session_id=uuid4().hex,
                    started_at=int(time.time()),
                    expires_at_monotonic=time.monotonic() + self.auth_timeout_sec,
                    session=session,
                )
                self._active_session = active_session
                return await self._serialize_active_session(active_session)
            except Exception as exc:
                await session.close()
                raise _to_provider_error(exc, action="start local login session") from exc

    async def confirm_auth_session(self, *, session_id: str) -> dict[str, Any]:
        async with self._lock:
            active_session = await self._require_active_session(session_id)
            try:
                result = await save_login_session_state(
                    active_session.session,
                    stable_path=self.settings.plugin_data_dir / "storage_state.json",
                )
            except Exception as exc:
                raise _to_provider_error(exc, action="save local login state") from exc

            saved_at = int(time.time())
            await active_session.session.close()
            self._active_session = None
            return {
                "ok": True,
                "session_id": session_id,
                "status": "saved",
                "saved_path": str(result["saved_path"]),
                "mirrored_paths": [str(path) for path in result["mirrored_paths"]],
                "saved_at": saved_at,
            }

    async def cancel_auth_session(self, *, session_id: str) -> dict[str, Any]:
        async with self._lock:
            active_session = await self._require_active_session(session_id)
            await active_session.session.close()
            self._active_session = None
            return {
                "ok": True,
                "session_id": session_id,
                "status": "cancelled",
                "cancelled_at": int(time.time()),
            }

    async def close(self) -> None:
        async with self._lock:
            if self._active_session is not None:
                await self._active_session.session.close()
                self._active_session = None

    async def _require_active_session(self, session_id: str) -> LocalAuthSession:
        await self._expire_active_session_if_needed()
        if self._active_session is None:
            raise RuntimeError("no active login session")
        if self._active_session.session_id != session_id:
            raise RuntimeError("login session id does not match active session")
        return self._active_session

    async def _expire_active_session_if_needed(
        self,
        *,
        raise_on_timeout: bool = True,
    ) -> None:
        if self._active_session is None:
            return
        if time.monotonic() < self._active_session.expires_at_monotonic:
            return

        expired_session = self._active_session
        self._active_session = None
        await expired_session.session.close()
        if raise_on_timeout:
            raise RuntimeError(
                f"login session timed out after {int(self.auth_timeout_sec)} seconds"
            )

    async def _serialize_active_session(
        self,
        active_session: LocalAuthSession,
    ) -> dict[str, Any]:
        try:
            snapshot = await active_session.session.capture_snapshot()
        except Exception as exc:
            raise _to_provider_error(exc, action="capture local login snapshot") from exc
        return {
            "ok": True,
            "session_id": active_session.session_id,
            "status": "active",
            "started_at": active_session.started_at,
            "expires_at": active_session.started_at + int(self.auth_timeout_sec),
            "timeout_sec": int(self.auth_timeout_sec),
            "page_url": snapshot.page_url,
            "screenshot_base64": snapshot.screenshot_base64,
        }


def _to_provider_error(exc: Exception, *, action: str) -> ProviderError:
    if isinstance(exc, ProviderError):
        return exc

    message = str(exc).strip() or exc.__class__.__name__
    lowered = message.lower()
    if "playwright is not installed" in lowered or "executable" in lowered:
        return ProviderError(
            ProviderErrorCode.DEPENDENCY_MISSING,
            f"failed to {action}: {message}",
        )
    return ProviderError(
        ProviderErrorCode.UNKNOWN,
        f"failed to {action}: {message}",
    )
