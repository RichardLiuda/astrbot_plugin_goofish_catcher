"""P0 登录认证链路平台化测试。

覆盖：
1. GoofishLoginSession 的 SiteProfile 注入（login_url / 校验标记 / auth 判定取自档案）。
2. _match_login_status_api 对驼峰 api 参数（api=mtop.user.getUserSimple）的命中。
3. LocalAuthSessionController 按平台解析 storage_state 路径与 profile 稳定目录。
4. RemoteAuthRecoveryCoordinator 按平台分 flow：淘宝 controller、flow 隔离、
   登录成功后只恢复同平台订阅（真 SubscriptionStorage）。
5. provider._try_quick_login 在 TAOBAO_PROFILE 下直接返回 False（不触碰页面）。

注意：unittest discover 按文件名字母序加载，本文件排在最前；astrbot stub
必须在 import app.* 之前安装（参照 test_recommend_price_threshold.py），
且 MessageChain / Plain / Reply 为 functional stub（test_remote_auth_flow /
test_reply_favorite 的既有用例依赖这些模块）。
"""
from __future__ import annotations

import sys
import tempfile
import time
import types
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace


def _install_astrbot_stubs() -> None:
    class _MessageChain:
        def __init__(self) -> None:
            self.texts: list[str] = []
            self.images: list[str] = []

        def message(self, text):
            self.texts.append(str(text))
            return self

        def base64_image(self, image):
            self.images.append(image)
            return self

    class Plain:
        def __init__(self, text: str = "") -> None:
            self.text = text

    class Image:
        def __init__(self, *args, **kwargs) -> None:
            pass

    class Reply:
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    astrbot_module = types.ModuleType("astrbot")
    astrbot_api_module = types.ModuleType("astrbot.api")
    astrbot_api_module.logger = SimpleNamespace(
        warning=lambda *args, **kwargs: None,
        info=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
        debug=lambda *args, **kwargs: None,
    )
    astrbot_api_star_module = types.ModuleType("astrbot.api.star")
    astrbot_api_star_module.Context = object
    astrbot_api_star_module.StarTools = object
    astrbot_api_event_module = types.ModuleType("astrbot.api.event")
    astrbot_api_event_module.MessageChain = _MessageChain
    astrbot_api_message_components_module = types.ModuleType(
        "astrbot.api.message_components"
    )
    astrbot_api_message_components_module.Image = Image
    astrbot_api_message_components_module.Plain = Plain
    astrbot_api_message_components_module.Reply = Reply

    sys.modules.setdefault("astrbot", astrbot_module)
    sys.modules["astrbot.api"] = astrbot_api_module
    sys.modules["astrbot.api.star"] = astrbot_api_star_module
    sys.modules["astrbot.api.event"] = astrbot_api_event_module
    sys.modules["astrbot.api.message_components"] = (
        astrbot_api_message_components_module
    )


_install_astrbot_stubs()

from app.auth_session import LocalAuthSessionController
from app.config import PluginSettings
from app.login_session import (
    DEFAULT_LOGIN_URL,
    GoofishLoginSession,
    _match_login_status_api,
)
from app.platforms.goofish import GOOFISH_PROFILE
from app.platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO
from app.platforms.taobao import TAOBAO_PROFILE
from app.provider_playwright import PlaywrightSearchProvider
from app.remote_auth_recovery import RemoteAuthRecoveryCoordinator
from app.storage import SubscriptionStorage


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
        playwright_user_data_dir=None,
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


class _StubAuthController:
    def __init__(self, *, session_prefix: str) -> None:
        self.session_prefix = session_prefix
        self.start_calls: list[bool] = []
        self.confirm_calls: list[str] = []
        self.cancel_calls: list[str] = []
        self.closed = False

    async def start_auth_session(self, *, force_restart: bool = False):
        self.start_calls.append(force_restart)
        return {
            "ok": True,
            "session_id": f"{self.session_prefix}-{len(self.start_calls)}",
            "status": "active",
            "started_at": int(time.time()),
            "timeout_sec": 60,
            "page_url": "https://example.com/login",
            "screenshot_base64": "ZmFrZS1pbWFnZQ==",
        }

    async def confirm_auth_session(self, *, session_id: str):
        self.confirm_calls.append(session_id)
        return {
            "ok": True,
            "session_id": session_id,
            "status": "saved",
            "saved_path": f"/tmp/{session_id}.json",
            "mirrored_paths": [],
            "saved_at": int(time.time()),
        }

    async def cancel_auth_session(self, *, session_id: str):
        self.cancel_calls.append(session_id)
        return {"ok": True, "session_id": session_id, "status": "cancelled"}

    async def close(self) -> None:
        self.closed = True


