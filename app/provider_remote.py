from __future__ import annotations

from typing import Any

import httpx

from .config import PluginSettings
from .types import NormalizedItem, ProviderError, ProviderErrorCode


class RemoteSearchProvider:
    def __init__(self, settings: PluginSettings) -> None:
        self.settings = settings
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.settings.remote_timeout_sec)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
    ) -> list[NormalizedItem]:
        if not self.settings.remote_base_url:
            raise ProviderError(
                ProviderErrorCode.NETWORK_ERROR,
                "remote_base_url is empty",
            )

        client = await self._ensure_client()
        url = f"{self.settings.remote_base_url.rstrip('/')}/v1/search"
        headers = {"Content-Type": "application/json"}
        if self.settings.remote_api_key:
            headers["Authorization"] = f"Bearer {self.settings.remote_api_key}"
            headers["X-API-Key"] = self.settings.remote_api_key

        payload = {
            "keyword": keyword,
            "pages": pages,
            "timeout_ms": int(timeout_sec * 1000),
            "sort": "time_desc",
            "use_login": True,
        }

        try:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=max(1, timeout_sec),
            )
        except httpx.TimeoutException as exc:
            raise ProviderError(
                ProviderErrorCode.TIMEOUT,
                f"remote provider timeout: {exc}",
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(
                ProviderErrorCode.NETWORK_ERROR,
                f"remote provider network error: {exc}",
            ) from exc

        data: dict[str, Any]
        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderError(
                ProviderErrorCode.PARSE_ERROR,
                f"remote provider returned invalid json: {exc}",
            ) from exc

        if response.status_code >= 400:
            err = data.get("error") if isinstance(data, dict) else None
            code_raw = str((err or {}).get("code", "UNKNOWN"))
            message = str((err or {}).get("message", response.text))
            retry_after = (err or {}).get("retry_after_sec")
            code = _map_remote_error_code(code_raw)
            raise ProviderError(code, message, _safe_int(retry_after))

        if not isinstance(data, dict):
            raise ProviderError(
                ProviderErrorCode.PARSE_ERROR,
                "remote provider json root is not an object",
            )
        if data.get("ok") is False:
            err = data.get("error", {})
            code_raw = str(err.get("code", "UNKNOWN"))
            message = str(err.get("message", "remote provider returned error"))
            raise ProviderError(
                _map_remote_error_code(code_raw),
                message,
                _safe_int(err.get("retry_after_sec")),
            )

        items_raw = data.get("items", [])
        if not isinstance(items_raw, list):
            raise ProviderError(
                ProviderErrorCode.PARSE_ERROR,
                "remote provider items is not a list",
            )

        items: list[NormalizedItem] = []
        for item in items_raw:
            if not isinstance(item, dict):
                continue
            normalized = _to_item(item)
            if normalized is not None:
                items.append(normalized)
        return items


def _map_remote_error_code(code_raw: str) -> ProviderErrorCode:
    code_upper = code_raw.strip().upper()
    mapping = {
        "AUTH_REQUIRED": ProviderErrorCode.AUTH_REQUIRED,
        "CAPTCHA": ProviderErrorCode.CAPTCHA,
        "RATE_LIMITED": ProviderErrorCode.RATE_LIMITED,
        "TIMEOUT": ProviderErrorCode.TIMEOUT,
        "PARSE_ERROR": ProviderErrorCode.PARSE_ERROR,
    }
    return mapping.get(code_upper, ProviderErrorCode.UNKNOWN)


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_item(raw: dict[str, Any]) -> NormalizedItem | None:
    item_id = str(raw.get("item_id", "")).strip()
    title = str(raw.get("title", "")).strip()
    url = str(raw.get("url", "")).strip()
    if not item_id or not title or not url:
        return None

    try:
        price = float(raw.get("price"))
    except (TypeError, ValueError):
        return None

    publish_time = _safe_int(raw.get("publish_time"))
    return NormalizedItem(
        item_id=item_id,
        title=title,
        price=price,
        url=url,
        publish_time=publish_time,
        raw=raw,
    )
