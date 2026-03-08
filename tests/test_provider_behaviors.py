from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from data.plugins.astrbot_plugin_goofish_catcher.app.config import (
    PluginSettings,
    load_plugin_settings,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.provider import (
    ProviderConfigurationError,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.provider_playwright import (
    PlaywrightSearchProvider,
    _parse_price,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.provider_remote import (
    RemoteSearchProvider,
)
from data.plugins.astrbot_plugin_goofish_catcher.app.types import ProviderError


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
        playwright_force_direct=True,
        webhook_url=None,
        remote_base_url="https://example.com",
        remote_api_key="",
        remote_headers_json=None,
        remote_timeout_sec=20,
        remote_healthcheck_on_init=True,
        remote_healthcheck_timeout_sec=10,
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
    def __init__(
        self,
        *,
        status_code: int = 200,
        payload: dict | list | None = None,
        text: str = "ok",
        json_exc: Exception | None = None,
    ):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text
        self._json_exc = json_exc

    def json(self):
        if self._json_exc is not None:
            raise self._json_exc
        return self._payload


class _FakeClient:
    def __init__(self):
        self.timeout_arg = None
        self.last_method = None
        self.last_url = None
        self.last_headers = None
        self.last_json = None
        self.response: _FakeResponse | Exception = _FakeResponse(
            payload={
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
        )

    async def request(self, method, url, **kwargs):
        self.last_method = method
        self.last_url = url
        self.last_headers = kwargs.get("headers")
        self.last_json = kwargs.get("json")
        self.timeout_arg = kwargs.get("timeout")
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


@pytest.mark.asyncio
async def test_remote_provider_respects_per_call_timeout(tmp_path: Path):
    settings = _make_settings(tmp_path)
    provider = RemoteSearchProvider(settings)
    fake_client = _FakeClient()
    provider._client = fake_client
    items = await provider.search(keyword="镜头", pages=1, timeout_sec=7)
    assert fake_client.timeout_arg == 7
    assert len(items) == 1


@pytest.mark.asyncio
async def test_remote_provider_merges_api_key_and_extra_headers(tmp_path: Path):
    settings = _make_settings(tmp_path)
    settings.remote_api_key = "secret-token"
    settings.remote_headers_json = json.dumps(
        {
            "CF-Access-Client-Id": "cf-id",
            "CF-Access-Client-Secret": "cf-secret",
        }
    )
    provider = RemoteSearchProvider(settings)
    fake_client = _FakeClient()
    provider._client = fake_client

    await provider.search(keyword="镜头", pages=1, timeout_sec=7)

    assert fake_client.last_method == "POST"
    assert fake_client.last_url == "https://example.com/v1/search"
    assert fake_client.last_headers["Authorization"] == "Bearer secret-token"
    assert fake_client.last_headers["X-API-Key"] == "secret-token"
    assert fake_client.last_headers["CF-Access-Client-Id"] == "cf-id"
    assert fake_client.last_headers["CF-Access-Client-Secret"] == "cf-secret"
    assert fake_client.last_json["keyword"] == "镜头"


@pytest.mark.asyncio
async def test_remote_provider_healthcheck_success(tmp_path: Path):
    settings = _make_settings(tmp_path)
    provider = RemoteSearchProvider(settings)
    fake_client = _FakeClient()
    fake_client.response = _FakeResponse(
        payload={
            "ok": True,
            "provider": "playwright_local",
            "auth": "configured",
            "storage_state": True,
        }
    )
    provider._client = fake_client

    payload = await provider.healthcheck(timeout_sec=3)

    assert fake_client.last_method == "GET"
    assert fake_client.last_url == "https://example.com/health"
    assert fake_client.timeout_arg == 3
    assert payload["storage_state"] is True


@pytest.mark.asyncio
async def test_remote_provider_healthcheck_raises_on_worker_auth_failure(tmp_path: Path):
    settings = _make_settings(tmp_path)
    provider = RemoteSearchProvider(settings)
    fake_client = _FakeClient()
    fake_client.response = _FakeResponse(
        status_code=401,
        payload={
            "ok": False,
            "error": {
                "code": "NETWORK_ERROR",
                "message": "worker authorization failed",
            },
        },
        text="worker authorization failed",
    )
    provider._client = fake_client

    with pytest.raises(ProviderError) as exc_info:
        await provider.healthcheck(timeout_sec=3)

    assert exc_info.value.code.value == "NETWORK_ERROR"
    assert "worker authorization failed" in exc_info.value.message


def test_remote_provider_invalid_headers_json_raises(tmp_path: Path):
    settings = _make_settings(tmp_path)
    settings.remote_headers_json = "{invalid"

    with pytest.raises(ProviderConfigurationError):
        RemoteSearchProvider(settings)


def test_load_plugin_settings_copy_storage_state_to_stable_path(tmp_path: Path):
    external_dir = tmp_path / "external"
    external_dir.mkdir(parents=True, exist_ok=True)
    source = external_dir / "state.json"
    source.write_text('{"cookies":[{"name":"a"}]}', encoding="utf-8")

    settings = load_plugin_settings(
        config={"playwright_storage_state_file": [str(source)]},
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path / "plugin_data",
    )
    assert settings.playwright_storage_state_path is not None
    assert settings.playwright_storage_state_path.name == "storage_state.json"
    assert settings.playwright_storage_state_path.exists()
    assert settings.playwright_storage_state_path.read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    )


def test_load_plugin_settings_use_stable_fallback_when_config_path_missing(tmp_path: Path):
    plugin_data = tmp_path / "plugin_data"
    plugin_data.mkdir(parents=True, exist_ok=True)
    stable = plugin_data / "storage_state.json"
    stable.write_text('{"cookies":[{"name":"stable"}]}', encoding="utf-8")

    settings = load_plugin_settings(
        config={"playwright_storage_state_file": [str(plugin_data / "missing.json")]},
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=plugin_data,
    )
    assert settings.playwright_storage_state_path == stable


def test_load_plugin_settings_playwright_force_direct_default_true(tmp_path: Path):
    settings = load_plugin_settings(
        config={},
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path / "plugin_data",
    )
    assert settings.playwright_force_direct is True


def test_load_plugin_settings_playwright_force_direct_can_disable(tmp_path: Path):
    settings = load_plugin_settings(
        config={"playwright_force_direct": False},
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path / "plugin_data",
    )
    assert settings.playwright_force_direct is False


def test_playwright_launch_args_force_direct_enabled(tmp_path: Path):
    settings = _make_settings(tmp_path)
    provider = PlaywrightSearchProvider(settings)
    args = provider._build_launch_args()
    assert "--no-proxy-server" in args
    assert "--proxy-server=direct://" in args
    assert "--proxy-bypass-list=*" in args


def test_playwright_launch_args_force_direct_disabled(tmp_path: Path):
    settings = _make_settings(tmp_path)
    settings.playwright_force_direct = False
    provider = PlaywrightSearchProvider(settings)
    args = provider._build_launch_args()
    assert "--no-proxy-server" not in args
    assert "--proxy-server=direct://" not in args
    assert "--proxy-bypass-list=*" not in args


class _FakeBrowserContext:
    def __init__(self):
        self.last_path = None

    async def storage_state(self, *, path: str):
        self.last_path = path
        Path(path).write_text('{"cookies":[{"name":"persisted"}]}', encoding="utf-8")


@pytest.mark.asyncio
async def test_playwright_provider_persists_context_storage_state(tmp_path: Path):
    settings = _make_settings(tmp_path)
    settings.playwright_storage_state_path = tmp_path / "storage_state.json"
    provider = PlaywrightSearchProvider(settings)
    context = _FakeBrowserContext()
    await provider._persist_context_storage_state(context)
    assert context.last_path == str(settings.playwright_storage_state_path)
    assert settings.playwright_storage_state_path.exists()


def test_load_plugin_settings_remote_options(tmp_path: Path):
    settings = load_plugin_settings(
        config={
            "provider_mode": "remote_rest",
            "remote_base_url": "https://worker.example.com",
            "remote_api_key": "secret",
            "remote_headers_json": '{"CF-Access-Client-Id":"id"}',
            "remote_timeout_sec": 33,
            "remote_healthcheck_on_init": False,
            "remote_healthcheck_timeout_sec": 12,
        },
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=tmp_path / "plugin_data",
    )
    assert settings.provider_mode == "remote_rest"
    assert settings.remote_base_url == "https://worker.example.com"
    assert settings.remote_api_key == "secret"
    assert settings.remote_headers_json == '{"CF-Access-Client-Id":"id"}'
    assert settings.remote_timeout_sec == 33
    assert settings.remote_healthcheck_on_init is False
    assert settings.remote_healthcheck_timeout_sec == 12


def test_conf_schema_exposes_remote_settings():
    schema_path = Path(__file__).resolve().parents[1] / "_conf_schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for key in {
        "provider_mode",
        "remote_base_url",
        "remote_api_key",
        "remote_headers_json",
        "remote_timeout_sec",
        "remote_healthcheck_on_init",
        "remote_healthcheck_timeout_sec",
    }:
        assert key in schema