class _StubContext:
    def __init__(self) -> None:
        self.sent: list[tuple[str, object]] = []

    async def send_message(self, umo, chain) -> None:
        self.sent.append((umo, chain))


class LoginSessionProfileInjectionTests(unittest.TestCase):
    """任务 6.1：GoofishLoginSession 档案注入（不启动浏览器）。"""

    def test_default_profile_is_goofish_and_login_url_unchanged(self) -> None:
        session = GoofishLoginSession()
        self.assertIs(session._profile, GOOFISH_PROFILE)
        self.assertEqual(session.login_url, GOOFISH_PROFILE.login_url)
        # 旧的 DEFAULT_LOGIN_URL 默认值链路不受影响
        self.assertEqual(session.login_url, DEFAULT_LOGIN_URL)

    def test_taobao_profile_injection_uses_taobao_profile_data(self) -> None:
        session = GoofishLoginSession(profile=TAOBAO_PROFILE)
        self.assertIs(session._profile, TAOBAO_PROFILE)
        self.assertEqual(
            session.login_url, "https://login.taobao.com/member/login.jhtml"
        )
        self.assertEqual(
            session._profile.login_status_api_markers,
            ("mtop.user.getusersimple",),
        )
        self.assertFalse(session._profile.quick_login_enabled)
        # auth / captcha 判定取自淘宝档案钩子
        self.assertTrue(
            session._profile.is_auth_url(
                "https://login.taobao.com/member/login.jhtml"
            )
        )
        self.assertFalse(
            session._profile.is_auth_url(
                "https://passport.goofish.com/mini_login.htm"
            )
        )

    def test_explicit_login_url_overrides_profile_login_url(self) -> None:
        session = GoofishLoginSession(
            profile=TAOBAO_PROFILE,
            login_url="https://example.com/custom-login",
        )
        self.assertEqual(session.login_url, "https://example.com/custom-login")
        # 缺省 profile 时显式 login_url 也优先生效（旧调用方式）
        legacy = GoofishLoginSession(login_url="https://example.com/legacy")
        self.assertEqual(legacy.login_url, "https://example.com/legacy")
        self.assertIs(legacy._profile, GOOFISH_PROFILE)


class MatchLoginStatusApiTests(unittest.TestCase):
    """任务 6.2：_match_login_status_api 大小写兼容。"""

    def test_matches_camelcase_api_param_for_taobao_marker(self) -> None:
        url = (
            "https://h5api.m.taobao.com/h5/mtop.user.getusersimple/1.0/"
            "?jsv=2.7.2&appKey=12574478&t=123&api=mtop.user.getUserSimple&v=1.0"
        )
        self.assertEqual(
            _match_login_status_api(url, TAOBAO_PROFILE.login_status_api_markers),
            "mtop.user.getusersimple",
        )

    def test_default_markers_remain_goofish_scoped(self) -> None:
        goofish_url = (
            "https://h5api.m.goofish.com/h5/mtop.taobao.idlemessage.pc.loginuser.get/1.0/"
            "?api=mtop.taobao.idlemessage.pc.loginuser.get"
        )
        self.assertEqual(
            _match_login_status_api(goofish_url),
            "mtop.taobao.idlemessage.pc.loginuser.get",
        )
        # 缺省（goofish）标记不会命中淘宝接口
        self.assertIsNone(
            _match_login_status_api(
                "https://h5api.m.taobao.com/h5/x/1.0/?api=mtop.user.getUserSimple"
            )
        )


