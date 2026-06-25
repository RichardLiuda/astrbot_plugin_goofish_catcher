from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace


astrbot_module = types.ModuleType("astrbot")
astrbot_api_module = types.ModuleType("astrbot.api")
astrbot_api_module.logger = SimpleNamespace(
    warning=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
)
astrbot_api_star_module = types.ModuleType("astrbot.api.star")
astrbot_api_star_module.Context = object

sys.modules.setdefault("astrbot", astrbot_module)
sys.modules["astrbot.api"] = astrbot_api_module
sys.modules["astrbot.api.star"] = astrbot_api_star_module

from app.recommender import GoofishRecommender
from app.types import DeepAnalysisResult, RecommendationCandidate, SearchFilters


class RecommendPriceThresholdTest(unittest.IsolatedAsyncioTestCase):
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
