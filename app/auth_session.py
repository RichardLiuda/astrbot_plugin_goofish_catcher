from __future__ import annotations

import asyncio
import logging
import shutil
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
    profile_dir: Path | None = None
    cleanup_profile_dir: bool = True


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
        on_before_start: Any | None = None,
        on_after_confirm: Any | None = None,
    ) -> None:
        self.settings = settings
        self.auth_timeout_sec = max(1.0, float(auth_timeout_sec))
        self.on_before_start = on_before_start
        self.on_after_confirm = on_after_confirm
        self._lock = asyncio.Lock()
        self._active_session: LocalAuthSession | None = None

    async def start_auth_session(self, *, force_restart: bool = False) -> dict[str, Any]:
        async with self._lock:
            await self._expire_active_session_if_needed(raise_on_timeout=False)
            if self._active_session is not None and not force_restart:
                return await self._serialize_active_session(self._active_session)

            if self._active_session is not None:
                await self._active_session.session.close()
                await _cleanup_profile_dir(
                    self._active_session.profile_dir,
                    enabled=self._active_session.cleanup_profile_dir,
                )
                self._active_session = None

            if callable(self.on_before_start):
                await self.on_before_start()

            profile_dir, cleanup_profile_dir = self._build_session_profile_dir()
            session = GoofishLoginSession(
                executable_path=self.settings.playwright_executable_path,
                user_data_dir=profile_dir,
                force_direct=self.settings.playwright_force_direct,
            )
            try:
                await session.start_login_session()
                active_session = LocalAuthSession(
                    session_id=uuid4().hex,
                    started_at=int(time.time()),
                    expires_at_monotonic=time.monotonic() + self.auth_timeout_sec,
                    session=session,
                    profile_dir=profile_dir,
                    cleanup_profile_dir=cleanup_profile_dir,
                )
                self._active_session = active_session
                return await self._serialize_active_session(active_session)
            except Exception as exc:
                await session.close()
                await _cleanup_profile_dir(profile_dir, enabled=cleanup_profile_dir)
                raise _to_provider_error(exc, action="start local login session") from exc

    async def confirm_auth_session(self, *, session_id: str) -> dict[str, Any]:
        async with self._lock:
            active_session = await self._require_active_session(session_id)
            validation = await active_session.session.validate_login()
            if not validation.get("ok"):
                code_text = str(validation.get("code", "AUTH_REQUIRED")).strip()
                reason = str(validation.get("reason", "")).strip() or "登录态尚未生效"
                if code_text == ProviderErrorCode.CAPTCHA.value:
                    raise ProviderError(
                        ProviderErrorCode.CAPTCHA,
                        f"扫码后仍触发验证码/风控：{reason}",
                    )
                raise ProviderError(
                    ProviderErrorCode.AUTH_REQUIRED,
                    f"扫码后登录态仍未生效：{reason}",
                )
            try:
                result = await save_login_session_state(
                    active_session.session,
                    stable_path=self.settings.plugin_data_dir / "storage_state.json",
                )
            except Exception as exc:
                raise _to_provider_error(exc, action="save local login state") from exc

            saved_at = int(time.time())
            profile_dir = active_session.profile_dir
            session_transferred = False
            mirrored_paths: list[str] = []
            if callable(self.on_after_confirm):
                transfer_result = await self.on_after_confirm(active_session.session)
                session_transferred = bool(transfer_result)
            if not session_transferred:
                await active_session.session.close()
                if (
                    active_session.cleanup_profile_dir
                    and profile_dir is not None
                    and self.settings.playwright_user_data_dir is not None
                ):
                    try:
                        mirrored_dir = _mirror_profile_dir(
                            profile_dir,
                            self.settings.playwright_user_data_dir,
                        )
                        mirrored_paths.append(str(mirrored_dir))
                    finally:
                        await _cleanup_profile_dir(profile_dir)
                else:
                    await _cleanup_profile_dir(
                        profile_dir,
                        enabled=active_session.cleanup_profile_dir,
                    )
                stable_validation = await self._validate_saved_login_state()
                if not stable_validation.get("ok"):
                    await self._clear_saved_login_state()
                    code_text = str(
                        stable_validation.get("code", "AUTH_REQUIRED")
                    ).strip()
                    reason = (
                        str(stable_validation.get("reason", "")).strip()
                        or "登录态保存后复检失败"
                    )
                    if code_text == ProviderErrorCode.CAPTCHA.value:
                        raise ProviderError(
                            ProviderErrorCode.CAPTCHA,
                            f"登录态保存后仍触发验证码/风控：{reason}",
                        )
                    raise ProviderError(
                        ProviderErrorCode.AUTH_REQUIRED,
                        f"登录态保存后复检失败：{reason}",
                    )
            self._active_session = None
            return {
                "ok": True,
                "session_id": session_id,
                "status": "saved",
                "saved_path": str(result["saved_path"]),
                "mirrored_paths": mirrored_paths,
                "saved_at": saved_at,
            }

    async def cancel_auth_session(self, *, session_id: str) -> dict[str, Any]:
        async with self._lock:
            active_session = await self._require_active_session(session_id)
            await active_session.session.close()
            await _cleanup_profile_dir(
                active_session.profile_dir,
                enabled=active_session.cleanup_profile_dir,
            )
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
                await _cleanup_profile_dir(
                    self._active_session.profile_dir,
                    enabled=self._active_session.cleanup_profile_dir,
                )
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
        await _cleanup_profile_dir(
            expired_session.profile_dir,
            enabled=expired_session.cleanup_profile_dir,
        )
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

    def _build_session_profile_dir(self) -> tuple[Path, bool]:
        if self.settings.playwright_user_data_dir is not None:
            return self.settings.playwright_user_data_dir, False
        return (
            self.settings.plugin_data_dir
            / "login_profiles"
            / uuid4().hex,
            True,
        )

    async def _validate_saved_login_state(self) -> dict[str, Any]:
        stable_profile_dir = self.settings.playwright_user_data_dir
        if stable_profile_dir is None:
            return {
                "ok": True,
                "code": "OK",
                "reason": "persistent profile validation skipped",
            }
        session = GoofishLoginSession(
            executable_path=self.settings.playwright_executable_path,
            user_data_dir=stable_profile_dir,
            force_direct=self.settings.playwright_force_direct,
        )
        try:
            await session.start_login_session()
            result = await session.validate_login()
            logger.info(
                "[goofish_catcher] post-save login validation: ok=%s code=%s reason=%s page_url=%s frame_urls=%s payloads=%s",
                result.get("ok"),
                result.get("code"),
                result.get("reason"),
                result.get("page_url"),
                result.get("frame_urls"),
                result.get("payload_rets"),
            )
            return result
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] post-save login validation crashed: %s",
                exc,
            )
            raise _to_provider_error(exc, action="validate saved local login state") from exc
        finally:
            await session.close()

    async def _clear_saved_login_state(self) -> None:
        storage_state = self.settings.plugin_data_dir / "storage_state.json"
        try:
            storage_state.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to remove invalid storage_state %s: %s",
                storage_state,
                exc,
            )
        stable_profile_dir = self.settings.playwright_user_data_dir
        if stable_profile_dir is not None:
            await _cleanup_profile_dir(stable_profile_dir)


def _mirror_profile_dir(source_dir: Path, target_dir: Path) -> Path:
    source = Path(source_dir).expanduser()
    target = Path(target_dir).expanduser()
    if not source.exists():
        raise RuntimeError(f"login profile directory does not exist: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return target


async def _cleanup_profile_dir(
    profile_dir: Path | None,
    *,
    enabled: bool = True,
) -> None:
    if profile_dir is None or not enabled:
        return
    try:
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
    except Exception as exc:
        logger.warning(
            "[goofish_catcher] failed to cleanup temporary login profile %s: %s",
            profile_dir,
            exc,
        )


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
