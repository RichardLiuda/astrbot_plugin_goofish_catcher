from __future__ import annotations

from typing import Protocol

from .config import (
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
    PluginSettings,
)
from .types import FavoriteItemResult, NormalizedItem


class SearchProvider(Protocol):
    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
    ) -> list[NormalizedItem]: ...

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
