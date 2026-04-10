from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:
    from .app.auth_session import AUTH_SESSION_TIMEOUT_SEC
    from .app.config import PROVIDER_MODE_PLAYWRIGHT_LOCAL, PluginSettings
    from .app.login_session import GoofishLoginSession
    from .app.provider_playwright import PlaywrightSearchProvider
    from .app.types import FavoriteItemResult, ProviderError, ProviderErrorCode
except ImportError:
    from app.auth_session import AUTH_SESSION_TIMEOUT_SEC
    from app.config import PROVIDER_MODE_PLAYWRIGHT_LOCAL, PluginSettings
    from app.login_session import GoofishLoginSession
    from app.provider_playwright import PlaywrightSearchProvider
    from app.types import FavoriteItemResult, ProviderError, ProviderErrorCode


class SearchRequest(BaseModel):
    keyword: str
    pages: int = Field(default=1, ge=1)
    timeout_ms: int = Field(default=20_000, ge=1_000)
    sort: str = "time_desc"
    use_login: bool = True


class AuthStartRequest(BaseModel):
    force_restart: bool = False


class AuthSessionRequest(BaseModel):
    session_id: str = Field(min_length=1)


class FavoriteRequest(BaseModel):
    url: str = Field(min_length=1)
    item_id: str | None = None
    timeout_ms: int = Field(default=20_000, ge=1_000)


@dataclass(slots=True)
class WorkerAuthConfig:
    api_key: str | None
    cf_access_client_id: str | None
    cf_access_client_secret: str | None
    error: str | None = None

    @property
    def status(self) -> str:
        if self.error:
            return "misconfigured"
        if self.api_key or (
            self.cf_access_client_id and self.cf_access_client_secret
        ):
            return "configured"
        return "disabled"


@dataclass(slots=True)
class WorkerLoginSession:
    session_id: str
    started_at: int
    expires_at_monotonic: float
    session: GoofishLoginSession


class WorkerLoginSessionManager:
    def __init__(
        self,
        settings: PluginSettings | None,
        *,
        auth_timeout_sec: float = AUTH_SESSION_TIMEOUT_SEC,
    ) -> None:
        self.settings = settings
        self.auth_timeout_sec = max(1.0, float(auth_timeout_sec))
        self._lock = asyncio.Lock()
        self._active_session: WorkerLoginSession | None = None

    async def start_session(self, *, force_restart: bool) -> dict[str, Any]:
        async with self._lock:
            if self.settings is None:
                raise RuntimeError("worker settings are not ready")
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
                active_session = WorkerLoginSession(
                    session_id=uuid4().hex,
                    started_at=int(time.time()),
                    expires_at_monotonic=time.monotonic() + self.auth_timeout_sec,
                    session=session,
                )
                self._active_session = active_session
                return await self._serialize_active_session(active_session)
            except Exception:
                await session.close()
                raise

    async def confirm_session(self, session_id: str) -> dict[str, Any]:
        async with self._lock:
            active_session = await self._require_active_session(session_id)
            if self.settings is None or self.settings.playwright_storage_state_path is None:
                raise RuntimeError("worker storage_state path is not configured")

            saved_path = await active_session.session.save_storage_state(
                self.settings.playwright_storage_state_path
            )
            saved_at = int(time.time())
            await active_session.session.close()
            self._active_session = None
            return {
                "ok": True,
                "session_id": session_id,
                "status": "saved",
                "saved_path": str(saved_path),
                "saved_at": saved_at,
            }

    async def cancel_session(self, session_id: str) -> dict[str, Any]:
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

    async def _require_active_session(self, session_id: str) -> WorkerLoginSession:
        await self._expire_active_session_if_needed()
        if self._active_session is None:
            raise ValueError("no active login session")
        if self._active_session.session_id != session_id:
            raise ValueError("login session id does not match active session")
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
            raise ValueError(
                f"login session timed out after {int(self.auth_timeout_sec)} seconds"
            )

    async def _serialize_active_session(
        self,
        active_session: WorkerLoginSession,
    ) -> dict[str, Any]:
        snapshot = await active_session.session.capture_snapshot()
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


@dataclass(slots=True)
class WorkerRuntime:
    settings: PluginSettings | None
    provider: Any | None
    auth: WorkerAuthConfig
    login_manager: WorkerLoginSessionManager | None = None
    provider_error: str | None = None
    provider_error_code: ProviderErrorCode = ProviderErrorCode.UNKNOWN


