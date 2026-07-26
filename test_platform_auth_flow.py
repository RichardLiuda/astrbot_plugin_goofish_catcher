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
    # 真实 astrbot 可导入时不装桩：直接赋值会顶掉真模块，污染全量 discover 中
    # 后续加载的测试（如 test_reply_favorite）。仅裸环境装桩，且一律 setdefault。
    try:
        import astrbot.api.message_components  # noqa: F401

        return
    except ImportError:
        pass

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
    sys.modules.setdefault("astrbot.api", astrbot_api_module)
    sys.modules.setdefault("astrbot.api.star", astrbot_api_star_module)
    sys.modules.setdefault("astrbot.api.event", astrbot_api_event_module)
    sys.modules.setdefault(
        "astrbot.api.message_components", astrbot_api_message_components_module
    )


_install_astrbot_stubs()


def _chain_plain_texts(chain) -> list[str]:
    """兼容桩 MessageChain（.texts）与真实 MessageChain（.chain 内 Plain 组件）。"""
    texts = getattr(chain, "texts", None)
    if texts is not None:
        return list(texts)
    return [
        part.text
        for part in getattr(chain, "chain", [])
        if getattr(part, "text", None)
    ]

from app.auth_session import (
    LocalAuthSessionController,
    resolve_local_storage_state_path,
)
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

    def test_settings_platform_path_helpers_match_controller(self) -> None:
        """settings 收口的路径推导与 controller/build_providers 取值一致。"""
        settings = build_settings(self.base_dir)
        controller = LocalAuthSessionController(settings, platform="taobao")
        self.assertEqual(
            settings.storage_state_path_for(PLATFORM_TAOBAO),
            controller._resolve_storage_state_path(),
        )
        self.assertEqual(
            settings.browser_profile_dir_for(PLATFORM_TAOBAO),
            controller._resolve_stable_profile_dir(),
        )
        # goofish 走配置字段链路
        self.assertEqual(
            settings.storage_state_path_for(PLATFORM_GOOFISH),
            settings.playwright_storage_state_path,
        )
        self.assertEqual(
            settings.browser_profile_dir_for(PLATFORM_GOOFISH),
            settings.playwright_user_data_dir,
        )

    def test_resolve_local_storage_state_path_platform_suffix(self) -> None:
        self.assertEqual(
            resolve_local_storage_state_path().name, "storage_state.json"
        )
        self.assertEqual(
            resolve_local_storage_state_path("taobao").name,
            "storage_state.taobao.json",
        )

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
        chain_text = "\n".join(_chain_plain_texts(chain))
        self.assertIn("检测到需要重新登录淘宝。", chain_text)
        # 超时重启提示指向真实存在的带平台参数命令（不再是「淘宝登录工具」）
        self.assertIn("/闲鱼 登录 淘宝", chain_text)
        self.assertIn("/闲鱼 登录取消", chain_text)
        self.assertNotIn("登录工具", chain_text)
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

    async def test_restart_markers_resolve_platform(self) -> None:
        """restart 消息标记带平台后缀时路由到对应平台（无后缀 = goofish）。"""
        from app.remote_auth_recovery import LOGIN_RESTART_MARKERS

        self.assertIn("闲鱼 登录 淘宝", LOGIN_RESTART_MARKERS)
        self.assertIn("/闲鱼 登录 taobao", LOGIN_RESTART_MARKERS)
        resolve = RemoteAuthRecoveryCoordinator.resolve_restart_platform
        self.assertEqual(resolve("/闲鱼 登录"), PLATFORM_GOOFISH)
        self.assertEqual(resolve("闲鱼 登录"), PLATFORM_GOOFISH)
        self.assertEqual(resolve("闲鱼 登录 淘宝"), PLATFORM_TAOBAO)
        self.assertEqual(resolve("/闲鱼 登录 淘宝"), PLATFORM_TAOBAO)
        self.assertEqual(resolve("/Goofish Login Taobao"), PLATFORM_TAOBAO)
        # 非标记消息回落 goofish（仅在 should_restart 为 True 后调用）
        self.assertEqual(resolve("随便回复"), PLATFORM_GOOFISH)

        coordinator, _context, _goofish_controller, _taobao_controller = (
            self._build_coordinator()
        )
        await coordinator.handle_provider_auth_failure(
            umo="umo-1", sub_id=1, platform="taobao"
        )
        self.assertTrue(
            await coordinator.should_restart_login_from_message(
                umo="umo-1", message_text="/闲鱼 登录 淘宝"
            )
        )
        await coordinator.close()

    async def test_complete_login_multi_platform_flows_same_umo(self) -> None:
        """同一会话同时有两个平台 flow 时逐个确认：一败一成不再卡死。"""

        class _FailingConfirmController(_StubAuthController):
            async def confirm_auth_session(self, *, session_id: str):
                self.confirm_calls.append(session_id)
                raise RuntimeError("扫码后登录态仍未生效")

        class _StubResumeStorage:
            async def resume_subscriptions_by_pause_reasons(
                self, reasons, *, now_ts, platform=None
            ):
                return []

        context = _StubContext()
        goofish_controller = _FailingConfirmController(session_prefix="goofish")
        taobao_controller = _StubAuthController(session_prefix="taobao")
        coordinator = RemoteAuthRecoveryCoordinator(
            context=context,
            settings=build_settings(self.base_dir),
            auth_controller=goofish_controller,
            auth_timeout_sec=60,
        )
        coordinator.set_auth_controller("taobao", taobao_controller)

        await coordinator.handle_provider_auth_failure(umo="umo-1", sub_id=1)
        await coordinator.handle_provider_auth_failure(
            umo="umo-1", sub_id=2, platform="taobao"
        )
        self.assertEqual(len(coordinator._active_flows), 2)

        result = await coordinator.complete_login(
            umo="umo-1",
            storage=_StubResumeStorage(),
            scheduler=None,
        )

        # 两个 flow 都被尝试确认；淘宝成功、闲鱼失败但不吞掉成功结果
        self.assertEqual(goofish_controller.confirm_calls, ["goofish-1"])
        self.assertEqual(taobao_controller.confirm_calls, ["taobao-1"])
        self.assertIn("淘宝登录态已保存。", result)
        self.assertIn("登录确认失败", result)
        # 失败的 goofish flow 保留（可重扫再确认），成功的淘宝 flow 清除
        self.assertIn(PLATFORM_GOOFISH, coordinator._active_flows)
        self.assertNotIn(PLATFORM_TAOBAO, coordinator._active_flows)
        # 保留的 flow 必须重新武装超时看门狗（否则成为永不超时的僵尸 flow，
        # 卡住 scheduler 的 wait_until_idle 且超时后无任何通知）
        self.assertIn(PLATFORM_GOOFISH, coordinator._timeout_tasks)
        await coordinator.close()

    async def test_expired_first_flow_does_not_block_live_second_flow_gating(
        self,
    ) -> None:
        """残留的过期 flow（dict 首位）不能挡住另一平台仍有效 flow 的确认。"""
        coordinator, _context, _goofish_controller, _taobao_controller = (
            self._build_coordinator()
        )
        await coordinator.handle_provider_auth_failure(umo="umo-1", sub_id=1)
        await coordinator.handle_provider_auth_failure(
            umo="umo-1", sub_id=2, platform="taobao"
        )
        # 人为把先插入的 goofish flow 置为已过期
        coordinator._active_flows[PLATFORM_GOOFISH].expires_at = time.time() - 1

        self.assertTrue(
            await coordinator.should_auto_complete_from_message(
                umo="umo-1", message_text="扫好了"
            )
        )
        self.assertTrue(
            await coordinator.should_restart_login_from_message(
                umo="umo-1", message_text="/闲鱼 登录 淘宝"
            )
        )
        await coordinator.close()

    async def test_cancel_login_isolates_per_flow_errors(self) -> None:
        """某平台 controller 取消失败不拦住其余平台，flow 状态一律清除。"""

        class _FailingCancelController(_StubAuthController):
            async def cancel_auth_session(self, *, session_id: str):
                self.cancel_calls.append(session_id)
                raise RuntimeError("controller cancel boom")

        context = _StubContext()
        goofish_controller = _FailingCancelController(session_prefix="goofish")
        taobao_controller = _StubAuthController(session_prefix="taobao")
        coordinator = RemoteAuthRecoveryCoordinator(
            context=context,
            settings=build_settings(self.base_dir),
            auth_controller=goofish_controller,
            auth_timeout_sec=60,
        )
        coordinator.set_auth_controller("taobao", taobao_controller)
        await coordinator.handle_provider_auth_failure(umo="umo-1", sub_id=1)
        await coordinator.handle_provider_auth_failure(
            umo="umo-1", sub_id=2, platform="taobao"
        )

        result = await coordinator.cancel_login(umo="umo-1")

        # goofish controller 抛异常，但淘宝仍被取消；两个 flow 都清除
        self.assertEqual(goofish_controller.cancel_calls, ["goofish-1"])
        self.assertEqual(taobao_controller.cancel_calls, ["taobao-1"])
        self.assertEqual(result, "已取消当前登录恢复流程。")
        self.assertFalse(coordinator.has_active_flow())
        await coordinator.close()

    async def test_cancel_login_single_flow_error_still_raises(self) -> None:
        """单 flow 全部取消失败时保持抛异常语义（调用方渲染取消失败）。"""

        class _FailingCancelController(_StubAuthController):
            async def cancel_auth_session(self, *, session_id: str):
                self.cancel_calls.append(session_id)
                raise RuntimeError("controller cancel boom")

        context = _StubContext()
        goofish_controller = _FailingCancelController(session_prefix="goofish")
        coordinator = RemoteAuthRecoveryCoordinator(
            context=context,
            settings=build_settings(self.base_dir),
            auth_controller=goofish_controller,
            auth_timeout_sec=60,
        )
        await coordinator.handle_provider_auth_failure(umo="umo-1", sub_id=1)

        with self.assertRaises(RuntimeError):
            await coordinator.cancel_login(umo="umo-1")
        # 抛错但 coordinator 状态已清除（不残留僵尸 flow）
        self.assertFalse(coordinator.has_active_flow())
        await coordinator.close()

    async def test_cancel_login_cancels_all_owned_flows(self) -> None:
        coordinator, _context, goofish_controller, taobao_controller = (
            self._build_coordinator()
        )
        await coordinator.handle_provider_auth_failure(umo="umo-1", sub_id=1)
        await coordinator.handle_provider_auth_failure(
            umo="umo-1", sub_id=2, platform="taobao"
        )

        result = await coordinator.cancel_login(umo="umo-1")

        self.assertEqual(result, "已取消当前登录恢复流程。")
        self.assertEqual(goofish_controller.cancel_calls, ["goofish-1"])
        self.assertEqual(taobao_controller.cancel_calls, ["taobao-1"])
        self.assertFalse(coordinator.has_active_flow())
        await coordinator.close()


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


