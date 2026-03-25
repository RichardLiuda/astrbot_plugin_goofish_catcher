from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"
PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"
DEFAULT_LOGIN_URL = "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC"
DEFAULT_VIEWPORT = {"width": 1280, "height": 960}


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
        force_direct: bool = False,
        login_url: str = DEFAULT_LOGIN_URL,
    ) -> None:
        self.executable_path = normalize_executable_path(executable_path)
        self.force_direct = force_direct
        self.login_url = login_url
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

            self._browser = await self._playwright.chromium.launch(**launch_kwargs)
            self._context = await self._browser.new_context(viewport=DEFAULT_VIEWPORT)
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

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        self._context = None
        self._page = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def _settle_page(self) -> None:
        if self._page is None:
            return
        await self._page.wait_for_timeout(1200)
        try:
            await self._page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            await self._page.wait_for_timeout(600)

