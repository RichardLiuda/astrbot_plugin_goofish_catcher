from __future__ import annotations

from pathlib import Path

import pytest

from data.plugins.astrbot_plugin_goofish_catcher.app.config import PluginSettings
from data.plugins.astrbot_plugin_goofish_catcher.app.provider_playwright import (
    _parse_price,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.provider_remote import (
    RemoteSearchProvider,
)


def _make_settings(tmp_path: Path) -> PluginSettings:
    return PluginSettings(
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path,
        db_path=tmp_path / "test.db",
        provider_mode="remote_rest",
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
        playwright_headless=False,
        playwright_block_assets=True,
        webhook_url=None,
        remote_base_url="https://example.com",
        remote_api_key="",
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


def test_parse_price_with_chinese_units():
    assert _parse_price("1.2万") == pytest.approx(12000.0)
    assert _parse_price("7.5k") == pytest.approx(7500.0)
    assert _parse_price("￥6,899") == pytest.approx(6899.0)


class _FakeResponse:
    status_code = 200
    text = "ok"

    def json(self):
        return {
            "ok": True,
            "items": [
                {
                    "item_id": "1",
                    "title": "test",
                    "url": "https://www.goofish.com/item?id=1",
                    "price": 100.0,
                }
            ],
        }


class _FakeClient:
    def __init__(self):
        self.timeout_arg = None

    async def post(self, *args, **kwargs):
        self.timeout_arg = kwargs.get("timeout")
        return _FakeResponse()


@pytest.mark.asyncio
async def test_remote_provider_respects_per_call_timeout(tmp_path: Path):
    settings = _make_settings(tmp_path)
    provider = RemoteSearchProvider(settings)
    fake_client = _FakeClient()
    provider._client = fake_client
    items = await provider.search(keyword="镜头", pages=1, timeout_sec=7)
    assert fake_client.timeout_arg == 7
    assert len(items) == 1