def build_worker_settings_from_env() -> PluginSettings:
    config = load_worker_config()
    plugin_data_dir = Path(
        _cfg_str(config, "data_dir", "GOOFISH_WORKER_DATA_DIR", ".goofish_worker")
    ).expanduser()
    plugin_data_dir.mkdir(parents=True, exist_ok=True)

    storage_state_file = _cfg_str(
        config,
        "storage_state_file",
        "GOOFISH_WORKER_STORAGE_STATE_FILE",
        "",
    )
    if storage_state_file:
        storage_state_path = Path(storage_state_file).expanduser()
        if not storage_state_path.is_absolute():
            storage_state_path = plugin_data_dir / storage_state_path
    else:
        storage_state_path = plugin_data_dir / "storage_state.json"
    executable_path = _cfg_optional_str(
        config,
        "executable_path",
        "GOOFISH_WORKER_EXECUTABLE_PATH",
    )

    return PluginSettings(
        plugin_name="goofish_worker",
        plugin_data_dir=plugin_data_dir,
        db_path=plugin_data_dir / "goofish_catcher.db",
        provider_mode=PROVIDER_MODE_PLAYWRIGHT_LOCAL,
        default_interval_sec=600,
        default_pages=1,
        max_pages=max(1, _cfg_int(config, "max_pages", "GOOFISH_WORKER_MAX_PAGES", 2)),
        scheduler_tick_sec=15,
        max_concurrency=1,
        fetch_timeout_sec=max(
            5,
            _cfg_int(
                config,
                "fetch_timeout_sec",
                "GOOFISH_WORKER_FETCH_TIMEOUT_SEC",
                20,
            ),
        ),
        max_retries=0,
        retry_base_sec=30,
        retry_max_sec=900,
        default_new_window_sec=1800,
        default_drop_abs=50.0,
        default_drop_pct=0.05,
        default_cooldown_sec=21600,
        playwright_storage_state_path=storage_state_path,
        playwright_executable_path=(
            Path(executable_path).expanduser() if executable_path else None
        ),
        playwright_headless=False,
        playwright_block_assets=_cfg_bool(
            config,
            "block_assets",
            "GOOFISH_WORKER_BLOCK_ASSETS",
            True,
        ),
        playwright_force_direct=_cfg_bool(
            config,
            "force_direct",
            "GOOFISH_WORKER_FORCE_DIRECT",
            True,
        ),
        webhook_url=None,
        remote_base_url=None,
        remote_api_key=None,
        remote_headers_json=None,
        remote_timeout_sec=20,
        remote_healthcheck_on_init=False,
        remote_healthcheck_timeout_sec=10,
        queue_max_size=256,
        llm_enabled=False,
        llm_provider_id=None,
        llm_prefilter_provider_id=None,
        llm_timeout_sec=25,
        llm_top_k=3,
        llm_min_score=0.0,
        llm_max_candidates=20,
        llm_prefilter_enabled=False,
        llm_prefilter_timeout_sec=6,
        llm_prefilter_max_items=30,
    )


def build_worker_auth_from_env() -> WorkerAuthConfig:
    config = load_worker_config()
    api_key = _cfg_optional_str(config, "api_key", "GOOFISH_WORKER_API_KEY")
    cf_access_client_id = _cfg_optional_str(
        config,
        "cf_access_client_id",
        "GOOFISH_WORKER_CF_ACCESS_CLIENT_ID",
    )
    cf_access_client_secret = _cfg_optional_str(
        config,
        "cf_access_client_secret",
        "GOOFISH_WORKER_CF_ACCESS_CLIENT_SECRET",
    )
    error = None
    if bool(cf_access_client_id) != bool(cf_access_client_secret):
        error = (
            "cloudflare access service token requires both client id and client secret"
        )
    return WorkerAuthConfig(
        api_key=api_key,
        cf_access_client_id=cf_access_client_id,
        cf_access_client_secret=cf_access_client_secret,
        error=error,
    )


