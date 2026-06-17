---
name: run-goofish-scraper
description: Run, test, and drive the GooFish scraping pipeline. Use when verifying the PlaywrightSearchProvider works, debugging why search returns 0 items, checking login state, or understanding the established scraping patterns for the browser agent.
---

# run-goofish-scraper

This plugin's core scraping layer is `app/provider_playwright.py` — a `PlaywrightSearchProvider`
that can be imported and run directly without AstrBot, using a saved `storage_state.json` session.
The driver is `.claude/skills/run-goofish-scraper/driver.py`, run from the AstrBot root.

## Prerequisites

All dependencies come from AstrBot's venv:

```bash
cd /Users/richardliu/Documents/Coding/AstrBot
.venv/bin/python -m playwright install chromium   # if Chromium is missing
```

No additional packages needed — Playwright is already in the venv.

## Run (agent path)

```bash
cd /Users/richardliu/Documents/Coding/AstrBot

# Check if the saved session is still valid
.venv/bin/python data/plugins/astrbot_plugin_goofish_catcher/.claude/skills/run-goofish-scraper/driver.py --login-only

# Run a search (headless)
.venv/bin/python data/plugins/astrbot_plugin_goofish_catcher/.claude/skills/run-goofish-scraper/driver.py "尼康 Z9"

# Search 2 pages
.venv/bin/python data/plugins/astrbot_plugin_goofish_catcher/.claude/skills/run-goofish-scraper/driver.py "iPhone 15" 2
```

Output to stdout:

```
storage_state: /.../storage_state.json  exists=True
[SEARCH] keyword='尼康 Z9' pages=1  →  12 items
  [123456789] ¥4500    '尼康 Z9 单机 成色很新'
    https://www.goofish.com/item?id=123456789
  ...
```

When 0 items returned, run `--login-only` first to confirm the session. If `auth_required`, restart
AstrBot and re-authenticate with `/闲鱼 登录`.

## Established scraping patterns (key domain knowledge)

These patterns are stable, battle-tested. The browser agent and any new scraping code should
follow them.

### Search URL

```
https://www.goofish.com/search?q={URL-encoded-keyword}
```

Direct navigation — do NOT use the search box on the homepage. Navigate here directly.

### Item page URL

```
https://www.goofish.com/item?id={item_id}
```

Item IDs are pure digits. Extract from URL: `?id=`, `?item_id=`, `?itemId=`, or path pattern `item[=/](\d+)`.

### Auth detection (login wall)

Three layers, checked in order:

1. **URL-based** — any of these mean auth required:
   - `passport.goofish.com` + path contains `mini_login.htm`, `/login`, or `/login/`
   - `goofish.com` + path contains `mini_login.htm` or `member/login`
2. **HTML marker** — page source contains `alibaba-login-box` or `passport.goofish.com/mini_login.htm`
3. **API payload** — response `ret` field contains `fail_sys_session_expired`,
   `fail_sys_illegal_access`, `session过期`, `请登录`, or `need_login`

If any of these fire → raise `ProviderError(AUTH_REQUIRED)`.

### CAPTCHA detection

URL-based: host contains `cf.aliyun.com` + path contains `nocaptcha`, or any path contains `captcha`.
Payload-based: `ret` field contains `captcha`, `验证码`, or `滑块`.

### Item data extraction (three-tier cascade)

**Tier 1 — JSON payload interception** (zero additional latency):

The search API fires `mtop.taobao.idle.*` endpoints returning JSON. Capture all JSON responses
and recursively walk the payload tree looking for objects with all of: a title field
(`title`, `item_title`, `name`, `itemName`, `subject`), a price field, and an ID. Item IDs
are found under `item_id`, `itemId`, `id`, `auctionId`, `targetId`, `itemid`.

**Tier 2 — DOM extraction** (fallback when API returns 0 items):

```css
a[href*='item']
```

Each matching node: `href` → URL, `innerText.split('\n')[0]` → title, full `innerText` → price
search with `_parse_price`. Requires both title and a parseable price to be accepted.

**Tier 3 — AX Tree + LLM** (fallback when both above return 0):

Only fires when `llm_enabled=True`. Takes Playwright's accessibility snapshot, serialises it
to compact text via `ax_tree_to_text()`, sends to LLM. This fallback handles Goofish frontend
updates that break CSS selectors.

