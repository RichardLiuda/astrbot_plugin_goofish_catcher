"""
本地实验台：脱离 AstrBot，直接驱动插件的抓取/登录层。

用途：
1. 走一遍项目核心流程（扫码登录 -> 会话探测 -> 实时搜索）
2. SSO 验证实验：检查闲鱼登录态能否直接带通淘宝搜索

用法（在仓库根目录执行）：
  .venv/Scripts/python.exe scripts/local_lab.py login              # 扫码登录，保存会话
  .venv/Scripts/python.exe scripts/local_lab.py login-taobao       # 手机淘宝扫码登录，保存淘宝独立会话
  .venv/Scripts/python.exe scripts/local_lab.py check              # 探测已存会话是否有效
  .venv/Scripts/python.exe scripts/local_lab.py search "RTX 5090" [pages] [--headless]
  .venv/Scripts/python.exe scripts/local_lab.py search-taobao "RTX 5090" [pages] [--headless]
  .venv/Scripts/python.exe scripts/local_lab.py watch-taobao "RTX 5090" [--interval=600] [--cycles=N] [--headless]
  .venv/Scripts/python.exe scripts/local_lab.py sso ["RTX 5090"] [--headless]

产物都写在 local_data/ 下（storage_state.json、qr.jpg、sso 探针截图/HTML），
该目录含登录 cookie，切勿提交 git。
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Windows GBK 控制台无法编码 "¥" 等字符，替换显示而不是崩溃；行缓冲便于后台任务实时看输出
sys.stdout.reconfigure(errors="replace", line_buffering=True)
sys.stderr.reconfigure(errors="replace", line_buffering=True)

LOCAL_DATA = REPO_ROOT / "local_data"
STORAGE_STATE = LOCAL_DATA / "storage_state.json"
TAOBAO_STORAGE_STATE = LOCAL_DATA / "storage_state.taobao.json"
TAOBAO_SEARCH_URL = "https://s.taobao.com/search?q={kw}"

from app.config import PROVIDER_MODE_PLAYWRIGHT_LOCAL, PluginSettings
from app.detector import evaluate_price_drop
from app.login_session import GoofishLoginSession
from app.platforms import TAOBAO_PROFILE
from app.provider_playwright import PlaywrightSearchProvider
from app.storage import SubscriptionStorage
from app.types import ProviderError, ProviderErrorCode

logging.basicConfig(
    level=os.environ.get("LAB_LOG", "WARNING").upper(),
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


def _make_settings(*, headless: bool, block_assets: bool = True) -> PluginSettings:
    """Mirror .claude/skills/run-goofish-scraper/driver.py, with local paths."""
    return PluginSettings(
        plugin_name="astrbot_plugin_goofish_catcher",
        plugin_data_dir=LOCAL_DATA,
        provider_mode=PROVIDER_MODE_PLAYWRIGHT_LOCAL,
        playwright_headless=headless,
        playwright_storage_state_path=STORAGE_STATE if STORAGE_STATE.exists() else None,
        playwright_user_data_dir=None,  # mutually exclusive with storage_state
        playwright_block_assets=block_assets,
        playwright_force_direct=os.environ.get("LAB_FORCE_DIRECT", "") == "1",
        playwright_executable_path=None,
        llm_enabled=False,
        db_path=LOCAL_DATA / "goofish.db",
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


def _cookie_domains(state_path: Path = STORAGE_STATE) -> dict[str, list[str]]:
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    domains: dict[str, list[str]] = {}
    for cookie in payload.get("cookies", []):
        domains.setdefault(str(cookie.get("domain", "")), []).append(
            str(cookie.get("name", ""))
        )
    return domains


def _print_cookie_summary(state_path: Path = STORAGE_STATE) -> None:
    domains = _cookie_domains(state_path)
    total = sum(len(v) for v in domains.values())
    print(f"[COOKIE] 共 {total} 个 cookie，按域分布：")
    for domain, names in sorted(domains.items()):
        print(f"  {domain:<28} {len(names):>3} 个: {', '.join(sorted(set(names))[:10])}")


async def cmd_login(platform: str = "goofish") -> int:
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    is_taobao = platform == "taobao"
    storage_path = TAOBAO_STORAGE_STATE if is_taobao else STORAGE_STATE
    app_name = "淘宝" if is_taobao else "闲鱼"
    session = GoofishLoginSession(
        force_direct=os.environ.get("LAB_FORCE_DIRECT", "") == "1",
        profile=TAOBAO_PROFILE if is_taobao else None,
    )
    try:
        snapshot = await session.start_login_session()
        print(f"[LOGIN] 浏览器已打开: {snapshot.page_url}")
        try:
            img = await session.capture_screenshot_base64()
            (LOCAL_DATA / "qr.jpg").write_bytes(base64.b64decode(img))
        except Exception:
            pass
        print(f"[LOGIN] 请用手机{app_name} App 扫**浏览器窗口里**的二维码，并在手机上点确认")
        print("      （qr.jpg 有备份截图；确认后页面会自动跳转，脚本检测到即自动保存，")
        print("       二维码在扫码前不会被刷新，可以慢慢扫）")

        page = session._page  # lab 脚本内省自己的会话对象
        reloaded = asyncio.Event()

        def _on_nav(frame) -> None:
            try:
                if frame == page.main_frame:
                    reloaded.set()
            except Exception:
                pass

        page.on("framenavigated", _on_nav)
        # 关键：不主动轮询 validate_login——它会 goto 重载页面、把二维码刷掉。
        # 改为监听主框架导航：用户扫码确认后闲鱼会自动跳转，此时再 validate。
        # 每 ~30s 兜底 validate 一次（防止导航事件漏接）。
        for attempt in range(60):  # 最长约 6 分钟
            try:
                await asyncio.wait_for(reloaded.wait(), timeout=5)
            except asyncio.TimeoutError:
                if attempt % 6 != 5:
                    continue
                # 仍停留在登录页时不要 validate——goto 探测页会把二维码从屏幕上拖走
                try:
                    current = str(getattr(page, "url", "") or "")
                    if session._profile.is_auth_url(current):
                        continue
                except Exception:
                    pass
            result = await session.validate_login()
            await asyncio.sleep(1)
            reloaded.clear()  # validate 自身的 goto 也会触发导航事件，清掉避免空转
            if result.get("ok"):
                path = await session.save_storage_state(storage_path)
                print(f"[LOGIN] 登录成功，会话已保存: {path}")
                _print_cookie_summary(storage_path)
                return 0
            print(f"[LOGIN] 等待扫码... ({result.get('code')}: {str(result.get('reason', ''))[:60]})")
        print("[LOGIN] 等待超时。二维码可能已过期，请重新运行 login。")
        return 1
    finally:
        await session.close()


async def cmd_check() -> int:
    print(f"[CHECK] storage_state: {STORAGE_STATE}  exists={STORAGE_STATE.exists()}")
    if not STORAGE_STATE.exists():
        print("[CHECK] 没有已存会话，先运行 login。")
        return 1
    settings = _make_settings(headless=True, block_assets=False)
    provider = PlaywrightSearchProvider(settings)
    try:
        # check_login_state() 在浏览器未打开时直接返回 error，
        # 因此像 driver.py 一样自己开 context 再做页面状态分类。
        context, should_close = await provider._open_operation_context()
        page = await context.new_page()
        error_flags: set[str] = set()
        provider._attach_page_state_watchers(page, error_flags)
        await page.goto(
            "https://www.goofish.com", wait_until="domcontentloaded", timeout=20_000
        )
        await page.wait_for_timeout(2000)
        err = await provider._classify_timeout_page_state(page, error_flags=error_flags)
        await page.close()
        if should_close:
            await context.close()
        if err is None:
            print("[CHECK] state=ok —— 会话有效，可以搜索。")
            return 0
        print(f"[CHECK] state={err.code.value} —— {err.message}")
        return 1
    finally:
        await provider.close()


async def cmd_search(keyword: str, pages: int, headless: bool) -> int:
    if not STORAGE_STATE.exists():
        print("[SEARCH] 没有已存会话，先运行 login。")
        return 1
    settings = _make_settings(headless=headless)
    provider = PlaywrightSearchProvider(settings)
    try:
        items = await provider.search(
            keyword=keyword, pages=pages, timeout_sec=60
        )
        print(f"\n[SEARCH] keyword={keyword!r} pages={pages} → {len(items)} items")
        if not items:
            print("  (0 条结果 —— 先 check 确认会话；再用")
            print('   $env:LAB_LOG="INFO"; .venv/Scripts/python.exe scripts/local_lab.py search "..." --headed')
            print("   观察页面实况与 payload 计数（payloads=3 + 0 items = 会话过期）)")
            return 1
        for item in items[:10]:
            print(f"  [{item.item_id}] ¥{item.price:<8.0f} {item.title[:50]!r}")
            print(f"    {item.url}")
        return 0
    finally:
        await provider.close()


async def cmd_search_taobao(keyword: str, pages: int, headless: bool) -> int:
    # 有淘宝独立会话就用，没有就访客态（淘宝允许访客搜索，但新指纹可能弹滑块）
    state = TAOBAO_STORAGE_STATE if TAOBAO_STORAGE_STATE.exists() else None
    if state:
        print(f"[TAOBAO] 使用淘宝独立会话: {state}")
    settings = _make_settings(headless=headless)
    settings.playwright_storage_state_path = state
    provider = PlaywrightSearchProvider(settings, profile=TAOBAO_PROFILE)
    try:
        items = await provider.search(keyword=keyword, pages=pages, timeout_sec=60)
        print(f"\n[TAOBAO] keyword={keyword!r} pages={pages} → {len(items)} items")
        if not items:
            print("  (0 条结果 —— 可能触发滑块/风控，用 --headed 手动过后再试)")
            return 1
        for item in items[:10]:
            raw = item.raw or {}
            print(f"  [{item.item_id}] ¥{item.price:<10.2f} {item.title[:40]!r}")
            print(f"    店铺={raw.get('shopName') or '-'}  销量={raw.get('salesText') or '-'}")
            print(f"    {item.url}")
        return 0
    except ProviderError as exc:
        print(f"[TAOBAO] {exc.code.value}: {exc.message}")
        if exc.code in (ProviderErrorCode.CAPTCHA, ProviderErrorCode.AUTH_REQUIRED):
            print("  提示：用 --headed 重跑，在弹出的窗口里手动过验证")
        return 1
    finally:
        await provider.close()


async def cmd_watch_taobao(keyword: str, interval: int, max_cycles: int, headless: bool) -> int:
    """淘宝轮询监控实验（阶段 1.5a）。

    双重目的：①实证淘宝对自动轮询的风控容忍度（多少次/什么频率触发 punish）；
    ②走通平台化存储链路——订阅/商品/价格历史/市场 EMA 全部带 platform=taobao 落库。
    """
    state = TAOBAO_STORAGE_STATE if TAOBAO_STORAGE_STATE.exists() else None
    settings = _make_settings(headless=headless)
    settings.playwright_storage_state_path = state
    provider = PlaywrightSearchProvider(settings, profile=TAOBAO_PROFILE)
    storage = SubscriptionStorage(LOCAL_DATA / "goofish.db")
    await storage.initialize()
    sub, created = await storage.upsert_subscription(
        umo="local_lab:cli",
        keyword=keyword,
        platform="taobao",
        interval_sec=interval,
        pages=1,
        recommend_max_price=None,
        drop_abs=50.0,
        drop_pct=0.05,
        new_window_sec=86400,
        cooldown_sec=0,
    )
    print(f"[WATCH] 订阅 #{sub.id}（{'新建' if created else '复用'}，platform={sub.platform}）"
          f" keyword={keyword!r} interval={interval}s cycles={'∞' if max_cycles <= 0 else max_cycles}")
    captcha_streak = 0
    cycle = 0
    try:
        while max_cycles <= 0 or cycle < max_cycles:
            cycle += 1
            started_at = int(time.time())
            run_id = await storage.create_fetch_run(sub.id, started_at)
            try:
                items = await provider.search(keyword=keyword, pages=1, timeout_sec=60)
            except ProviderError as exc:
                await storage.finish_fetch_run(
                    run_id, finished_at=int(time.time()), status="failed",
                    err_type=exc.code.value, err_msg=str(exc)[:200],
                )
                await storage.update_schedule_failure(sub.id, int(time.time()), 60)
                if exc.code == ProviderErrorCode.CAPTCHA:
                    captcha_streak += 1
                    print(f"[WATCH] #{cycle} ⛔ 风控（连续 {captcha_streak} 次）: {exc.message}")
                    if captcha_streak >= 3:
                        print("[WATCH] 连续 3 次风控，判定此频率不可用。"
                              "请重跑 sso 刷新会话后加大 --interval 再试。")
                        break
                else:
                    print(f"[WATCH] #{cycle} ❌ {exc.code.value}: {exc.message}")
                await asyncio.sleep(interval)
                continue
            captcha_streak = 0
            now_ts = int(time.time())
            new_items: list = []
            drops: list = []
            price_rows: list[tuple[int, str, float, int, str]] = []
            for item in items:
                existing = await storage.get_item(sub.id, item.item_id)
                if existing is None:
                    new_items.append(item)
                    price_rows.append((sub.id, item.item_id, item.price, now_ts, "watch_taobao"))
                else:
                    decision = evaluate_price_drop(
                        existing.last_price, item.price, sub.drop_abs, sub.drop_pct
                    )
                    if decision.triggered:
                        drops.append((item, existing.last_price, decision))
                    if existing.last_price != item.price:
                        price_rows.append(
                            (sub.id, item.item_id, item.price, now_ts, "watch_taobao")
                        )
            await storage.upsert_items_bulk(sub.id, items, now_ts)
            await storage.insert_price_history_bulk(price_rows)
            ema_text = ""
            prices = [i.price for i in items if i.price > 0]
            if prices:
                mp = await storage.upsert_market_price(
                    sub.keyword, prices, now_ts, platform=sub.platform
                )
                ema_text = f" EMA={mp.ema_price:.0f}(n={mp.sample_count})"
            await storage.finish_fetch_run(
                run_id, finished_at=now_ts, status="success", items_count=len(items)
            )
            await storage.update_schedule_success(sub.id, now_ts, interval)
            print(f"[WATCH] #{cycle} ✅ {len(items)} 条（新 {len(new_items)} / 降价 {len(drops)}）{ema_text}")
            for item in new_items[:3]:
                print(f"  🆕 [{item.item_id}] ¥{item.price:.2f} {item.title[:36]!r}")
            for item, last, dec in drops[:3]:
                print(f"  📉 [{item.item_id}] ¥{last:.2f} → ¥{item.price:.2f}"
                      f"（-{dec.drop_pct:.1%}）{item.title[:30]!r}")
            if max_cycles <= 0 or cycle < max_cycles:
                await asyncio.sleep(interval)
    finally:
        await provider.close()
        await storage.close()
    print(f"[WATCH] 结束，共 {cycle} 轮。fetch_runs/items/price_history/market_price"
          f" 已写入 local_data/goofish.db")
    return 0


async def cmd_sso(keyword: str, headless: bool) -> int:
    if not STORAGE_STATE.exists():
        print("[SSO] 没有已存会话，先运行 login。")
        return 1

    # ---- 第 1 步：离线 cookie 域分析 ----
    print("=" * 60)
    print("[SSO] 第 1 步：storage_state.json cookie 域分析")
    print("=" * 60)
    _print_cookie_summary()
    domains = _cookie_domains()
    key_names = {"cookie2", "unb", "_tb_token_", "sgcookie", "_m_h5_tk", "cna", "t"}
    print("\n[SSO] 阿里系关键域的关键 cookie：")
    for domain, names in sorted(domains.items()):
        if not any(k in domain for k in ("taobao", "tmall", "alibaba", "mmstat")):
            continue
        hits = sorted(set(names) & key_names)
        print(f"  {domain:<28} 关键 cookie: {hits if hits else '无'}")
    has_tb_session = any(
        domain.endswith(".taobao.com") and "cookie2" in names
        for domain, names in domains.items()
    )
    print(f"\n[SSO] .taobao.com 域是否已持有登录态 cookie (cookie2): {has_tb_session}")

    # ---- 第 2 步：带同一套会话实测淘宝搜索 ----
    print("\n" + "=" * 60)
    print(f"[SSO] 第 2 步：携带该会话访问 {TAOBAO_SEARCH_URL.format(kw=quote(keyword))}")
    print("=" * 60)
    # 优先使用淘宝独立会话文件（含上次手动登录/过验证后的 cookie）；
    # 首次运行没有它时退回闲鱼会话 —— 这正是"按平台隔离存储"的微缩验证。
    tb_state = TAOBAO_STORAGE_STATE if TAOBAO_STORAGE_STATE.exists() else STORAGE_STATE
    if tb_state == TAOBAO_STORAGE_STATE:
        print("[SSO] 使用淘宝独立会话 storage_state.taobao.json")
    settings = _make_settings(headless=headless)
    settings.playwright_storage_state_path = tb_state if tb_state.exists() else None
    provider = PlaywrightSearchProvider(settings)
    try:
        context, should_close = await provider._open_operation_context()
        page = await context.new_page()
        payloads: list = []

        async def _on_response(response) -> None:
            try:
                if "json" not in (response.headers.get("content-type") or ""):
                    return
                payloads.append(await response.json())
            except Exception:
                return

        page.on("response", lambda r: asyncio.create_task(_on_response(r)))
        await page.goto(
            TAOBAO_SEARCH_URL.format(kw=quote(keyword)),
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        await page.wait_for_timeout(3000)
        await page.mouse.wheel(0, 2000)  # trigger lazy-load / mtop XHRs
        await page.wait_for_timeout(4000)

        final_url = str(page.url)
        html = await page.content()
        login_hit = "login.taobao.com" in final_url or "passport.taobao" in final_url
        captcha_hit = any(
            m in html for m in ("验证码", "滑块", "baxia", "nocaptcha", "rgv587")
        )

        if (login_hit or captcha_hit) and not headless:
            what = "登录墙" if login_hit else "验证码/风控"
            print(f"[SSO] 命中{what}。请在浏览器窗口里手动完成验证/登录，")
            print("      脚本每 3 秒自动检测（最长 6 分钟），检测到商品即继续...")
            cleared = False
            for _ in range(120):
                await page.wait_for_timeout(3000)
                probe = provider._extract_items_from_payloads(payloads)
                if not probe:
                    try:
                        probe = await provider._extract_items_from_dom(page)
                    except Exception:
                        probe = []
                if len(probe) >= 3:
                    cleared = True
                    break
            print(f"[SSO] 手动处理{'完成' if cleared else '超时（6 分钟）'}")
            final_url = str(page.url)
            html = await page.content()
            login_hit = "login.taobao.com" in final_url or "passport.taobao" in final_url
            captcha_hit = any(
                m in html for m in ("验证码", "滑块", "baxia", "nocaptcha", "rgv587")
            )
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(3000)

        items = provider._extract_items_from_payloads(payloads)
        extract_tier = "payload"
        if not items:
            # 淘宝搜索结果以 SSR DOM 为主，XHR 里多是埋点/配置；
            # 退到第二级 DOM 提取（a[href*='item']）。
            try:
                items = await provider._extract_items_from_dom(page)
                extract_tier = "dom"
            except Exception as exc:
                print(f"[SSO] DOM 提取异常: {exc}")
        (LOCAL_DATA / "sso_taobao.html").write_text(html, encoding="utf-8")
        (LOCAL_DATA / "sso_payloads.json").write_text(
            json.dumps(payloads, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        await page.screenshot(path=str(LOCAL_DATA / "sso_taobao.png"), full_page=False)

        # 把淘宝侧会话（含手动登录/过验证后的新 cookie）独立落盘，
        # 下次 probe 复用 —— 用于验证"保持登录"在持久会话下是否生效。
        try:
            await context.storage_state(path=str(TAOBAO_STORAGE_STATE))
            print(f"[SSO] 淘宝会话已独立保存: {TAOBAO_STORAGE_STATE}")
        except Exception as exc:
            print(f"[SSO] 淘宝会话保存失败: {exc}")

        print(f"\n[SSO] 最终 URL: {final_url}")
        print(f"[SSO] 登录墙: {login_hit}  风控/验证码: {captcha_hit}")
        print(f"[SSO] 捕获 JSON 响应 {len(payloads)} 个，"
              f"提取商品 {len(items)} 条（来源: {extract_tier} 层）")
        for item in items[:5]:
            print(f"  [{item.item_id}] ¥{item.price:<8.2f} {item.title[:50]!r}")
            print(f"    {item.url}")
        print("[SSO] 快照已保存: local_data/sso_taobao.png / sso_taobao.html / sso_payloads.json")

        print("\n" + "=" * 60)
        print("[SSO] 实验结论判定")
        print("=" * 60)
        if len(items) >= 3:
            print(f"结论 A：访客/共享会话可访问淘宝搜索，{extract_tier} 层可提取商品。")
            print("        → 淘宝适配 = 新搜索 URL + DOM/字段规则（SiteProfile）。")
            print("        注意：cookie 分析显示闲鱼登录并未播种 .taobao.com 域，")
            print("        登录态仍需按平台隔离（本次能搜是因为淘宝允许访客搜索）。")
            return 0
        if login_hit:
            print("结论 C：淘宝会话未建立（被重定向到登录页）。")
            print("        → 淘宝需要独立登录/播种流程，登录态必须按平台隔离。")
            return 1
        if captcha_hit:
            print("结论 B：淘宝对新浏览器指纹触发风控（与是否有会话无关——")
            print("        cookie 分析已确认 .taobao.com 无登录态，本质是访客访问）。")
            print("        → 需要为淘宝建立独立登录态 + 低频冷却策略。")
            return 1
        print("结论不明确：未命中登录墙/风控，但也没提取到商品。")
        print("        → 需要人工查看 local_data/sso_taobao.png 与 html 判断")
        print("          是页面结构问题还是 payload 形状不兼容。")
        return 1
    finally:
        await provider.close()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    cmd, rest = args[0], args[1:]
    positional = [a for a in rest if not a.startswith("-")]

    if cmd == "login":
        return asyncio.run(cmd_login())
    if cmd == "login-taobao":
        return asyncio.run(cmd_login(platform="taobao"))
    if cmd == "check":
        return asyncio.run(cmd_check())
    if cmd == "search":
        keyword = positional[0] if positional else "RTX 5090"
        pages = int(positional[1]) if len(positional) > 1 else 1
        # 默认有头（与生产 config.py:353 对齐）；headless 易被限流，仅调试用
        return asyncio.run(cmd_search(keyword, pages, headless="--headless" in rest))
    if cmd == "search-taobao":
        keyword = positional[0] if positional else "RTX 5090"
        pages = int(positional[1]) if len(positional) > 1 else 1
        # 默认有头：淘宝新指纹常弹滑块，可见窗口便于手动过验证
        return asyncio.run(
            cmd_search_taobao(keyword, pages, headless="--headless" in rest)
        )
    if cmd == "watch-taobao":
        keyword = positional[0] if positional else "RTX 5090"
        interval = 600
        cycles = 0
        for a in rest:
            if a.startswith("--interval="):
                interval = int(a.split("=", 1)[1])
            elif a.startswith("--cycles="):
                cycles = int(a.split("=", 1)[1])
        return asyncio.run(
            cmd_watch_taobao(keyword, interval, cycles, headless="--headless" in rest)
        )
    if cmd == "sso":
        keyword = positional[0] if positional else "RTX 5090"
        # 默认有头：第一次接触淘宝，看得见页面、能手动过滑块，对实验更有价值
        return asyncio.run(cmd_sso(keyword, headless="--headless" in rest))
    print(f"未知命令: {cmd}\n{__doc__}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
