from __future__ import annotations

import asyncio
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import worker_server
from app.auth_session import LocalAuthSessionController
from app.config import PluginSettings, load_plugin_settings
from app.provider_playwright import PlaywrightSearchProvider
from app.provider_remote import RemoteSearchProvider
from app.provider_retry import (
    estimate_captcha_retry_timeout_sec,
    search_with_captcha_retry,
)
from app.remote_auth_recovery import ActiveRemoteAuthFlow, RemoteAuthRecoveryCoordinator
from app.storage import SubscriptionStorage
from app.types import FavoriteItemResult, ProviderError, ProviderErrorCode


def build_settings(base_dir: Path) -> PluginSettings:
    return PluginSettings(
        plugin_name="goofish_worker",
        plugin_data_dir=base_dir,
        db_path=base_dir / "goofish_catcher.db",
        provider_mode="playwright_local",
        default_interval_sec=600,
        default_pages=1,
        max_pages=2,
        scheduler_tick_sec=15,
        max_concurrency=1,
        fetch_timeout_sec=20,
        max_retries=0,
        retry_base_sec=30,
        retry_max_sec=900,
        default_new_window_sec=1800,
        default_drop_abs=50.0,
        default_drop_pct=0.05,
        default_cooldown_sec=21600,
        playwright_storage_state_path=base_dir / "storage_state.json",
        playwright_executable_path=None,
        playwright_headless=False,
        playwright_block_assets=True,
        playwright_force_direct=True,
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


class FakeGoofishLoginSession:
    created_count = 0

    def __init__(self, **_: object) -> None:
        type(self).created_count += 1
        self.page_url = "https://passport.goofish.example/login"
        self.closed = False

    async def start_login_session(self):
        return await self.capture_snapshot()

    async def capture_snapshot(self):
        return SimpleNamespace(
            page_url=self.page_url,
            screenshot_base64="ZmFrZS1pbWFnZQ==",
        )

    async def save_storage_state(self, target_path):
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fake-state", encoding="utf-8")
        return target

    async def close(self):
        self.closed = True


class WorkerAuthRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.base_dir = Path(self._temp_dir.name)
        FakeGoofishLoginSession.created_count = 0

    def test_auth_start_reuses_active_session_and_confirm_saves_state(self) -> None:
        settings = build_settings(self.base_dir)
        manager = worker_server.WorkerLoginSessionManager(settings)
        runtime = worker_server.WorkerRuntime(
            settings=settings,
            provider=object(),
            auth=worker_server.WorkerAuthConfig(
                api_key=None,
                cf_access_client_id=None,
                cf_access_client_secret=None,
            ),
            login_manager=manager,
        )

        with patch.object(
            worker_server,
            "GoofishLoginSession",
            FakeGoofishLoginSession,
        ):
            with TestClient(worker_server.create_app(runtime)) as client:
                first = client.post("/v1/auth/start", json={"force_restart": False})
                self.assertEqual(first.status_code, 200)
                first_payload = first.json()
                self.assertEqual(first_payload["status"], "active")
                self.assertTrue(first_payload["session_id"])
                self.assertTrue(first_payload["screenshot_base64"])
                self.assertEqual(first_payload["timeout_sec"], 60)

                second = client.post("/v1/auth/start", json={"force_restart": False})
                self.assertEqual(second.status_code, 200)
                second_payload = second.json()
                self.assertEqual(
                    second_payload["session_id"],
                    first_payload["session_id"],
                )
                self.assertEqual(FakeGoofishLoginSession.created_count, 1)

                confirm = client.post(
                    "/v1/auth/confirm",
                    json={"session_id": first_payload["session_id"]},
                )
                self.assertEqual(confirm.status_code, 200)
                confirm_payload = confirm.json()
                self.assertEqual(confirm_payload["status"], "saved")
                saved_path = Path(confirm_payload["saved_path"])
                self.assertTrue(saved_path.exists())
                self.assertEqual(saved_path.read_text(encoding="utf-8"), "fake-state")

                confirm_again = client.post(
                    "/v1/auth/confirm",
                    json={"session_id": first_payload["session_id"]},
                )
                self.assertEqual(confirm_again.status_code, 409)
                self.assertIn(
                    "no active login session",
                    confirm_again.json()["error"]["message"],
                )

    def test_auth_cancel_clears_active_session(self) -> None:
        settings = build_settings(self.base_dir)
        manager = worker_server.WorkerLoginSessionManager(settings)
        runtime = worker_server.WorkerRuntime(
            settings=settings,
            provider=object(),
            auth=worker_server.WorkerAuthConfig(
                api_key=None,
                cf_access_client_id=None,
                cf_access_client_secret=None,
            ),
            login_manager=manager,
        )

        with patch.object(
            worker_server,
            "GoofishLoginSession",
            FakeGoofishLoginSession,
        ):
            with TestClient(worker_server.create_app(runtime)) as client:
                first = client.post("/v1/auth/start", json={"force_restart": False})
                session_id = first.json()["session_id"]

                cancel = client.post("/v1/auth/cancel", json={"session_id": session_id})
                self.assertEqual(cancel.status_code, 200)
                self.assertEqual(cancel.json()["status"], "cancelled")

                confirm = client.post("/v1/auth/confirm", json={"session_id": session_id})
                self.assertEqual(confirm.status_code, 409)
                self.assertIn("no active login session", confirm.json()["error"]["message"])

    def test_auth_confirm_rejects_timed_out_session(self) -> None:
        settings = build_settings(self.base_dir)
        manager = worker_server.WorkerLoginSessionManager(settings)
        runtime = worker_server.WorkerRuntime(
            settings=settings,
            provider=object(),
            auth=worker_server.WorkerAuthConfig(
                api_key=None,
                cf_access_client_id=None,
                cf_access_client_secret=None,
            ),
            login_manager=manager,
        )

        with patch.object(
            worker_server,
            "GoofishLoginSession",
            FakeGoofishLoginSession,
        ):
            with TestClient(worker_server.create_app(runtime)) as client:
                first = client.post("/v1/auth/start", json={"force_restart": False})
                session_id = first.json()["session_id"]
                assert manager._active_session is not None
                manager._active_session.expires_at_monotonic = 0.0

                confirm = client.post("/v1/auth/confirm", json={"session_id": session_id})
                self.assertEqual(confirm.status_code, 409)
                self.assertIn("timed out after 60 seconds", confirm.json()["error"]["message"])


class LocalAuthSessionControllerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)
        FakeGoofishLoginSession.created_count = 0

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_local_auth_start_reuses_active_session_and_confirm_mirrors_state(self) -> None:
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings)

        with patch("app.auth_session.GoofishLoginSession", FakeGoofishLoginSession):
            first = await controller.start_auth_session(force_restart=False)
            self.assertEqual(first["status"], "active")
            self.assertTrue(first["session_id"])
            self.assertTrue(first["screenshot_base64"])
            self.assertEqual(first["timeout_sec"], 60)

            second = await controller.start_auth_session(force_restart=False)
            self.assertEqual(second["session_id"], first["session_id"])
            self.assertEqual(FakeGoofishLoginSession.created_count, 1)

            confirm = await controller.confirm_auth_session(
                session_id=first["session_id"]
            )
            self.assertEqual(confirm["status"], "saved")
            saved_path = Path(confirm["saved_path"])
            self.assertTrue(saved_path.exists())
            self.assertEqual(saved_path.read_text(encoding="utf-8"), "fake-state")
            self.assertEqual(confirm["mirrored_paths"], [])

            with self.assertRaises(RuntimeError):
                await controller.confirm_auth_session(session_id=first["session_id"])

    async def test_local_auth_cancel_clears_active_session(self) -> None:
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings)

        with patch("app.auth_session.GoofishLoginSession", FakeGoofishLoginSession):
            first = await controller.start_auth_session(force_restart=False)
            session_id = first["session_id"]

            cancel = await controller.cancel_auth_session(session_id=session_id)
            self.assertEqual(cancel["status"], "cancelled")

            with self.assertRaises(RuntimeError):
                await controller.cancel_auth_session(session_id=session_id)

    async def test_local_auth_confirm_rejects_timed_out_session(self) -> None:
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings)

        with patch("app.auth_session.GoofishLoginSession", FakeGoofishLoginSession):
            first = await controller.start_auth_session(force_restart=False)
            assert controller._active_session is not None
            controller._active_session.expires_at_monotonic = 0.0

            with self.assertRaisesRegex(
                RuntimeError,
                "timed out after 60 seconds",
            ):
                await controller.confirm_auth_session(session_id=first["session_id"])