def create_runtime_from_env() -> WorkerRuntime:
    auth = build_worker_auth_from_env()
    settings: PluginSettings | None = None
    try:
        settings = build_worker_settings_from_env()
        provider = PlaywrightSearchProvider(settings)
        return WorkerRuntime(
            settings=settings,
            provider=provider,
            auth=auth,
            login_manager=WorkerLoginSessionManager(settings),
        )
    except ModuleNotFoundError as exc:
        return WorkerRuntime(
            settings=settings,
            provider=None,
            auth=auth,
            login_manager=(
                WorkerLoginSessionManager(settings) if settings is not None else None
            ),
            provider_error=(
                "playwright is not installed. "
                "Run: uv pip install -r requirements.txt && "
                "uv run python -m playwright install chromium chromium-headless-shell"
            ),
            provider_error_code=ProviderErrorCode.DEPENDENCY_MISSING,
        )
    except Exception as exc:
        return WorkerRuntime(
            settings=settings,
            provider=None,
            auth=auth,
            login_manager=(
                WorkerLoginSessionManager(settings) if settings is not None else None
            ),
            provider_error=str(exc),
            provider_error_code=ProviderErrorCode.UNKNOWN,
        )


def load_worker_config() -> dict[str, Any]:
    config_path = Path(
        os.getenv("GOOFISH_WORKER_CONFIG", "worker_config.json")
    ).expanduser()
    if not config_path.exists():
        return {}
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid worker config json: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("worker config root must be a JSON object")
    return raw


