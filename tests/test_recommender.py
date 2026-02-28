from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import PluginSettings  # noqa: E402
from app.recommender import GoofishRecommender  # noqa: E402
from app.types import NormalizedItem, RecommendationCandidate  # noqa: E402


class _ProviderMeta:
    def __init__(self, provider_id: str):
        self.id = provider_id


class _Provider:
    def __init__(self, provider_id: str = "test_provider"):
        self._meta = _ProviderMeta(provider_id)

    def meta(self):
        return self._meta


class _LLMResp:
    def __init__(self, text: str):
        self.completion_text = text


class _FakeContext:
    def __init__(
        self,
        *,
        llm_text: str = "",
        delay_sec: float = 0.0,
        raise_exc: Exception | None = None,
        with_session_provider: bool = True,
        with_fallback_provider: bool = True,
    ):
        self.llm_text = llm_text
        self.delay_sec = delay_sec
        self.raise_exc = raise_exc
        self._session_provider = _Provider() if with_session_provider else None
        self._fallback_providers = (
            [_Provider("fallback")] if with_fallback_provider else []
        )
        self.last_chat_provider_id: str | None = None

    def get_using_provider(self, umo: str):
        return self._session_provider

    def get_all_providers(self):
        return self._fallback_providers

    def get_provider_by_id(self, provider_id: str):
        all_providers = []
        if self._session_provider is not None:
            all_providers.append(self._session_provider)
        all_providers.extend(self._fallback_providers)
        for provider in all_providers:
            if provider.meta().id == provider_id:
                return provider
        return None

    async def llm_generate(self, **kwargs):
        self.last_chat_provider_id = kwargs.get("chat_provider_id")
        if self.delay_sec > 0:
            await asyncio.sleep(self.delay_sec)
        if self.raise_exc is not None:
            raise self.raise_exc
        return _LLMResp(self.llm_text)


def _make_settings(tmp_path: Path, **overrides) -> PluginSettings:
    settings = PluginSettings(
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path,
        db_path=tmp_path / "test.db",
        provider_mode="playwright_local",
        default_interval_sec=600,
        default_pages=1,
        max_pages=2,
        scheduler_tick_sec=15,
        max_concurrency=1,
        fetch_timeout_sec=20,
        max_retries=3,
        retry_base_sec=30,
        retry_max_sec=900,
        default_new_window_sec=1800,
        default_drop_abs=50.0,
        default_drop_pct=0.05,
        default_cooldown_sec=3600,
        playwright_storage_state_path=None,
        playwright_headless=True,
        playwright_block_assets=True,
        webhook_url=None,
        remote_base_url=None,
        remote_api_key=None,
        remote_timeout_sec=20,
        queue_max_size=256,
        llm_enabled=True,
        llm_provider_id=None,
        llm_prefilter_provider_id=None,
        llm_timeout_sec=25,
        llm_top_k=3,
        llm_max_candidates=20,
        llm_prefilter_enabled=True,
        llm_prefilter_timeout_sec=6,
        llm_prefilter_max_items=30,
    )
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


def _candidates() -> list[RecommendationCandidate]:
    return [
        RecommendationCandidate(
            event_type="PRICE_DROP",
            keyword="镜头",
            item_id="1",
            title="适马 60-600",
            price=6800.0,
            url="https://www.goofish.com/item?id=1",
            publish_time=1_700_000_000,
            observed_at=1_700_000_100,
            last_price=7500.0,
            drop_abs=700.0,
            drop_pct=700.0 / 7500.0,
        ),
        RecommendationCandidate(
            event_type="NEW",
            keyword="镜头",
            item_id="2",
            title="适马 60-600 全新",
            price=7300.0,
            url="https://www.goofish.com/item?id=2",
            publish_time=1_700_000_050,
            observed_at=1_700_000_100,
        ),
    ]


@pytest.mark.asyncio
async def test_recommender_llm_json_parse_and_topk(tmp_path: Path):
    llm_payload = {
        "summary": "推荐优先看降价幅度高的条目。",
        "top": [
            {
                "item_id": "1",
                "score": 91,
                "reason": "降价幅度大",
                "risk": "注意快门和对焦",
            },
            {
                "item_id": "2",
                "score": 70,
                "reason": "较新",
                "risk": "价格偏高",
            },
        ],
    }
    context = _FakeContext(llm_text=json.dumps(llm_payload, ensure_ascii=False))
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_top_k=1),
    )
    result = await recommender.analyze(
        umo="webchat:test",
        keyword="镜头",
        candidates=_candidates(),
        top_k=1,
    )
    assert result.used_llm
    assert len(result.top) == 1
    assert result.top[0].item_id == "1"


@pytest.mark.asyncio
async def test_recommender_timeout_fallback_to_heuristic(tmp_path: Path):
    context = _FakeContext(llm_text='{"summary":"x","top":[]}', delay_sec=1.5)
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_timeout_sec=1),
    )
    result = await recommender.analyze(
        umo="webchat:test",
        keyword="镜头",
        candidates=_candidates(),
    )
    assert not result.used_llm
    assert result.fallback_reason == "LLM_TIMEOUT"
    assert len(result.top) >= 1


