from __future__ import annotations

from data.plugins.astrbot_plugin_goofish_catcher.app.types import (
    NormalizedItem,
    RecommendationItem,
    RecommendationResult,
)
from data.plugins.astrbot_plugin_goofish_catcher.main import (
    _build_query_candidates,
    _extract_subcommand_args,
    _parse_query_input,
    _render_items_detail,
    _render_query_recommendation_preview,
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


def test_build_query_candidates():
    items = [
        NormalizedItem(
            item_id="1001",
            title="适马 60-600",
            price=6800.0,
            url="https://www.goofish.com/item?id=1001",
            publish_time=1_700_000_000,
        )
    ]
    candidates = _build_query_candidates(
        keyword="适马60-600",
        items=items,
        observed_at=1_700_000_100,
    )
    assert len(candidates) == 1
    assert candidates[0].event_type == "NEW"
    assert candidates[0].keyword == "适马60-600"
    assert candidates[0].item_id == "1001"


def test_render_query_recommendation_preview():
    result = RecommendationResult(
        keyword="适马60-600",
        summary="优先关注低风险且分数高的条目。",
        top=[
            RecommendationItem(
                item_id="1001",
                score=90.0,
                reason="相关度高，发布时间新",
                risk="注意验货",
                title="适马 60-600 国行",
                price=6800.0,
                url="https://www.goofish.com/item?id=1001",
            )
        ],
        total_candidates=5,
        used_llm=True,
        fallback_reason=None,
    )
    text = _render_query_recommendation_preview(
        recommendation=result,
        page_count=2,
        raw_total=30,
        filtered_total=12,
        filter_mode="LLM_PREFILTER",
    )
    assert "【查询推荐】关键词：适马60-600" in text
    assert "初筛模式：LLM_PREFILTER" in text
    assert "可再次执行 /闲鱼 查询 适马60-600" in text


def test_parse_query_input_with_pages_suffix():
    keyword, pages = _parse_query_input(
        "适马 60-600 Sports --pages 3",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "适马 60-600 Sports"
    assert pages == 3


def test_parse_query_input_without_pages_suffix():
    keyword, pages = _parse_query_input(
        "适马 60-600 Sports",
        default_pages=2,
        max_pages=5,
    )
    assert keyword == "适马 60-600 Sports"
    assert pages == 2


def test_extract_subcommand_args_with_spaces():
    args = _extract_subcommand_args("闲鱼 查询 适马 60-600 Sports -p 2")
    assert args == "适马 60-600 Sports -p 2"


def test_extract_subcommand_args_empty():
    args = _extract_subcommand_args("闲鱼 查询")
    assert args == ""
