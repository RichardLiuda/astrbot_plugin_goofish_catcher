from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace


# 真实 astrbot 可导入时不装桩：直接赋值会顶掉真模块，污染全量 discover 中
# 后续加载的测试（如 test_reply_favorite）。仅裸环境装桩，且一律 setdefault。
try:
    import astrbot.api.message_components  # noqa: F401
except ImportError:
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
    astrbot_api_event_module.MessageChain = object
    astrbot_api_message_components_module = types.ModuleType("astrbot.api.message_components")
    astrbot_api_message_components_module.Image = object
    astrbot_api_message_components_module.Plain = object

    class _Reply:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    astrbot_api_message_components_module.Reply = _Reply

    sys.modules.setdefault("astrbot", astrbot_module)
    sys.modules.setdefault("astrbot.api", astrbot_api_module)
    sys.modules.setdefault("astrbot.api.star", astrbot_api_star_module)
    sys.modules.setdefault("astrbot.api.event", astrbot_api_event_module)
    sys.modules.setdefault(
        "astrbot.api.message_components", astrbot_api_message_components_module
    )

try:
    import httpx as _httpx  # noqa: F401
except ModuleNotFoundError:
    httpx_module = types.ModuleType("httpx")
    httpx_module.AsyncClient = object
    sys.modules.setdefault("httpx", httpx_module)

from dataclasses import asdict

from app.admin_service import AdminService
from app.config import PluginSettings
from app.platforms.goofish import GOOFISH_PROFILE
from app.platforms.taobao import TAOBAO_PROFILE
from app.provider import build_providers
from app.provider_playwright import PlaywrightSearchProvider
from app.provider_remote import RemoteSearchProvider
from app.scheduler import MonitoringScheduler
from app.storage import SubscriptionStorage
from app.types import (
    DeepAnalysisResult,
    NormalizedItem,
    RecommendationCandidate,
    RecommendationResult,
    Subscription,
)

# main.py 是相对导入 + Star 基类，只能在真实 astrbot 环境中加载；
# 裸环境下集成层用例自动跳过，不影响单文件运行。
try:
    import astrbot.core.star  # noqa: F401

    _HAS_REAL_ASTRBOT = True
except ImportError:
    _HAS_REAL_ASTRBOT = False


def build_settings(
    base_dir: Path,
    *,
    provider_mode: str = "playwright_local",
    remote_base_url: str | None = None,
    taobao_enabled: bool = False,
) -> PluginSettings:
    return PluginSettings(
        plugin_name="goofish_worker",
        plugin_data_dir=base_dir,
        db_path=base_dir / "goofish_catcher.db",
        provider_mode=provider_mode,
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
        remote_base_url=remote_base_url,
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
        taobao_enabled=taobao_enabled,
    )


class FakeProvider:
    def __init__(self) -> None:
        self.search_keywords: list[str] = []
        self.analyzed_item_ids: list[str] = []

    async def search(self, *, keyword, pages, timeout_sec, filters=None, **_):
        self.search_keywords.append(keyword)
        return []

    async def analyze_item_detail(self, *, item, timeout_sec):
        self.analyzed_item_ids.append(item.item_id)
        return DeepAnalysisResult(
            item_id=item.item_id,
            analyzed_at=1700000000,
            status="ok",
            credit_status="good",
            credit_reason="fake",
            summary="fake",
            risk="",
            image_urls=[],
        )

    async def close(self) -> None:
        return None


class StubNotifier:
    def __init__(self) -> None:
        self.alerts: list[dict] = []

    async def send_alert(self, *, umo, keyword, code, message, action_hint=None):
        self.alerts.append(
            {
                "umo": umo,
                "keyword": keyword,
                "code": code,
                "message": message,
                "action_hint": action_hint,
            }
        )
        return True

    async def send_recommendation_summary(self, *, umo, recommendation):
        return True


class StubRecommender:
    async def prefilter_items(self, *, umo, keyword, items):
        return list(items), "PASS"

    async def analyze(self, *, umo, keyword, candidates, top_k=None, recommend_max_price=None):
        return SimpleNamespace(top=[])


