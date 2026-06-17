"""
Standalone smoke driver for the GooFish scraping pipeline.

Runs search + login-check directly against PlaywrightSearchProvider
without starting AstrBot. All paths are absolute so this runs from
any working directory.

Usage (from any directory):
  /Users/richardliu/Documents/Coding/AstrBot/.venv/bin/python \\
    /Users/richardliu/Documents/Coding/AstrBot/data/plugins/\\
    astrbot_plugin_goofish_catcher/.claude/skills/run-goofish-scraper/driver.py [args]

  Or from the AstrBot root:
  .venv/bin/python data/plugins/astrbot_plugin_goofish_catcher/.claude/skills/run-goofish-scraper/driver.py [args]

Arguments:
  --login-only          Only probe login state, skip search
  <keyword>             Search keyword (default: 单反相机)
  <keyword> <pages>     Search keyword and page count (default pages: 1)
"""
import asyncio
import logging
import sys
from pathlib import Path

ASTRBOT_DIR = Path("/Users/richardliu/Documents/Coding/AstrBot")
PLUGIN_DIR = ASTRBOT_DIR / "data/plugins/astrbot_plugin_goofish_catcher"
STORAGE_STATE = ASTRBOT_DIR / "data/plugin_data/astrbot_plugin_goofish_catcher/storage_state.json"

sys.path.insert(0, str(ASTRBOT_DIR))
sys.path.insert(0, str(PLUGIN_DIR))

from app.config import PluginSettings, PROVIDER_MODE_PLAYWRIGHT_LOCAL
from app.provider_playwright import PlaywrightSearchProvider
from app.types import ProviderErrorCode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


def _make_settings(block_assets: bool = True) -> PluginSettings:
    return PluginSettings(
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=PLUGIN_DIR,
        provider_mode=PROVIDER_MODE_PLAYWRIGHT_LOCAL,
        playwright_headless=True,
        playwright_storage_state_path=STORAGE_STATE if STORAGE_STATE.exists() else None,
        playwright_user_data_dir=None,
        playwright_block_assets=block_assets,
        playwright_force_direct=False,
        playwright_executable_path=None,
        llm_enabled=False,
        db_path=PLUGIN_DIR / "data/goofish.db",
        fetch_timeout_sec=30,
        max_pages=3,
        default_interval_sec=300,
        default_pages=1,
        scheduler_tick_sec=10,
        max_concurrency=2,
        max_retries=3,
        retry_base_sec=30,
        retry_max_sec=300,
        default_new_window_sec=86400,
        default_drop_abs=0.0,
        default_drop_pct=0.0,
        default_cooldown_sec=60,
        webhook_url=None,
        remote_base_url=None,
        remote_api_key=None,
        remote_headers_json=None,
        remote_timeout_sec=15,
        remote_healthcheck_on_init=False,
        remote_healthcheck_timeout_sec=10,
        queue_max_size=100,
        llm_provider_id=None,
        llm_prefilter_provider_id=None,
    )


async def check_login() -> str:
    """
    Probe Goofish login state.

    Note: PlaywrightSearchProvider.check_login_state() returns 'error' immediately
    when no browser/context is open. We open a context ourselves before checking,
    then classify the page state directly.
    """
    settings = _make_settings(block_assets=False)
    provider = PlaywrightSearchProvider(settings)
    try:
        context, should_close = await provider._open_operation_context()
        page = await context.new_page()
        error_flags: set[str] = set()
        provider._attach_page_state_watchers(page, error_flags)
        await page.goto(
            "https://www.goofish.com",
            wait_until="domcontentloaded",
            timeout=20_000,
        )
        await page.wait_for_timeout(2000)
        err = await provider._classify_timeout_page_state(page, error_flags=error_flags)
        await page.close()
        if should_close:
            await context.close()
        if err is None:
            return "ok"
        if err.code == ProviderErrorCode.AUTH_REQUIRED:
            return "auth_required"
        if err.code == ProviderErrorCode.CAPTCHA:
            return "captcha"
        return f"error: {err.code.value}"
    except Exception as exc:
        return f"error: {exc}"
    finally:
        await provider.close()


async def run_search(keyword: str, pages: int = 1) -> None:
    settings = _make_settings()
    provider = PlaywrightSearchProvider(settings)
    try:
        items = await provider.search(keyword=keyword, pages=pages, timeout_sec=30)
        print(f"\n[SEARCH] keyword={keyword!r} pages={pages}  →  {len(items)} items")
        if not items:
            print("  (0 items — session may be expired; run --login-only first)")
            return
        for item in items[:10]:
            ts = f"  ts={item.publish_time}" if item.publish_time else ""
            print(f"  [{item.item_id}] ¥{item.price:<8.0f}  {item.title[:50]!r}{ts}")
            print(f"    {item.url}")
    finally:
        await provider.close()


async def main() -> None:
    args = sys.argv[1:]

    if "--login-only" in args:
        print(f"storage_state: {STORAGE_STATE}  exists={STORAGE_STATE.exists()}")
        state = await check_login()
        print(f"[LOGIN] state={state!r}")
        if state == "ok":
            print("  Session is valid — scraping will work.")
        elif state == "auth_required":
            print("  Session EXPIRED. Restart AstrBot and run /闲鱼 登录 to re-authenticate.")
        elif state == "captcha":
            print("  CAPTCHA wall detected. Wait a few minutes then retry.")
        else:
            print(f"  state={state!r}")
        return

    keyword = next((a for a in args if not a.startswith("-")), "单反相机")
    pages_args = [a for a in args if a.isdigit()]
    pages = int(pages_args[0]) if pages_args else 1

    print(f"storage_state: {STORAGE_STATE}  exists={STORAGE_STATE.exists()}")
    await run_search(keyword, pages)


if __name__ == "__main__":
    asyncio.run(main())
