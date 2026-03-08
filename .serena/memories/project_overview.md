# astrbot_plugin_goofish_catcher project overview
- Purpose: AstrBot plugin for Goofish keyword monitoring, subscription polling, new-item/price-drop detection, recommendation analysis, and notifications.
- Tech stack: Python 3.10+, AstrBot plugin API, aiosqlite, httpx, playwright.
- Rough structure: `main.py` plugin commands and lifecycle; `app/config.py` settings; `app/provider.py` provider factory; `app/provider_playwright.py` local browser scraping; `app/provider_remote.py` remote REST provider client; `app/scheduler.py` polling and retry orchestration; `app/storage.py` sqlite persistence; `tests/` pytest coverage.
- Current remote state: config model and remote provider client already exist (`remote_rest`), but `_conf_schema.json` does not expose remote settings and there is no worker server implementation yet.
- Scheduler already handles ProviderErrorCode-based pause/retry/alert flows, so remote integration should preserve existing error contracts instead of adding a parallel mechanism.