class StubActivityMonitor:
    async def start_task(self, **kwargs) -> str:
        return "task-stub"

    async def update_task(self, task_id, **kwargs) -> None:
        return None

    async def finish_task(self, task_id) -> None:
        return None


class BuildProvidersTest(unittest.TestCase):
    def test_taobao_enabled_local_builds_both_providers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = build_settings(Path(tmpdir), taobao_enabled=True)
            providers = build_providers(settings)

            self.assertEqual(set(providers), {"goofish", "taobao"})
            self.assertIs(providers["goofish"]._profile, GOOFISH_PROFILE)

            taobao = providers["taobao"]
            self.assertIsInstance(taobao, PlaywrightSearchProvider)
            self.assertIs(taobao._profile, TAOBAO_PROFILE)
            self.assertEqual(
                taobao.settings.playwright_storage_state_path.name,
                "storage_state.taobao.json",
            )
            self.assertEqual(
                taobao.settings.playwright_user_data_dir.name,
                "browser_profile_taobao",
            )

    def test_taobao_disabled_builds_goofish_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = build_settings(Path(tmpdir), taobao_enabled=False)
            providers = build_providers(settings)
            self.assertEqual(set(providers), {"goofish"})

    def test_remote_mode_skips_taobao(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = build_settings(
                Path(tmpdir),
                provider_mode="remote_rest",
                remote_base_url="http://127.0.0.1:9",
                taobao_enabled=True,
            )
            providers = build_providers(settings)
            self.assertEqual(set(providers), {"goofish"})
            self.assertIsInstance(providers["goofish"], RemoteSearchProvider)


class DetailAnalysisShortCircuitTest(unittest.IsolatedAsyncioTestCase):
    async def test_taobao_detail_hook_wired_and_safe_without_browser(self) -> None:
        # 1.3 起淘宝支持详情分析：profile 必须接好钩子；
        # 垃圾 HTML 直接调钩子也必须安全返回保守结果（不抛异常、无需浏览器）。
        self.assertTrue(TAOBAO_PROFILE.supports_item_detail)
        self.assertIsNotNone(TAOBAO_PROFILE.parse_detail_page)

        item = NormalizedItem(item_id="taobao:1", title="t", price=1.0, url="u")
        result = TAOBAO_PROFILE.parse_detail_page("<html>no data here</html>", [], item)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.credit_status, "unknown")
        self.assertEqual(result.item_id, "taobao:1")


class SchedulerPlatformRoutingTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self._tmpdir.name)
        self.storage = SubscriptionStorage(self.base_dir / "test.db")
        await self.storage.initialize()
        self.notifier = StubNotifier()

    async def asyncTearDown(self) -> None:
        await self.storage.close()
        self._tmpdir.cleanup()

    def _make_scheduler(self, provider) -> MonitoringScheduler:
        return MonitoringScheduler(
            context=object(),
            settings=build_settings(self.base_dir),
            storage=self.storage,
            provider=provider,
            notifier=self.notifier,
            recommender=StubRecommender(),
            activity_monitor=StubActivityMonitor(),
            remote_auth_coordinator=None,
        )

    async def _upsert_sub(self, keyword: str, platform: str):
        sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword=keyword,
            interval_sec=3600,
            pages=1,
            recommend_max_price=None,
            drop_abs=100.0,
            drop_pct=0.1,
            new_window_sec=86400,
            cooldown_sec=3600,
            platform=platform,
        )
        return sub

    async def test_constructor_normalizes_single_provider(self) -> None:
        fake = FakeProvider()
        scheduler = self._make_scheduler(fake)
        self.assertEqual(scheduler._providers, {"goofish": fake})
        self.assertIs(scheduler.provider, fake)

    async def test_process_subscription_routes_per_platform(self) -> None:
        fake_goofish = FakeProvider()
        fake_taobao = FakeProvider()
        scheduler = self._make_scheduler(
            {"goofish": fake_goofish, "taobao": fake_taobao}
        )

        sub_goofish = await self._upsert_sub("macmini", "goofish")
        sub_taobao = await self._upsert_sub("iphone", "taobao")

        await scheduler._process_subscription(sub_goofish, 0)
        await scheduler._process_subscription(sub_taobao, 0)

        self.assertEqual(fake_goofish.search_keywords, ["macmini"])
        self.assertEqual(fake_taobao.search_keywords, ["iphone"])

    async def test_platform_unavailable_pauses_subscription(self) -> None:
        fake_goofish = FakeProvider()
        scheduler = self._make_scheduler({"goofish": fake_goofish})
        sub = await self._upsert_sub("iphone", "taobao")

        await scheduler._process_subscription(sub, 0)

        updated = await self.storage.get_subscription_by_id(sub.id)
        self.assertIsNotNone(updated)
        assert updated is not None
        self.assertFalse(updated.enabled)
        self.assertEqual(updated.paused_reason, "PLATFORM_UNAVAILABLE")
        self.assertEqual(fake_goofish.search_keywords, [])
        self.assertTrue(
            any(alert["code"] == "PLATFORM_UNAVAILABLE" for alert in self.notifier.alerts)
        )

    async def test_deep_analysis_routes_by_item_platform(self) -> None:
        fake_goofish = FakeProvider()
        fake_taobao = FakeProvider()
        scheduler = self._make_scheduler(
            {"goofish": fake_goofish, "taobao": fake_taobao}
        )
        candidate = RecommendationCandidate(
            event_type="NEW",
            keyword="iphone",
            item_id="taobao:123",
            title="t",
            price=1.0,
            url="u",
            publish_time=None,
            observed_at=1700000000,
            payload_hash="h1",
        )
        kept = await scheduler.deep_analyze_candidates([candidate])
        self.assertEqual(fake_taobao.analyzed_item_ids, ["taobao:123"])
        self.assertEqual(fake_goofish.analyzed_item_ids, [])
        self.assertEqual(len(kept), 1)
        self.assertIsNotNone(kept[0].deep_analysis)

    async def test_deep_analysis_skipped_when_platform_unavailable(self) -> None:
        fake_goofish = FakeProvider()
        scheduler = self._make_scheduler({"goofish": fake_goofish})
        candidate = RecommendationCandidate(
            event_type="NEW",
            keyword="iphone",
            item_id="taobao:123",
            title="t",
            price=1.0,
            url="u",
            publish_time=None,
            observed_at=1700000000,
            payload_hash="h1",
        )
        kept = await scheduler.deep_analyze_candidates([candidate])
        # 候选保留，深度分析留 None，且不调用任何 provider
        self.assertEqual(len(kept), 1)
        self.assertIsNone(kept[0].deep_analysis)
        self.assertEqual(fake_goofish.analyzed_item_ids, [])


def _make_subscription(sub_id: int, keyword: str, platform: str) -> Subscription:
    return Subscription(
        id=sub_id,
        umo="umo-1",
        keyword=keyword,
        interval_sec=3600,
        pages=1,
        recommend_max_price=None,
        drop_abs=100.0,
        drop_pct=0.1,
        new_window_sec=86400,
        cooldown_sec=3600,
        enabled=True,
        paused_reason=None,
        last_run_at=None,
        next_run_at=None,
        consecutive_failures=0,
        platform=platform,
    )


def _async_value(value):
    async def _call(*args, **kwargs):
        return value

    return _call


class AdminServicePlatformGuardTest(unittest.IsolatedAsyncioTestCase):
    """admin_service 平台守卫：平台缺 provider 时明确报错，绝不回退 goofish。"""

    async def test_manual_check_platform_unavailable_never_falls_back(self) -> None:
        fake_goofish = FakeProvider()
        plugin = SimpleNamespace(
            _provider_error=None,
            providers={"goofish": fake_goofish},
            provider=fake_goofish,
            storage=None,
        )
        service = AdminService(plugin)

        with self.assertRaises(RuntimeError) as ctx:
            await service._run_manual_subscription_check(
                _make_subscription(1, "iphone", "taobao")
            )

        self.assertIn("PLATFORM_UNAVAILABLE", str(ctx.exception))
        self.assertIn("淘宝", str(ctx.exception))
        # 绝不回退 goofish：闲鱼 provider 未被搜索
        self.assertEqual(fake_goofish.search_keywords, [])

    async def test_trigger_deep_search_platform_unavailable(self) -> None:
        fake_goofish = FakeProvider()
        summary = SimpleNamespace(title="t", price=1.0, url="u", publish_time=None)
        plugin = SimpleNamespace(
            _provider_error=None,
            providers={"goofish": fake_goofish},
            provider=fake_goofish,
            storage=SimpleNamespace(get_item_summary=_async_value(summary)),
        )
        service = AdminService(plugin)

        with self.assertRaises(RuntimeError) as ctx:
            await service.trigger_deep_search("taobao:812345")

        self.assertIn("淘宝", str(ctx.exception))
        # 绝不硬用 goofish provider 打开淘宝详情页
        self.assertEqual(fake_goofish.analyzed_item_ids, [])

    def test_subscription_summary_includes_platform(self) -> None:
        service = AdminService(SimpleNamespace())
        payload = asdict(
            service._to_subscription_summary(_make_subscription(7, "kw", "taobao"))
        )
        self.assertEqual(payload["platform"], "taobao")


