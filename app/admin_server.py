from __future__ import annotations

import asyncio
import secrets
import time
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from astrbot.api import logger
except ModuleNotFoundError:  # pragma: no cover - used in plugin runtime only
    import logging

    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .admin_service import AdminService
from .types import ProviderError

ADMIN_SESSION_COOKIE = "goofish_admin_session"


class LoginRequest(BaseModel):
    api_key: str = Field(min_length=1)


class SubscriptionRequest(BaseModel):
    umo: str | None = None
    keyword: str | None = None
    interval_sec: int | None = Field(default=None, ge=1)
    pages: int | None = Field(default=None, ge=1)
    recommend_max_price: float | None = Field(default=None, ge=0)
    drop_abs: float | None = Field(default=None, ge=0)
    drop_pct: float | None = Field(default=None, ge=0)
    new_window_sec: int | None = Field(default=None, ge=1)
    cooldown_sec: int | None = Field(default=None, ge=1)
    price_min: float | None = Field(default=None, ge=0)
    price_max: float | None = Field(default=None, ge=0)
    personal_only: bool | None = None
    free_shipping: bool | None = None
    new_publish_option: str | None = None
    region: str | None = None


class QueryRequest(BaseModel):
    keyword: str = Field(min_length=1)
    pages: int = Field(default=1, ge=1)
    price_min: float | None = Field(default=None, ge=0)
    price_max: float | None = Field(default=None, ge=0)
    personal_only: bool = False
    free_shipping: bool = False
    new_publish_option: str | None = None
    region: str | None = None


class ConfigUpdateRequest(BaseModel):
    values: dict[str, Any]


class ItemDeleteRequest(BaseModel):
    item_ids: list[str] = Field(min_length=1)
    sub_id: int = Field(default=0, ge=0)



class _SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, int] = {}

    def issue(self) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = int(time.time())
        return token

    def exists(self, token: str | None) -> bool:
        return bool(token) and token in self._sessions

    def revoke(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)


def create_admin_app(plugin: Any) -> FastAPI:
    service = AdminService(plugin)
    sessions = _SessionStore()
    ui_dir = Path(__file__).resolve().parents[1] / "data" / "admin_webui"
    app = FastAPI(title="Goofish Admin WebUI")
    app.mount("/assets", StaticFiles(directory=ui_dir), name="assets")

    async def require_admin(request: Request) -> None:
        session_id = request.cookies.get(ADMIN_SESSION_COOKIE)
        if not sessions.exists(session_id):
            raise HTTPException(status_code=401, detail="admin authentication required")

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "error": {"message": str(exc.detail)}},
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": {"message": str(exc)}},
        )

    @app.exception_handler(KeyError)
    async def handle_key_error(_: Request, exc: KeyError):
        return JSONResponse(
            status_code=404,
            content={"ok": False, "error": {"message": str(exc)}},
        )

    @app.exception_handler(RuntimeError)
    async def handle_runtime_error(_: Request, exc: RuntimeError):
        return JSONResponse(
            status_code=503,
            content={"ok": False, "error": {"message": str(exc)}},
        )

    @app.exception_handler(ProviderError)
    async def handle_provider_error(_: Request, exc: ProviderError):
        payload = {
            "ok": False,
            "error": {
                "code": exc.code.value,
                "message": exc.message,
            },
        }
        if exc.retry_after_sec is not None:
            payload["error"]["retry_after_sec"] = exc.retry_after_sec
        return JSONResponse(status_code=400, content=payload)

    @app.get("/")
    async def index():
        return FileResponse(ui_dir / "index.html")

    @app.post("/api/admin/login")
    async def login(payload: LoginRequest, response: Response):
        if not plugin.settings.admin_webui_api_key:
            raise HTTPException(
                status_code=503,
                detail="admin webui api key is not configured",
            )
        if not secrets.compare_digest(payload.api_key, plugin.settings.admin_webui_api_key):
            raise HTTPException(status_code=401, detail="invalid admin api key")
        session_id = sessions.issue()
        response.set_cookie(
            key=ADMIN_SESSION_COOKIE,
            value=session_id,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
        )
        return {"ok": True}

    @app.post("/api/admin/logout")
    async def logout(request: Request, response: Response, _: None = Depends(require_admin)):
        sessions.revoke(request.cookies.get(ADMIN_SESSION_COOKIE))
        response.delete_cookie(ADMIN_SESSION_COOKIE, path="/")
        return {"ok": True}

    @app.get("/api/overview")
    async def overview(_: None = Depends(require_admin)):
        return {"ok": True, **await service.get_overview()}

    @app.get("/api/subscriptions")
    async def list_subscriptions(
        keyword: str = "",
        umo: str = "",
        status: str = "all",
        limit: int = 50,
        offset: int = 0,
        _: None = Depends(require_admin),
    ):
        return {"ok": True, **await service.list_subscriptions(
            keyword=keyword,
            umo=umo,
            status=status,
            limit=limit,
            offset=offset,
        )}

    @app.get("/api/subscriptions/options")
    async def list_subscription_options(_: None = Depends(require_admin)):
        return {"ok": True, **await service.list_subscription_options()}

    @app.post("/api/subscriptions")
    async def create_subscription(payload: SubscriptionRequest, _: None = Depends(require_admin)):
        return {"ok": True, **await service.create_subscription(payload.model_dump(exclude_unset=True))}

    @app.patch("/api/subscriptions/{sub_id}")
    async def update_subscription(
        sub_id: int,
        payload: SubscriptionRequest,
        _: None = Depends(require_admin),
    ):
        return {"ok": True, **await service.update_subscription(sub_id, payload.model_dump(exclude_unset=True))}

    @app.delete("/api/subscriptions/{sub_id}")
    async def delete_subscription(sub_id: int, _: None = Depends(require_admin)):
        return {"ok": True, **await service.delete_subscription(sub_id)}

    @app.post("/api/subscriptions/{sub_id}/pause")
    async def pause_subscription(sub_id: int, _: None = Depends(require_admin)):
        return {"ok": True, **await service.pause_subscription(sub_id)}

    @app.post("/api/subscriptions/{sub_id}/resume")
    async def resume_subscription(sub_id: int, _: None = Depends(require_admin)):
        return {"ok": True, **await service.resume_subscription(sub_id)}

    @app.post("/api/subscriptions/{sub_id}/check")
    async def check_subscription(sub_id: int, _: None = Depends(require_admin)):
        return {"ok": True, **await service.check_subscription(sub_id)}

    @app.get("/api/subscriptions/{sub_id}/analytics")
    async def subscription_analytics(sub_id: int, _: None = Depends(require_admin)):
        return {"ok": True, **await service.get_subscription_analytics(sub_id)}

    @app.post("/api/query")
    async def query(payload: QueryRequest, _: None = Depends(require_admin)):
        return {"ok": True, **await service.query(payload.model_dump())}

    @app.get("/api/items")
    async def list_items(
        search: str = "",
        sub_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "last_seen_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        _: None = Depends(require_admin),
    ):
        return {
            "ok": True,
            **await service.list_items(
                search=search,
                sub_id=sub_id,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
                offset=offset,
            ),
        }

    @app.get("/api/items/by-subscription")
    async def list_items_by_subscription(
        search: str = "",
        sub_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "last_seen_at",
        sort_order: str = "desc",
        limit: int = 120,
        offset: int = 0,
        _: None = Depends(require_admin),
    ):
        return {
            "ok": True,
            **await service.list_items_by_subscription(
                search=search,
                sub_id=sub_id,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
                offset=offset,
            ),
        }

    @app.get("/api/items/{item_id}")
    async def get_item_detail(item_id: str, _: None = Depends(require_admin)):
        return {"ok": True, "item": await service.get_item_detail(item_id)}

    @app.delete("/api/items")
    async def delete_items(payload: ItemDeleteRequest, _: None = Depends(require_admin)):
        return {"ok": True, **await service.delete_items(payload.item_ids, payload.sub_id)}

    @app.get("/api/fetch-runs")
    async def get_fetch_runs(
        status: str = "",
        limit: int = 50,
        offset: int = 0,
        _: None = Depends(require_admin),
    ):
        return {"ok": True, **await service.list_fetch_runs(status=status, limit=limit, offset=offset)}

    @app.get("/api/activity-monitor")
    async def get_activity_monitor(_: None = Depends(require_admin)):
        return {"ok": True, **await service.get_activity_monitor()}

    @app.get("/api/provider/health")
    async def get_provider_health(refresh: bool = False, _: None = Depends(require_admin)):
        return {"ok": True, "health": await service.get_provider_health(refresh=refresh)}

    @app.get("/api/config")
    async def get_config(_: None = Depends(require_admin)):
        return {"ok": True, "config": await service.get_config()}

    @app.put("/api/config")
    async def update_config(payload: ConfigUpdateRequest, _: None = Depends(require_admin)):
        result = await service.update_config(payload.values)
        status_code = 200 if result.get("ok") else 400
        return JSONResponse(status_code=status_code, content=result)

    @app.post("/api/config/reload")
    async def reload_config(_: None = Depends(require_admin)):
        return {"ok": True, **await service.reload_config()}

    return app


