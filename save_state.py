from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"
PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"


def _get_astrbot_root() -> Path:
    if root := os.getenv("ASTRBOT_ROOT"):
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def _load_local_plugin_config() -> dict[str, Any]:
    config_path = (
        _get_astrbot_root()
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


def _load_worker_config() -> dict[str, Any]:
    config_path = Path(
        os.getenv("GOOFISH_WORKER_CONFIG", "worker_config.json")
    ).expanduser()
    if not config_path.exists():
        return {}
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise RuntimeError("worker config root must be a JSON object")
    return raw


def _resolve_executable_path() -> Path | None:
    env_value = os.getenv("GOOFISH_WORKER_EXECUTABLE_PATH")
    if env_value is not None:
        raw_path = env_value.strip()
    else:
        local_config = _load_local_plugin_config()
        if (
            local_config.get("provider_mode") == PROVIDER_MODE_PLAYWRIGHT_LOCAL
            and str(local_config.get("playwright_executable_path", "")).strip()
        ):
            raw_path = str(local_config.get("playwright_executable_path", "")).strip()
        else:
            raw_path = str(_load_worker_config().get("executable_path", "")).strip()

    if not raw_path:
        return None

    candidate = Path(raw_path).expanduser()
    if not candidate.exists():
        raise RuntimeError(
            f"configured browser executable does not exist: {candidate}"
        )
    if not candidate.is_file():
        raise RuntimeError(
            f"configured browser executable is not a file: {candidate}"
        )
    return candidate


async def main():
    executable_path = _resolve_executable_path()
    async with async_playwright() as p:
        launch_kwargs: dict[str, Any] = {"headless": False}
        if executable_path is not None:
            launch_kwargs["executable_path"] = str(executable_path)
            print(f"使用自定义浏览器: {executable_path}")
        else:
            print("使用 Playwright 自带 Chromium")

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.goofish.com/")
        print("请在浏览器完成登录，回到终端按 Enter 保存登录态...")
        await asyncio.get_running_loop().run_in_executor(None, input)
        await context.storage_state(path="storage_state.json")
        await browser.close()
        print("已保存: storage_state.json")


if __name__ == "__main__":
    asyncio.run(main())