def _load_plugin_main():
    """以包上下文加载 main.py（内部是相对导入），不污染顶层 app.* 模块。"""
    import importlib

    pkg_name = "_gf_integration_pkg"
    mod_name = f"{pkg_name}.main"
    if mod_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(Path(__file__).resolve().parent)]
        sys.modules.setdefault(pkg_name, pkg)
        importlib.import_module(mod_name)
    return sys.modules[mod_name]


class _ResultRecommender:
    async def analyze(
        self, *, umo, keyword, candidates, top_k=None, recommend_max_price=None
    ):
        return RecommendationResult(
            keyword=keyword,
            summary="s",
            top=[],
            total_candidates=len(candidates),
            used_llm=False,
        )


class _ImmediateFakeScheduler:
    running = True

    def __init__(self) -> None:
        self.acquired: list[int] = []
        self.released: list[int] = []
        self.enqueued: list[int] = []

    async def try_acquire_subscription(self, sub_id):
        self.acquired.append(sub_id)
        return True

    async def release_subscription(self, sub_id):
        self.released.append(sub_id)

    async def process_manual_fetch(self, *, sub, items, now_ts):
        return [], 0

    async def persist_notifications(self, **kwargs):
        return None

    async def enqueue_manual_check(self, sub_id):
        self.enqueued.append(sub_id)
        return True


