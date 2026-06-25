from __future__ import annotations

import asyncio
import math
from typing import Any

from .types import ProviderError, ProviderErrorCode
from .types import SearchFilters

DEFAULT_CAPTCHA_RETRIES = 2
DEFAULT_CAPTCHA_RETRY_DELAY_SEC = 1.0
DEFAULT_ATTEMPT_TIMEOUT_SLACK_SEC = 10


def estimate_captcha_retry_timeout_sec(
    *,
    timeout_sec: int,
    captcha_retries: int = DEFAULT_CAPTCHA_RETRIES,
    retry_delay_sec: float = DEFAULT_CAPTCHA_RETRY_DELAY_SEC,
    attempt_timeout_slack_sec: int = DEFAULT_ATTEMPT_TIMEOUT_SLACK_SEC,
) -> int:
    total_attempts = max(0, captcha_retries) + 1
    per_attempt_timeout = max(1, timeout_sec) + max(0, attempt_timeout_slack_sec)
    retry_budget_sec = math.ceil(max(0.0, retry_delay_sec) * max(0, total_attempts - 1))
    return max(45, (per_attempt_timeout * total_attempts) + retry_budget_sec)


async def search_with_captcha_retry(
    provider: Any,
    *,
    keyword: str,
    pages: int,
    timeout_sec: int,
    captcha_retries: int = DEFAULT_CAPTCHA_RETRIES,
    retry_delay_sec: float = DEFAULT_CAPTCHA_RETRY_DELAY_SEC,
    filters: SearchFilters | None = None,
    price_lower: float | None = None,
    price_upper: float | None = None,
) -> list:
    last_exc: ProviderError | None = None
    total_attempts = max(0, captcha_retries) + 1

    for attempt in range(total_attempts):
        try:
            return await provider.search(
                keyword=keyword,
                pages=pages,
                timeout_sec=timeout_sec,
                filters=filters,
                price_lower=price_lower,
                price_upper=price_upper,
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
