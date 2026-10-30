"""Backend for the AstrBot WebUI plugin view (``views/admin``).

The view runs inside the AstrBot dashboard and talks to the plugin through the
``window.AstrBotPluginView`` bridge, which only supports GET and POST. Instead of
duplicating every admin route, requests are forwarded in-process to the same
FastAPI admin app used by the standalone WebUI (without its API-key session,
since the dashboard has already authenticated the user).
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .admin_server import create_admin_app

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_INTERNAL_HOST = "goofish-admin"


class _InternalRequestLogFilter(logging.Filter):
    """Drop httpx access logs for in-process forwarding (polled every few seconds)."""

    def filter(self, record: logging.LogRecord) -> bool:
        return _INTERNAL_HOST not in record.getMessage()


_httpx_logger = logging.getLogger("httpx")
if not any(isinstance(f, _InternalRequestLogFilter) for f in _httpx_logger.filters):
    _httpx_logger.addFilter(_InternalRequestLogFilter())


class AdminPluginViewApi:
    def __init__(self, plugin: Any, plugin_name: str) -> None:
        self.plugin = plugin
        self.plugin_name = plugin_name
        self._client: httpx.AsyncClient | None = None

    def register(self, context: Any) -> None:
        context.register_web_api(
            f"/{self.plugin_name}/api/<path:subpath>",
            self.handle,
            ["GET", "POST"],
            "Goofish admin plugin view API",
        )

    async def handle(self, subpath: str) -> dict[str, Any]:
        # Imported lazily: plugin views (and astrbot.api.web) need AstrBot >= 4.29,
        # while the rest of the plugin still loads on older versions.
        from astrbot.api.web import request

        if request.method == "GET":
            return await self.forward("GET", subpath, dict(request.query.items()), None)
        envelope = await request.json(default={})
        if not isinstance(envelope, dict):
            envelope = {}
        query = envelope.get("query")
        return await self.forward(
            str(envelope.get("method") or "POST"),
            subpath,
            query if isinstance(query, dict) else {},
            envelope.get("body"),
        )

    async def forward(
        self,
        method: str,
        subpath: str,
        query: dict[str, Any],
        body: Any,
    ) -> dict[str, Any]:
        method = method.upper()
        if method not in ALLOWED_METHODS:
            return {"status": "error", "message": f"unsupported method: {method}"}
        response = await self._get_client().request(
            method,
            f"/api/{subpath.lstrip('/')}",
            params={k: v for k, v in query.items() if v is not None},
            json=body if method != "GET" else None,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        # Always "ok" at the bridge level so the view receives the original
        # status code and error payload (e.g. field_errors) unchanged.
        return {
            "status": "ok",
            "data": {"status_code": response.status_code, "body": payload},
        }

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            app = create_admin_app(self.plugin, auth_required=False)
            self._client = httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
                base_url=f"http://{_INTERNAL_HOST}",
                timeout=None,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
