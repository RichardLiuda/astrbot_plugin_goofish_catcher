"""
GofishBrowserAgent — 独立 Chromium 进程，由 LLM 通过 ReAct 循环驱动，
在闲鱼（goofish.com）上执行自然语言描述的任意浏览器任务。

与调度器的 PlaywrightSearchProvider 完全隔离：
  - 独立 async_playwright() 进程，不共享 user_data_dir
  - 登录态通过 storage_state dict（内存传递）注入
  - headless=True，用完即销毁
"""
from __future__ import annotations

import asyncio
import logging
import traceback
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .provider_agent import _extract_json_object

# ── 全局活跃实例计数 ──────────────────────────────────────────────────────────
_active_agents: int = 0

# ── 常量 ─────────────────────────────────────────────────────────────────────

_GOOFISH_BASE = "https://www.goofish.com"
_ALLOWED_DOMAIN = "goofish.com"
_MAX_HISTORY = 8        # 历史记录最多保留步数
_AX_MAX_CHARS = 20_000  # aria_snapshot 字符上限，防止 prompt 过长

# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
你是一个闲鱼（goofish.com）网页操作助手。你通过控制浏览器来完成用户指定的任务。

## 操作规则
1. 你只能在 goofish.com 域名内操作，不得导航到其他网站。
2. 每一步你会收到当前页面的无障碍树（Accessibility Tree），根据它决定下一步操作。
3. 你必须输出且仅输出一个 JSON 对象作为你的下一步动作，不要添加任何其他文字或 Markdown。
4. 如果遇到登录墙（出现登录/扫码提示），立即使用 fail 动作，reason 填 "AUTH_REQUIRED"。
5. 如果遇到验证码/滑块，立即使用 fail 动作，reason 填 "CAPTCHA"。
6. 任务完成后使用 done 动作附带结果摘要。
7. click 动作的 target 字段填写无障碍树中元素的 name 字段内容（引号内的文字）。
   例如树中有 [button] "收藏"，则 target 填 "收藏"。
   role 可选，用于区分同名的不同类型元素（link / button / textbox 等）。
8. extract 动作不导航，对当前页面内容提取指定信息，结果记录在历史中供后续使用。
9. 尽量用最少步骤完成任务。

## 闲鱼页面结构（已验证的固定模式）

### 搜索
- 搜索页 URL：https://www.goofish.com/search?q={关键词（URL 编码）}
- **直接导航到搜索 URL，不要通过首页搜索框搜索。**
- 商品卡片是 `a[href*='item']` 链接，标题在链接文本第一行，价格在后续行。
- 搜索结果可能需要向下滚动才能完整加载。

### 商品详情页
- 商品 URL 格式：https://www.goofish.com/item?id={纯数字 ID}
- 商品 ID 是纯数字，可从 URL 的 `?id=` 参数提取。
- 收藏按钮：页面右侧操作区，文本为 **"收藏"**（未收藏）或 **"已收藏"**（已收藏）。
  点击后等待文本变为"已收藏"即为收藏成功。

### 登录墙识别（任意一项出现即为 AUTH_REQUIRED）
- 当前 URL 包含 `passport.goofish.com`，路径含 `mini_login.htm`、`/login`
- 当前 URL 包含 `goofish.com/member/login`
- 页面 HTML 含 `alibaba-login-box`
- AX 树中出现"登录"、"扫码"、"请登录"等提示

### 验证码识别（出现即为 CAPTCHA）
- URL 含 `cf.aliyun.com` 且含 `nocaptcha`
- 页面出现"滑块"、"验证码"文字

## 可用动作及字段
- navigate:      url（字符串，必须是 goofish.com 域名）
- extract_items: 无额外字段。**提取当前页面全部商品**（自动走 JSON 拦截 → DOM 降级，速度与纯脚本相当）
- click:         target（元素名称/可见文本），role（可选：link/button/textbox/heading/listitem）
- type:          target（输入框名称），text（要输入的内容）
- scroll:        direction（down 或 up）
- wait:          seconds（数字，0.5 到 5）
- extract:       description（用 LLM 从 AX 树提取指定信息，仅在无法用 extract_items 时使用）
- done:          result（任务完成摘要或提取的数据）
- fail:          reason（失败原因，如 AUTH_REQUIRED / CAPTCHA / 其他描述）