def create_app(runtime: WorkerRuntime | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = runtime or create_runtime_from_env()
        try:
            yield
        finally:
            current_runtime: WorkerRuntime | None = getattr(app.state, "runtime", None)
            provider = getattr(current_runtime, "provider", None)
            if provider is not None and hasattr(provider, "close"):
                await provider.close()
            login_manager = getattr(current_runtime, "login_manager", None)
            if login_manager is not None and hasattr(login_manager, "close"):
                await login_manager.close()

    app = FastAPI(title="Goofish Remote Worker", lifespan=lifespan)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_, exc: HTTPException):
        return _error_response(
            status_code=exc.status_code,
            code=ProviderErrorCode.NETWORK_ERROR,
            message=str(exc.detail),
        )

    @app.get("/health")
    async def health(
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        if current_runtime.provider_error:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error,
            )

        storage_state = bool(
            current_runtime.settings
            and current_runtime.settings.playwright_storage_state_path
            and current_runtime.settings.playwright_storage_state_path.exists()
        )
        payload = {
            "ok": True,
            "provider": (
                current_runtime.settings.provider_mode
                if current_runtime.settings is not None
                else PROVIDER_MODE_PLAYWRIGHT_LOCAL
            ),
            "auth": current_runtime.auth.status,
            "storage_state": storage_state,
        }
        return payload

    @app.post("/v1/search")
    async def search(
        req: SearchRequest,
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        if current_runtime.provider_error or current_runtime.provider is None:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error or "worker provider is unavailable",
            )

        try:
            items = await current_runtime.provider.search(
                keyword=req.keyword,
                pages=req.pages,
                timeout_sec=max(5, req.timeout_ms // 1000),
            )
        except ProviderError as exc:
            return _error_response(
                status_code=400,
                code=exc.code,
                message=exc.message,
                retry_after_sec=exc.retry_after_sec,
            )
        except Exception as exc:
            return _error_response(
                status_code=500,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )

        return {
            "ok": True,
            "items": [asdict(item) for item in items],
        }

    @app.post("/v1/auth/start")
    async def start_auth_session(
        req: AuthStartRequest,
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        login_manager = current_runtime.login_manager
        if login_manager is None:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error or "worker login manager is unavailable",
            )

        try:
            return await login_manager.start_session(force_restart=req.force_restart)
        except ValueError as exc:
            return _error_response(
                status_code=409,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )
        except Exception as exc:
            return _error_response(
                status_code=500,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )

    @app.post("/v1/favorite")
    async def favorite(
        req: FavoriteRequest,
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        if current_runtime.provider_error or current_runtime.provider is None:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error or "worker provider is unavailable",
            )

        try:
            result: FavoriteItemResult = await current_runtime.provider.favorite_item(
                url=req.url,
                item_id=req.item_id,
                timeout_sec=max(5, req.timeout_ms // 1000),
            )
        except ProviderError as exc:
            return _error_response(
                status_code=400,
                code=exc.code,
                message=exc.message,
                retry_after_sec=exc.retry_after_sec,
            )
        except Exception as exc:
            return _error_response(
                status_code=500,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )

        return {
            "ok": True,
            "status": result.status,
            "url": result.url,
            "item_id": result.item_id,
            "title": result.title,
        }

    @app.post("/v1/auth/confirm")
    async def confirm_auth_session(
        req: AuthSessionRequest,
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        login_manager = current_runtime.login_manager
        if login_manager is None:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error or "worker login manager is unavailable",
            )

        try:
            return await login_manager.confirm_session(req.session_id)
        except ValueError as exc:
            return _error_response(
                status_code=409,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )
        except Exception as exc:
            return _error_response(
                status_code=500,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )

    @app.post("/v1/auth/cancel")
    async def cancel_auth_session(
        req: AuthSessionRequest,
        authorization: str | None = Header(None),
        x_api_key: str | None = Header(None),
        cf_access_client_id: str | None = Header(None, alias="CF-Access-Client-Id"),
        cf_access_client_secret: str | None = Header(
            None,
            alias="CF-Access-Client-Secret",
        ),
    ):
        current_runtime = _get_runtime(app)
        _verify_request_auth(
            current_runtime.auth,
            authorization=authorization,
            x_api_key=x_api_key,
            cf_access_client_id=cf_access_client_id,
            cf_access_client_secret=cf_access_client_secret,
        )
        login_manager = current_runtime.login_manager
        if login_manager is None:
            return _error_response(
                status_code=503,
                code=current_runtime.provider_error_code,
                message=current_runtime.provider_error or "worker login manager is unavailable",
            )

        try:
            return await login_manager.cancel_session(req.session_id)
        except ValueError as exc:
            return _error_response(
                status_code=409,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )
        except Exception as exc:
            return _error_response(
                status_code=500,
                code=ProviderErrorCode.UNKNOWN,
                message=str(exc),
            )

    return app


def _get_runtime(app: FastAPI) -> WorkerRuntime:
    runtime: WorkerRuntime | None = getattr(app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="worker runtime is not ready")
    return runtime


def _verify_request_auth(
    auth: WorkerAuthConfig,
    *,
    authorization: str | None,
    x_api_key: str | None,
    cf_access_client_id: str | None,
    cf_access_client_secret: str | None,
) -> None:
    if auth.error:
        raise HTTPException(status_code=503, detail=auth.error)
    if auth.status == "disabled":
        return

    bearer_token = _extract_bearer_token(authorization)
    if auth.api_key and (
        bearer_token == auth.api_key or x_api_key == auth.api_key
    ):
        return
    if (
        auth.cf_access_client_id
        and auth.cf_access_client_secret
        and cf_access_client_id == auth.cf_access_client_id
        and cf_access_client_secret == auth.cf_access_client_secret
    ):
        return

    raise HTTPException(status_code=401, detail="worker authorization failed")


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.strip().split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip() or None
    return authorization.strip() or None


def _cfg_optional_str(
    config: dict[str, Any],
    key: str,
    env_name: str,
) -> str | None:
    env_value = os.getenv(env_name)
    if env_value is not None:
        return env_value.strip() or None
    raw_value = config.get(key)
    if raw_value is None:
        return None
    return str(raw_value).strip() or None


def _cfg_str(
    config: dict[str, Any],
    key: str,
    env_name: str,
    default: str,
) -> str:
    return _cfg_optional_str(config, key, env_name) or default


def _cfg_bool(
    config: dict[str, Any],
    key: str,
    env_name: str,
    default: bool,
) -> bool:
    raw = os.getenv(env_name)
    if raw is not None:
        return _parse_bool(raw, default)
    if key in config:
        return _parse_bool(config.get(key), default)
    return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return _parse_bool(raw, default)


def _parse_bool(raw: Any, default: bool) -> bool:
    if isinstance(raw, bool):
        return raw
    if raw is None:
        return default
    lowered = str(raw).strip().lower()
    if lowered in {"true", "1", "yes", "on"}:
        return True
    if lowered in {"false", "0", "no", "off"}:
        return False
    return default


def _cfg_int(
    config: dict[str, Any],
    key: str,
    env_name: str,
    default: int,
) -> int:
    raw = os.getenv(env_name)
    if raw is not None:
        return _env_int(env_name, default)
    raw = config.get(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _error_response(
    *,
    status_code: int,
    code: ProviderErrorCode,
    message: str,
    retry_after_sec: int | None = None,
) -> JSONResponse:
    error = {
        "code": code.value,
        "message": message,
    }
    if retry_after_sec is not None:
        error["retry_after_sec"] = retry_after_sec
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": error,
        },
    )


app = create_app()