### Price normalization

Handles: plain float/int, `"1500"`, `"1.5万"`, `"1.5w"`, `"1.5k"`, dict with `price`/`amount`/`value`
key, list (takes first parseable value). Regex: `(\d+(?:\.\d+)?)` × multiplier.

### Favorite button

```css
div[class*='buttons--'] div[class*='right--']
```

Text states: `"收藏"` (can favorite) / `"已收藏"` (already favorited). Clicking the button and
waiting for the text to switch to `"已收藏"` confirms success. Auth prompt may appear instead
— check `_classify_favorite_page_state` first.

### Asset blocking

When `playwright_block_assets=True`, abort `image`, `font`, `media` requests to speed up scraping.
This has no effect on JSON API calls or HTML rendering.

### Wait strategy

1. `domcontentloaded` → `networkidle` (up to 6s)
2. Poll DOM every 350ms; stop when ≥6 items or 2 consecutive stable counts
3. Scroll every 2nd poll to trigger lazy loading

### Key API endpoints to monitor (for debugging)

| Endpoint substring | What it means |
|---|---|
| `mtop.taobao.idle.pc.detail` | Item detail page data |
| `mtop.taobao.idlemessage.pc.loginuser.get` | Login user check |
| `mtop.taobao.idle.collect.item` | Favorite / collect action |
| `com.taobao.idle.unfavor.item` | Un-favorite action |
| `mtop.idle.web.user.page.nav` | Page navigation data |

## How this knowledge helps the browser agent

`GofishBrowserAgent` runs a ReAct loop driven by an LLM. Its system prompt currently is
generic. Key improvements the agent can make using the patterns above:

1. Navigate directly to `https://www.goofish.com/search?q={keyword}` instead of the homepage
2. Recognize auth signals by URL/text without needing LLM interpretation
3. Know the exact CSS/AX path to the favorite button
4. Expect item IDs in URL `?id=` parameters

To inject this knowledge into the agent, update `_SYSTEM_PROMPT` in `app/browser_agent.py`
with the search URL pattern, auth markers, and favorite button location.

## Gotchas

- **`check_login_state()` returns `'error'` before any browser is opened.** The method checks
  `self._persistent_context is None and self._browser is None` before making any network calls
  — it returns `'error'` immediately when both are None. Must open a page context first.
  The driver's `check_login()` function works around this by calling `_open_operation_context()`
  directly.

- **Storage_state path vs user_data_dir are mutually exclusive.** When `playwright_user_data_dir`
  is set, Chromium runs as a persistent profile (one process per dir). When only
  `playwright_storage_state_path` is set, each operation creates a fresh context with imported
  cookies. The two cannot be used simultaneously.

- **`playwright_block_assets=True` can cause 0 items.** If Goofish ever loads item cards via
  images (lazy-loaded content), blocking assets can cause 0 items. Disable for debugging.

- **Goofish rate-limits headless Chromium after ~3 requests in quick succession.**
  Symptoms: `ERR_CONNECTION_RESET`. Wait 30–60 seconds between test runs.

- **The mtop API endpoints often fire only after scroll.** A bare `goto + wait_for_timeout`
  may get 0 API payloads. The production code scrolls every 2nd poll to trigger them.

- **`payloads=3` with 0 items usually means expired session.** The 3 JSON responses are
  `xux-web-config.oss-accelerate.aliyuncs.com/aes-config/idle_pc/qnrForm.json` — a
  questionnaire config, not search results. Real search payloads go through `mtop.*` endpoints.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `0 items, payloads=3` | Session expired. Re-auth in AstrBot with `/闲鱼 登录`. |
| `ERR_CONNECTION_RESET` | Rate-limited. Wait 60s, reduce test frequency. |
| `login_state='error'` from driver | Normal when no browser context exists yet — the driver's `check_login()` opens one. The plugin's `check_login_state()` only works after `_persistent_context` or `_browser` is initialized. |
| `DEPENDENCY_MISSING` error | Run: `cd /Users/richardliu/Documents/Coding/AstrBot && .venv/bin/python -m playwright install chromium` |
| Favorite button not found | CSS class names changed in a Goofish deploy. Enable LLM fallback (`llm_enabled=True`) or update `_DETAIL_FAVORITE_BUTTON_SELECTOR`. |