## 搜索任务的标准路径（最快）
1. `navigate` → `https://www.goofish.com/search?q={关键词}`
2. `extract_items`（无需等待，直接提取）
3. 若返回空，`scroll` 一次再 `extract_items`
4. `done` 并汇总结果

**不要**用 AX 树手动读取商品标题和价格，`extract_items` 比 LLM 解析 AX 树快 10 倍且更准确。
"""

_STEP_PROMPT_TEMPLATE = """\
## 任务
{task}

## 当前状态
- 步骤：第 {step}/{max_steps} 步
- 当前页面 URL：{current_url}

## 历史操作记录
{history}

## 当前页面无障碍树
{ax_tree_text}

输出你的下一步动作（仅输出 JSON 对象）：\
"""

_EXTRACT_SYSTEM = "你是一个网页数据提取助手，只输出所需数据，不添加任何解释。"
_EXTRACT_PROMPT_TEMPLATE = """\
以下是页面的无障碍树：
{ax_tree_text}

请提取：{description}

直接输出提取结果（JSON 或文本均可）：\
"""


# ── 主类 ──────────────────────────────────────────────────────────────────────

class GofishBrowserAgent:
    """独立浏览器 Agent，通过 ReAct 循环执行自然语言任务。

    用法::

        storage_state = await provider.export_storage_state()
        async with GofishBrowserAgent(
            storage_state=storage_state,
            llm_call=llm_call,
        ) as agent:
            result = await agent.run("搜索尼康Z9并收藏第一个结果")
    """

    def __init__(
        self,
        *,
        storage_state: dict[str, Any] | None = None,
        llm_call,           # async (prompt: str, system_prompt: str) -> str
        max_steps: int = 15,
        step_timeout_sec: int = 60,
        headless: bool = False,
        executable_path: Path | str | None = None,
        force_direct: bool = False,
    ) -> None:
        self._storage_state = storage_state
        self._llm_call = llm_call
        self._max_steps = max(3, max_steps)
        self._step_timeout_sec = max(10, step_timeout_sec)
        self._headless = headless
        self._executable_path = (
            Path(executable_path).expanduser()
            if executable_path is not None
            else None
        )
        self._force_direct = force_direct

        # 运行时状态，由 __aenter__ 初始化
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        # 拦截到的 JSON 响应 payload，供 extract_items 使用
        self._captured_payloads: list[Any] = []
        self._page = None

    # ── 生命周期 ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "GofishBrowserAgent":
        global _active_agents
        try:
            from playwright.async_api import async_playwright
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "playwright is not installed. "
                "Run: uv pip install playwright && python -m playwright install chromium"
            ) from exc

        caller_stack = "".join(traceback.format_stack(limit=6)[:-1]).strip()
        _active_agents += 1
        logger.debug(
            "[goofish_catcher][browser_agent] LAUNCH start — active_agents=%d headless=%s\n%s",
            _active_agents,
            self._headless,
            caller_stack,
        )

        self._playwright = await async_playwright().start()
        launch_kwargs: dict[str, Any] = {
            "headless": self._headless,
            "args": self._build_launch_args(),
        }
        if self._executable_path is not None:
            launch_kwargs["executable_path"] = str(self._executable_path)

        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        logger.info(
            "[goofish_catcher][browser_agent] Chromium launched — active_agents=%d pid=%s",
            _active_agents,
            getattr(getattr(self._browser, "process", None), "pid", "?"),
        )

        context_kwargs: dict[str, Any] = {
            "viewport": {"width": 1280, "height": 800},
        }
        if self._storage_state is not None:
            context_kwargs["storage_state"] = self._storage_state

        self._context = await self._browser.new_context(**context_kwargs)
        self._page = await self._context.new_page()

        # 拦截 JSON 响应，供 extract_items 动作使用（零额外延迟）
        captured = self._captured_payloads

        async def _on_response(response) -> None:
            ct = (response.headers.get("content-type") or "").lower()
            if "json" not in ct:
                return
            try:
                payload = await response.json()
                if isinstance(payload, (dict, list)):
                    captured.append(payload)
            except Exception:
                pass

        self._page.on("response", _on_response)
        return self

    async def __aexit__(self, *exc_info) -> None:
        global _active_agents
        for obj, name in [
            (self._page, "page"),
            (self._context, "context"),
            (self._browser, "browser"),
        ]:
            if obj is not None:
                try:
                    await obj.close()
                except Exception as e:
                    logger.debug(
                        "[goofish_catcher][browser_agent] %s close error: %s", name, e
                    )
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception as e:
                logger.debug(
                    "[goofish_catcher][browser_agent] playwright stop error: %s", e
                )
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
        _active_agents = max(0, _active_agents - 1)
        logger.info(
            "[goofish_catcher][browser_agent] Chromium closed — active_agents=%d",
            _active_agents,
        )

    # ── 公开 API ──────────────────────────────────────────────────────────────

    async def run(self, task: str) -> str:
        """执行任务，返回结果摘要字符串。"""
        if self._page is None:
            raise RuntimeError("agent has not been started (use async with)")

        logger.info("[goofish_catcher][browser_agent] task=%r", task)

        # 先导航到首页，确保处于已知起点
        try:
            await self._page.goto(
                _GOOFISH_BASE,
                wait_until="domcontentloaded",
                timeout=15_000,
            )
        except Exception as exc:
            logger.warning(
                "[goofish_catcher][browser_agent] initial navigation failed: %s", exc
            )

        history: list[str] = []

        for step in range(1, self._max_steps + 1):
            # ① 快照 AX Tree
            ax_text = await self._get_ax_text()
            current_url = str(getattr(self._page, "url", "") or _GOOFISH_BASE)

            # ② 构建 prompt 并调用 LLM
            user_prompt = _STEP_PROMPT_TEMPLATE.format(
                task=task,
                step=step,
                max_steps=self._max_steps,
                current_url=current_url,
                history=_format_history(history),
                ax_tree_text=ax_text,
            )

            try:
                raw_response = await asyncio.wait_for(
                    self._llm_call(user_prompt, _SYSTEM_PROMPT),
                    timeout=self._step_timeout_sec,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "[goofish_catcher][browser_agent] LLM timeout at step %d", step
                )
                history.append(f"第{step}步: (LLM 超时，跳过)")
                continue
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher][browser_agent] LLM error at step %d: %s",
                    step,
                    exc,
                )
                history.append(f"第{step}步: (LLM 错误: {exc})")
                continue

            # ③ 解析动作
            action_dict = _extract_json_object(raw_response or "")
            action = str(action_dict.get("action", "")).strip().lower()

            logger.info(
                "[goofish_catcher][browser_agent] step=%d action=%s",
                step,
                action_dict,
            )

            # ④ 执行动作
            if action == "done":
                result = str(action_dict.get("result", "任务已完成"))
                logger.info(
                    "[goofish_catcher][browser_agent] done after %d steps: %r",
                    step,
                    result[:120],
                )
                return result

            if action == "fail":
                reason = str(action_dict.get("reason", "未知原因"))
                logger.warning(
                    "[goofish_catcher][browser_agent] fail at step %d: %s",
                    step,
                    reason,
                )
                return f"任务失败：{reason}"

            step_result = await self._execute_action(action_dict, ax_text)
            history.append(f"第{step}步: {_summarize_action(action_dict)} → {step_result}")
            # 裁剪历史，只保留最近 N 步
            if len(history) > _MAX_HISTORY:
                history = history[-_MAX_HISTORY:]

        return f"任务未在 {self._max_steps} 步内完成，请尝试更具体的描述。"

    # ── 动作执行 ──────────────────────────────────────────────────────────────

    async def _execute_action(
        self,
        action_dict: dict[str, Any],
        ax_text: str,
    ) -> str:
        """执行单个动作，返回结果描述字符串。"""
        action = str(action_dict.get("action", "")).strip().lower()

        if action == "navigate":
            return await self._do_navigate(str(action_dict.get("url", "")))

        if action == "click":
            return await self._do_click(
                target=str(action_dict.get("target", "")),
                role=str(action_dict.get("role", "")).strip() or None,
            )

        if action == "type":
            return await self._do_type(
                target=str(action_dict.get("target", "")),
                text=str(action_dict.get("text", "")),
            )

        if action == "scroll":
            direction = str(action_dict.get("direction", "down")).strip().lower()
            return await self._do_scroll(direction)

        if action == "wait":
            try:
                seconds = float(action_dict.get("seconds", 1.0))
            except (TypeError, ValueError):
                seconds = 1.0
            seconds = max(0.5, min(5.0, seconds))
            await asyncio.sleep(seconds)
            return f"等待 {seconds:.1f}s ✓"

        if action == "extract":
            return await self._do_extract(
                description=str(action_dict.get("description", "")),
                ax_text=ax_text,
            )

        if action == "extract_items":
            return await self._do_extract_items()

        return f"未知动作 {action!r}，跳过"

    async def _do_navigate(self, url: str) -> str:
        url = url.strip()
        if not url:
            return "URL 为空，跳过"
        # 域名安全检查
        parsed = urlparse(url)
        if parsed.netloc and _ALLOWED_DOMAIN not in parsed.netloc:
            return f"导航被阻止（仅允许 {_ALLOWED_DOMAIN}）"
        # 补全协议
        if not url.startswith("http"):
            url = "https://" + url.lstrip("/")
        try:
            await self._page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15_000,
            )
            return f"已导航到 {url} ✓"
        except Exception as exc:
            return f"导航失败: {exc}"

    async def _do_click(self, target: str, role: str | None) -> str:
        if not target:
            return "click target 为空，跳过"
        try:
            # 策略一：按 role + name 定位
            if role:
                locator = self._page.get_by_role(role, name=target).first
                if await locator.count() > 0:
                    await locator.click(timeout=5_000)
                    return f"点击 [{role}] {target!r} ✓"

            # 策略二：按可见文本定位
            locator = self._page.get_by_text(target, exact=False).first
            if await locator.count() > 0:
                await locator.click(timeout=5_000)
                return f"点击 {target!r}（文本匹配）✓"

            # 策略三：aria-label 模糊匹配
            locator = self._page.locator(f'[aria-label*="{target}"]').first
            if await locator.count() > 0:
                await locator.click(timeout=5_000)
                return f"点击 {target!r}（aria-label 匹配）✓"

            return f"未找到元素 {target!r}，请在下一步用更精确的描述重试"
        except Exception as exc:
            return f"点击失败: {exc}"

    async def _do_type(self, target: str, text: str) -> str:
        if not target:
            return "type target 为空，跳过"
        try:
            # 优先按 placeholder / label / role 定位输入框
            locator = self._page.get_by_role("textbox", name=target).first
            if await locator.count() == 0:
                locator = self._page.get_by_placeholder(target).first
            if await locator.count() == 0:
                locator = self._page.get_by_label(target).first
            if await locator.count() == 0:
                return f"未找到输入框 {target!r}"
            await locator.clear()
            await locator.fill(text)
            return f"在 {target!r} 中输入了 {text!r} ✓"
        except Exception as exc:
            return f"输入失败: {exc}"

    async def _do_scroll(self, direction: str) -> str:
        try:
            if direction == "up":
                await self._page.evaluate("window.scrollBy(0, -600)")
            else:
                await self._page.evaluate("window.scrollBy(0, 600)")
            await asyncio.sleep(0.4)
            return f"向{('上' if direction == 'up' else '下')}滚动 ✓"
        except Exception as exc:
            return f"滚动失败: {exc}"

    async def _do_extract_items(self) -> str:
        """用既有的快速抓取逻辑提取当前页面的商品列表。

        优先从拦截到的 JSON 响应中提取（与 PlaywrightSearchProvider 相同的逻辑），
        降级到 DOM 提取。不需要 LLM，速度与纯脚本模式相当。
        提取完成后清空 payload 缓存，避免翻页后数据串台。
        """
        import json as _json
        from .provider_playwright import (
            _normalize_url,
            _extract_item_id_from_url,
            _parse_price,
            _pick_first_text,
            _extract_price,
        )

        items: list[dict[str, Any]] = []
        seen: set[str] = set()

        # ── Tier 1: JSON payload（零额外延迟，与 PlaywrightSearchProvider 同路径）──
        def _try_normalize(data: dict) -> dict[str, Any] | None:
            title = _pick_first_text(
                data, ("title", "item_title", "name", "itemName", "subject")
            )
            if not title:
                return None
            url = _normalize_url(
                _pick_first_text(data, ("url", "item_url", "detail_url", "jumpUrl")),
                _GOOFISH_BASE,
            )
            item_id = _pick_first_text(
                data, ("item_id", "itemId", "id", "auctionId", "targetId", "itemid")
            )
            if not item_id and url:
                item_id = _extract_item_id_from_url(url)
            if not item_id:
                return None
            price = _extract_price(data)
            if price is None:
                return None
            if not url:
                url = f"{_GOOFISH_BASE}/item?id={item_id}"
            return {"item_id": item_id, "title": title, "price": price, "url": url}

        stack: list[Any] = list(self._captured_payloads)
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                candidate = _try_normalize(node)
                if candidate and candidate["item_id"] not in seen:
                    seen.add(candidate["item_id"])
                    items.append(candidate)
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(node, list):
                for child in node:
                    if isinstance(child, (dict, list)):
                        stack.append(child)

        # ── Tier 2: DOM fallback ──────────────────────────────────────────────
        if not items:
            try:
                cards = await self._page.eval_on_selector_all(
                    "a[href*='item']",
                    """(nodes) => nodes.slice(0, 80).map(n => ({
                        href: n.href || n.getAttribute('href') || '',
                        text: (n.innerText || '').trim(),
                        title: ((n.innerText || '').trim().split('\\n')[0] || '').trim(),
                    }))""",
                )
                for card in cards:
                    url = _normalize_url(card.get("href"), _GOOFISH_BASE)
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
                        {"item_id": item_id, "title": title, "price": price, "url": url}
                    )
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher][browser_agent] extract_items DOM error: %s", exc
                )

        self._captured_payloads.clear()

        if not items:
            return (
                "当前页面未提取到商品。"
                "可能原因：页面尚未完全加载（先 scroll 再试）、触发了登录墙或验证码。"
            )

        logger.info(
            "[goofish_catcher][browser_agent] extract_items: %d items from %s",
            len(items),
            self._page.url,
        )
        return _json.dumps(items[:60], ensure_ascii=False)

    async def _do_extract(self, description: str, ax_text: str) -> str:
        """对当前页面内容做二次 LLM 提取，不导航。"""
        if not description:
            return "extract description 为空，跳过"
        prompt = _EXTRACT_PROMPT_TEMPLATE.format(
            ax_tree_text=ax_text,
            description=description,
        )
        try:
            result = await asyncio.wait_for(
                self._llm_call(prompt, _EXTRACT_SYSTEM),
                timeout=self._step_timeout_sec,
            )
            short = (result or "（空）")[:400]
            return f"提取结果: {short}"
        except asyncio.TimeoutError:
            return "提取超时"
        except Exception as exc:
            return f"提取失败: {exc}"

    # ── 辅助 ──────────────────────────────────────────────────────────────────

    async def _get_ax_text(self) -> str:
        """Get the page's accessibility tree as text.

        Playwright ≥ 1.41 removed page.accessibility and replaced it with
        Locator.aria_snapshot() which returns a YAML-like string directly
        usable by the LLM.
        """
        try:
            text = await self._page.locator("body").aria_snapshot(timeout=5_000)
            if text:
                return text[:_AX_MAX_CHARS]
        except Exception as exc:
            logger.debug(
                "[goofish_catcher][browser_agent] aria_snapshot error: %s", exc
            )
        # Fallback for old Playwright (<1.41): page.accessibility.snapshot() → dict
        try:
            from .provider_agent import ax_tree_to_text
            snapshot = await self._page.accessibility.snapshot()  # type: ignore[attr-defined]
            if snapshot:
                return ax_tree_to_text(snapshot, max_nodes=800)
        except Exception as exc:
            logger.debug(
                "[goofish_catcher][browser_agent] accessibility.snapshot error: %s", exc
            )
        return "(无法获取页面结构)"

    def _build_launch_args(self) -> list[str]:
        args = ["--disable-blink-features=AutomationControlled"]
        if self._force_direct:
            args.extend(
                [
                    "--no-proxy-server",
                    "--proxy-server=direct://",
                    "--proxy-bypass-list=*",
                ]
            )
        return args


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _format_history(history: list[str]) -> str:
    if not history:
        return "（暂无历史操作）"
    return "\n".join(history)


def _summarize_action(action_dict: dict[str, Any]) -> str:
    action = str(action_dict.get("action", "?"))
    if action == "navigate":
        return f"navigate {action_dict.get('url', '')}"
    if action == "click":
        role = action_dict.get("role", "")
        target = action_dict.get("target", "")
        return f"click {f'[{role}] ' if role else ''}{target!r}"
    if action == "type":
        return f"type {action_dict.get('target', '')!r} = {str(action_dict.get('text', ''))[:30]!r}"
    if action == "scroll":
        return f"scroll {action_dict.get('direction', '')}"
    if action == "wait":
        return f"wait {action_dict.get('seconds', '?')}s"
    if action == "extract":
        return f"extract {str(action_dict.get('description', ''))[:40]!r}"
    return action