class LocalStorageStatePathTests(unittest.TestCase):
    def test_resolve_local_storage_state_path_uses_runtime_plugin_data_dir(self) -> None:
        expected_dir = Path("/tmp/goofish-plugin-data")

        with patch(
            "app.auth_session.StarTools",
            SimpleNamespace(get_data_dir=lambda plugin_name: expected_dir),
        ):
            from app.auth_session import resolve_local_storage_state_path

            resolved = resolve_local_storage_state_path()

        self.assertEqual(resolved, expected_dir / "storage_state.json")


class PluginSettingsStoragePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.base_dir = Path(self._temp_dir.name)
        self.plugin_data_dir = self.base_dir / "plugin_data"
        self.plugin_data_dir.mkdir(parents=True, exist_ok=True)

    def test_local_mode_always_uses_stable_storage_state_path(self) -> None:
        settings = load_plugin_settings(
            {"provider_mode": "playwright_local"},
            "goofish_catcher",
            self.plugin_data_dir,
        )

        stable_path = self.plugin_data_dir / "storage_state.json"
        self.assertEqual(settings.playwright_storage_state_path, stable_path)

    def test_remote_mode_ignores_stable_storage_state_when_missing(self) -> None:
        settings = load_plugin_settings(
            {"provider_mode": "remote_rest"},
            "goofish_catcher",
            self.plugin_data_dir,
        )

        self.assertIsNone(settings.playwright_storage_state_path)


class StorageResumeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)
        self.storage = SubscriptionStorage(self.base_dir / "goofish_catcher.db")
        await self.storage.initialize()

    async def _cleanup_temp_dir(self) -> None:
        await self.storage.close()
        self._temp_dir.cleanup()

    async def test_resume_subscriptions_by_pause_reasons_only_resumes_auth_pauses(self) -> None:
        auth_sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword="auth-sub",
            interval_sec=600,
            pages=1,
            drop_abs=50.0,
            drop_pct=0.05,
            new_window_sec=1800,
            cooldown_sec=21600,
        )
        captcha_sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword="captcha-sub",
            interval_sec=600,
            pages=1,
            drop_abs=50.0,
            drop_pct=0.05,
            new_window_sec=1800,
            cooldown_sec=21600,
        )
        manual_sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword="manual-sub",
            interval_sec=600,
            pages=1,
            drop_abs=50.0,
            drop_pct=0.05,
            new_window_sec=1800,
            cooldown_sec=21600,
        )

        await self.storage.pause_subscription(auth_sub.id, "AUTH_REQUIRED")
        await self.storage.pause_subscription(captcha_sub.id, "CAPTCHA")
        await self.storage.pause_subscription(manual_sub.id, "MANUAL_PAUSE")

        resumed = await self.storage.resume_subscriptions_by_pause_reasons(
            ("AUTH_REQUIRED", "CAPTCHA"),
            now_ts=1234567890,
        )

        self.assertEqual({sub.keyword for sub in resumed}, {"auth-sub", "captcha-sub"})
        self.assertTrue(all(sub.enabled for sub in resumed))
        self.assertTrue(all(sub.paused_reason is None for sub in resumed))
        self.assertTrue(all(sub.next_run_at == 1234567890 for sub in resumed))

        auth_after = await self.storage.get_subscription("umo-1", "auth-sub")
        captcha_after = await self.storage.get_subscription("umo-1", "captcha-sub")
        manual_after = await self.storage.get_subscription("umo-1", "manual-sub")

        self.assertIsNotNone(auth_after)
        self.assertIsNotNone(captcha_after)
        self.assertIsNotNone(manual_after)
        self.assertTrue(auth_after.enabled)
        self.assertTrue(captcha_after.enabled)
        self.assertFalse(manual_after.enabled)
        self.assertEqual(manual_after.paused_reason, "MANUAL_PAUSE")


class ProviderCaptchaRetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_retry_timeout_budget_accounts_for_all_attempts(self) -> None:
        self.assertEqual(
            estimate_captcha_retry_timeout_sec(timeout_sec=20),
            92,
        )

    async def test_search_retries_captcha_twice_before_success(self) -> None:
        class FakeProvider:
            def __init__(self) -> None:
                self.calls = 0

            async def search(self, *, keyword, pages, timeout_sec):
                self.calls += 1
                if self.calls < 3:
                    raise ProviderError(
                        ProviderErrorCode.CAPTCHA,
                        "captcha required",
                    )
                return [{"keyword": keyword, "pages": pages, "timeout_sec": timeout_sec}]

        provider = FakeProvider()
        result = await search_with_captcha_retry(
            provider,
            keyword="camera",
            pages=2,
            timeout_sec=20,
            retry_delay_sec=0,
        )

        self.assertEqual(provider.calls, 3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["keyword"], "camera")

    async def test_search_raises_after_final_captcha_retry(self) -> None:
        class FakeProvider:
            def __init__(self) -> None:
                self.calls = 0

            async def search(self, *, keyword, pages, timeout_sec):
                self.calls += 1
                raise ProviderError(
                    ProviderErrorCode.CAPTCHA,
                    f"captcha attempt {self.calls}",
                )

        provider = FakeProvider()
        with self.assertRaises(ProviderError) as ctx:
            await search_with_captcha_retry(
                provider,
                keyword="lens",
                pages=1,
                timeout_sec=20,
                retry_delay_sec=0,
            )

        self.assertEqual(provider.calls, 3)
        self.assertEqual(ctx.exception.code, ProviderErrorCode.CAPTCHA)
        self.assertEqual(ctx.exception.message, "captcha attempt 3")


class RemoteProviderTimeoutBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_remote_search_uses_timeout_buffer(self) -> None:
        settings = replace(
            build_settings(self.base_dir),
            provider_mode="remote_rest",
            remote_base_url="https://worker.example",
        )
        provider = RemoteSearchProvider(settings)

        async def fake_request_json(*, method, path, timeout_sec, json_body=None):
            self.assertEqual(method, "POST")
            self.assertEqual(path, "/v1/search")
            self.assertEqual(timeout_sec, 30)
            return SimpleNamespace(status_code=200, text=""), {"ok": True, "items": []}

        provider._request_json = fake_request_json  # type: ignore[method-assign]
        items = await provider.search(
            keyword="flash",
            pages=1,
            timeout_sec=20,
        )

        self.assertEqual(items, [])

    async def test_remote_favorite_uses_route_and_parses_response(self) -> None:
        settings = replace(
            build_settings(self.base_dir),
            provider_mode="remote_rest",
            remote_base_url="https://worker.example",
        )
        provider = RemoteSearchProvider(settings)

        async def fake_request_json(*, method, path, timeout_sec, json_body=None):
            self.assertEqual(method, "POST")
            self.assertEqual(path, "/v1/favorite")
            self.assertEqual(timeout_sec, 30)
            self.assertEqual(
                json_body,
                {
                    "url": "https://www.goofish.com/item?id=123",
                    "item_id": "123",
                    "timeout_ms": 20000,
                },
            )
            return SimpleNamespace(status_code=200, text=""), {
                "ok": True,
                "status": "favorited",
                "url": "https://www.goofish.com/item?id=123",
                "item_id": "123",
                "title": "Sony A7C2",
            }

        provider._request_json = fake_request_json  # type: ignore[method-assign]
        result = await provider.favorite_item(
            url="https://www.goofish.com/item?id=123",
            item_id="123",
            timeout_sec=20,
        )

        self.assertEqual(result.status, "favorited")
        self.assertEqual(result.item_id, "123")
        self.assertEqual(result.title, "Sony A7C2")

    async def test_timeout_page_state_maps_login_page_to_auth_required(self) -> None:
        settings = build_settings(self.base_dir)
        provider = PlaywrightSearchProvider(settings)

        class FakePage:
            url = "https://passport.goofish.com/login"

            async def content(self) -> str:
                return "<html><body>login</body></html>"

        error = await provider._classify_timeout_page_state(FakePage())
        self.assertIsNotNone(error)
        self.assertEqual(error.code, ProviderErrorCode.AUTH_REQUIRED)


class WorkerFavoriteRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.base_dir = Path(self._temp_dir.name)

    def test_worker_favorite_route_returns_provider_payload(self) -> None:
        async def _favorite_item(*, url: str, item_id: str | None, timeout_sec: int):
            self.assertEqual(url, "https://www.goofish.com/item?id=123")
            self.assertEqual(item_id, "123")
            self.assertEqual(timeout_sec, 20)
            return FavoriteItemResult(
                status="already_favorited",
                url=url,
                item_id=item_id,
                title="Canon R6",
            )

        runtime = worker_server.WorkerRuntime(
            settings=build_settings(self.base_dir),
            provider=SimpleNamespace(favorite_item=_favorite_item),
            auth=worker_server.WorkerAuthConfig(
                api_key=None,
                cf_access_client_id=None,
                cf_access_client_secret=None,
            ),
        )

        with TestClient(worker_server.create_app(runtime)) as client:
            response = client.post(
                "/v1/favorite",
                json={
                    "url": "https://www.goofish.com/item?id=123",
                    "item_id": "123",
                    "timeout_ms": 20000,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "ok": True,
                "status": "already_favorited",
                "url": "https://www.goofish.com/item?id=123",
                "item_id": "123",
                "title": "Canon R6",
            },
        )


class PlaywrightFavoriteBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_favorite_item_returns_idempotent_success_when_already_favorited(self) -> None:
        settings = build_settings(self.base_dir)
        provider = PlaywrightSearchProvider(settings)
        browser, page = _build_fake_favorite_browser(button_text="已收藏")

        async def fake_ensure_browser():
            return browser

        provider._ensure_browser = fake_ensure_browser  # type: ignore[method-assign]
        result = await provider.favorite_item(
            url="https://www.goofish.com/item?id=123",
            item_id="123",
            timeout_sec=20,
        )

        self.assertEqual(result.status, "already_favorited")
        self.assertEqual(result.item_id, "123")
        self.assertEqual(page.favorite_locator.click_count, 0)
        self.assertEqual(page.wait_for_function_calls, 0)

    async def test_favorite_item_clicks_and_waits_for_collected_state(self) -> None:
        settings = build_settings(self.base_dir)
        provider = PlaywrightSearchProvider(settings)
        browser, page = _build_fake_favorite_browser(button_text="收藏")

        async def fake_ensure_browser():
            return browser

        provider._ensure_browser = fake_ensure_browser  # type: ignore[method-assign]
        result = await provider.favorite_item(
            url="https://www.goofish.com/item?id=123",
            item_id="123",
            timeout_sec=20,
        )

        self.assertEqual(result.status, "favorited")
        self.assertEqual(page.favorite_locator.click_count, 1)
        self.assertEqual(page.favorite_locator.text, "已收藏")
        self.assertEqual(page.wait_for_function_calls, 1)


class RemoteAuthAutoCompleteTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_auto_complete_accepts_plain_reply_for_owner(self) -> None:
        async def _send_message(*args, **kwargs) -> None:
            return None

        settings = replace(build_settings(self.base_dir), provider_mode="remote_rest")
        provider = SimpleNamespace(
            start_auth_session=lambda **_: None,
            confirm_auth_session=lambda **_: None,
            cancel_auth_session=lambda **_: None,
        )
        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=settings,
            provider=provider,
        )
        coordinator._active_flow = ActiveRemoteAuthFlow(
            session_id="session-1",
            owner_umo="umo-1",
            started_at=1,
            expires_at=time.time() + 120,
            page_url="https://example.com/login",
        )

        should_complete = await coordinator.should_auto_complete_from_message(
            umo="umo-1",
            message_text="好了，继续",
        )

        self.assertTrue(should_complete)

    async def test_auto_complete_ignores_commands_and_non_owner_messages(self) -> None:
        async def _send_message(*args, **kwargs) -> None:
            return None

        settings = replace(build_settings(self.base_dir), provider_mode="remote_rest")
        provider = SimpleNamespace(
            start_auth_session=lambda **_: None,
            confirm_auth_session=lambda **_: None,
            cancel_auth_session=lambda **_: None,
        )
        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=settings,
            provider=provider,
        )
        coordinator._active_flow = ActiveRemoteAuthFlow(
            session_id="session-1",
            owner_umo="umo-1",
            started_at=1,
            expires_at=time.time() + 120,
            page_url="https://example.com/login",
        )

        self.assertFalse(
            await coordinator.should_auto_complete_from_message(
                umo="umo-1",
                message_text="/闲鱼 登录",
            )
        )
        self.assertFalse(
            await coordinator.should_auto_complete_from_message(
                umo="umo-1",
                message_text="闲鱼 登录",
            )
        )
        self.assertFalse(
            await coordinator.should_auto_complete_from_message(
                umo="umo-1",
                message_text="/闲鱼 登录取消",
            )
        )
        self.assertFalse(
            await coordinator.should_auto_complete_from_message(
                umo="umo-2",
                message_text="好了",
            )
        )

    async def test_restart_login_message_is_detected_for_owner(self) -> None:
        async def _send_message(*args, **kwargs) -> None:
            return None

        settings = replace(build_settings(self.base_dir), provider_mode="remote_rest")
        provider = SimpleNamespace(
            start_auth_session=lambda **_: None,
            confirm_auth_session=lambda **_: None,
            cancel_auth_session=lambda **_: None,
        )
        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=settings,
            provider=provider,
        )
        coordinator._active_flow = ActiveRemoteAuthFlow(
            session_id="session-1",
            owner_umo="umo-1",
            started_at=1,
            expires_at=time.time() + 120,
            page_url="https://example.com/login",
        )

        self.assertTrue(
            await coordinator.should_restart_login_from_message(
                umo="umo-1",
                message_text="闲鱼 登录",
            )
        )
        self.assertTrue(
            await coordinator.should_restart_login_from_message(
                umo="umo-1",
                message_text="/闲鱼 登录",
            )
        )
        self.assertFalse(
            await coordinator.should_restart_login_from_message(
                umo="umo-1",
                message_text="好了继续",
            )
        )
        self.assertFalse(
            await coordinator.should_restart_login_from_message(
                umo="umo-1",
                message_text="/闲鱼 登录完成",
            )
        )
        self.assertFalse(
            await coordinator.should_restart_login_from_message(
                umo="umo-1",
                message_text="/闲鱼 登录取消",
            )
        )

    async def test_start_login_restarts_existing_owner_flow(self) -> None:
        sent_messages: list[tuple[str, object]] = []
        force_restart_flags: list[bool] = []

        async def _send_message(umo, chain) -> None:
            sent_messages.append((umo, chain))

        async def _start_auth_session(*, force_restart: bool = False):
            force_restart_flags.append(force_restart)
            return {
                "session_id": "session-restarted",
                "status": "active",
                "started_at": int(time.time()),
                "timeout_sec": 60,
                "page_url": "https://www.goofish.com/member/login",
                "screenshot_base64": "ZmFrZS1pbWFnZQ==",
            }

        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=replace(build_settings(self.base_dir), provider_mode="remote_rest"),
            auth_controller=SimpleNamespace(
                start_auth_session=_start_auth_session,
                confirm_auth_session=lambda **_: None,
                cancel_auth_session=lambda **_: None,
            ),
        )
        coordinator._active_flow = ActiveRemoteAuthFlow(
            session_id="session-1",
            owner_umo="umo-1",
            started_at=1,
            expires_at=time.time() + 120,
            page_url="https://example.com/login",
        )

        message = await coordinator.start_login(umo="umo-1")

        self.assertEqual(message, "已重启登录流程并将新的二维码发送到当前会话。")
        self.assertEqual(force_restart_flags, [True])
        self.assertEqual(len(sent_messages), 1)
        await coordinator.close()

    async def test_local_mode_auth_failure_can_start_login_recovery(self) -> None:
        sent_messages: list[tuple[str, object]] = []

        async def _send_message(umo, chain) -> None:
            sent_messages.append((umo, chain))

        async def _start_auth_session(*, force_restart: bool = False):
            self.assertFalse(force_restart)
            return {
                "session_id": "local-session-1",
                "status": "active",
                "started_at": 1,
                "page_url": "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC",
                "screenshot_base64": "ZmFrZS1pbWFnZQ==",
            }

        settings = build_settings(self.base_dir)
        async def _confirm_auth_session(**_):
            return None

        async def _cancel_auth_session(**_):
            return None

        auth_controller = SimpleNamespace(
            start_auth_session=_start_auth_session,
            confirm_auth_session=_confirm_auth_session,
            cancel_auth_session=_cancel_auth_session,
        )
        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=settings,
            auth_controller=auth_controller,
        )

        message = await coordinator.handle_provider_auth_failure(
            umo="umo-1",
            sub_id=123,
        )

        self.assertEqual(
            message,
            "已向当前会话发送登录二维码，扫码登录后回复任意消息即可继续。",
        )
        self.assertEqual(len(sent_messages), 1)
        await coordinator.close()

    async def test_login_flow_times_out_and_auto_cancels_session(self) -> None:
        sent_messages: list[tuple[str, object]] = []
        cancelled_session_ids: list[str] = []

        async def _send_message(umo, chain) -> None:
            sent_messages.append((umo, chain))

        async def _start_auth_session(*, force_restart: bool = False):
            self.assertFalse(force_restart)
            return {
                "session_id": "session-timeout-1",
                "status": "active",
                "started_at": int(time.time()),
                "timeout_sec": 1,
                "page_url": "https://www.goofish.com/member/login",
                "screenshot_base64": "ZmFrZS1pbWFnZQ==",
            }

        async def _cancel_auth_session(*, session_id: str):
            cancelled_session_ids.append(session_id)
            return {
                "ok": True,
                "session_id": session_id,
                "status": "cancelled",
            }

        settings = replace(build_settings(self.base_dir), provider_mode="remote_rest")
        coordinator = RemoteAuthRecoveryCoordinator(
            context=SimpleNamespace(send_message=_send_message),
            settings=settings,
            auth_controller=SimpleNamespace(
                start_auth_session=_start_auth_session,
                confirm_auth_session=lambda **_: None,
                cancel_auth_session=_cancel_auth_session,
            ),
            auth_timeout_sec=1,
        )

        await coordinator.start_login(umo="umo-1")
        await asyncio.wait_for(coordinator.wait_until_idle(), timeout=2.5)

        self.assertEqual(cancelled_session_ids, ["session-timeout-1"])
        self.assertFalse(coordinator.has_active_flow())
        self.assertEqual(len(sent_messages), 2)


