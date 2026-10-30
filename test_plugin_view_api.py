"""AstrBot plugin view bridge forwarding to the admin API app."""

from __future__ import annotations

import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest import mock

import httpx
from app import admin_server
from app.plugin_view_api import AdminPluginViewApi


class _FakeService:
    def __init__(self, plugin) -> None:
        self.plugin = plugin
        self.calls: list[tuple] = []

    async def get_overview(self):
        return {"total": 1}

    async def list_subscriptions(self, **kwargs):
        self.calls.append(("list", kwargs))
        return {"items": [], "keyword": kwargs["keyword"]}

    async def delete_items(self, item_ids, sub_id):
        self.calls.append(("delete", item_ids, sub_id))
        return {"deleted": len(item_ids)}

    async def update_subscription(self, sub_id, payload):
        raise KeyError(f"subscription {sub_id} not found")


def _plugin():
    return SimpleNamespace(settings=SimpleNamespace(admin_webui_api_key="secret"))


class AdminPluginViewApiTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        patcher = mock.patch.object(admin_server, "AdminService", _FakeService)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.api = AdminPluginViewApi(_plugin(), "astrbot_plugin_goofish_catcher")
        self.addAsyncCleanup(self.api.close)

    def test_registers_catch_all_route(self) -> None:
        context = mock.Mock()
        self.api.register(context)
        route, handler, methods, _ = context.register_web_api.call_args.args
        self.assertEqual(route, "/astrbot_plugin_goofish_catcher/api/<path:subpath>")
        self.assertEqual(handler, self.api.handle)
        self.assertEqual(methods, ["GET", "POST"])

    async def test_get_skips_admin_session(self) -> None:
        result = await self.api.forward("GET", "overview", {}, None)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["status_code"], 200)
        self.assertEqual(result["data"]["body"], {"ok": True, "total": 1})

    async def test_get_passes_query(self) -> None:
        result = await self.api.forward(
            "GET", "subscriptions", {"keyword": "相机", "umo": None}, None
        )
        self.assertEqual(result["data"]["body"]["keyword"], "相机")

    async def test_method_override_with_body(self) -> None:
        result = await self.api.forward(
            "DELETE", "items", {}, {"item_ids": ["a", "b"], "sub_id": 3}
        )
        self.assertEqual(result["data"]["body"], {"ok": True, "deleted": 2})

    async def test_error_status_and_payload_are_preserved(self) -> None:
        result = await self.api.forward("PATCH", "subscriptions/9", {}, {})
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["status_code"], 404)
        self.assertFalse(result["data"]["body"]["ok"])
        self.assertIn("not found", result["data"]["body"]["error"]["message"])

    def _stub_request(self, method: str, query=(), body=None):
        async def _json(default=None):
            return default if body is None else body

        web = ModuleType("astrbot.api.web")
        web.request = SimpleNamespace(
            method=method,
            query=SimpleNamespace(items=lambda: list(query)),
            json=_json,
        )
        patcher = mock.patch.dict(sys.modules, {"astrbot.api.web": web})
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_handle_get_reads_query(self) -> None:
        self._stub_request("GET", query=[("keyword", "相机")])
        result = await self.api.handle("subscriptions")
        self.assertEqual(result["data"]["body"]["keyword"], "相机")

    async def test_handle_post_unwraps_method_envelope(self) -> None:
        self._stub_request(
            "POST",
            body={"method": "DELETE", "body": {"item_ids": ["a"], "sub_id": 0}},
        )
        result = await self.api.handle("items")
        self.assertEqual(result["data"]["body"], {"ok": True, "deleted": 1})

    async def test_rejects_unknown_method(self) -> None:
        result = await self.api.forward("TRACE", "overview", {}, None)
        self.assertEqual(result["status"], "error")


class StandaloneAdminAppTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        patcher = mock.patch.object(admin_server, "AdminService", _FakeService)
        patcher.start()
        self.addCleanup(patcher.stop)
        app = admin_server.create_admin_app(_plugin())
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        )
        self.addAsyncCleanup(self.client.aclose)

    async def test_requires_session(self) -> None:
        response = await self.client.get("/api/overview")
        self.assertEqual(response.status_code, 401)

    async def test_serves_view_assets(self) -> None:
        index = await self.client.get("/")
        self.assertEqual(index.status_code, 200)
        self.assertIn("./app.bundle.js", index.text)
        bundle = await self.client.get("/app.bundle.js")
        self.assertEqual(bundle.status_code, 200)


if __name__ == "__main__":
    unittest.main()