@pytest.mark.asyncio
async def test_recommender_risk_keyword_penalty(tmp_path: Path):
    context = _FakeContext(with_session_provider=False, with_fallback_provider=False)
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_enabled=False),
    )
    candidates = [
        RecommendationCandidate(
            event_type="PRICE_DROP",
            keyword="镜头",
            item_id="safe",
            title="适马 60-600 国行",
            price=7000.0,
            url="https://www.goofish.com/item?id=safe",
            publish_time=1_700_000_000,
            observed_at=1_700_000_100,
            last_price=7600.0,
            drop_abs=600.0,
            drop_pct=600.0 / 7600.0,
        ),
        RecommendationCandidate(
            event_type="PRICE_DROP",
            keyword="镜头",
            item_id="risk",
            title="适马 60-600 配件机 不退不换",
            price=7000.0,
            url="https://www.goofish.com/item?id=risk",
            publish_time=1_700_000_000,
            observed_at=1_700_000_100,
            last_price=7600.0,
            drop_abs=600.0,
            drop_pct=600.0 / 7600.0,
        ),
    ]
    result = await recommender.analyze(
        umo="webchat:test",
        keyword="镜头",
        candidates=candidates,
    )
    assert not result.used_llm
    assert result.top[0].item_id == "safe"


@pytest.mark.asyncio
async def test_recommender_prefers_configured_provider(tmp_path: Path):
    llm_payload = {
        "summary": "ok",
        "top": [
            {
                "item_id": "1",
                "score": 88,
                "reason": "ok",
                "risk": "ok",
            }
        ],
    }
    context = _FakeContext(
        llm_text=json.dumps(llm_payload, ensure_ascii=False),
        with_session_provider=True,
        with_fallback_provider=True,
    )
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_provider_id="fallback"),
    )
    result = await recommender.analyze(
        umo="webchat:test",
        keyword="镜头",
        candidates=_candidates(),
    )
    assert result.top
    assert context.last_chat_provider_id == "fallback"


@pytest.mark.asyncio
async def test_prefilter_items_by_llm(tmp_path: Path):
    items = [
        NormalizedItem(
            item_id="1",
            title="适马 60-600 国行",
            price=6800.0,
            url="https://www.goofish.com/item?id=1",
            publish_time=None,
        ),
        NormalizedItem(
            item_id="2",
            title="佳能 24-70",
            price=5200.0,
            url="https://www.goofish.com/item?id=2",
            publish_time=None,
        ),
    ]
    context = _FakeContext(llm_text='{"keep_item_ids":["1"]}')
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_prefilter_timeout_sec=2),
    )
    filtered, mode = await recommender.prefilter_items(
        umo="webchat:test",
        keyword="适马60-600",
        items=items,
    )
    assert mode == "LLM_PREFILTER"
    assert [item.item_id for item in filtered] == ["1"]


@pytest.mark.asyncio
async def test_prefilter_uses_dedicated_provider_if_configured(tmp_path: Path):
    items = [
        NormalizedItem(
            item_id="1",
            title="閫傞┈ 60-600 鍥借",
            price=6800.0,
            url="https://www.goofish.com/item?id=1",
            publish_time=None,
        )
    ]
    context = _FakeContext(llm_text='{"keep_item_ids":["1"]}')
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(
            tmp_path,
            llm_provider_id="test_provider",
            llm_prefilter_provider_id="fallback",
        ),
    )
    filtered, mode = await recommender.prefilter_items(
        umo="webchat:test",
        keyword="閫傞┈60-600",
        items=items,
    )
    assert mode == "LLM_PREFILTER"
    assert [item.item_id for item in filtered] == ["1"]
    assert context.last_chat_provider_id == "fallback"


@pytest.mark.asyncio
async def test_prefilter_fallback_to_heuristic_on_timeout(tmp_path: Path):
    items = [
        NormalizedItem(
            item_id="1",
            title="适马 60-600 国行",
            price=6800.0,
            url="https://www.goofish.com/item?id=1",
            publish_time=None,
        ),
        NormalizedItem(
            item_id="2",
            title="苹果手机壳",
            price=20.0,
            url="https://www.goofish.com/item?id=2",
            publish_time=None,
        ),
    ]
    context = _FakeContext(delay_sec=1.2, llm_text='{"keep_item_ids":["2"]}')
    recommender = GoofishRecommender(
        context=context,
        settings=_make_settings(tmp_path, llm_prefilter_timeout_sec=1),
    )
    filtered, mode = await recommender.prefilter_items(
        umo="webchat:test",
        keyword="适马60-600",
        items=items,
    )
    assert mode == "HEURISTIC_PREFILTER"
    assert [item.item_id for item in filtered] == ["1"]
