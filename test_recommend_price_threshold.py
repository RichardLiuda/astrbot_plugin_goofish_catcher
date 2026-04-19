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
from app.types import RecommendationCandidate


class RecommendPriceThresholdTest(unittest.IsolatedAsyncioTestCase):
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


if __name__ == "__main__":
    unittest.main()