class LocalAuthSessionControllerPlatformTests(unittest.TestCase):
    """任务 6.3：controller 平台化的路径解析。"""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.base_dir = Path(self._temp_dir.name)

    def test_taobao_platform_resolves_taobao_paths_and_profile(self) -> None:
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings, platform="taobao")
        self.assertEqual(controller.platform, PLATFORM_TAOBAO)
        self.assertIs(controller._profile, TAOBAO_PROFILE)
        self.assertEqual(
            controller._resolve_storage_state_path(),
            self.base_dir / "storage_state.taobao.json",
        )
        self.assertEqual(
            controller._resolve_stable_profile_dir(),
            self.base_dir / "browser_profile_taobao",
        )

    def test_goofish_default_paths_unchanged(self) -> None:
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings)
        self.assertEqual(controller.platform, PLATFORM_GOOFISH)
        self.assertIs(controller._profile, GOOFISH_PROFILE)
        self.assertEqual(
            controller._resolve_storage_state_path(),
            self.base_dir / "storage_state.json",
        )
        # playwright_user_data_dir=None 时稳定目录为 None（仅 storage_state）
        self.assertIsNone(controller._resolve_stable_profile_dir())

        settings_with_profile = replace(
            settings,
            playwright_user_data_dir=self.base_dir / "browser_profile",
        )
        controller_with_profile = LocalAuthSessionController(settings_with_profile)
        self.assertEqual(
            controller_with_profile._resolve_stable_profile_dir(),
            self.base_dir / "browser_profile",
        )

    def test_unknown_platform_raises_value_error(self) -> None:
        settings = build_settings(self.base_dir)
        with self.assertRaises(ValueError):
            LocalAuthSessionController(settings, platform="jd")

    def test_probe_url_judged_by_profile_base_url(self) -> None:
        settings = build_settings(self.base_dir)
        goofish_controller = LocalAuthSessionController(settings)
        self.assertTrue(
            goofish_controller._looks_like_logged_in_probe_url(
                "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC"
            )
        )
        self.assertFalse(
            goofish_controller._looks_like_logged_in_probe_url(
                "https://passport.goofish.com/mini_login.htm"
            )
        )

        taobao_controller = LocalAuthSessionController(settings, platform="taobao")
        self.assertTrue(
            taobao_controller._looks_like_logged_in_probe_url(
                "https://www.taobao.com"
            )
        )
        self.assertFalse(
            taobao_controller._looks_like_logged_in_probe_url(
                "https://login.taobao.com/member/login.jhtml"
            )
        )
        # 淘宝 controller 不再把闲鱼页面当作自己的已登录探测页
        self.assertFalse(
            taobao_controller._looks_like_logged_in_probe_url(
                "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC"
            )
        )