@unittest.skipUnless(_HAS_REAL_ASTRBOT, "main.py 需要真实 astrbot 才能加载")
class MainIntegrationPlatformRoutingTest(unittest.IsolatedAsyncioTestCase):
    """main.py 集成层的平台路由回归（立即检查 / 心跳 / 自动登录恢复 / 列表 / 深度分析）。"""

    async def asyncSetUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self._tmpdir.name)
        self.storage = SubscriptionStorage(self.base_dir / "main_integration.db")
        await self.storage.initialize()
        self.main_mod = _load_plugin_main()

        plugin_cls = self.main_mod.GoofishCatcherPlugin

        class _TestPlugin(plugin_cls):
            def __init__(inner) -> None:  # 跳过 Star.__init__，只装配测试所需字段
                pass

        self.fake_goofish = FakeProvider()
        self.plugin = _TestPlugin()
        self.plugin.settings = build_settings(self.base_dir)
        self.plugin.storage = self.storage
        self.plugin.providers = {"goofish": self.fake_goofish}
        self.plugin.provider = self.fake_goofish
        self.plugin.scheduler = _ImmediateFakeScheduler()
        self.plugin.recommender = _ResultRecommender()
        self.plugin._provider_error = None
        self.plugin._ready = True

    async def asyncTearDown(self) -> None:
        await self.storage.close()
        self._tmpdir.cleanup()

    async def _upsert_sub(self, keyword: str, platform: str):
        sub, _ = await self.storage.upsert_subscription(
            umo="umo-1",
            keyword=keyword,
            interval_sec=3600,
            pages=1,
            recommend_max_price=None,
            drop_abs=100.0,
            drop_pct=0.1,
            new_window_sec=86400,
            cooldown_sec=3600,
            platform=platform,
        )
        return sub

    async def test_immediate_check_platform_unavailable_never_falls_back(self) -> None:
        sub = await self._upsert_sub("iphone", "taobao")

        with self.assertRaises(RuntimeError) as ctx:
            await self.plugin._run_immediate_subscription_check(umo="umo-1", sub=sub)

        self.assertIn("淘宝", str(ctx.exception))
        self.assertIn("不可用", str(ctx.exception))
        # 绝不回退 goofish：淘宝订阅的关键词不能拿去搜闲鱼
        self.assertEqual(self.fake_goofish.search_keywords, [])

    async def test_immediate_check_goofish_uses_goofish_provider(self) -> None:
        sub = await self._upsert_sub("macmini", "goofish")

        recommendation = await self.plugin._run_immediate_subscription_check(
            umo="umo-1", sub=sub
        )

        self.assertEqual(self.fake_goofish.search_keywords, ["macmini"])
        self.assertEqual(recommendation.keyword, "macmini")
        self.assertEqual(self.plugin.scheduler.released, [sub.id])

    async def test_check_now_batch_reports_platform_unavailable(self) -> None:
        await self._upsert_sub("macmini", "goofish")
        await self._upsert_sub("iphone", "taobao")
        event = SimpleNamespace(
            unified_msg_origin="umo-1",
            plain_result=lambda text: text,
        )

        outputs = [chunk async for chunk in self.plugin.check_now(event, keyword="")]

        self.assertEqual(len(outputs), 1)
        text = outputs[0]
        self.assertIn("平台「淘宝」当前不可用", text)
        # 淘宝订阅的关键词绝未搜闲鱼；goofish 订阅正常执行
        self.assertEqual(self.fake_goofish.search_keywords, ["macmini"])

    async def test_resume_after_auto_login_scoped_to_platform(self) -> None:
        sub_g = await self._upsert_sub("macmini", "goofish")
        sub_t = await self._upsert_sub("iphone", "taobao")
        await self.storage.pause_subscription(sub_g.id, "AUTH_REQUIRED")
        await self.storage.pause_subscription(sub_t.id, "AUTH_REQUIRED")

        message = await self.plugin._resume_subs_after_auto_login()

        self.assertIn("已恢复订阅 1 个", message)
        goofish_after = await self.storage.get_subscription("umo-1", "macmini")
        taobao_after = await self.storage.get_subscription(
            "umo-1", "iphone", "taobao"
        )
        self.assertTrue(goofish_after.enabled)
        # 闲鱼快速登录不能恢复淘宝的 AUTH_REQUIRED 暂停
        self.assertFalse(taobao_after.enabled)
        self.assertEqual(taobao_after.paused_reason, "AUTH_REQUIRED")

    async def test_heartbeat_pause_scopes_to_goofish(self) -> None:
        await self._upsert_sub("macmini", "goofish")
        await self._upsert_sub("iphone", "taobao")

        class _AuthExpiredProvider(FakeProvider):
            async def check_login_state(self, *, timeout_sec=15):
                return "auth_required"

        recovery_calls: list[dict] = []

        class _FakeCoordinator:
            async def handle_provider_auth_failure(self, **kwargs):
                recovery_calls.append(kwargs)
                return None

        class _FakeNotifier:
            async def broadcast_alert(self, **kwargs):
                return None

        self.plugin.provider = _AuthExpiredProvider()
        self.plugin.remote_auth_coordinator = _FakeCoordinator()
        self.plugin.notifier = _FakeNotifier()

        await self.plugin._run_heartbeat_probe()

        goofish_after = await self.storage.get_subscription("umo-1", "macmini")
        taobao_after = await self.storage.get_subscription(
            "umo-1", "iphone", "taobao"
        )
        self.assertFalse(goofish_after.enabled)
        self.assertEqual(goofish_after.paused_reason, "AUTH_REQUIRED")
        # 心跳只探测 goofish，淘宝订阅不能被连坐暂停
        self.assertTrue(taobao_after.enabled)
        self.assertEqual(len(recovery_calls), 1)

    async def test_list_subscriptions_prefix_only_for_non_goofish(self) -> None:
        sub_g = await self._upsert_sub("macmini", "goofish")
        await self._upsert_sub("iphone", "taobao")
        event = SimpleNamespace(
            unified_msg_origin="umo-1",
            plain_result=lambda text: text,
        )

        outputs = [
            chunk async for chunk in self.plugin.list_subscriptions(event)
        ]

        self.assertEqual(len(outputs), 1)
        lines = outputs[0].split("\n")
        goofish_line = next(line for line in lines if "macmini" in line)
        taobao_line = next(line for line in lines if "iphone" in line)
        # goofish 行与 master 格式逐字一致（零变化承诺：无平台前缀）
        refreshed = await self.storage.get_subscription("umo-1", "macmini")
        self.assertEqual(
            goofish_line,
            f"- macmini | 启用 | 每3600s | pages=1 | 推荐价≤不限 | "
            f"下次={self.main_mod._format_ts(refreshed.next_run_at)}",
        )
        self.assertTrue(taobao_line.startswith("- [淘宝] iphone | "))
        self.assertIsNotNone(sub_g)

    async def test_analyze_item_detail_routes_by_item_platform(self) -> None:
        self.plugin.scheduler = None
        self.plugin._llm_tools_guard = lambda: None

        result = await self.plugin.goofish_analyze_item_detail(
            None, item_id="taobao:812345", force_refresh=True
        )

        self.assertIn("淘宝平台当前不可用", result)
        self.assertEqual(self.fake_goofish.analyzed_item_ids, [])

        fake_taobao = FakeProvider()
        self.plugin.providers = {
            "goofish": self.fake_goofish,
            "taobao": fake_taobao,
        }
        result2 = await self.plugin.goofish_analyze_item_detail(
            None, item_id="taobao:812345", force_refresh=True
        )

        self.assertIn('"source": "fresh"', result2)
        self.assertEqual(fake_taobao.analyzed_item_ids, ["taobao:812345"])
        self.assertEqual(self.fake_goofish.analyzed_item_ids, [])


