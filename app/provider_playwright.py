from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any
from urllib.parse import parse_qs, quote, urlparse

from playwright.async_api import Browser, Playwright, TimeoutError, async_playwright
from playwright.async_api import Error as PlaywrightError

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .config import PluginSettings
from .provider import ProviderConfigurationError
from .types import FavoriteItemResult, NormalizedItem, ProviderError, ProviderErrorCode

_PRICE_RE = re.compile(r"(\d+(?:\.\d+)?)")
_DETAIL_FAVORITE_BUTTON_SELECTOR = "div[class*='buttons--'] div[class*='right--']"
_FAVORITE_HINT_TEXT = "收藏"
_FAVORITED_HINT_TEXT = "已收藏"


class PlaywrightSearchProvider:
    BASE_URL = "https://www.goofish.com"

    def __init__(self, settings: PluginSettings) -> None:
        self.settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._init_lock = asyncio.Lock()
        self._operation_lock = asyncio.Lock()
        self._configured_executable_path = self._validate_executable_path()

    def _build_launch_args(self) -> list[str]:
        args = ["--disable-blink-features=AutomationControlled"]
        if self.settings.playwright_force_direct:
            # Force direct egress and bypass system proxy to reduce IP switching.
            args.extend(
                [
                    "--no-proxy-server",
                    "--proxy-server=direct://",
                    "--proxy-bypass-list=*",
                ]
            )
        return args

    def _validate_executable_path(self) -> Path | None:
        executable_path = self.settings.playwright_executable_path
        if executable_path is None:
            return None

        candidate = executable_path.expanduser()
        if not candidate.exists():
            raise ProviderConfigurationError(
                f"playwright_executable_path does not exist: {candidate}"
            )
        if not candidate.is_file():
            raise ProviderConfigurationError(
                f"playwright_executable_path is not a file: {candidate}"
            )
        return candidate

    def _build_launch_kwargs(
        self,
        *,
        executable_path: Path | str | None = None,
    ) -> dict[str, Any]:
        launch_kwargs: dict[str, Any] = {
            "headless": self.settings.playwright_headless,
            "args": self._build_launch_args(),
        }
        if executable_path is not None:
            launch_kwargs["executable_path"] = str(executable_path)
        return launch_kwargs

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def _ensure_browser(self) -> Browser:
        if self._browser is not None:
            return self._browser

        async with self._init_lock:
            if self._browser is not None:
                return self._browser
            playwright = await async_playwright().start()
            if playwright is None:
                raise ProviderError(
                    ProviderErrorCode.UNKNOWN,
                    "playwright start failed",
                    retry_after_sec=300,
                )

            try:
                browser = await playwright.chromium.launch(
                    **self._build_launch_kwargs(
                        executable_path=self._configured_executable_path
                    )
                )
            except PlaywrightError as exc:
                message = str(exc)
                if self._configured_executable_path is not None:
                    await playwright.stop()
                    raise ProviderError(
                        ProviderErrorCode.DEPENDENCY_MISSING,
                        "failed to launch configured playwright executable: "
                        f"{self._configured_executable_path}: {message}",
                        retry_after_sec=1800,
                    ) from exc
                if (
                    self.settings.playwright_headless
                    and "Executable doesn't exist" in message
                    and "chromium_headless_shell" in message
                ):
                    chromium_exec = playwright.chromium.executable_path
                    if chromium_exec and Path(chromium_exec).exists():
                        try:
                            browser = await playwright.chromium.launch(
                                **self._build_launch_kwargs(
                                    executable_path=chromium_exec
                                )
                            )
                        except PlaywrightError as fallback_exc:
                            await playwright.stop()
                            raise ProviderError(
                                ProviderErrorCode.DEPENDENCY_MISSING,
                                "playwright fallback launch failed. Run: "
                                "uv run python -m playwright install",
                                retry_after_sec=1800,
                            ) from fallback_exc
                    else:
                        await playwright.stop()
                        raise ProviderError(
                            ProviderErrorCode.DEPENDENCY_MISSING,
                            "playwright browser executable is missing. Run: "
                            "uv run python -m playwright install chromium chromium-headless-shell",
                            retry_after_sec=3600,
                        ) from exc
                else:
                    await playwright.stop()
                    raise ProviderError(
                        ProviderErrorCode.DEPENDENCY_MISSING,
                        "failed to launch playwright browser. "
                        "Run: uv run python -m playwright install",
                        retry_after_sec=1800,
                    ) from exc
            except Exception:
                await playwright.stop()
                raise
            self._playwright = playwright
            self._browser = browser
            return self._browser

    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
    ) -> list[NormalizedItem]:
        async with self._operation_lock:
            browser = await self._ensure_browser()
            unique: dict[str, NormalizedItem] = {}
            page_count = max(1, pages)
            timeout_ms = max(5, timeout_sec) * 1000

            for page_index in range(1, page_count + 1):
                page_items = await self._fetch_single_page(
                    browser=browser,
                    keyword=keyword,
                    page_index=page_index,
                    timeout_ms=timeout_ms,
                )
                for item in page_items:
                    unique[item.item_id] = item

                if not page_items:
                    break

            return list(unique.values())

    async def favorite_item(
        self,
        *,
        url: str,
        timeout_sec: int,
        item_id: str | None = None,
    ) -> FavoriteItemResult:
        async with self._operation_lock:
            browser = await self._ensure_browser()
            timeout_ms = max(5, timeout_sec) * 1000
            context = await browser.new_context(**self._build_context_kwargs())
            page = await context.new_page()
            if hasattr(page, "set_default_timeout"):
                page.set_default_timeout(timeout_ms)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                await self._maybe_wait_for_network_idle(page, timeout_ms)
                await page.wait_for_timeout(1200)

                page_error = await self._classify_favorite_page_state(page)
                if page_error is not None:
                    raise page_error

                favorite_button = await self._wait_for_favorite_button(page, timeout_ms)
                button_text = await favorite_button.inner_text()
                title = _normalize_item_page_title(await page.title())
                resolved_url = str(getattr(page, "url", "") or url).strip() or url
                resolved_item_id = (
                    (item_id or "").strip()
                    or _extract_item_id_from_url(resolved_url)
                    or _extract_item_id_from_url(url)
                )

                state = _classify_favorite_button_text(button_text)
                if state == "already_favorited":
                    await self._persist_context_storage_state(context)
                    return FavoriteItemResult(
                        status="already_favorited",
                        url=resolved_url,
                        item_id=resolved_item_id or None,
                        title=title or None,
                    )
                if state != "favoritable":
                    raise ProviderError(
                        ProviderErrorCode.PARSE_ERROR,
                        "favorite button state is not recognizable",
                    )

                await favorite_button.click(timeout=max(2500, min(timeout_ms, 8_000)))
                try:
                    await page.wait_for_function(
                        """
                        (selector) => {
                          const el = document.querySelector(selector);
                          if (!el) {
                            return false;
                          }
                          const text = (el.innerText || "").trim();
                          return text.includes("已收藏");
                        }
                        """,
                        arg=_DETAIL_FAVORITE_BUTTON_SELECTOR,
                        timeout=max(2500, min(timeout_ms, 8_000)),
                    )
                except TimeoutError as exc:
                    page_error = await self._classify_favorite_page_state(page)
                    if page_error is not None:
                        raise page_error from exc
                    latest_text = ""
                    try:
                        latest_text = await favorite_button.inner_text()
                    except Exception:
                        latest_text = ""
                    if (
                        _classify_favorite_button_text(latest_text)
                        != "already_favorited"
                    ):
                        raise ProviderError(
                            ProviderErrorCode.TIMEOUT,
                            "favorite button did not switch to collected state in time",
                        ) from exc

                await self._persist_context_storage_state(context)
                return FavoriteItemResult(
                    status="favorited",
                    url=resolved_url,
                    item_id=resolved_item_id or None,
                    title=title or None,
                )
            except TimeoutError as exc:
                timeout_error = await self._classify_timeout_page_state(page)
                if timeout_error is not None:
                    raise timeout_error from exc
                raise ProviderError(
                    ProviderErrorCode.TIMEOUT,
                    f"playwright timeout while favoriting item: {exc}",
                ) from exc
            except PlaywrightError as exc:
                raise ProviderError(
                    ProviderErrorCode.UNKNOWN,
                    f"playwright page error: {exc}",
                    retry_after_sec=300,
                ) from exc
            finally:
                await context.close()

    def _build_context_kwargs(self) -> dict[str, Any]:
        context_kwargs: dict[str, Any] = {
            "viewport": {"width": 1280, "height": 800},
        }
        if self.settings.playwright_storage_state_path is not None:
            storage_path: Path = self.settings.playwright_storage_state_path
            if storage_path.exists():
                context_kwargs["storage_state"] = str(storage_path)
        return context_kwargs

    async def _fetch_single_page(
        self,
        *,
        browser: Browser,
        keyword: str,
        page_index: int,
        timeout_ms: int,
    ) -> list[NormalizedItem]:
        context = await browser.new_context(**self._build_context_kwargs())
        page = await context.new_page()
        captured_payloads: list[dict[str, Any] | list[Any]] = []
        error_flags: set[str] = set()

        if self.settings.playwright_block_assets:
            await context.route("**/*", _route_handler)

        async def on_response(response) -> None:
            url = response.url.lower()
            content_type = (response.headers.get("content-type") or "").lower()

            if "captcha" in url:
                error_flags.add("captcha")
            # Only treat auth as failure when main document is redirected to login.
            # Static subresources from passport domains are common even in valid sessions.
            if response.request.resource_type == "document" and response.status in {
                301,
                302,
                303,
                307,
                308,
            }:
                location = (response.headers.get("location") or "").lower()
                if "login" in location or "passport" in location:
                    error_flags.add("auth")

            if "json" not in content_type:
                return

            try:
                payload = await response.json()
            except Exception:
                try:
                    text = await response.text()
                except Exception:
                    return
                lowered = text.lower()
                if "被挤爆" in text or "rate limit" in lowered:
                    error_flags.add("rate_limited")
                if "captcha" in lowered or "验证码" in text or "滑块" in text:
                    error_flags.add("captcha")
                return

            if isinstance(payload, (dict, list)):
                captured_payloads.append(payload)

        page.on("response", on_response)
        search_url = self._build_search_url(keyword=keyword)

        try:
            await page.goto(
                search_url, wait_until="domcontentloaded", timeout=timeout_ms
            )
            await self._maybe_wait_for_network_idle(page, timeout_ms)
            current_url = page.url.lower()
            if "login" in current_url or "passport" in current_url:
                raise ProviderError(
                    ProviderErrorCode.AUTH_REQUIRED,
                    "goofish redirected to login page",
                )
            html = await page.content()
            if "验证码" in html or "captcha" in html.lower() or "滑块" in html:
                raise ProviderError(
                    ProviderErrorCode.CAPTCHA,
                    "captcha detected on goofish page",
                )

            if page_index > 1:
                # Goofish keeps the browser URL stable and drives pagination
                # through the bottom pager + search API payload pageNumber.
                await self._wait_for_items_ready(
                    page=page,
                    captured_payloads=captured_payloads,
                    timeout_ms=timeout_ms,
                )
                captured_payloads.clear()
                await self._navigate_to_page_index(
                    page=page,
                    page_index=page_index,
                    timeout_ms=timeout_ms,
                )
                await self._maybe_wait_for_network_idle(page, timeout_ms)

            items = await self._wait_for_items_ready(
                page=page,
                captured_payloads=captured_payloads,
                timeout_ms=timeout_ms,
            )

            if not items and "rate_limited" in error_flags:
                raise ProviderError(
                    ProviderErrorCode.RATE_LIMITED,
                    "goofish rate limited current request",
                    retry_after_sec=60,
                )

            if "captcha" in error_flags:
                raise ProviderError(
                    ProviderErrorCode.CAPTCHA,
                    "captcha response detected",
                )
            if "auth" in error_flags:
                raise ProviderError(
                    ProviderErrorCode.AUTH_REQUIRED,
                    "authentication required by goofish",
                )
            if not items:
                logger.info(
                    "[goofish_catcher] page=%s no items after wait, payloads=%s",
                    page_index,
                    len(captured_payloads),
                )
            await self._persist_context_storage_state(context)
            return items
        except TimeoutError as exc:
            timeout_error = await self._classify_timeout_page_state(page)
            if timeout_error is not None:
                raise timeout_error from exc
            raise ProviderError(
                ProviderErrorCode.TIMEOUT,
                f"playwright timeout while fetching page {page_index}: {exc}",
            ) from exc
        except PlaywrightError as exc:
            raise ProviderError(
                ProviderErrorCode.UNKNOWN,
                f"playwright page error: {exc}",
                retry_after_sec=300,
            ) from exc
        finally:
            await context.close()

    async def _persist_context_storage_state(self, context) -> None:
        storage_path = self.settings.playwright_storage_state_path
        if storage_path is None:
            return
        try:
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(storage_path))
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] failed to persist storage_state to %s: %s",
                storage_path,
                exc,
            )

    async def _wait_for_favorite_button(self, page, timeout_ms: int):
        wait_timeout_ms = max(2500, min(timeout_ms, 10_000))
        await page.wait_for_selector(
            _DETAIL_FAVORITE_BUTTON_SELECTOR,
            timeout=wait_timeout_ms,
        )
        return page.locator(_DETAIL_FAVORITE_BUTTON_SELECTOR).first

    async def _classify_favorite_page_state(self, page) -> ProviderError | None:
        return await self._classify_timeout_page_state(page)

    def _build_search_url(self, *, keyword: str) -> str:
        return f"{self.BASE_URL}/search?q={quote(keyword)}"

    async def _navigate_to_page_index(
        self,
        *,
        page,
        page_index: int,
        timeout_ms: int,
    ) -> None:
        pager_timeout_ms = max(2500, min(10000, timeout_ms // 2))
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await page.wait_for_timeout(600)
        await page.wait_for_selector(
            "div[class*='search-pagination-page-box'], "
            "input[class*='search-pagination-to-page-input']",
            timeout=pager_timeout_ms,
        )

        target_text = str(page_index)
        page_boxes = page.locator("div[class*='search-pagination-page-box']")
        target = None
        for idx in range(await page_boxes.count()):
            candidate = page_boxes.nth(idx)
            try:
                if (await candidate.inner_text()).strip() == target_text:
                    target = candidate
                    break
            except Exception:
                continue

        if target is not None:
            await target.click(timeout=pager_timeout_ms)
        else:
            page_input = page.locator(
                "input[class*='search-pagination-to-page-input']"
            ).first
            confirm_button = page.locator(
                "button[class*='search-pagination-to-page-confirm-button']"
            ).first
            await page_input.fill(target_text, timeout=pager_timeout_ms)
            await confirm_button.click(timeout=pager_timeout_ms)

        await page.wait_for_function(
            """
            (pageIndex) => {
              const active = document.querySelector(
                "div[class*='search-pagination-page-box-active']"
              );
              return active && active.innerText.trim() === String(pageIndex);
            }
            """,
            arg=page_index,
            timeout=pager_timeout_ms,
        )
        await page.wait_for_timeout(600)

    async def _extract_items_from_dom(self, page) -> list[NormalizedItem]:
        try:
            cards = await page.eval_on_selector_all(
                "a[href*='item']",
                """
                (nodes) => {
                  return nodes.slice(0, 80).map((node) => {
                    const href = node.href || node.getAttribute('href') || '';
                    const text = (node.innerText || '').trim();
                    const lines = text.split('\\n').map((line) => line.trim()).filter(Boolean);
                    return {
                      href,
                      text,
                      title: lines[0] || ''
                    };
                  });
                }
                """,
            )
        except Exception:
            return []

        items: list[NormalizedItem] = []
        seen: set[str] = set()
        for card in cards:
            if not isinstance(card, dict):
                continue
            url = _normalize_url(card.get("href"), self.BASE_URL)
            if not url:
                continue
            item_id = _extract_item_id_from_url(url)
            title = str(card.get("title", "")).strip()
            price = _parse_price(card.get("text"))
            if not item_id or not title or price is None:
                continue
            if item_id in seen:
                continue
            seen.add(item_id)
            items.append(
                NormalizedItem(
                    item_id=item_id,
                    title=title,
                    price=price,
                    url=url,
                    publish_time=None,
                    raw=card,
                )
            )
        return items

    async def _maybe_wait_for_network_idle(self, page, timeout_ms: int) -> None:
        idle_timeout = max(1200, min(6000, timeout_ms // 3))
        try:
            await page.wait_for_load_state("networkidle", timeout=idle_timeout)
        except Exception:
            await page.wait_for_timeout(min(1800, idle_timeout))

    async def _classify_timeout_page_state(self, page) -> ProviderError | None:
        try:
            current_url = str(getattr(page, "url", "") or "").lower()
        except Exception:
            current_url = ""
        if "login" in current_url or "passport" in current_url:
            return ProviderError(
                ProviderErrorCode.AUTH_REQUIRED,
                "goofish redirected to login page",
            )
        if "captcha" in current_url:
            return ProviderError(
                ProviderErrorCode.CAPTCHA,
                "captcha detected on goofish page",
            )

        try:
            html = await page.content()
        except Exception:
            html = ""
        lowered = html.lower()
        if "验证码" in html or "滑块" in html or "captcha" in lowered:
            return ProviderError(
                ProviderErrorCode.CAPTCHA,
                "captcha detected on goofish page",
            )
        if "登录" in html or "login" in lowered or "passport" in lowered:
            return ProviderError(
                ProviderErrorCode.AUTH_REQUIRED,
                "goofish redirected to login page",
            )
        return None

    async def _wait_for_items_ready(
        self,
        *,
        page,
        captured_payloads: list[dict[str, Any] | list[Any]],
        timeout_ms: int,
    ) -> list[NormalizedItem]:
        wait_budget_ms = max(2000, min(12000, int(timeout_ms * 0.65)))
        deadline = monotonic() + (wait_budget_ms / 1000.0)
        poll_ms = 350
        last_dom_count = -1
        stable_rounds = 0
        loop_count = 0

        while monotonic() < deadline:
            payload_items = self._extract_items_from_payloads(captured_payloads)
            if payload_items:
                return payload_items

            dom_items = await self._extract_items_from_dom(page)
            dom_count = len(dom_items)
            if dom_count > 0:
                if dom_count == last_dom_count:
                    stable_rounds += 1
                else:
                    stable_rounds = 0
                # Either enough cards, or count stabilized for a while.
                if dom_count >= 6 or stable_rounds >= 2:
                    return dom_items
            last_dom_count = dom_count

            loop_count += 1
            if loop_count % 2 == 0:
                try:
                    await page.evaluate(
                        "window.scrollBy(0, Math.max(window.innerHeight, 900));"
                    )
                except Exception:
                    pass
            await page.wait_for_timeout(poll_ms)

        payload_items = self._extract_items_from_payloads(captured_payloads)
        if payload_items:
            return payload_items
        return await self._extract_items_from_dom(page)

    def _extract_items_from_payloads(
        self, payloads: list[dict[str, Any] | list[Any]]
    ) -> list[NormalizedItem]:
        results: list[NormalizedItem] = []
        seen: set[str] = set()
        stack: list[Any] = list(payloads)

        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                normalized = self._normalize_item_candidate(node)
                if normalized and normalized.item_id not in seen:
                    seen.add(normalized.item_id)
                    results.append(normalized)
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, (dict, list)):
                        stack.append(item)
        return results

    def _normalize_item_candidate(self, data: dict[str, Any]) -> NormalizedItem | None:
        title = _pick_first_text(
            data,
            ("title", "item_title", "name", "itemName", "subject"),
        )
        if not title:
            return None

        url = _normalize_url(
            _pick_first_text(data, ("url", "item_url", "detail_url", "jumpUrl")),
            self.BASE_URL,
        )

        item_id = _pick_first_text(
            data,
            ("item_id", "itemId", "id", "auctionId", "targetId", "itemid"),
        )
        if not item_id and url:
            item_id = _extract_item_id_from_url(url)
        if not item_id:
            return None

        price = _extract_price(data)
        if price is None:
            return None

        if not url:
            url = f"{self.BASE_URL}/item?id={item_id}"

        publish_time = _extract_publish_time(data)
        return NormalizedItem(
            item_id=item_id,
            title=title,
            price=price,
            url=url,
            publish_time=publish_time,
            raw=data,
        )


async def _route_handler(route) -> None:
    if route.request.resource_type in {"image", "font", "media"}:
        await route.abort()
        return
    await route.continue_()


def _pick_first_text(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        if key not in data:
            continue
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _normalize_url(url: Any, base_url: str) -> str | None:
    if url is None:
        return None
    text = str(url).strip()
    if not text:
        return None
    if text.startswith("//"):
        return "https:" + text
    if text.startswith("/"):
        return base_url + text
    return text


def _extract_item_id_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in ("id", "item_id", "itemId", "auctionId"):
        values = query.get(key)
        if not values:
            continue
        value = str(values[0]).strip()
        if value:
            return value

    match = re.search(r"item(?:_id)?[=/](\d+)", url)
    if match:
        return match.group(1)
    return None


def _classify_favorite_button_text(text: str) -> str:
    normalized = str(text or "").strip()
    if _FAVORITED_HINT_TEXT in normalized:
        return "already_favorited"
    if _FAVORITE_HINT_TEXT in normalized:
        return "favoritable"
    return "unknown"


def _normalize_item_page_title(title: str) -> str:
    text = str(title or "").strip()
    if text.endswith("_闲鱼"):
        text = text[: -len("_闲鱼")].strip()
    if text.endswith(" - 闲不住？上闲鱼！"):
        text = ""
    return text


def _extract_price(data: dict[str, Any]) -> float | None:
    candidate_keys = (
        "price",
        "current_price",
        "currentPrice",
        "displayPrice",
        "priceText",
        "amount",
        "salePrice",
        "finalPrice",
    )

    for key in candidate_keys:
        if key not in data:
            continue
        parsed = _parse_price(data.get(key))
        if parsed is not None:
            return parsed

    for key in ("priceInfo", "tradePrice", "item_price", "price_data"):
        if key not in data:
            continue
        parsed = _parse_price(data.get(key))
        if parsed is not None:
            return parsed
    return None


def _parse_price(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        lowered = text.lower()
        multiplier = 1.0
        if "万" in text or re.search(r"\d(?:\.\d+)?\s*w", lowered):
            multiplier = 10_000.0
        elif "千" in text or re.search(r"\d(?:\.\d+)?\s*k", lowered):
            multiplier = 1_000.0
        match = _PRICE_RE.search(text)
        if not match:
            return None
        try:
            return float(match.group(1)) * multiplier
        except ValueError:
            return None
    if isinstance(value, dict):
        for key in ("price", "amount", "value", "text", "display", "priceText"):
            if key in value:
                parsed = _parse_price(value.get(key))
                if parsed is not None:
                    return parsed
        return None
    if isinstance(value, list):
        for item in value:
            parsed = _parse_price(item)
            if parsed is not None:
                return parsed
    return None


def _extract_publish_time(data: dict[str, Any]) -> int | None:
    for key in (
        "publish_time",
        "publishTime",
        "create_time",
        "createTime",
        "gmtCreate",
        "ctime",
        "time",
    ):
        if key not in data:
            continue
        parsed = _parse_timestamp(data.get(key))
        if parsed is not None:
            return parsed
    return None


def _parse_timestamp(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        ts = int(value)
        if ts > 10_000_000_000:
            ts = ts // 1000
        return ts if ts > 0 else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            ts = int(text)
            if ts > 10_000_000_000:
                ts = ts // 1000
            return ts if ts > 0 else None
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        return int(dt.timestamp())
    return None
