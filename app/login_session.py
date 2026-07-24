from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .platforms.base import SiteProfile
# 0.3b：_payload_indicates_captcha 统一为 8 标记共享版（与 provider_playwright
# 同一份实现），私有 3 标记版已删除。
from .platforms.goofish import GOOFISH_PROFILE, _payload_indicates_captcha

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"
PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"
# 数据源 = GOOFISH_PROFILE（app/platforms/goofish.py）；
# 保留这三个模块级别名，兼容既有 import 与 GoofishLoginSession 的默认值链路。
DEFAULT_LOGIN_URL = GOOFISH_PROFILE.login_url
DEFAULT_VIEWPORT = {"width": 1280, "height": 960}
_LOGIN_STATUS_API_MARKERS = GOOFISH_PROFILE.login_status_api_markers
_EMBEDDED_LOGIN_MARKERS = GOOFISH_PROFILE.embedded_login_markers

# Button texts that indicate a one-click / quick login option is available.
# Clicking one of these should log the user in without QR scanning.
_QUICK_LOGIN_TEXTS = (
    "快速进入",
    "快速登录",
    "一键登录",
    "快捷登录",
)


def get_astrbot_root() -> Path:
    if root := os.getenv("ASTRBOT_ROOT"):
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


def load_local_plugin_config() -> dict[str, Any]:
    config_path = (
        get_astrbot_root()
        / "data"
        / "config"
        / f"{PLUGIN_NAME}_config.json"
    )
    if not config_path.exists():
        return {}
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise RuntimeError("local plugin config root must be a JSON object")
    return raw


def load_worker_config() -> dict[str, Any]:
    config_path = Path(
        os.getenv("GOOFISH_WORKER_CONFIG", "worker_config.json")
    ).expanduser()
    if not config_path.exists():
        return {}
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise RuntimeError("worker config root must be a JSON object")
    return raw


def normalize_executable_path(executable_path: Path | str | None) -> Path | None:
    if executable_path is None:
        return None

    candidate = Path(executable_path).expanduser()
    if not candidate.exists():
        raise RuntimeError(f"configured browser executable does not exist: {candidate}")
    if not candidate.is_file():
        raise RuntimeError(f"configured browser executable is not a file: {candidate}")
    return candidate


def resolve_save_state_executable_path() -> Path | None:
    env_value = os.getenv("GOOFISH_WORKER_EXECUTABLE_PATH")
    if env_value is not None:
        raw_path = env_value.strip()
    else:
        local_config = load_local_plugin_config()
        if (
            local_config.get("provider_mode") == PROVIDER_MODE_PLAYWRIGHT_LOCAL
            and str(local_config.get("playwright_executable_path", "")).strip()
        ):
            raw_path = str(local_config.get("playwright_executable_path", "")).strip()
        else:
            raw_path = str(load_worker_config().get("executable_path", "")).strip()

    if not raw_path:
        return None
    return normalize_executable_path(raw_path)


def build_login_launch_args(*, force_direct: bool = False) -> list[str]:
    args = ["--disable-blink-features=AutomationControlled"]
    if force_direct:
        args.extend(
            [
                "--no-proxy-server",
                "--proxy-server=direct://",
                "--proxy-bypass-list=*",
            ]
        )
    return args


@dataclass(slots=True)
class LoginSessionSnapshot:
    page_url: str
    screenshot_base64: str