class _FakeFavoriteLocator:
    def __init__(self, text: str) -> None:
        self.text = text
        self.click_count = 0

    @property
    def first(self) -> _FakeFavoriteLocator:
        return self

    async def inner_text(self) -> str:
        return self.text

    async def click(self, timeout: int | None = None) -> None:
        del timeout
        self.click_count += 1
        if "已收藏" not in self.text and "收藏" in self.text:
            self.text = "已收藏"


class _FakeFavoritePage:
    def __init__(self, button_text: str) -> None:
        self.url = "https://www.goofish.com/item?id=123"
        self.favorite_locator = _FakeFavoriteLocator(button_text)
        self.wait_for_function_calls = 0
        self.default_timeout = None

    def set_default_timeout(self, timeout: int) -> None:
        self.default_timeout = timeout

    async def goto(self, url: str, wait_until: str, timeout: int) -> None:
        del wait_until, timeout
        self.url = url

    async def wait_for_load_state(self, state: str, timeout: int) -> None:
        del state, timeout

    async def wait_for_timeout(self, timeout: int) -> None:
        del timeout

    async def wait_for_selector(self, selector: str, timeout: int) -> None:
        del selector, timeout

    def locator(self, selector: str) -> _FakeFavoriteLocator:
        del selector
        return self.favorite_locator

    async def title(self) -> str:
        return "测试商品 - 闲鱼"

    async def wait_for_function(self, script: str, arg: str, timeout: int) -> None:
        del script, arg, timeout
        self.wait_for_function_calls += 1
        if "已收藏" not in self.favorite_locator.text:
            raise AssertionError("favorite state did not change to collected")

    async def content(self) -> str:
        return "<html><body>ok</body></html>"


class _FakeFavoriteContext:
    def __init__(self, page: _FakeFavoritePage) -> None:
        self.page = page
        self.closed = False
        self.storage_state_paths: list[str] = []

    async def new_page(self) -> _FakeFavoritePage:
        return self.page

    async def storage_state(self, path: str) -> dict[str, object]:
        self.storage_state_paths.append(path)
        return {}

    async def close(self) -> None:
        self.closed = True


class _FakeFavoriteBrowser:
    def __init__(self, context: _FakeFavoriteContext) -> None:
        self.context = context
        self.last_context_kwargs: dict[str, object] | None = None

    async def new_context(self, **kwargs):
        self.last_context_kwargs = kwargs
        return self.context


def _build_fake_favorite_browser(
    *,
    button_text: str,
) -> tuple[_FakeFavoriteBrowser, _FakeFavoritePage]:
    page = _FakeFavoritePage(button_text)
    context = _FakeFavoriteContext(page)
    browser = _FakeFavoriteBrowser(context)
    return browser, page