class ProviderLoginProbeWatcherTests(unittest.IsolatedAsyncioTestCase):
    """check_login_state 的登录态接口 payload 监听（淘宝真实登录态探测）。"""

    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addAsyncCleanup(self._cleanup_temp_dir)
        self.base_dir = Path(self._temp_dir.name)

    async def _cleanup_temp_dir(self) -> None:
        self._temp_dir.cleanup()

    async def test_probe_watcher_classifies_marker_payloads(self) -> None:
        provider = PlaywrightSearchProvider(
            build_settings(self.base_dir),
            profile=TAOBAO_PROFILE,
        )
        handlers: dict[str, object] = {}

        class _FakePage:
            def on(self, event, handler):
                handlers[event] = handler

        states: set[str] = set()
        provider._attach_login_probe_watcher(_FakePage(), states)
        handler = handlers["response"]

        class _FakeResponse:
            def __init__(self, url, payload):
                self.url = url
                self._payload = payload

            async def json(self):
                return self._payload

        # 非登录态校验接口一律忽略
        await handler(
            _FakeResponse("https://s.taobao.com/other", {"ret": ["SUCCESS::ok"]})
        )
        self.assertEqual(states, set())

        # SESSION_EXPIRED → auth_required（URL 驼峰 api 名兼容）
        await handler(
            _FakeResponse(
                "https://h5api.m.taobao.com/h5/mtop.user.getUserSimple/1.0/",
                {"ret": ["FAIL_SYS_SESSION_EXPIRED::Session过期"]},
            )
        )
        self.assertEqual(states, {"auth_required"})

        # SUCCESS → ok
        states.clear()
        await handler(
            _FakeResponse(
                "https://h5api.m.taobao.com/h5/mtop.user.getusersimple/1.0/",
                {"ret": ["SUCCESS::调用成功"]},
            )
        )
        self.assertEqual(states, {"ok"})

    async def test_goofish_profile_has_no_probe_url(self) -> None:
        # goofish 无 validate_probe_url → check_login_state 维持 base_url 判定
        self.assertIsNone(GOOFISH_PROFILE.validate_probe_url)
        self.assertTrue(TAOBAO_PROFILE.validate_probe_url)

    async def test_taobao_is_auth_url_ignores_silent_login_probe(self) -> None:
        """login 域下 /newlogin/ 静默接口不是登录墙（AstrBot 实测：已登录页面
        例行触发 silentHasLogin.do，整域判定会把扫码成功误判 AUTH_REQUIRED）。"""
        is_auth = TAOBAO_PROFILE.is_auth_url
        self.assertFalse(
            is_auth(
                "https://login.taobao.com/newlogin/silentHasLogin.do"
                "?documentReferer=https%3A%2F%2Fs.taobao.com%2Fsearch&ltl=true"
            )
        )
        self.assertFalse(is_auth("https://login.taobao.com/newlogin/qrcode/generate.do"))
        # 真登录墙（文档跳转登录页）与 passport 域仍判定为 auth
        self.assertTrue(is_auth("https://login.taobao.com/member/login.jhtml"))
        self.assertTrue(is_auth("https://passport.taobao.com/iv/verify.htm"))
        self.assertFalse(is_auth("https://www.taobao.com/"))
        self.assertFalse(is_auth("https://s.taobao.com/search?q=x"))


if __name__ == "__main__":
    unittest.main()
