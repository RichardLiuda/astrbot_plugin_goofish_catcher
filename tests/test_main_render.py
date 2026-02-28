from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from data.plugins.astrbot_plugin_goofish_catcher.app.types import (  # noqa: E402
    NormalizedItem,
    RecommendationItem,
    RecommendationResult,
)
from data.plugins.astrbot_plugin_goofish_catcher.main import (  # noqa: E402
    _render_items_detail,
    _render_recommendation_preview,
)


def test_render_recommendation_preview():
    result = RecommendationResult(
        keyword="适马60-600",
        summary="优先考虑降价幅度高且无明显风险词的条目。",
        top=[
            RecommendationItem(
                item_id="1001",
                score=92.0,
                reason="降价明显",
                risk="注意验货",
                title="适马 60-600 国行",
                price=6800.0,
                url="https://www.goofish.com/item?id=1001",
            )
        ],
        total_candidates=3,
        used_llm=True,
        fallback_reason=None,
    )
    text = _render_recommendation_preview(result)
    assert "关键词：适马60-600" in text
    assert "推荐数：1" in text
    assert "查看逐条请用 /闲鱼 明细 适马60-600" in text


def test_render_items_detail():
    items = [
        NormalizedItem(
            item_id="1001",
            title="适马 60-600",
            price=6800.0,
            url="https://www.goofish.com/item?id=1001",
            publish_time=None,
        ),
        NormalizedItem(
            item_id="1002",
            title="适马 60-600 二手",
            price=6500.0,
            url="https://www.goofish.com/item?id=1002",
            publish_time=None,
        ),
    ]
    text = _render_items_detail("适马60-600", items, limit=1)
    assert "该次缓存共 2 条，展示前 1 条" in text
    assert "适马 60-600" in text