@unittest.skipUnless(_HAS_REAL_ASTRBOT, "notifier 消息链需要真实 astrbot 组件")
class NotifierDetailHintPlatformTest(unittest.IsolatedAsyncioTestCase):
    """推荐消息尾部『/闲鱼 明细』提示只对 goofish 订阅输出。"""

    @staticmethod
    def _make_recommendation(item_id: str, keyword: str) -> RecommendationResult:
        from app.types import RecommendationItem

        return RecommendationResult(
            keyword=keyword,
            summary="s",
            top=[
                RecommendationItem(
                    item_id=item_id,
                    score=9.0,
                    reason="r",
                    risk="",
                    title="t",
                    price=1.0,
                    url="u",
                )
            ],
            total_candidates=1,
            used_llm=False,
        )

    @staticmethod
    def _chain_text(chain) -> str:
        return "".join(
            getattr(part, "text", "") or "" for part in getattr(chain, "chain", [])
        )

    async def test_detail_hint_gated_by_platform(self) -> None:
        from app.notifier import Notifier
        from app.reply_favorite import recommendation_reply_hint

        class _Ctx:
            def __init__(self) -> None:
                self.sent: list[tuple[str, object]] = []

            async def send_message(self, umo, chain):
                self.sent.append((umo, chain))

        ctx = _Ctx()
        notifier = Notifier(context=ctx, webhook_url=None)

        await notifier.send_recommendation_summary(
            umo="qq:GroupMessage:1",
            recommendation=self._make_recommendation("123", "kw"),
        )
        goofish_text = self._chain_text(ctx.sent[-1][1])
        # goofish 消息尾部与 master 逐字一致
        self.assertTrue(
            goofish_text.endswith(
                "\n" + recommendation_reply_hint() + "\n查看逐条请用 /闲鱼 明细 kw"
            )
        )

        await notifier.send_recommendation_summary(
            umo="qq:GroupMessage:1",
            recommendation=self._make_recommendation("taobao:9", "kw2"),
        )
        taobao_text = self._chain_text(ctx.sent[-1][1])
        self.assertNotIn("/闲鱼 明细", taobao_text)
        self.assertTrue(
            taobao_text.endswith("\n" + recommendation_reply_hint())
        )


if __name__ == "__main__":
    unittest.main()
