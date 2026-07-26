from __future__ import annotations

import sys
import types
import unittest
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

from app.detector import should_recover_unsent_new_event
from app.recommender import GoofishRecommender
from app.types import DeepAnalysisResult, RecommendationCandidate, SearchFilters


class RecommendPriceThresholdTest(unittest.IsolatedAsyncioTestCase):
    def test_unsent_new_event_can_be_recovered_after_send_failure(self) -> None:
        self.assertTrue(
            should_recover_unsent_new_event(
                first_seen_at=1000,
                publish_time=None,
                now_ts=1100,
                new_window_sec=1800,
                recovery_sec=24 * 3600,
            )
        )

    def test_unsent_new_event_recovery_is_bounded(self) -> None:
        self.assertFalse(
            should_recover_unsent_new_event(
                first_seen_at=1000,
                publish_time=None,
                now_ts=1000 + 25 * 3600,
                new_window_sec=1800,
                recovery_sec=24 * 3600,
            )
        )

    def test_search_filters_normalize_advanced_fields(self) -> None:
        filters = SearchFilters(
            price_lower=0,
            price_upper=1500,
            personal_only=True,
            free_shipping=True,
            new_publish_option=" 24小时内 ",
            region=" 江苏/南京/全南京 ",
        ).normalized()

        self.assertIsNone(filters.price_lower)
        self.assertEqual(filters.price_upper, 1500)
        self.assertTrue(filters.personal_only)
        self.assertTrue(filters.free_shipping)
        self.assertEqual(filters.new_publish_option, "24小时内")
        self.assertEqual(filters.region, "江苏/南京/全南京")

    async def test_analyze_filters_items_above_threshold(self) -> None:
        recommender = GoofishRecommender(
            context=SimpleNamespace(),
            settings=SimpleNamespace(
                llm_top_k=3,
                llm_max_candidates=20,
                llm_enabled=False,
                llm_min_score=0.0,
            ),
        )
        candidates = [
            RecommendationCandidate(
                event_type="NEW",
                keyword="mac mini",
                item_id="cheap",
                title="Mac mini M4",
                price=2999.0,
                url="https://example.com/cheap",
                publish_time=None,
                observed_at=1,
            ),
            RecommendationCandidate(
                event_type="NEW",
                keyword="mac mini",
                item_id="expensive",
                title="Mac mini M4 Pro",
                price=6999.0,
                url="https://example.com/expensive",
                publish_time=None,
                observed_at=1,
            ),
        ]

        result = await recommender.analyze(
            umo="test",
            keyword="mac mini",
            candidates=candidates,
            recommend_max_price=5000.0,
        )

        self.assertEqual(result.total_candidates, 1)
        self.assertEqual([item.item_id for item in result.top], ["cheap"])

    async def test_analyze_returns_empty_when_threshold_filters_all(self) -> None:
        recommender = GoofishRecommender(
            context=SimpleNamespace(),
            settings=SimpleNamespace(
                llm_top_k=3,
                llm_max_candidates=20,
                llm_enabled=False,
                llm_min_score=0.0,
            ),
        )
        candidates = [
            RecommendationCandidate(
                event_type="NEW",
                keyword="相机",
                item_id="only",
                title="富士 X-T5",
                price=8999.0,
                url="https://example.com/only",
                publish_time=None,
                observed_at=1,
            )
        ]

        result = await recommender.analyze(
            umo="test",
            keyword="相机",
            candidates=candidates,
            recommend_max_price=5000.0,
        )

        self.assertEqual(result.top, [])
        self.assertEqual(result.fallback_reason, "PRICE_THRESHOLD_EMPTY")

    async def test_analyze_carries_deep_analysis_to_result(self) -> None:
        recommender = GoofishRecommender(
            context=SimpleNamespace(),
            settings=SimpleNamespace(
                llm_top_k=3,
                llm_max_candidates=20,
                llm_enabled=False,
                llm_min_score=0.0,
            ),
        )
        analysis = DeepAnalysisResult(
            item_id="good-credit",
            analyzed_at=1,
            status="passed",
            credit_status="good",
            credit_reason="卖家信用信息良好",
            summary="信用良好；想要 12",
            risk="未发现明确低信用风险",
            image_urls=["https://example.com/a.jpg"],
            want_count=12,
        )
        candidates = [
            RecommendationCandidate(
                event_type="NEW",
                keyword="镜头",
                item_id="good-credit",
                title="Sony 20-70",
                price=4999.0,
                url="https://example.com/good-credit",
                publish_time=None,
                observed_at=1,
                deep_analysis=analysis,
            )
        ]

        result = await recommender.analyze(
            umo="test",
            keyword="镜头",
            candidates=candidates,
        )

        self.assertEqual(result.top[0].deep_analysis, analysis)
        self.assertIn("good", result.top[0].deep_analysis.credit_status)


if __name__ == "__main__":
    unittest.main()