class CoordinatorPlatformFlowTests(unittest.IsolatedAsyncioTestCase):
    """任务 6.4：coordinator 按平台分 flow。"""

    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    def _build_coordinator(
        self,
    ) -> tuple[
        RemoteAuthRecoveryCoordinator,
        _StubContext,
        _StubAuthController,
        _StubAuthController,
    ]:
        context = _StubContext()
        goofish_controller = _StubAuthController(session_prefix="goofish")
        taobao_controller = _StubAuthController(session_prefix="taobao")
        coordinator = RemoteAuthRecoveryCoordinator(
            context=context,
            settings=build_settings(self.base_dir),
            auth_controller=goofish_controller,
            auth_timeout_sec=60,
        )
        coordinator.set_auth_controller("taobao", taobao_controller)
        return coordinator, context, goofish_controller, taobao_controller

    async def test_taobao_auth_failure_uses_taobao_controller_and_wording(
        self,
    ) -> None:
        coordinator, context, goofish_controller, taobao_controller = (
            self._build_coordinator()
        )

        message = await coordinator.handle_provider_auth_failure(
            umo="umo-1",
            sub_id=11,
            platform="taobao",
        )

        # 走淘宝 controller，goofish controller 未被触碰
        self.assertEqual(taobao_controller.start_calls, [False])
        self.assertEqual(goofish_controller.start_calls, [])
        # 文案带平台显示名，不再出现 /闲鱼 登录 提示
        self.assertEqual(
            message,
            "已向当前会话发送淘宝登录二维码，扫码登录后回复任意消息即可继续。",
        )
        self.assertEqual(len(context.sent), 1)
        umo, chain = context.sent[0]
        self.assertEqual(umo, "umo-1")
        chain_text = "\n".join(chain.texts)
        self.assertIn("检测到需要重新登录淘宝。", chain_text)
        self.assertNotIn("/闲鱼 登录", chain_text)
        self.assertIn("淘宝登录工具", chain_text)
        # flow 注册在 taobao 键下，goofish 无 flow
        self.assertIn("taobao", coordinator._active_flows)
        self.assertNotIn("goofish", coordinator._active_flows)
        self.assertTrue(coordinator.has_active_flow())
        await coordinator.close()

    async def test_platform_flows_are_independent(self) -> None:
        coordinator, _context, goofish_controller, taobao_controller = (
            self._build_coordinator()
        )

        await coordinator.handle_provider_auth_failure(umo="umo-g", sub_id=1)
        await coordinator.handle_provider_auth_failure(
            umo="umo-t", sub_id=2, platform="taobao"
        )

        self.assertEqual(goofish_controller.start_calls, [False])
        self.assertEqual(taobao_controller.start_calls, [False])
        self.assertEqual(
            set(coordinator._active_flows), {"goofish", "taobao"}
        )
        # umo-t 的任意回复应对其淘宝 flow 生效
        self.assertTrue(
            await coordinator.should_auto_complete_from_message(
                umo="umo-t", message_text="好了，继续"
            )
        )

        # 取消淘宝 flow 不影响闲鱼 flow
        cancel_message = await coordinator.cancel_login(umo="umo-t")
        self.assertEqual(cancel_message, "已取消当前登录恢复流程。")
        self.assertEqual(taobao_controller.cancel_calls, ["taobao-1"])
        self.assertEqual(goofish_controller.cancel_calls, [])
        self.assertEqual(set(coordinator._active_flows), {"goofish"})

        cancel_message = await coordinator.cancel_login(umo="umo-g")
        self.assertEqual(cancel_message, "已取消当前登录恢复流程。")
        self.assertEqual(goofish_controller.cancel_calls, ["goofish-1"])
        self.assertFalse(coordinator.has_active_flow())
        await coordinator.close()

    async def test_complete_login_resumes_only_same_platform_subscriptions(
        self,
    ) -> None:
        storage = SubscriptionStorage(self.base_dir / "platform_auth.db")
        await storage.initialize()
        try:
            goofish_sub, _ = await storage.upsert_subscription(
                umo="umo-1",
                keyword="goofish-sub",
                interval_sec=600,
                pages=1,
                recommend_max_price=None,
                drop_abs=50.0,
                drop_pct=0.05,
                new_window_sec=1800,
                cooldown_sec=21600,
            )
            taobao_sub, _ = await storage.upsert_subscription(
                umo="umo-1",
                keyword="taobao-sub",
                interval_sec=600,
                pages=1,
                recommend_max_price=None,
                drop_abs=50.0,
                drop_pct=0.05,
                new_window_sec=1800,
                cooldown_sec=21600,
                platform="taobao",
            )
            await storage.pause_subscription(goofish_sub.id, "AUTH_REQUIRED")
            await storage.pause_subscription(taobao_sub.id, "AUTH_REQUIRED")

            coordinator, _context, goofish_controller, taobao_controller = (
                self._build_coordinator()
            )
            await coordinator.handle_provider_auth_failure(
                umo="umo-1",
                sub_id=taobao_sub.id,
                platform="taobao",
            )

            result = await coordinator.complete_login(
                umo="umo-1",
                storage=storage,
                scheduler=None,
            )

            # 淘宝 controller 完成确认；goofish controller 未参与
            self.assertEqual(taobao_controller.confirm_calls, ["taobao-1"])
            self.assertEqual(goofish_controller.confirm_calls, [])
            self.assertIn("淘宝登录态已保存。", result)
            self.assertIn("已恢复订阅：1", result)

            # 只有淘宝订阅被恢复；闲鱼订阅保持 AUTH_REQUIRED 暂停
            goofish_after = await storage.get_subscription("umo-1", "goofish-sub")
            taobao_after = await storage.get_subscription(
                "umo-1", "taobao-sub", "taobao"
            )
            self.assertIsNotNone(goofish_after)
            self.assertIsNotNone(taobao_after)
            self.assertFalse(goofish_after.enabled)
            self.assertEqual(goofish_after.paused_reason, "AUTH_REQUIRED")
            self.assertTrue(taobao_after.enabled)
            self.assertIsNone(taobao_after.paused_reason)
            self.assertFalse(coordinator.has_active_flow())
            await coordinator.close()
        finally:
            await storage.close()


