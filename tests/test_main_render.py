from __future__ import annotations

from data.plugins.astrbot_plugin_goofish_catcher.app.types import (
    NormalizedItem,
    RecommendationItem,
    RecommendationResult,
)
from data.plugins.astrbot_plugin_goofish_catcher.main import (
    _build_query_candidates,
    _extract_subcommand_args,
    _merge_query_args,
    _parse_query_input,
    _render_items_detail,
    _render_query_recommendation_preview,
    _render_recommendation_preview,
)


def test_render_recommendation_preview():
    result = RecommendationResult(
        keyword="sigma 60-600",
        summary="pick stable low-risk items first",
        top=[
            RecommendationItem(
                item_id="1001",
                score=92.0,
                reason="good drop",
                risk="check condition",
                title="Sigma 60-600",
                price=6800.0,
                url="https://www.goofish.com/item?id=1001",
            )
        ],
        total_candidates=3,
        used_llm=True,
        fallback_reason=None,
    )
    text = _render_recommendation_preview(result)
    assert "sigma 60-600" in text
    assert "1" in text


def test_render_items_detail():
    items = [
        NormalizedItem(
            item_id="1001",
            title="Sigma 60-600",
            price=6800.0,
            url="https://www.goofish.com/item?id=1001",
            publish_time=None,
        ),
        NormalizedItem(
            item_id="1002",
            title="Sigma 60-600 used",
            price=6500.0,
            url="https://www.goofish.com/item?id=1002",
            publish_time=None,
        ),
    ]
    text = _render_items_detail("sigma 60-600", items, limit=1)
    assert "1" in text
    assert "Sigma 60-600" in text


def test_build_query_candidates():
    items = [
        NormalizedItem(
            item_id="1001",
            title="Sigma 60-600",
            price=6800.0,
            url="https://www.goofish.com/item?id=1001",
            publish_time=1_700_000_000,
        )
    ]
    candidates = _build_query_candidates(
        keyword="sigma 60-600",
        items=items,
        observed_at=1_700_000_100,
    )
    assert len(candidates) == 1
    assert candidates[0].event_type == "NEW"
    assert candidates[0].keyword == "sigma 60-600"
    assert candidates[0].item_id == "1001"


def test_render_query_recommendation_preview():
    result = RecommendationResult(
        keyword="sigma 60-600",
        summary="prioritize fresh listings",
        top=[
            RecommendationItem(
                item_id="1001",
                score=90.0,
                reason="relevant and fresh",
                risk="check condition",
                title="Sigma 60-600",
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
    assert "sigma 60-600" in text
    assert "LLM_PREFILTER" in text


def test_parse_query_input_with_pages_suffix():
    keyword, pages = _parse_query_input(
        "sigma 60-600 Sports --pages 3",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "sigma 60-600 Sports"
    assert pages == 3


def test_parse_query_input_with_pages_middle():
    keyword, pages = _parse_query_input(
        "适马 -p 2 60-600 Sports",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "适马 60-600 Sports"
    assert pages == 2


def test_parse_query_input_with_pages_punctuation():
    keyword, pages = _parse_query_input(
        "适马 60-600 -p 2。",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "适马 60-600"
    assert pages == 2


def test_parse_query_input_with_pages_no_space():
    keyword, pages = _parse_query_input(
        "适马 60-600 -p2",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "适马 60-600"
    assert pages == 2


def test_parse_query_input_with_pages_equals():
    keyword, pages = _parse_query_input(
        "适马 60-600 --pages=4",
        default_pages=1,
        max_pages=5,
    )
    assert keyword == "适马 60-600"
    assert pages == 4


def test_parse_query_input_without_pages_suffix():
    keyword, pages = _parse_query_input(
        "sigma 60-600 Sports",
        default_pages=2,
        max_pages=5,
    )
    assert keyword == "sigma 60-600 Sports"
    assert pages == 2


def test_extract_subcommand_args_with_spaces():
    args = _extract_subcommand_args("闲鱼 查询 适马 60-600 Sports -p 2")
    assert args == "适马 60-600 Sports -p 2"


def test_extract_subcommand_args_empty():
    args = _extract_subcommand_args("闲鱼 查询")
    assert args == ""


def test_merge_query_args_prepend_missing_keyword():
    merged = _merge_query_args(
        message_query_args="60-600 Sports -p 2",
        parsed_keyword="适马",
    )
    assert merged == "适马 60-600 Sports -p 2"


def test_merge_query_args_keep_message_when_complete():
    merged = _merge_query_args(
        message_query_args="适马 60-600 Sports -p 2",
        parsed_keyword="适马",
    )
    assert merged == "适马 60-600 Sports -p 2"