class AdminWebuiServer:
    def __init__(self, plugin: Any) -> None:
        self.plugin = plugin
        self._app: FastAPI | None = None
        self._server: uvicorn.Server | None = None
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def _on_task_done(self, task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            logger.error(
                "[goofish_catcher] admin webui crashed: %s",
                exc,
                exc_info=exc,
            )
        else:
            logger.warning("[goofish_catcher] admin webui task exited unexpectedly (no error)")

    async def start(self) -> None:
        if self.running:
            return
        if not self.plugin.settings.admin_webui_enabled:
            return
        try:
            self._app = create_admin_app(self.plugin)
        except Exception as exc:
            logger.error(
                "[goofish_catcher] admin webui failed to create app: %s",
                exc,
                exc_info=True,
            )
            return
        config = uvicorn.Config(
            self._app,
            host=self.plugin.settings.admin_webui_host,
            port=self.plugin.settings.admin_webui_port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._task = asyncio.create_task(self._server.serve(), name="goofish-admin-webui")
        self._task.add_done_callback(self._on_task_done)
        for _ in range(100):
            if self._server.started:
                break
            if self._task.done():
                # Task exited before server reported started — log the cause
                if not self._task.cancelled():
                    exc = self._task.exception()
                    if exc:
                        logger.error(
                            "[goofish_catcher] admin webui failed to start: %s",
                            exc,
                            exc_info=exc,
                        )
                    else:
                        logger.error(
                            "[goofish_catcher] admin webui task exited during startup with no error"
                            " (port=%s may already be in use)",
                            self.plugin.settings.admin_webui_port,
                        )
                return
            await asyncio.sleep(0.05)
        logger.info(
            "[goofish_catcher] admin webui listening on http://%s:%s",
            self.plugin.settings.admin_webui_host,
            self.plugin.settings.admin_webui_port,
        )

    async def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._task is not None:
            self._task.remove_done_callback(self._on_task_done)
            try:
                await self._task
            except Exception as exc:  # pragma: no cover - defensive cleanup
                logger.warning("[goofish_catcher] admin webui stopped with error: %s", exc)
        self._app = None
        self._server = None
        self._task = None
