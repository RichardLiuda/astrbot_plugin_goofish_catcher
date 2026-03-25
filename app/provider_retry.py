from __future__ import annotations

import asyncio
from typing import Any

from .types import ProviderError, ProviderErrorCode


async def search_with_captcha_retry(
    provider: Any,
    *,
    keyword: str,
    pages: int,
    timeout_sec: int,
    captcha_retries: int = 2,
    retry_delay_sec: float = 1.0,
) -> list:
    last_exc: ProviderError | None = None
    total_attempts = max(0, captcha_retries) + 1

    for attempt in range(total_attempts):
        try:
            return await provider.search(
                keyword=keyword,
                pages=pages,
                timeout_sec=timeout_sec,
            )
        except ProviderError as exc:
            if exc.code != ProviderErrorCode.CAPTCHA or attempt >= total_attempts - 1:
                raise
            last_exc = exc
            if retry_delay_sec > 0:
                await asyncio.sleep(retry_delay_sec)

    if last_exc is not None:
        raise last_exc
    return []
