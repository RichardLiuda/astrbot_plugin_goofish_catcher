from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import worker_server
from app.config import PluginSettings
from app.provider_playwright import PlaywrightSearchProvider
from app.provider_remote import RemoteSearchProvider
from app.provider_retry import search_with_captcha_retry
from app.remote_auth_recovery import ActiveRemoteAuthFlow, RemoteAuthRecoveryCoordinator
from app.storage import SubscriptionStorage
from app.types import ProviderError, ProviderErrorCode


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
                message_text="/闲鱼 登录取消",
            )
        )
        self.assertFalse(
            await coordinator.should_auto_complete_from_message(
                umo="umo-2",
                message_text="好了",
            )
        )