class StorageResumePlatformFilterTests(unittest.IsolatedAsyncioTestCase):
    """storage.resume_subscriptions_by_pause_reasons 的可选平台过滤。"""

    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)
        self.storage = SubscriptionStorage(self.base_dir / "resume_filter.db")
        await self.storage.initialize()

    async def _cleanup_temp_dir(self) -> None:
        await self.storage.close()
        self._temp_dir.cleanup()

    async def _create_paused_subs(self) -> tuple[int, int]:
        goofish_sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword="goofish-sub",
            interval_sec=600,
            pages=1,
            recommend_max_price=None,
            drop_abs=50.0,
            drop_pct=0.05,
            new_window_sec=1800,
            cooldown_sec=21600,
        )
        taobao_sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword="taobao-sub",
            interval_sec=600,
            pages=1,
            recommend_max_price=None,
            drop_abs=50.0,
            drop_pct=0.05,
            new_window_sec=1800,
            cooldown_sec=21600,
            platform="taobao",
        )
        await self.storage.pause_subscription(goofish_sub.id, "AUTH_REQUIRED")
        await self.storage.pause_subscription(taobao_sub.id, "AUTH_REQUIRED")
        return goofish_sub.id, taobao_sub.id

    async def test_platform_filter_scopes_resume(self) -> None:
        await self._create_paused_subs()

        resumed = await self.storage.resume_subscriptions_by_pause_reasons(
            ("AUTH_REQUIRED", "CAPTCHA"),
            now_ts=1234567890,
            platform="taobao",
        )

        self.assertEqual([sub.keyword for sub in resumed], ["taobao-sub"])
        # 恢复出的订阅保留真实平台归属
        self.assertEqual(resumed[0].platform, "taobao")
        goofish_after = await self.storage.get_subscription("umo-1", "goofish-sub")
        self.assertFalse(goofish_after.enabled)
        self.assertEqual(goofish_after.paused_reason, "AUTH_REQUIRED")

    async def test_default_without_platform_resumes_all(self) -> None:
        await self._create_paused_subs()

        resumed = await self.storage.resume_subscriptions_by_pause_reasons(
            ("AUTH_REQUIRED", "CAPTCHA"),
            now_ts=1234567890,
        )

        # 不传 platform = 旧行为：全平台恢复（main.py 自动登录恢复链路依赖）
        self.assertEqual(
            {sub.keyword for sub in resumed}, {"goofish-sub", "taobao-sub"}
        )


class ProviderQuickLoginGateTests(unittest.IsolatedAsyncioTestCase):
    """任务 6.5：provider._try_quick_login 在 TAOBAO_PROFILE 下短路。"""

    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_try_quick_login_disabled_for_taobao_profile(self) -> None:
        class _ExplodingPage:
            def __getattr__(self, name):
                raise AssertionError(f"page must not be touched: {name}")

        provider = PlaywrightSearchProvider(
            build_settings(self.base_dir),
            profile=TAOBAO_PROFILE,
        )

        result = await provider._try_quick_login(_ExplodingPage(), object())

        self.assertFalse(result)
        # 档案开关本身：goofish 保持启用，淘宝禁用
        self.assertTrue(GOOFISH_PROFILE.quick_login_enabled)
        self.assertFalse(TAOBAO_PROFILE.quick_login_enabled)


if __name__ == "__main__":
    unittest.main()
