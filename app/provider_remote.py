from __future__ import annotations

import json
from typing import Any

import httpx

from .config import PluginSettings
from .provider import ProviderConfigurationError
from .types import (
    FavoriteItemResult,
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
)


class RemoteSearchProvider:
    def __init__(self, settings: PluginSettings) -> None:
        if not settings.remote_base_url:
            raise ProviderConfigurationError("remote_base_url is empty")
        self.settings = settings
        self._client: httpx.AsyncClient | None = None
        self._extra_headers = _parse_extra_headers(settings.remote_headers_json)

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.settings.remote_timeout_sec)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_remote_headers(self, *, include_content_type: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if include_content_type:
            headers["Content-Type"] = "application/json"
        if self.settings.remote_api_key:
            headers["Authorization"] = f"Bearer {self.settings.remote_api_key}"
            headers["X-API-Key"] = self.settings.remote_api_key
        headers.update(self._extra_headers)
        return headers

    async def _request_json(
        self,
        *,
        method: str,
        path: str,
        timeout_sec: int,
        json_body: dict[str, Any] | None = None,
    ) -> tuple[httpx.Response, Any]:
        client = await self._ensure_client()
        url = f"{self.settings.remote_base_url.rstrip('/')}/{path.lstrip('/')}"
        request_kwargs: dict[str, Any] = {
            "headers": self._build_remote_headers(
                include_content_type=json_body is not None
            ),
            "timeout": max(1, timeout_sec),
        }
        if json_body is not None:
            request_kwargs["json"] = json_body

        try:
            response = await client.request(method, url, **request_kwargs)
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

        try:
            data = response.json()
        except ValueError as exc:
            raise ProviderError(
                ProviderErrorCode.PARSE_ERROR,
                _build_invalid_json_message(response=response, exc=exc),
            ) from exc

        return response, data

    async def healthcheck(self, *, timeout_sec: int | None = None) -> dict[str, Any]:
        response, data = await self._request_json(
            method="GET",
            path="/health",
            timeout_sec=timeout_sec or self.settings.remote_healthcheck_timeout_sec,
        )
        return _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote healthcheck json root is not an object",
            ok_error_message="remote healthcheck did not return ok=true",
            ok_error_code=ProviderErrorCode.NETWORK_ERROR,
        )

    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
    ) -> list[NormalizedItem]:
        # Give the remote worker enough time to finish its own Playwright timeout
        # and send back a structured AUTH_REQUIRED/CAPTCHA/TIMEOUT response.
        request_timeout_sec = max(timeout_sec + 10, int(timeout_sec * 1.5))
        payload = {
            "keyword": keyword,
            "pages": pages,
            "timeout_ms": int(timeout_sec * 1000),
            "sort": "time_desc",
            "use_login": True,
        }
        response, data = await self._request_json(
            method="POST",
            path="/v1/search",
            timeout_sec=request_timeout_sec,
            json_body=payload,
        )
        data = _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote provider json root is not an object",
            ok_error_message="remote provider did not return ok=true",
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

    async def favorite_item(
        self,
        *,
        url: str,
        timeout_sec: int,
        item_id: str | None = None,
    ) -> FavoriteItemResult:
        response, data = await self._request_json(
            method="POST",
            path="/v1/favorite",
            timeout_sec=max(5, timeout_sec + 10),
            json_body={
                "url": url,
                "item_id": item_id,
                "timeout_ms": int(timeout_sec * 1000),
            },
        )
        data = _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote favorite json root is not an object",
            ok_error_message="remote favorite did not return ok=true",
        )
        status = str(data.get("status", "")).strip()
        if status not in {"favorited", "already_favorited"}:
            raise ProviderError(
                ProviderErrorCode.PARSE_ERROR,
                f"remote favorite returned invalid status: {status or '<empty>'}",
            )
        return FavoriteItemResult(
            status=status,
            url=str(data.get("url") or url).strip() or url,
            item_id=str(data.get("item_id") or item_id or "").strip() or None,
            title=str(data.get("title") or "").strip() or None,
        )

    async def start_auth_session(
        self,
        *,
        force_restart: bool = False,
        timeout_sec: int | None = None,
    ) -> dict[str, Any]:
        response, data = await self._request_json(
            method="POST",
            path="/v1/auth/start",
            timeout_sec=timeout_sec or self.settings.remote_timeout_sec,
            json_body={"force_restart": force_restart},
        )
        return _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote auth start json root is not an object",
            ok_error_message="remote auth start did not return ok=true",
        )

    async def confirm_auth_session(
        self,
        *,
        session_id: str,
        timeout_sec: int | None = None,
    ) -> dict[str, Any]:
        response, data = await self._request_json(
            method="POST",
            path="/v1/auth/confirm",
            timeout_sec=timeout_sec or self.settings.remote_timeout_sec,
            json_body={"session_id": session_id},
        )
        return _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote auth confirm json root is not an object",
            ok_error_message="remote auth confirm did not return ok=true",
        )

    async def cancel_auth_session(
        self,
        *,
        session_id: str,
        timeout_sec: int | None = None,
    ) -> dict[str, Any]:
        response, data = await self._request_json(
            method="POST",
            path="/v1/auth/cancel",
            timeout_sec=timeout_sec or self.settings.remote_timeout_sec,
            json_body={"session_id": session_id},
        )
        return _expect_ok_object(
            response=response,
            data=data,
            parse_error_message="remote auth cancel json root is not an object",
            ok_error_message="remote auth cancel did not return ok=true",
        )


