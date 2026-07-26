from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any
from urllib.parse import parse_qs, quote, urlparse

from playwright.async_api import (
    Browser,
    BrowserContext,
    Playwright,
    TimeoutError,
    async_playwright,
)
from playwright.async_api import Error as PlaywrightError

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .config import PluginSettings
from .login_session import BASE_LAUNCH_ARGS, ensure_virtual_display
from .provider import ProviderConfigurationError
from .provider_agent import (
    extract_items_via_llm,
    check_login_via_llm,
    find_favorite_button_via_llm,
)
from .types import (
    DeepAnalysisResult,
    FavoriteItemResult,
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
    SearchFilters,
)

_PRICE_RE = re.compile(r"(\d+(?:\.\d+)?)")
_DETAIL_FAVORITE_BUTTON_SELECTOR = "div[class*='buttons--'] div[class*='right--']"
_FAVORITE_HINT_TEXT = "收藏"
_FAVORITED_HINT_TEXT = "已收藏"
_EMBEDDED_LOGIN_MARKERS = (
    "passport.goofish.com/mini_login.htm",
    "alibaba-login-box",
)


class PlaywrightSearchProvider:
    BASE_URL = "https://www.goofish.com"

    def __init__(self, settings: PluginSettings, *, llm_call=None) -> None:
        self.settings = settings
        # Optional: async callable(prompt: str, system_prompt: str) -> str
        # Injected by the plugin main to enable AX-tree-based LLM fallback
        # when CSS selectors break after a Goofish frontend update.
        self._llm_call = llm_call
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._persistent_context: BrowserContext | None = None
        self._init_lock = asyncio.Lock()
        self._operation_lock = asyncio.Lock()
        self._configured_executable_path = self._validate_executable_path()

    async def _ensure_display_for_headed_mode(self) -> None:
        """Headed 模式下确保有可用的 DISPLAY（无桌面环境时自动拉起 Xvfb）。

        headless 模式不需要 X server，直接跳过 —— 否则未装 Xvfb 的机器上
        headless 抓取也会被误判为缺依赖。to_thread：Xvfb 启动失败路径最长可
        阻塞 ~20s，不能卡事件循环。OSError 覆盖 Popen 本身失败（如容器内存
        紧张时 fork 报 ENOMEM）。
        """
        if self.settings.playwright_headless:
            return
        try:
            await asyncio.to_thread(ensure_virtual_display)
        except (RuntimeError, OSError) as exc:
            raise ProviderError(
                ProviderErrorCode.DEPENDENCY_MISSING,
                str(exc),
                retry_after_sec=1800,
            ) from exc

    def _build_launch_args(self) -> list[str]:
        # 基础 args（含 Docker /dev/shm 与 Xvfb 无 GPU 的 workaround）统一定义在
        # login_session.BASE_LAUNCH_ARGS，注释也在那里。
        args = list(BASE_LAUNCH_ARGS)
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
        proxy_server = getattr(self.settings, "playwright_proxy", None)
        if proxy_server:
            # When an upstream proxy is configured it takes priority over the
            # force_direct (--no-proxy-server) flags in _build_launch_args.
            launch_kwargs["proxy"] = {"server": proxy_server}
        return launch_kwargs

    async def export_storage_state(self) -> dict[str, Any] | None:
        """Export the current browser session's cookies/localStorage as an in-memory dict.

        Used by GofishBrowserAgent to inherit login state without sharing the
        user_data_dir file lock (Chromium only allows one process per directory).

        Returns None when no session is available.
        """
        # Preferred: live context export (most up-to-date cookies)
        if self._persistent_context is not None:
            try:
                return await self._persistent_context.storage_state()
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher] export_storage_state from context failed: %s", exc
                )

        # Fallback: read from the persisted storage_state.json file
        state_path = self.settings.playwright_storage_state_path
        if state_path is not None and state_path.exists():
            import json as _json
            try:
                return _json.loads(state_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher] export_storage_state from file failed: %s", exc
                )

        return None

    async def close(self) -> None:
        if self._persistent_context is not None:
            try:
                await self._persistent_context.close()
            except Exception:
                pass
            self._persistent_context = None
            self._browser = None
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    async def adopt_login_session(self, session) -> None:
        runtime = session.detach_runtime()
        context = runtime.get("context")
        playwright = runtime.get("playwright")
        browser = runtime.get("browser")
        if context is None or playwright is None:
            raise RuntimeError("login session runtime is not available for adoption")

        await self.close()
        self._playwright = playwright
        self._browser = browser
        self._persistent_context = context
        logger.info(
            "[goofish_catcher] adopted live login browser session into provider"
        )

    async def _ensure_persistent_context(self) -> BrowserContext:
        if self._persistent_context is not None:
            return self._persistent_context

        user_data_dir = self.settings.playwright_user_data_dir
        if user_data_dir is None:
            raise RuntimeError("persistent context requested without user_data_dir")

        async with self._init_lock:
            if self._persistent_context is not None:
                return self._persistent_context
            await self._ensure_display_for_headed_mode()
            playwright = await async_playwright().start()
            if playwright is None:
                raise ProviderError(
                    ProviderErrorCode.UNKNOWN,
                    "playwright start failed",
                    retry_after_sec=300,
                )

            launch_kwargs = self._build_launch_kwargs(
                executable_path=self._configured_executable_path
            )
            try:
                user_data_dir.mkdir(parents=True, exist_ok=True)
                context = await playwright.chromium.launch_persistent_context(
                    str(user_data_dir),
                    viewport={"width": 1280, "height": 800},
                    **launch_kwargs,
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
                await playwright.stop()
                raise ProviderError(
                    ProviderErrorCode.DEPENDENCY_MISSING,
                    "failed to launch persistent playwright browser. "
                    "Run: uv run python -m playwright install",
                    retry_after_sec=1800,
                ) from exc
            except Exception:
                await playwright.stop()
                raise

            self._playwright = playwright
            self._persistent_context = context
            self._browser = context.browser
            return context

    async def _ensure_browser(self) -> Browser:
        if self.settings.playwright_user_data_dir is not None:
            context = await self._ensure_persistent_context()
            browser = context.browser
            if browser is None:
                raise ProviderError(
                    ProviderErrorCode.UNKNOWN,
                    "persistent playwright context does not expose browser handle",
                    retry_after_sec=300,
                )
            return browser
        if self._browser is not None:
            return self._browser

        async with self._init_lock:
            if self._browser is not None:
                return self._browser
            # 当前配置下不可达（PLAYWRIGHT_LOCAL 模式必设 user_data_dir，见
            # config.py），但保持与持久化分支一致：headed 模式同样需要虚拟显示。
            await self._ensure_display_for_headed_mode()
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

    async def _open_operation_context(self) -> tuple[BrowserContext, bool]:
        if self.settings.playwright_user_data_dir is not None:
            return await self._ensure_persistent_context(), False

        browser = await self._ensure_browser()
        return await browser.new_context(**self._build_context_kwargs()), True

    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
        filters: SearchFilters | None = None,
        price_lower: float | None = None,
        price_upper: float | None = None,
    ) -> list[NormalizedItem]:
        async with self._operation_lock:
            effective_filters = (filters or SearchFilters(
                price_lower=price_lower,
                price_upper=price_upper,
            )).normalized()
            browser = None
            if self.settings.playwright_user_data_dir is None:
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
                    filters=effective_filters,
                )
                for item in page_items:
                    unique[item.item_id] = item

                if not page_items:
                    break

            return list(unique.values())

    async def analyze_item_detail(
        self,
        *,
        item: NormalizedItem,
        timeout_sec: int,
    ) -> DeepAnalysisResult:
        async with self._operation_lock:
            timeout_ms = max(5, timeout_sec) * 1000
            context, should_close_context = await self._open_operation_context()
            page = await context.new_page()
            captured_payloads: list[dict[str, Any] | list[Any]] = []
            error_flags: set[str] = set()
            self._attach_page_state_watchers(page, error_flags)

            async def on_response(response) -> None:
                url = response.url.lower()
                content_type = (response.headers.get("content-type") or "").lower()
                if _is_auth_url(url):
                    error_flags.add("auth")
                if _is_captcha_url(url):
                    error_flags.add("captcha")
                if "json" not in content_type:
                    return
                try:
                    payload = await response.json()
                except Exception:
                    return
                if isinstance(payload, (dict, list)):
                    captured_payloads.append(payload)

            page.on("response", on_response)
            try:
                await page.goto(item.url, wait_until="domcontentloaded", timeout=timeout_ms)
                await self._maybe_wait_for_network_idle(page, timeout_ms)
                await page.wait_for_timeout(1000)
                page_error = await self._classify_timeout_page_state(
                    page,
                    error_flags=error_flags,
                )
                if page_error is not None:
                    raise page_error
                detail = _build_deep_analysis_result(
                    item=item,
                    payloads=captured_payloads,
                    page_title=_normalize_item_page_title(await page.title()),
                )
                await self._persist_context_storage_state(context)
                return detail
            except TimeoutError as exc:
                timeout_error = await self._classify_timeout_page_state(
                    page,
                    error_flags=error_flags,
                )
                if timeout_error is not None:
                    raise timeout_error from exc
                raise ProviderError(
                    ProviderErrorCode.TIMEOUT,
                    f"playwright timeout while analyzing item detail: {exc}",
                ) from exc
            except PlaywrightError as exc:
                raise ProviderError(
                    ProviderErrorCode.UNKNOWN,
                    f"playwright detail page error: {exc}",
                    retry_after_sec=300,
                ) from exc
            finally:
                if callable(getattr(page, "close", None)):
                    await page.close()
                if should_close_context:
                    await context.close()

    async def favorite_item(
        self,
        *,
        url: str,
        timeout_sec: int,
        item_id: str | None = None,
    ) -> FavoriteItemResult:
        async with self._operation_lock:
            timeout_ms = max(5, timeout_sec) * 1000
            context, should_close_context = await self._open_operation_context()
            page = await context.new_page()
            error_flags: set[str] = set()
            self._attach_page_state_watchers(page, error_flags)
            logger.info(
                "[goofish_catcher] favorite start: url=%s item_id=%s persistent_profile=%s storage_state=%s",
                url,
                item_id or "-",
                str(self.settings.playwright_user_data_dir)
                if self.settings.playwright_user_data_dir is not None
                else "-",
                str(self.settings.playwright_storage_state_path)
                if self.settings.playwright_storage_state_path is not None
                else "-",
            )
            if hasattr(page, "set_default_timeout"):
                page.set_default_timeout(timeout_ms)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                await self._maybe_wait_for_network_idle(page, timeout_ms)
                await page.wait_for_timeout(1200)
                logger.info(
                    "[goofish_catcher] favorite after goto: page_url=%s flags=%s frames=%s",
                    str(getattr(page, "url", "") or ""),
                    sorted(error_flags),
                    _collect_frame_urls(page),
                )

                page_error = await self._classify_favorite_page_state(
                    page,
                    error_flags=error_flags,
                )
                if (
                    page_error is not None
                    and page_error.code == ProviderErrorCode.AUTH_REQUIRED
                ):
                    logger.info(
                        "[goofish_catcher] favorite AUTH_REQUIRED detected, attempting quick login: url=%s flags=%s frames=%s",
                        str(getattr(page, "url", "") or ""),
                        sorted(error_flags),
                        _collect_frame_urls(page),
                    )
                    if await self._try_quick_login(page, context):
                        error_flags.clear()
                        await page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=timeout_ms,
                        )
                        await self._maybe_wait_for_network_idle(page, timeout_ms)
                        await page.wait_for_timeout(1000)
                        page_error = await self._classify_favorite_page_state(
                            page,
                            error_flags=error_flags,
                        )
                        logger.info(
                            "[goofish_catcher] favorite after quick login reload: page_url=%s page_error=%s flags=%s frames=%s",
                            str(getattr(page, "url", "") or ""),
                            page_error.code.value if page_error else None,
                            sorted(error_flags),
                            _collect_frame_urls(page),
                        )
                if page_error is not None:
                    logger.warning(
                        "[goofish_catcher] favorite page rejected before button: url=%s code=%s message=%s flags=%s frames=%s",
                        str(getattr(page, "url", "") or ""),
                        page_error.code.value,
                        page_error.message,
                        sorted(error_flags),
                        _collect_frame_urls(page),
                    )
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
                logger.info(
                    "[goofish_catcher] favorite button detected: item_id=%s button_text=%s title=%s url=%s",
                    resolved_item_id or "-",
                    button_text.strip(),
                    title or "-",
                    resolved_url,
                )

                state = _classify_favorite_button_text(button_text)
                if state == "already_favorited":
                    await self._persist_context_storage_state(context)
                    logger.info(
                        "[goofish_catcher] favorite idempotent success: item_id=%s url=%s",
                        resolved_item_id or "-",
                        resolved_url,
                    )
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
                logger.info(
                    "[goofish_catcher] favorite click issued: item_id=%s url=%s",
                    resolved_item_id or "-",
                    resolved_url,
                )
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
                    page_error = await self._classify_favorite_page_state(
                        page,
                        error_flags=error_flags,
                    )
                    if (
                        page_error is not None
                        and page_error.code == ProviderErrorCode.AUTH_REQUIRED
                    ):
                        logger.info(
                            "[goofish_catcher] favorite AUTH_REQUIRED after click, attempting quick login: url=%s flags=%s frames=%s",
                            str(getattr(page, "url", "") or ""),
                            sorted(error_flags),
                            _collect_frame_urls(page),
                        )
                        if await self._try_quick_login(page, context):
                            error_flags.clear()
                            await page.goto(
                                url,
                                wait_until="domcontentloaded",
                                timeout=timeout_ms,
                            )
                            await self._maybe_wait_for_network_idle(page, timeout_ms)
                            await page.wait_for_timeout(1000)
                            favorite_button = await self._wait_for_favorite_button(
                                page,
                                timeout_ms,
                            )
                            latest_text = await favorite_button.inner_text()
                            if (
                                _classify_favorite_button_text(latest_text)
                                == "already_favorited"
                            ):
                                await self._persist_context_storage_state(context)
                                return FavoriteItemResult(
                                    status="already_favorited",
                                    url=str(getattr(page, "url", "") or url).strip() or url,
                                    item_id=resolved_item_id or None,
                                    title=title or None,
                                )
                            page_error = await self._classify_favorite_page_state(
                                page,
                                error_flags=error_flags,
                            )
                    if page_error is not None:
                        logger.warning(
                            "[goofish_catcher] favorite page rejected after click: url=%s code=%s message=%s flags=%s frames=%s",
                            str(getattr(page, "url", "") or ""),
                            page_error.code.value,
                            page_error.message,
                            sorted(error_flags),
                            _collect_frame_urls(page),
                        )
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
                logger.info(
                    "[goofish_catcher] favorite success: item_id=%s url=%s final_button=%s",
                    resolved_item_id or "-",
                    resolved_url,
                    (await favorite_button.inner_text()).strip(),
                )
                return FavoriteItemResult(
                    status="favorited",
                    url=resolved_url,
                    item_id=resolved_item_id or None,
                    title=title or None,
                )
            except TimeoutError as exc:
                timeout_error = await self._classify_timeout_page_state(
                    page,
                    error_flags=error_flags,
                )
                if timeout_error is not None:
                    logger.warning(
                        "[goofish_catcher] favorite timeout classified: page_url=%s code=%s message=%s flags=%s frames=%s",
                        str(getattr(page, "url", "") or ""),
                        timeout_error.code.value,
                        timeout_error.message,
                        sorted(error_flags),
                        _collect_frame_urls(page),
                    )
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
                if callable(getattr(page, "close", None)):
                    await page.close()
                if should_close_context:
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
        browser: Browser | None,
        keyword: str,
        page_index: int,
        timeout_ms: int,
        filters: SearchFilters | None = None,
    ) -> list[NormalizedItem]:
        del browser
        context, should_close_context = await self._open_operation_context()
        page = await context.new_page()
        captured_payloads: list[dict[str, Any] | list[Any]] = []
        error_flags: set[str] = set()
        self._attach_page_state_watchers(page, error_flags)

        if self.settings.playwright_block_assets:
            await page.route("**/*", _route_handler)

        async def on_response(response) -> None:
            url = response.url.lower()
            content_type = (response.headers.get("content-type") or "").lower()

            if "captcha" in url:
                error_flags.add("captcha")
            if _is_auth_url(url):
                error_flags.add("auth")
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

            if isinstance(payload, dict):
                if _payload_requires_login(payload):
                    error_flags.add("auth")
                if _payload_indicates_captcha(payload):
                    error_flags.add("captcha")
                captured_payloads.append(payload)
                return
            if isinstance(payload, list):
                captured_payloads.append(payload)

        page.on("response", on_response)
        filters = (filters or SearchFilters()).normalized()
        search_url = self._build_search_url(
            keyword=keyword,
            price_lower=filters.price_lower,
            price_upper=filters.price_upper,
        )

        try:
            await page.goto(
                search_url, wait_until="domcontentloaded", timeout=timeout_ms
            )
            await self._maybe_wait_for_network_idle(page, timeout_ms)
            page_error = await self._classify_timeout_page_state(
                page,
                error_flags=error_flags,
            )
            if page_error is not None and page_error.code == ProviderErrorCode.AUTH_REQUIRED:
                logger.info(
                    "[goofish_catcher] page=%s AUTH_REQUIRED detected, error_flags=%s, attempting quick login",
                    page_index, error_flags,
                )
                if await self._try_quick_login(page, context):
                    # 快速进入成功：清除所有登录前积累的 error_flags（包括登录页
                    # 自身触发的 captcha 初始化脚本误报），重新 goto 重新触发搜索 API
                    captured_payloads.clear()
                    error_flags.discard("auth")
                    error_flags.discard("captcha")
                    logger.info(
                        "[goofish_catcher] page=%s quick login OK, reloading search url, error_flags now=%s",
                        page_index, error_flags,
                    )
                    await page.goto(
                        search_url, wait_until="domcontentloaded", timeout=timeout_ms
                    )
                    await self._maybe_wait_for_network_idle(page, timeout_ms)
                    page_error = await self._classify_timeout_page_state(
                        page, error_flags=error_flags
                    )
                    logger.info(
                        "[goofish_catcher] page=%s after reload: page_error=%s error_flags=%s",
                        page_index,
                        page_error.code.value if page_error else None,
                        error_flags,
                    )
                else:
                    logger.warning(
                        "[goofish_catcher] page=%s quick login FAILED, error_flags=%s",
                        page_index, error_flags,
                    )
            if page_error is not None:
                raise page_error

            await self._apply_search_filters(
                page=page,
                filters=filters,
                captured_payloads=captured_payloads,
                timeout_ms=timeout_ms,
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
                page_available = await self._navigate_to_page_index(
                    page=page,
                    page_index=page_index,
                    timeout_ms=timeout_ms,
                )
                if not page_available:
                    logger.info(
                        "[goofish_catcher] page=%s not available for keyword=%s",
                        page_index,
                        keyword,
                    )
                    await self._persist_context_storage_state(context)
                    return []
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
                logger.info(
                    "[goofish_catcher] page=%s auth flag set after item wait, error_flags=%s, attempting quick login",
                    page_index, error_flags,
                )
                if not await self._try_quick_login(page, context):
                    logger.warning(
                        "[goofish_catcher] page=%s quick login FAILED (post-wait), error_flags=%s",
                        page_index, error_flags,
                    )
                    raise ProviderError(
                        ProviderErrorCode.AUTH_REQUIRED,
                        "authentication required by goofish",
                    )
                # 快速进入成功：清除登录前积累的所有 error_flags，重新 goto 重新抓取
                error_flags.discard("auth")
                error_flags.discard("captcha")
                captured_payloads.clear()
                logger.info(
                    "[goofish_catcher] page=%s quick login OK (post-wait), reloading, error_flags now=%s",
                    page_index, error_flags,
                )
                await page.goto(
                    search_url, wait_until="domcontentloaded", timeout=timeout_ms
                )
                await self._maybe_wait_for_network_idle(page, timeout_ms)
                await self._apply_search_filters(
                    page=page,
                    filters=filters,
                    captured_payloads=captured_payloads,
                    timeout_ms=timeout_ms,
                )
                items = await self._wait_for_items_ready(
                    page=page,
                    captured_payloads=captured_payloads,
                    timeout_ms=timeout_ms,
                )
                logger.info(
                    "[goofish_catcher] page=%s after quick-login reload: items=%s",
                    page_index, len(items),
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
            if callable(getattr(page, "close", None)):
                await page.close()
            if should_close_context:
                await context.close()

    async def _apply_search_filters(
        self,
        *,
        page,
        filters: SearchFilters,
        captured_payloads: list[dict[str, Any] | list[Any]],
        timeout_ms: int,
    ) -> None:
        """Best-effort UI filters. Search still succeeds if Goofish changes selectors."""
        if not (
            filters.personal_only
            or filters.free_shipping
            or filters.new_publish_option
            or filters.region
        ):
            return
        timeout = max(1500, min(6000, timeout_ms // 3))

        async def _click_text(text: str, *, exact: bool = True) -> bool:
            try:
                locator = page.get_by_text(text, exact=exact).first
                if await locator.count() <= 0:
                    return False
                captured_payloads.clear()
                await locator.click(timeout=timeout)
                await page.wait_for_timeout(900)
                return True
            except Exception as exc:
                logger.debug("[goofish_catcher] search filter click failed text=%r: %s", text, exc)
                return False

        if filters.new_publish_option:
            if await _click_text("新发布"):
                await _click_text(filters.new_publish_option, exact=False)

        if filters.personal_only:
            await _click_text("个人闲置")

        if filters.free_shipping:
            await _click_text("包邮")

        if filters.region:
            await self._apply_region_filter(page, filters.region, captured_payloads, timeout)

        await self._maybe_wait_for_network_idle(page, timeout_ms)

    async def _apply_region_filter(
        self,
        page,
        region: str,
        captured_payloads: list[dict[str, Any] | list[Any]],
        timeout_ms: int,
    ) -> None:
        parts = [part.strip() for part in str(region or "").split("/") if part.strip()]
        if not parts:
            return
        try:
            trigger = page.get_by_text("区域", exact=True).first
            if await trigger.count() <= 0:
                return
            await trigger.click(timeout=timeout_ms)
            await page.wait_for_timeout(800)
            popover = page.locator("div.ant-popover").last
            if await popover.count() <= 0:
                popover = page.locator("body")
            for part in parts[:3]:
                option = popover.get_by_text(part, exact=False).first
                if await option.count() > 0:
                    await option.click(timeout=timeout_ms)
                    await page.wait_for_timeout(500)
            search_btn = popover.get_by_text(re.compile(r"查看|确定|搜索"), exact=False).first
            if await search_btn.count() > 0:
                captured_payloads.clear()
                await search_btn.click(timeout=timeout_ms)
                await page.wait_for_timeout(900)
        except Exception as exc:
            logger.debug("[goofish_catcher] region filter failed region=%r: %s", region, exc)

    async def _try_quick_login(self, page, context) -> bool:
        """若页面弹出「快速进入」一键登录对话框（已记住账号），自动点击恢复会话。

        Returns True 表示已恢复登录态；False 表示需要手动登录。

        处理两种情形：
        1. 页面展示「快速进入」按钮 → 点击，等待弹窗消失。
        2. 浏览器凭已有 cookie 自动通过 iframe 完成认证，按钮未出现但
           mini_login iframe 已经自行消失（无需点击）。
        """
        # 分支 1：等待「快速进入」按钮出现并点击
        try:
            btn = page.get_by_role("button", name="快速进入").first
            btn_visible = await btn.is_visible(timeout=3_000)
            logger.info("[goofish_catcher] _try_quick_login: 快速进入 button visible=%s", btn_visible)
            if btn_visible:
                await btn.click(timeout=3_000)
                logger.info("[goofish_catcher] _try_quick_login: button clicked, waiting for dismiss")
                try:
                    await btn.wait_for(state="hidden", timeout=8_000)
                    logger.info("[goofish_catcher] _try_quick_login: button dismissed")
                except Exception as e:
                    logger.info("[goofish_catcher] _try_quick_login: button dismiss wait: %s", e)
                await page.wait_for_timeout(1_000)
                await self._persist_context_storage_state(context)
                logger.info("[goofish_catcher] quick login succeeded via button click, storage_state refreshed")
                return True
        except Exception as exc:
            logger.info("[goofish_catcher] _try_quick_login button check: %s", exc)

        # 分支 2：按钮未出现，轮询 mini_login iframe 是否已自动消失
        try:
            deadline_ms = 6_000
            poll_ms = 300
            elapsed = 0
            frames_snapshot = [str(getattr(f, "url", "") or "") for f in (getattr(page, "frames", []) or [])]
            logger.info("[goofish_catcher] _try_quick_login: entering iframe poll, frames=%s", frames_snapshot)
            while elapsed < deadline_ms:
                frames = list(getattr(page, "frames", []) or [])
                auth_frames = [
                    str(getattr(f, "url", "") or "")
                    for f in frames
                    if _is_auth_url(str(getattr(f, "url", "") or ""))
                ]
                logger.debug(
                    "[goofish_catcher] _try_quick_login: poll %dms/%dms, auth_frames=%s",
                    elapsed, deadline_ms, auth_frames,
                )
                if not auth_frames:
                    await page.wait_for_timeout(500)
                    await self._persist_context_storage_state(context)
                    logger.info(
                        "[goofish_catcher] quick login succeeded via auto-auth (iframe gone at %dms), storage_state refreshed",
                        elapsed,
                    )
                    return True
                await page.wait_for_timeout(poll_ms)
                elapsed += poll_ms
            logger.info("[goofish_catcher] _try_quick_login: iframe still present after %dms poll, giving up", deadline_ms)
        except Exception as exc:
            logger.info("[goofish_catcher] _try_quick_login iframe poll: %s", exc)

        logger.warning("[goofish_catcher] _try_quick_login: no recovery path found")
        return False

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
        try:
            await page.wait_for_selector(
                _DETAIL_FAVORITE_BUTTON_SELECTOR,
                timeout=wait_timeout_ms,
            )
            return page.locator(_DETAIL_FAVORITE_BUTTON_SELECTOR).first
        except TimeoutError:
            # ── Agent fallback: CSS class-based selector timed out (likely a
            # frontend update changed the class names).  Ask the LLM to find
            # the button by its accessible name instead.
            if self._llm_call is None:
                raise
            logger.info(
                "[goofish_catcher][agent] CSS favorite selector timed out, "
                "trying AX+LLM fallback"
            )
            result = await find_favorite_button_via_llm(
                page,
                llm_call=self._llm_call,
                timeout_sec=8,
            )
            if result is None or result["status"] == "unknown":
                logger.warning(
                    "[goofish_catcher][agent] LLM could not locate favorite button"
                )
                raise
            button_name = result["button_name"]
            if not button_name:
                raise
            # Locate by accessible name — stable across class-name changes.
            locator = page.get_by_role("button", name=button_name).first
            if await locator.count() == 0:
                locator = page.get_by_text(button_name).first
            logger.info(
                "[goofish_catcher][agent] LLM located favorite button: "
                "name=%r status=%s",
                button_name,
                result["status"],
            )
            return locator

    async def _classify_favorite_page_state(
        self,
        page,
        *,
        error_flags: set[str] | None = None,
    ) -> ProviderError | None:
        return await self._classify_timeout_page_state(
            page,
            error_flags=error_flags,
        )

    async def check_login_state(self, *, timeout_sec: int = 15) -> str:
        """Probe Goofish and return the current auth state.

        Returns one of:
          ``"ok"``            – browser is reachable and session is valid
          ``"auth_required"`` – session expired / not logged in
          ``"captcha"``       – CAPTCHA wall detected
          ``"error"``         – browser not initialised or network failure

        This method is intentionally lightweight: it opens a minimal page,
        checks URL / HTML markers (no CSS selectors, no LLM), and closes the
        page immediately.  Safe to call from a periodic heartbeat task.
        """
        if self._persistent_context is None and self._browser is None:
            return "error"

        timeout_ms = max(5, timeout_sec) * 1000
        try:
            context, should_close = await self._open_operation_context()
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] heartbeat: failed to open context: %s", exc
            )
            return "error"

        page = None
        try:
            page = await context.new_page()
            error_flags: set[str] = set()
            self._attach_page_state_watchers(page, error_flags)

            await page.goto(
                self.BASE_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )
            await self._maybe_wait_for_network_idle(page, timeout_ms)

            err = await self._classify_timeout_page_state(page, error_flags=error_flags)
            if err is None:
                return "ok"
            if err.code == ProviderErrorCode.AUTH_REQUIRED:
                return "auth_required"
            if err.code == ProviderErrorCode.CAPTCHA:
                return "captcha"
            return "error"
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] heartbeat: probe failed: %s", exc
            )
            return "error"
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass
            if should_close:
                try:
                    await context.close()
                except Exception:
                    pass

    def _build_search_url(
        self,
        *,
        keyword: str,
        price_lower: float | None = None,
        price_upper: float | None = None,
    ) -> str:
        url = f"{self.BASE_URL}/search?q={quote(keyword)}"
        if price_lower is not None and price_lower > 0:
            url += f"&priceLower={int(price_lower)}"
        if price_upper is not None and price_upper > 0:
            url += f"&priceUpper={int(price_upper)}"
        return url

    async def _navigate_to_page_index(
        self,
        *,
        page,
        page_index: int,
        timeout_ms: int,
    ) -> bool:
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
            available_pages = await self._extract_visible_page_numbers(page_boxes)
            if available_pages and max(available_pages) < page_index:
                return False
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
        return True

    async def _extract_visible_page_numbers(self, page_boxes) -> list[int]:
        values: list[int] = []
        for idx in range(await page_boxes.count()):
            candidate = page_boxes.nth(idx)
            try:
                text = (await candidate.inner_text()).strip()
            except Exception:
                continue
            if not text.isdigit():
                continue
            values.append(int(text))
        return values

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

    def _attach_page_state_watchers(self, page, error_flags: set[str]) -> None:
        on = getattr(page, "on", None)
        if not callable(on):
            return

        def _on_frame_navigated(frame) -> None:
            frame_url = str(getattr(frame, "url", "") or "")
            if _is_auth_url(frame_url):
                error_flags.add("auth")
                logger.info(
                    "[goofish_catcher] detected auth frame navigation: %s",
                    frame_url,
                )
            if _is_captcha_url(frame_url):
                error_flags.add("captcha")
                logger.info(
                    "[goofish_catcher] detected captcha frame navigation: %s",
                    frame_url,
                )

        async def _on_response(response) -> None:
            url = str(getattr(response, "url", "") or "")
            if _is_auth_url(url):
                error_flags.add("auth")
                logger.info(
                    "[goofish_catcher] detected auth response: status=%s url=%s",
                    getattr(response, "status", "?"),
                    url,
                )
            if _is_captcha_url(url):
                error_flags.add("captcha")
                logger.info(
                    "[goofish_catcher] detected captcha response: status=%s url=%s",
                    getattr(response, "status", "?"),
                    url,
                )

            content_type = ""
            try:
                content_type = (response.headers.get("content-type") or "").lower()
            except Exception:
                content_type = ""

            if _should_log_response_url(url):
                logger.info(
                    "[goofish_catcher] observed response: status=%s resource=%s url=%s content_type=%s",
                    getattr(response, "status", "?"),
                    getattr(getattr(response, "request", None), "resource_type", "?"),
                    url,
                    content_type or "-",
                )
            if "json" not in content_type:
                return
            try:
                payload = await response.json()
            except Exception:
                return
            if isinstance(payload, dict):
                if _should_log_response_url(url):
                    logger.info(
                        "[goofish_catcher] response payload summary: url=%s ret=%s auth=%s captcha=%s",
                        url,
                        _payload_ret_summary(payload),
                        _payload_requires_login(payload),
                        _payload_indicates_captcha(payload),
                    )
                if _payload_requires_login(payload):
                    error_flags.add("auth")
                    logger.info(
                        "[goofish_catcher] payload requires login: url=%s ret=%s",
                        url,
                        _payload_ret_summary(payload),
                    )
                if _payload_indicates_captcha(payload):
                    error_flags.add("captcha")
                    logger.info(
                        "[goofish_catcher] payload indicates captcha: url=%s ret=%s",
                        url,
                        _payload_ret_summary(payload),
                    )

        on("framenavigated", _on_frame_navigated)
        on("response", _on_response)

    async def _classify_timeout_page_state(
        self,
        page,
        *,
        error_flags: set[str] | None = None,
    ) -> ProviderError | None:
        if error_flags and "auth" in error_flags:
            return ProviderError(
                ProviderErrorCode.AUTH_REQUIRED,
                "goofish showed embedded login prompt",
            )
        if error_flags and "captcha" in error_flags:
            return ProviderError(
                ProviderErrorCode.CAPTCHA,
                "captcha detected on goofish page",
            )
        try:
            current_url = str(getattr(page, "url", "") or "").lower()
        except Exception:
            current_url = ""
        if _is_auth_url(current_url):
            return ProviderError(
                ProviderErrorCode.AUTH_REQUIRED,
                "goofish redirected to login page",
            )
        if _is_captcha_url(current_url):
            return ProviderError(
                ProviderErrorCode.CAPTCHA,
                "captcha detected on goofish page",
            )

        try:
            frames = list(getattr(page, "frames", []) or [])
        except Exception:
            frames = []
        for frame in frames:
            try:
                frame_url = str(getattr(frame, "url", "") or "").lower()
            except Exception:
                frame_url = ""
            if _is_auth_url(frame_url):
                return ProviderError(
                    ProviderErrorCode.AUTH_REQUIRED,
                    "goofish showed embedded login prompt",
                )
            if _is_captcha_url(frame_url):
                return ProviderError(
                    ProviderErrorCode.CAPTCHA,
                    "captcha detected on goofish page",
                )

        try:
            html = await page.content()
        except Exception:
            html = ""
        lowered = html.lower()
        if any(marker in lowered for marker in _EMBEDDED_LOGIN_MARKERS):
            return ProviderError(
                ProviderErrorCode.AUTH_REQUIRED,
                "goofish showed embedded login prompt",
            )
        if (
            "验证码" in html
            or "滑块" in html
            or "请按住滑块" in html
            or "baxia-dialog-mask" in lowered
            or "j_middleware_frame_widget" in lowered
            or "captcha" in lowered
        ):
            return ProviderError(
                ProviderErrorCode.CAPTCHA,
                "captcha detected on goofish page",
            )

        # ── Agent fallback: heuristic rules found nothing suspicious.
        # Ask the LLM to visually interpret the AX tree as a last-resort check.
        # Only fires when all hard-coded URL / HTML markers have missed, so it
        # adds no latency to the normal (logged-in) path.
        if self._llm_call is not None:
            logged_in = await check_login_via_llm(
                page,
                llm_call=self._llm_call,
                timeout_sec=8,
            )
            if logged_in is False:
                logger.info(
                    "[goofish_catcher][agent] LLM login check reports not logged in"
                )
                return ProviderError(
                    ProviderErrorCode.AUTH_REQUIRED,
                    "goofish login wall detected by LLM (heuristics missed)",
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

        dom_items = await self._extract_items_from_dom(page)
        if dom_items:
            return dom_items

        # ── Agent fallback: CSS selectors may have broken after a frontend update.
        # Fall through to AX Tree + LLM extraction only when both fast paths
        # returned nothing, so normal operation has zero LLM cost.
        if self._llm_call is not None:
            keyword = ""
            try:
                from urllib.parse import parse_qs, urlparse
                keyword = parse_qs(urlparse(page.url).query).get("q", [""])[0]
            except Exception:
                pass
            logger.info(
                "[goofish_catcher][agent] CSS selectors returned nothing, "
                "falling back to AX+LLM extraction (keyword=%r)",
                keyword,
            )
            llm_items = await extract_items_via_llm(
                page,
                keyword=keyword,
                llm_call=self._llm_call,
                timeout_sec=max(10, (timeout_ms // 1000) - 2),
            )
            if llm_items:
                logger.info(
                    "[goofish_catcher][agent] AX+LLM extracted %d items",
                    len(llm_items),
                )
                return llm_items
            logger.warning("[goofish_catcher][agent] AX+LLM extraction also empty")

        return []

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


def _build_deep_analysis_result(
    *,
    item: NormalizedItem,
    payloads: list[dict[str, Any] | list[Any]],
    page_title: str,
) -> DeepAnalysisResult:
    detail_payload = _find_item_detail_payload(payloads)
    detail_payload_found = detail_payload is not None
    if detail_payload is not None:
        item_do = detail_payload.get("itemDO")
        seller_do = detail_payload.get("sellerDO")
        if not isinstance(item_do, dict):
            item_do = _find_first_nested_dict(
                detail_payload, ("itemDO", "item", "itemInfo", "auction")
            )
        if not isinstance(seller_do, dict):
            seller_do = _find_first_nested_dict(
                detail_payload, ("sellerDO", "seller", "sellerInfo")
            )
    else:
        merged = _merge_detail_payloads(payloads)
        item_do = _find_first_nested_dict(merged, ("itemDO", "item", "itemInfo", "auction"))
        # Avoid generic ``user`` here: detail pages also load recommendation feeds
        # whose cardData.user is not the current item's seller.
        seller_do = _find_first_nested_dict(merged, ("sellerDO", "seller", "sellerInfo"))

    item_do = item_do if isinstance(item_do, dict) else None
    seller_do = seller_do if isinstance(seller_do, dict) else None
    detail_source: dict[str, Any] = {}
    if isinstance(item.raw, dict):
        detail_source.update(item.raw)
    if item_do:
        detail_source.update(item_do)
    if seller_do:
        detail_source["seller"] = seller_do

    title = _pick_first_text(item_do or {}, ("title", "itemTitle", "subject")) if item_do else None
    seller_name = _pick_first_text(
        seller_do or {},
        ("nick", "nickName", "sellerNick", "userNick", "nickname"),
    ) if seller_do else None
    seller_id = _pick_first_text(
        seller_do or {},
        ("sellerId", "userId", "id"),
    ) if seller_do else None
    seller_credit = _pick_first_text(
        seller_do or {},
        ("zhimaLevel", "zhimaLevelName", "levelName", "creditLevel", "creditText"),
    ) if seller_do else None
    if seller_do and not seller_credit:
        zhima_info = seller_do.get("zhimaLevelInfo")
        if isinstance(zhima_info, dict):
            seller_credit = _pick_first_text(zhima_info, ("levelName", "name", "text"))
    if seller_do:
        structured_seller_credit = _extract_structured_seller_credit(seller_do)
        if seller_credit and structured_seller_credit:
            seller_credit = _join_unique_credit_parts(
                seller_credit,
                structured_seller_credit,
            )
        elif structured_seller_credit:
            seller_credit = structured_seller_credit

    image_urls = _extract_image_urls(detail_source)
    want_count = _parse_optional_int(_pick_first_text(item_do or {}, ("wantCnt", "wantCount", "want_count"))) if item_do else None
    browse_count = _parse_optional_int(_pick_first_text(item_do or {}, ("browseCnt", "browseCount", "browse_count"))) if item_do else None

    credit_status, credit_reason = _classify_credit(
        seller_credit=seller_credit,
        seller_payload=seller_do or {},
        item_payload=item_do or {},
    )
    logger.info(
        "[goofish_catcher] detail parse item_id=%s payloads=%s detail_payload=%s item_do=%s item_do_item_id=%s seller_do=%s seller_keys=%s seller_name=%s seller_id=%s seller_credit=%s credit_status=%s credit_reason=%s want=%s browse=%s page_title=%r",
        item.item_id,
        len(payloads),
        detail_payload_found,
        bool(item_do),
        _pick_first_text(item_do or {}, ("itemId", "item_id", "id", "auctionId", "targetId")),
        bool(seller_do),
        list((seller_do or {}).keys())[:25],
        seller_name or "-",
        seller_id or "-",
        seller_credit or "-",
        credit_status,
        credit_reason,
        want_count,
        browse_count,
        page_title,
    )
    status = "rejected" if credit_status == "bad" else "passed"
    risk = "信用风险较高" if status == "rejected" else "未发现明确低信用风险"
    summary_parts = [
        f"信用：{seller_credit or credit_status}",
        credit_reason,
    ]
    if want_count is not None:
        summary_parts.append(f"想要 {want_count}")
    if browse_count is not None:
        summary_parts.append(f"浏览 {browse_count}")
    if seller_name:
        summary_parts.append(f"卖家 {seller_name}")

    return DeepAnalysisResult(
        item_id=item.item_id,
        analyzed_at=int(time.time()),
        status=status,
        credit_status=credit_status,
        credit_reason=credit_reason,
        summary="；".join(part for part in summary_parts if part),
        risk=risk,
        image_urls=image_urls,
        seller_name=seller_name,
        seller_id=seller_id,
        seller_credit=seller_credit,
        want_count=want_count,
        browse_count=browse_count,
        raw={
            "title": title or page_title or item.title,
            "payload_count": len(payloads),
            "item": _safe_jsonable(item_do or {}),
            "seller": _safe_jsonable(seller_do or {}),
        },
    )


def _merge_detail_payloads(payloads: list[dict[str, Any] | list[Any]]) -> dict[str, Any]:
    return {"payloads": payloads}


def _find_item_detail_payload(
    payloads: list[dict[str, Any] | list[Any]],
) -> dict[str, Any] | None:
    """Return the data object from the current item's detail API response.

    A detail page can load several unrelated JSON payloads after the item
    response, especially recommendation feeds.  Those feeds contain
    ``cardData.user`` objects for other sellers.  Deep analysis must bind seller
    info to the mtop.taobao.idle.pc.detail payload instead of globally taking
    the first nested seller/user-like object.
    """

    candidates: list[dict[str, Any]] = []
    saw_detail_api = False
    stack: list[Any] = list(payloads)
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            data = current.get("data")
            if isinstance(data, dict):
                api = str(current.get("api") or "").lower()
                has_detail_shape = isinstance(data.get("itemDO"), dict) or isinstance(
                    data.get("sellerDO"), dict
                )
                if api == "mtop.taobao.idle.pc.detail":
                    saw_detail_api = True
                    logger.info(
                        "[goofish_catcher] detail payload candidate api=%s ret=%s has_detail_shape=%s data_keys=%s",
                        current.get("api") or "-",
                        _payload_ret_summary(current),
                        has_detail_shape,
                        list(data.keys())[:30],
                    )
                if api == "mtop.taobao.idle.pc.detail" and has_detail_shape:
                    return data
                if isinstance(data.get("itemDO"), dict) and isinstance(data.get("sellerDO"), dict):
                    candidates.append(data)
            stack.extend(value for value in current.values() if isinstance(value, (dict, list)))
        elif isinstance(current, list):
            stack.extend(value for value in current if isinstance(value, (dict, list)))
    if candidates:
        logger.info(
            "[goofish_catcher] detail payload fallback using shaped candidate, count=%s",
            len(candidates),
        )
        return candidates[0]
    logger.info(
        "[goofish_catcher] detail payload not found payloads=%s saw_detail_api=%s",
        len(payloads),
        saw_detail_api,
    )
    return None


def _find_first_nested_dict(node: Any, keys: tuple[str, ...]) -> dict[str, Any] | None:
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key in keys:
                value = current.get(key)
                if isinstance(value, dict):
                    return value
            stack.extend(value for value in current.values() if isinstance(value, (dict, list)))
        elif isinstance(current, list):
            stack.extend(value for value in current if isinstance(value, (dict, list)))
    return None


def _extract_image_urls(node: Any, *, limit: int = 6) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add_url(value: Any) -> None:
        if len(urls) >= limit:
            return
        text = str(value or "").strip()
        if not text:
            return
        if text.startswith("//"):
            text = "https:" + text
        if not (text.startswith("http://") or text.startswith("https://")):
            return
        lowered = text.lower()
        if not any(marker in lowered for marker in (".jpg", ".jpeg", ".png", ".webp", "alicdn", "img")):
            return
        if text in seen:
            return
        seen.add(text)
        urls.append(text)

    def add_structured_image_list(value: Any) -> None:
        if len(urls) >= limit or not isinstance(value, list):
            return
        image_entries = [entry for entry in value if isinstance(entry, dict)]
        image_entries.sort(key=lambda entry: 0 if entry.get("major") is True else 1)
        for entry in image_entries:
            if len(urls) >= limit:
                return
            add_url(
                entry.get("url")
                or entry.get("image")
                or entry.get("imageUrl")
                or entry.get("picUrl")
                or entry.get("src")
            )

    def add_priority_images(current: Any) -> None:
        stack_for_priority = [current]
        while stack_for_priority and len(urls) < limit:
            node = stack_for_priority.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    lowered_key = str(key).lower()
                    if lowered_key in {"imageinfos", "image_infos", "images", "image_list"}:
                        add_structured_image_list(value)
                    if isinstance(value, (dict, list)):
                        stack_for_priority.append(value)
            elif isinstance(node, list):
                stack_for_priority.extend(
                    value for value in reversed(node) if isinstance(value, (dict, list))
                )

    add_priority_images(node)

    stack = [node]
    while stack and len(urls) < limit:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                lowered_key = str(key).lower()
                if lowered_key in {"url", "image", "imageurl", "picurl", "src"} or "image" in lowered_key or "pic" in lowered_key:
                    if isinstance(value, str):
                        add_url(value)
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(
                value
                for value in reversed(current)
                if isinstance(value, (dict, list, str))
            )
        elif isinstance(current, str):
            add_url(current)
    return urls


def _extract_structured_seller_credit(seller_payload: dict[str, Any]) -> str | None:
    parts: list[str] = []

    good_ratio = _pick_first_text(
        seller_payload,
        ("newGoodRatioRate", "goodRatioRate", "goodRate", "positiveRate", "goodRatio"),
    )
    if good_ratio:
        parts.append(f"好评率{good_ratio}")

    sold_count = _parse_optional_int(
        _pick_first_text(
            seller_payload,
            ("hasSoldNumInteger", "soldCnt", "soldCount", "sellCount"),
        )
    )
    if sold_count is not None:
        parts.append(f"卖出{sold_count}件")

    reg_days = _parse_optional_int(seller_payload.get("userRegDay"))
    if reg_days:
        if reg_days >= 365:
            parts.append(f"来闲鱼{max(1, reg_days // 365)}年")
        else:
            parts.append(f"来闲鱼{reg_days}天")

    level = _extract_seller_level(seller_payload)
    if level is not None:
        parts.append(f"闲鱼信用等级{level}")

    if seller_payload.get("zhimaAuth") is True:
        parts.append("已芝麻认证")

    identity_tags = seller_payload.get("identityTags")
    if isinstance(identity_tags, list):
        for tag in identity_tags:
            if not isinstance(tag, dict):
                continue
            text = _pick_first_text(tag, ("text", "title", "name"))
            if text and "认证" in text:
                parts.append(text)

    return "，".join(parts) if parts else None


def _join_unique_credit_parts(*values: str | None) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        for part in re.split(r"[，,；;]", value):
            normalized = part.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            parts.append(normalized)
    return "，".join(parts)


def _classify_credit(
    *,
    seller_credit: str | None,
    seller_payload: dict[str, Any],
    item_payload: dict[str, Any],
) -> tuple[str, str]:
    seller_text = " ".join(
        str(value)
        for value in (
            seller_credit,
            json.dumps(seller_payload, ensure_ascii=False)[:1200],
        )
        if value
    )
    item_text = json.dumps(item_payload, ensure_ascii=False)[:800].lower()
    lowered = seller_text.lower()
    bad_markers = (
        "信用较差",
        "信用差",
        "芝麻较差",
        "较差",
        "差评很多",
        "风险卖家",
        "严重违规",
        "骗子",
        "诈骗",
    )
    good_markers = (
        "信用极好",
        "信用优秀",
        "芝麻信用优秀",
        "优秀",
        "极好",
        "良好",
    )
    severe_item_markers = ("风险卖家", "严重违规", "骗子", "诈骗")
    if any(marker in lowered for marker in bad_markers) or any(
        marker in item_text for marker in severe_item_markers
    ):
        return "bad", "检测到明确低信用或严重负面风险标记"
    if any(marker in lowered for marker in good_markers):
        return "good", "卖家信用信息良好"

    seller_level = _extract_seller_level(seller_payload)
    good_ratio = _parse_percent(
        _pick_first_text(
            seller_payload,
            ("newGoodRatioRate", "goodRatioRate", "goodRate", "positiveRate", "goodRatio"),
        )
    )
    sold_count = _parse_optional_int(
        _pick_first_text(
            seller_payload,
            ("hasSoldNumInteger", "soldCnt", "soldCount", "sellCount"),
        )
    )
    remark_do = seller_payload.get("remarkDO")
    bad_remarks = None
    good_remarks = None
    if isinstance(remark_do, dict):
        bad_remarks = _parse_optional_int(remark_do.get("sellerBadRemarkCnt"))
        good_remarks = _parse_optional_int(remark_do.get("sellerGoodRemarkCnt"))

    if seller_level is not None and seller_level <= 2:
        return "bad", f"卖家闲鱼信用等级偏低：{seller_level}"
    if (
        good_ratio is not None
        and good_ratio < 90
        and (sold_count or 0) >= 10
    ):
        return "bad", f"卖家好评率偏低：{good_ratio:.0f}%"
    if (
        bad_remarks is not None
        and bad_remarks >= 3
        and bad_remarks > (good_remarks or 0)
    ):
        return "bad", "卖家负面评价数量偏高"

    if seller_level is not None and seller_level >= 4:
        return "good", f"卖家闲鱼信用等级较好：{seller_level}"
    if good_ratio is not None and good_ratio >= 95:
        return "good", f"卖家好评率较高：{good_ratio:.0f}%"
    if (
        good_ratio is not None
        and good_ratio >= 90
        and (sold_count or 0) >= 10
    ):
        return "good", f"卖家交易评价较稳定：好评率{good_ratio:.0f}%"

    if seller_credit:
        return "unknown", f"卖家信用信息：{seller_credit}"
    return "unknown", "未获取到明确卖家信用信息，按保守规则不过滤"


def _extract_seller_level(seller_payload: dict[str, Any]) -> int | None:
    level_tag = seller_payload.get("idleFishCreditTag")
    if isinstance(level_tag, dict):
        track_params = level_tag.get("trackParams")
        if isinstance(track_params, dict):
            level = _parse_optional_int(track_params.get("sellerLevel"))
            if level is not None:
                return level

    for tag in seller_payload.get("levelTags") or ():
        if not isinstance(tag, dict):
            continue
        track_params = tag.get("trackParams")
        if isinstance(track_params, dict):
            level = _parse_optional_int(track_params.get("sellerLevel"))
            if level is not None:
                return level
    return None


def _parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _safe_jsonable(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        return str(value)


def _is_auth_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    if "passport.goofish.com" in host and (
        "mini_login.htm" in path or path == "/login" or path.startswith("/login/")
    ):
        return True
    if "goofish.com" in host and "mini_login.htm" in path:
        return True
    if "goofish.com" in host and "member/login" in path:
        return True
    return False


def _is_captcha_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    return bool(
        ("cf.aliyun.com" in host and "nocaptcha" in path)
        or "captcha" in path
    )


def _payload_requires_login(payload: dict[str, Any]) -> bool:
    lowered = _payload_ret_summary(payload).lower()
    return any(
        marker in lowered
        for marker in (
            "fail_sys_session_expired",
            "fail_sys_illegal_access",
            "session过期",
            "请登录",
            "need_login",
        )
    )


def _payload_indicates_captcha(payload: dict[str, Any]) -> bool:
    ret = payload.get("ret")
    ret_text = " ".join(str(item) for item in ret) if isinstance(ret, list) else str(ret)
    lowered = ret_text.lower()
    return any(
        marker in lowered
        for marker in (
            "captcha",
            "验证码",
            "滑块",
            "fail_sys_user_validate",
            "rgv587_error",
            "被挤爆",
            "punish",
            "baxia",
        )
    )


def _payload_ret_summary(payload: dict[str, Any]) -> str:
    ret = payload.get("ret")
    if isinstance(ret, list):
        return " | ".join(str(item) for item in ret[:3]) or "-"
    text = str(ret or "").strip()
    return text or "-"


def _should_log_response_url(url: str) -> bool:
    lowered = str(url or "").lower()
    return any(
        marker in lowered
        for marker in (
            "mtop.taobao.idle.pc.detail",
            "mtop.taobao.idlemessage.pc.loginuser.get",
            "mtop.taobao.idle.collect.item",
            "com.taobao.idle.unfavor.item",
            "passport.goofish.com/mini_login.htm",
            "mtop.idle.web.user.page.nav",
        )
    )


def _collect_frame_urls(page) -> list[str]:
    try:
        frames = list(getattr(page, "frames", []) or [])
    except Exception:
        return []
    urls: list[str] = []
    for frame in frames:
        try:
            url = str(getattr(frame, "url", "") or "").strip()
        except Exception:
            url = ""
        if url:
            urls.append(url)
    return urls


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
    # 优先检查带展示文本的字段（如 "1.62万"），这类字段包含单位信息，
    # 比裸数字字段（price/amount 可能是 1 分钱或其他无单位整数）更可靠。
    display_keys = (
        "priceText",
        "displayPrice",
        "salePrice",
        "finalPrice",
        "currentPrice",
        "current_price",
    )
    for key in display_keys:
        if key not in data:
            continue
        parsed = _parse_price(data.get(key))
        if parsed is not None:
            return parsed

    # 次优先：raw 数字字段；若已被 display_keys 覆盖则不会走到这里
    for key in ("price", "amount"):
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
            # round 消除浮点乘法误差（如 1.62 * 10000 = 16200.000000000002）
            return round(float(match.group(1)) * multiplier, 2)
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
        # 闲鱼富文本价格格式：list of dicts，每个 dict 有 "type" 和 "text" 字段
        # 例：[{"type":"sign","text":"¥"},{"type":"integer","text":"1"},
        #      {"type":"decimal","text":".58"},{"type":"unit","text":"万"}]
        # 先判断是否是这种格式（所有 item 都是带 "text" 的 dict）
        if value and all(isinstance(i, dict) and "text" in i for i in value):
            combined = "".join(str(i.get("text", "")) for i in value)
            parsed = _parse_price(combined)
            if parsed is not None:
                return parsed
        # 否则退回到逐项尝试（取第一个能解析的）
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
