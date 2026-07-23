from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace


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
try:
    import httpx as _httpx  # noqa: F401
except ModuleNotFoundError:
    httpx_module = types.ModuleType("httpx")
    httpx_module.AsyncClient = object
    sys.modules.setdefault("httpx", httpx_module)

sys.modules.setdefault("astrbot", astrbot_module)
sys.modules["astrbot.api"] = astrbot_api_module
sys.modules["astrbot.api.star"] = astrbot_api_star_module
sys.modules["astrbot.api.event"] = astrbot_api_event_module
sys.modules["astrbot.api.message_components"] = astrbot_api_message_components_module

from app.config import PluginSettings
from app.platforms.goofish import GOOFISH_PROFILE
from app.platforms.taobao import TAOBAO_PROFILE
from app.provider import build_providers
from app.provider_playwright import PlaywrightSearchProvider
from app.provider_remote import RemoteSearchProvider
from app.scheduler import MonitoringScheduler
from app.storage import SubscriptionStorage
from app.types import DeepAnalysisResult, NormalizedItem, RecommendationCandidate


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
    async def test_taobao_profile_short_circuits_without_browser(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = build_settings(Path(tmpdir))
            provider = PlaywrightSearchProvider(settings, profile=TAOBAO_PROFILE)
            result = await provider.analyze_item_detail(
                item=NormalizedItem(item_id="taobao:1", title="t", price=1.0, url="u"),
                timeout_sec=5,
            )
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.credit_status, "unknown")
            self.assertIn("暂未支持深度分析", result.credit_reason)
            self.assertEqual(result.item_id, "taobao:1")
            # 未启动浏览器
            self.assertIsNone(provider._playwright)
            self.assertIsNone(provider._browser)
            self.assertIsNone(provider._persistent_context)


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


if __name__ == "__main__":
    unittest.main()