def _map_remote_error_code(code_raw: str) -> ProviderErrorCode:
    code_upper = code_raw.strip().upper()
    mapping = {
        "DEPENDENCY_MISSING": ProviderErrorCode.DEPENDENCY_MISSING,
        "AUTH_REQUIRED": ProviderErrorCode.AUTH_REQUIRED,
        "CAPTCHA": ProviderErrorCode.CAPTCHA,
        "RATE_LIMITED": ProviderErrorCode.RATE_LIMITED,
        "TIMEOUT": ProviderErrorCode.TIMEOUT,
        "PARSE_ERROR": ProviderErrorCode.PARSE_ERROR,
        "NETWORK_ERROR": ProviderErrorCode.NETWORK_ERROR,
        "UNKNOWN": ProviderErrorCode.UNKNOWN,
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


def _parse_extra_headers(raw_value: str | None) -> dict[str, str]:
    if not raw_value:
        return {}
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ProviderConfigurationError(
            f"remote_headers_json is not valid JSON: {exc}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ProviderConfigurationError("remote_headers_json must be a JSON object")

    headers: dict[str, str] = {}
    for key, value in parsed.items():
        key_text = str(key).strip()
        if not key_text or value is None:
            continue
        headers[key_text] = str(value)
    return headers


def _raise_for_remote_error(response: httpx.Response, data: Any) -> None:
    if response.status_code < 400 and not (
        isinstance(data, dict) and data.get("ok") is False
    ):
        return

    err = data.get("error") if isinstance(data, dict) else None
    code_raw = str((err or {}).get("code", "UNKNOWN"))
    message = str((err or {}).get("message", response.text))
    retry_after = (err or {}).get("retry_after_sec")
    raise ProviderError(
        _map_remote_error_code(code_raw),
        message,
        _safe_int(retry_after),
    )


def _expect_ok_object(
    *,
    response: httpx.Response,
    data: Any,
    parse_error_message: str,
    ok_error_message: str,
    ok_error_code: ProviderErrorCode = ProviderErrorCode.NETWORK_ERROR,
) -> dict[str, Any]:
    _raise_for_remote_error(response, data)
    if not isinstance(data, dict):
        raise ProviderError(
            ProviderErrorCode.PARSE_ERROR,
            parse_error_message,
        )
    if data.get("ok") is not True:
        raise ProviderError(
            ok_error_code,
            ok_error_message,
        )
    return data


def _build_invalid_json_message(
    *,
    response: httpx.Response,
    exc: ValueError,
) -> str:
    status = response.status_code
    url = str(response.request.url)
    content_type = response.headers.get("content-type", "").strip() or "-"
    location = response.headers.get("location", "").strip()
    body_preview = _response_body_preview(response)

    parts = [
        f"remote provider returned invalid json: {exc}",
        f"status={status}",
        f"url={url}",
        f"content_type={content_type}",
    ]
    if location:
        parts.append(f"location={location}")
    parts.append(f"body={body_preview}")
    return ", ".join(parts)


def _response_body_preview(response: httpx.Response, limit: int = 160) -> str:
    body = response.text.strip()
    if not body:
        return "<empty>"
    compact = " ".join(body.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit]}..."
