from __future__ import annotations

import dataclasses
import logging
from typing import Protocol

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .config import (
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
    PluginSettings,
)
from .platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO
from .platforms.taobao import TAOBAO_PROFILE
from .types import DeepAnalysisResult, FavoriteItemResult, NormalizedItem, SearchFilters


class SearchProvider(Protocol):
    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
        filters: SearchFilters | None = None,
        price_lower: float | None = None,
        price_upper: float | None = None,
    ) -> list[NormalizedItem]: ...

    async def analyze_item_detail(
        self,
        *,
        item: NormalizedItem,
        timeout_sec: int,
    ) -> DeepAnalysisResult: ...

    async def favorite_item(
        self,
        *,
        url: str,
        timeout_sec: int,
        item_id: str | None = None,
    ) -> FavoriteItemResult: ...

    async def close(self) -> None: ...


class ProviderDependencyError(RuntimeError):
    """Raised when provider runtime dependencies are missing."""


class ProviderConfigurationError(RuntimeError):
    """Raised when provider configuration is invalid."""


def build_provider(settings: PluginSettings, *, llm_call=None) -> SearchProvider:
    if settings.provider_mode == PROVIDER_MODE_PLAYWRIGHT_LOCAL:
        try:
            from .provider_playwright import PlaywrightSearchProvider
        except ModuleNotFoundError as exc:
            raise ProviderDependencyError(
                "playwright is not installed. "
                "Run: uv pip install playwright && python -m playwright install chromium"
            ) from exc

        return PlaywrightSearchProvider(settings, llm_call=llm_call)

    if settings.provider_mode == PROVIDER_MODE_REMOTE_REST:
        try:
            from .provider_remote import RemoteSearchProvider
        except ModuleNotFoundError as exc:
            raise ProviderDependencyError(
                "httpx is not installed for remote provider mode."
            ) from exc

        return RemoteSearchProvider(settings)

    raise ValueError(f"unsupported provider mode: {settings.provider_mode}")


def build_providers(settings: PluginSettings, *, llm_call=None) -> dict[str, SearchProvider]:
    """按平台构建 provider 路由表；永远包含 goofish。

    taobao_enabled 且本地 playwright 模式时，额外构建独立会话目录的淘宝 provider；
    远程 worker 模式暂不支持淘宝（worker 多平台推迟），仅打 warning 跳过。
    """
    providers: dict[str, SearchProvider] = {
        PLATFORM_GOOFISH: build_provider(settings, llm_call=llm_call),
    }
    if not settings.taobao_enabled:
        return providers
    if settings.provider_mode != PROVIDER_MODE_PLAYWRIGHT_LOCAL:
        logger.warning(
            "[goofish_catcher] taobao_enabled=true，但远程模式暂不支持淘宝，已跳过"
        )
        return providers

    from .provider_playwright import PlaywrightSearchProvider

    taobao_settings = dataclasses.replace(
        settings,
        playwright_storage_state_path=(
            settings.plugin_data_dir / "storage_state.taobao.json"
        ),
        playwright_user_data_dir=settings.plugin_data_dir / "browser_profile_taobao",
    )
    providers[PLATFORM_TAOBAO] = PlaywrightSearchProvider(
        taobao_settings,
        llm_call=llm_call,
        profile=TAOBAO_PROFILE,
    )
    return providers