class GoofishLoginSession:
    def __init__(
        self,
        *,
        executable_path: Path | str | None = None,
        user_data_dir: Path | str | None = None,
        force_direct: bool = False,
        proxy: str | None = None,
        login_url: str | None = None,
        profile: SiteProfile | None = None,
    ) -> None:
        self.executable_path = normalize_executable_path(executable_path)
        self.user_data_dir = (
            Path(user_data_dir).expanduser()
            if user_data_dir is not None
            else None
        )
        self.force_direct = force_direct
        self.proxy = proxy
        # 站点档案：缺省闲鱼；login_url 显式传入时优先于 profile.login_url
        # （旧调用方不传 login_url 时行为与旧的 DEFAULT_LOGIN_URL 默认值一致）。
        self._profile = profile or GOOFISH_PROFILE
        self.login_url = login_url if login_url is not None else self._profile.login_url
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._context: Any | None = None
        self._page: Any | None = None

    @property
    def page_url(self) -> str:
        if self._page is None:
            return ""
        return str(getattr(self._page, "url", "") or "")

    async def start_login_session(self) -> LoginSessionSnapshot:
        if self._page is not None:
            return await self.capture_snapshot()

        try:
            from playwright.async_api import async_playwright
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "playwright is not installed. "
                "Run: uv pip install -r requirements.txt && "
                "uv run python -m playwright install chromium chromium-headless-shell"
            ) from exc

        self._playwright = await async_playwright().start()
        try:
            launch_kwargs: dict[str, Any] = {
                "headless": False,
                "args": build_login_launch_args(force_direct=self.force_direct),
            }
            if self.executable_path is not None:
                launch_kwargs["executable_path"] = str(self.executable_path)
            if self.proxy:
                # Route the login browser through the configured upstream proxy so
                # the session cookie is bound to the same egress IP the worker uses.
                launch_kwargs["proxy"] = {"server": self.proxy}

            if self.user_data_dir is not None:
                self.user_data_dir.mkdir(parents=True, exist_ok=True)
                self._context = await self._playwright.chromium.launch_persistent_context(
                    str(self.user_data_dir),
                    viewport=DEFAULT_VIEWPORT,
                    **launch_kwargs,
                )
                self._browser = self._context.browser
                self._page = (
                    self._context.pages[0]
                    if getattr(self._context, "pages", None)
                    else None
                )
                if self._page is None:
                    self._page = await self._context.new_page()
            else:
                self._browser = await self._playwright.chromium.launch(**launch_kwargs)
                self._context = await self._browser.new_context(
                    viewport=DEFAULT_VIEWPORT
                )
                self._page = await self._context.new_page()
            await self._page.goto(
                self.login_url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await self._settle_page()
            return await self.capture_snapshot()
        except Exception:
            await self.close()
            raise

    async def capture_snapshot(self) -> LoginSessionSnapshot:
        screenshot_base64 = await self.capture_screenshot_base64()
        return LoginSessionSnapshot(
            page_url=self.page_url,
            screenshot_base64=screenshot_base64,
        )

    async def capture_screenshot_base64(self) -> str:
        if self._page is None:
            raise RuntimeError("login session has not been started")
        await self._settle_page()
        image_bytes = await self._page.screenshot(
            type="jpeg",
            quality=70,
            full_page=False,
        )
        return base64.b64encode(image_bytes).decode("ascii")

    async def save_storage_state(self, target_path: Path | str) -> Path:
        if self._context is None:
            raise RuntimeError("login session has not been started")

        target = Path(target_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target.parent / f".{target.name}.{uuid4().hex}.tmp"
        try:
            await self._context.storage_state(path=str(temp_path))
            os.replace(temp_path, target)
            return target
        except Exception:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise

    async def validate_login(self) -> dict[str, Any]:
        if self._context is None:
            raise RuntimeError("login session has not been started")

        page = self._page
        if page is None:
            page = await self._context.new_page()
            self._page = page

        # 平台判定钩子与标记全部取自站点档案（模块级别名仍保留给其他 import 方）。
        profile = self._profile
        is_auth_url = profile.is_auth_url
        is_captcha_url = profile.is_captcha_url
        login_status_api_markers = profile.login_status_api_markers
        embedded_login_markers = profile.embedded_login_markers

        auth_flags: set[str] = set()
        captcha_flags: set[str] = set()
        payload_rets: dict[str, str] = {}
        payload_hits: set[str] = set()

        def _on_frame_navigated(frame) -> None:
            frame_url = str(getattr(frame, "url", "") or "")
            if is_auth_url(frame_url):
                auth_flags.add(frame_url)
            if is_captcha_url(frame_url):
                captcha_flags.add(frame_url)

        async def _on_response(response) -> None:
            url = str(getattr(response, "url", "") or "")
            if is_auth_url(url):
                auth_flags.add(url)
            if is_captcha_url(url):
                captcha_flags.add(url)

            lowered = url.lower()
            if not any(marker.lower() in lowered for marker in login_status_api_markers):
                return

            try:
                payload = await response.json()
            except Exception:
                return
            if not isinstance(payload, dict):
                return
            payload_rets[url] = _payload_ret_summary(payload)
            matched_marker = _match_login_status_api(url, login_status_api_markers)
            if matched_marker is not None:
                payload_hits.add(matched_marker)
            if _payload_requires_login(payload):
                auth_flags.add(f"payload:{payload_rets[url]}")
            if _payload_indicates_captcha(payload):
                captcha_flags.add(f"payload:{payload_rets[url]}")

        on = getattr(page, "on", None)
        if callable(on):
            on("framenavigated", _on_frame_navigated)
            on("response", _on_response)

        await page.goto(
            self._profile.validate_probe_url or self.login_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        await self._settle_page()

        current_url = str(getattr(page, "url", "") or "")
        frame_urls = _collect_frame_urls(page)
        try:
            html = await page.content()
        except Exception:
            html = ""
        lowered_html = html.lower()
        reason_text = "; ".join(payload_rets.values()) if payload_rets else "-"
        logger.info(
            "[goofish_catcher] validate_login result probe: page_url=%s hits=%s auth_flags=%s captcha_flags=%s frame_urls=%s payloads=%s",
            current_url,
            sorted(payload_hits),
            sorted(auth_flags),
            sorted(captcha_flags),
            frame_urls,
            payload_rets,
        )

        if auth_flags or is_auth_url(current_url) or any(
            is_auth_url(frame_url) for frame_url in frame_urls
        ) or any(marker in lowered_html for marker in embedded_login_markers):
            return {
                "ok": False,
                "code": "AUTH_REQUIRED",
                "reason": reason_text if payload_rets else "登录态尚未生效，页面仍出现登录提示",
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        if captcha_flags or is_captcha_url(current_url) or (
            "验证码" in html or "滑块" in html or "captcha" in lowered_html
        ):
            return {
                "ok": False,
                "code": "CAPTCHA",
                "reason": reason_text if payload_rets else "登录校验期间触发验证码或风控",
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        missing_hits = [
            marker for marker in login_status_api_markers if marker not in payload_hits
        ]
        if missing_hits:
            return {
                "ok": False,
                "code": "AUTH_REQUIRED",
                "reason": "登录校验缺少关键接口成功响应："
                + ", ".join(missing_hits),
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        if payload_rets:
            return {
                "ok": True,
                "code": "OK",
                "reason": reason_text,
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        return {
            "ok": False,
            "code": "AUTH_REQUIRED",
            "reason": "未观察到登录态成功响应，请确认扫码后页面已完成登录",
            "page_url": current_url,
            "frame_urls": frame_urls,
            "payload_rets": payload_rets,
        }

    async def close(self) -> None:
        if self._context is not None:
            await self._context.close()
            self._context = None
        elif self._browser is not None:
            await self._browser.close()
        self._browser = None
        self._page = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    def detach_runtime(self) -> dict[str, Any]:
        runtime = {
            "playwright": self._playwright,
            "browser": self._browser,
            "context": self._context,
            "page": self._page,
        }
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        return runtime

    async def _settle_page(self) -> None:
        if self._page is None:
            return
        await self._page.wait_for_timeout(1200)
        try:
            await self._page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            await self._page.wait_for_timeout(600)

    async def try_quick_login(self) -> bool:
        """Click a quick-login button if one is visible on the current page.

        Returns True if a button was found and clicked (page may have changed).
        Should be called after start_login_session(); if it returns True the
        caller must re-validate with validate_login() to confirm success.
        """
        # 档案禁用 quick-login 捷径的平台（如淘宝）直接放弃，避免访客态误判。
        if not self._profile.quick_login_enabled:
            return False
        if self._page is None:
            return False
        for text in _QUICK_LOGIN_TEXTS:
            try:
                locator = self._page.get_by_text(text, exact=True).first
                if await locator.count() > 0:
                    logger.info(
                        "[goofish_catcher] quick login option found: %r, clicking", text
                    )
                    await locator.click(timeout=3_000)
                    await self._settle_page()
                    return True
            except Exception as exc:
                logger.debug(
                    "[goofish_catcher] quick login click failed for %r: %s", text, exc
                )
        return False


def _payload_ret_summary(payload: dict[str, Any]) -> str:
    ret = payload.get("ret")
    if isinstance(ret, list):
        return " | ".join(str(item) for item in ret[:3]) or "-"
    text = str(ret or "").strip()
    return text or "-"


def _payload_requires_login(payload: dict[str, Any]) -> bool:
    ret_text = _payload_ret_summary(payload).lower()
    return any(
        marker in ret_text
        for marker in (
            "fail_sys_session_expired",
            "fail_sys_illegal_access",
            "session过期",
            "请登录",
            "need_login",
        )
    )


# 谓词实现与 provider_playwright 版逐字一致，已收口至 GOOFISH_PROFILE
# （app/platforms/goofish.py）；保留模块级别名，auth_session.py 仍经此 import。
_is_auth_url = GOOFISH_PROFILE.is_auth_url
_is_captcha_url = GOOFISH_PROFILE.is_captcha_url


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


def _match_login_status_api(
    url: str,
    markers: tuple[str, ...] = _LOGIN_STATUS_API_MARKERS,
) -> str | None:
    # URL 里的 api 名可能是驼峰（如 api=mtop.user.getUserSimple），
    # 匹配前对 URL 与标记统一 lower()。
    lowered = str(url or "").lower()
    for marker in markers:
        if marker.lower() in lowered:
            return marker
    return None
