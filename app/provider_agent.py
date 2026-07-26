"""
Agent-style fallback helpers for PlaywrightSearchProvider.

When CSS selectors break after a Goofish frontend update, these functions
take over: they read the page's Accessibility Tree, pass a compact text
representation to the AstrBot LLM, and parse the structured response back
into NormalizedItem / bool results.

No extra dependencies — uses only Playwright's built-in accessibility
snapshot and the existing AstrBot LLM context (same as GoofishRecommender).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

from .platforms.base import SiteProfile
from .platforms.registry import (
    PLATFORM_GOOFISH,
    build_item_url,
    make_item_id,
    platform_display_name,
)
from .types import NormalizedItem

_PRICE_RE = re.compile(r"(\d+(?:\.\d+)?)")
_BASE_URL = "https://www.goofish.com"

# ── AX Tree serialisation ────────────────────────────────────────────────────

# Roles that carry no semantic value on their own; collapse them unless they
# have a name/value so the text fed to the LLM stays compact.
_SKIP_ROLES = frozenset(
    {"generic", "none", "presentation", "group", "region", "section"}
)

# Roles worth preserving even without a name (they signal structure).
_STRUCTURAL_ROLES = frozenset(
    {"link", "button", "listitem", "img", "heading", "textbox"}
)


async def _get_ax_text(page) -> str:
    """获取页面的 AX 文本快照，兼容新旧 Playwright API。

    - Playwright ≥ 1.35（含 1.58）：page.accessibility 已移除，
      改用 page.locator("body").aria_snapshot() 返回 YAML 格式文本。
    - 旧版本：fallback 到 page.accessibility.snapshot() + ax_tree_to_text()。
    """
    # 优先用新 API
    try:
        body = page.locator("body")
        text = await body.aria_snapshot()
        if text:
            return text
    except Exception:
        pass
    # 旧版本 fallback
    try:
        snapshot: dict | None = await page.accessibility.snapshot()
        if snapshot:
            return ax_tree_to_text(snapshot)
    except Exception:
        pass
    return ""


def ax_tree_to_text(
    node: dict[str, Any] | None,
    *,
    depth: int = 0,
    max_depth: int = 10,
    max_nodes: int = 600,
    _counter: list[int] | None = None,
) -> str:
    """
    Recursively serialise a Playwright accessibility snapshot dict into a
    compact indented text suitable for LLM consumption.

    Playwright snapshot format:
        {"role": "button", "name": "收藏", "children": [...]}
    """
    if node is None:
        return ""
    if _counter is None:
        _counter = [0]
    if depth > max_depth or _counter[0] >= max_nodes:
        return ""
    _counter[0] += 1

    role: str = node.get("role", "")
    name: str = (node.get("name") or "").strip()
    value: str = (node.get("value") or "").strip()
    url: str = (node.get("url") or "").strip()         # links expose url

    children: list[dict] = node.get("children") or []

    # Collapse pure containers with no interesting info
    if role in _SKIP_ROLES and not name and not value and not url:
        parts = []
        for child in children:
            t = ax_tree_to_text(
                child,
                depth=depth,
                max_depth=max_depth,
                max_nodes=max_nodes,
                _counter=_counter,
            )
            if t:
                parts.append(t)
        return "\n".join(parts)

    indent = "  " * depth
    parts: list[str] = []

    # Build the line for this node
    if role or name:
        line = f"{indent}[{role}]"
        if name:
            line += f' "{name}"'
        if value and value != name:
            line += f' val="{value}"'
        if url:
            line += f" href={url}"
        parts.append(line)

    for child in children:
        t = ax_tree_to_text(
            child,
            depth=depth + 1,
            max_depth=max_depth,
            max_nodes=max_nodes,
            _counter=_counter,
        )
        if t:
            parts.append(t)

    return "\n".join(parts)


# ── JSON parsing helpers ─────────────────────────────────────────────────────

def _extract_json_array(text: str) -> list[Any]:
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    # strip markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}


# ── NormalizedItem construction ───────────────────────────────────────────────

def _parse_price(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    m = _PRICE_RE.search(str(value or ""))
    if not m:
        return None
    return float(m.group(1))


def _resolve_url(raw: str, base_url: str = _BASE_URL) -> str:
    raw = str(raw or "").strip()
    if raw.startswith("//"):
        return "https:" + raw
    if raw.startswith("/"):
        return base_url + raw
    return raw


def _item_id_from_url(url: str) -> str:
    from urllib.parse import parse_qs, urlparse
    q = parse_qs(urlparse(url).query)
    for key in ("id", "itemId", "item_id"):
        vals = q.get(key)
        if vals:
            return str(vals[0]).strip()
    m = re.search(r"item(?:_id)?[=/](\d+)", url)
    if m:
        return m.group(1)
    return ""


def normalize_llm_items(
    raw_list: list[Any],
    *,
    profile: SiteProfile | None = None,
) -> list[NormalizedItem]:
    """Convert a list of LLM-extracted dicts into NormalizedItem objects.

    ``profile`` 提供平台上下文：item_id 经 make_item_id 前缀化（goofish 保持
    裸 ID）、URL 兜底走 build_item_url、platform 字段随平台落库，避免非闲鱼
    平台的兜底产物以裸 ID + 闲鱼 URL 污染 ID 命名空间。缺省为闲鱼语义。
    """
    platform = profile.platform if profile is not None else PLATFORM_GOOFISH
    base_url = profile.base_url if profile is not None else _BASE_URL
    results: list[NormalizedItem] = []
    seen: set[str] = set()
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        price = _parse_price(item.get("price"))
        if price is None:
            continue
        url = _resolve_url(item.get("url") or "", base_url)
        raw_id = str(item.get("item_id") or "").strip()
        if not raw_id and url:
            raw_id = _item_id_from_url(url)
        if not raw_id:
            continue
        item_id = make_item_id(platform, raw_id)
        if item_id in seen:
            continue
        seen.add(item_id)
        if not url:
            url = build_item_url(item_id)
        results.append(
            NormalizedItem(
                item_id=item_id,
                title=title,
                price=price,
                url=url,
                publish_time=None,
                raw=item,
                platform=platform,
            )
        )
    return results


# ── Prompts ───────────────────────────────────────────────────────────────────

_SEARCH_EXTRACT_SYSTEM = (
    "你是一个网页数据提取助手，只输出 JSON，不要任何解释文字。"
)

_SEARCH_EXTRACT_PROMPT = """\
以下是{display_name}搜索页面的无障碍树（Accessibility Tree）。
搜索关键词：{keyword}

请提取页面中所有商品卡片，每个商品包含：
- title: 商品标题（字符串）
- price: 价格（纯数字，单位元）
- url: 商品链接（完整 URL 或 /item?id=... 格式）
- item_id: 商品 ID（url 里的 id 参数，若能找到）

输出格式：只输出一个 JSON 数组，例如：
[{{"title":"iPhone 15","price":4200,"url":"{base_url}/item?id=123","item_id":"123"}}]

页面无障碍树：
{ax_text}
"""

_LOGIN_CHECK_SYSTEM = (
    "你是一个网页状态分析助手，只输出 JSON，不要任何解释文字。"
)

_LOGIN_CHECK_PROMPT = """\
以下是闲鱼页面的无障碍树。

判断当前页面是否已登录：
- 已登录：右上角有用户昵称、"我的闲鱼"、个人头像入口等
- 未登录：出现"登录"/"登录/注册"按钮、或弹出了登录框

只输出 JSON：{{"logged_in": true}} 或 {{"logged_in": false}}

页面无障碍树：
{ax_text}
"""

_FAVORITE_BUTTON_SYSTEM = (
    "你是一个网页元素定位助手，只输出 JSON，不要任何解释文字。"
)

_FAVORITE_BUTTON_PROMPT = """\
以下是闲鱼商品详情页的无障碍树。

请找到收藏按钮并返回：
- status: "favorited"（已收藏）/ "not_favorited"（未收藏）/ "unknown"（找不到）
- button_name: 按钮的 name 字段值

只输出 JSON：{{"status":"not_favorited","button_name":"收藏"}}

页面无障碍树：
{ax_text}
"""


# ── Public API ────────────────────────────────────────────────────────────────

async def extract_items_via_llm(
    page,
    *,
    keyword: str,
    llm_call,          # async callable(prompt, system_prompt) -> str
    timeout_sec: int = 20,
    profile: SiteProfile | None = None,
) -> list[NormalizedItem]:
    """
    Snapshot the page's AX tree, ask the LLM to extract product items,
    and return a list of NormalizedItem.

    ``profile`` 提供平台上下文（提示词措辞 / ID 前缀 / URL 兜底），
    缺省为闲鱼语义。

    ``llm_call`` signature::

        async def llm_call(prompt: str, system_prompt: str) -> str: ...
    """
    import asyncio

    try:
        ax_text = await _get_ax_text(page)
    except Exception as exc:
        logger.warning("[goofish_catcher][agent] ax snapshot failed: %s", exc)
        return []

    if not ax_text.strip():
        logger.info("[goofish_catcher][agent] ax snapshot empty")
        return []

    display_name = (
        profile.display_name
        if profile is not None
        else platform_display_name(PLATFORM_GOOFISH)
    )
    base_url = profile.base_url if profile is not None else _BASE_URL
    prompt = _SEARCH_EXTRACT_PROMPT.format(
        keyword=keyword,
        ax_text=ax_text,
        display_name=display_name,
        base_url=base_url,
    )
    logger.info(
        "[goofish_catcher][agent] extract_items_via_llm: ax_nodes=%d ax_chars=%d",
        ax_text.count("\n") + 1,
        len(ax_text),
    )

    try:
        response: str = await asyncio.wait_for(
            llm_call(prompt, _SEARCH_EXTRACT_SYSTEM),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        logger.warning("[goofish_catcher][agent] extract LLM timeout (%ss)", timeout_sec)
        return []
    except Exception as exc:
        logger.warning("[goofish_catcher][agent] extract LLM error: %s", exc)
        return []

    raw_list = _extract_json_array(response)
    items = normalize_llm_items(raw_list, profile=profile)
    logger.info(
        "[goofish_catcher][agent] extract_items_via_llm: raw=%d normalized=%d",
        len(raw_list),
        len(items),
    )
    return items


async def check_login_via_llm(
    page,
    *,
    llm_call,
    timeout_sec: int = 10,
) -> bool | None:
    """
    Return True if logged in, False if not, None if the LLM call failed.
    """
    import asyncio

    ax_text = await _get_ax_text(page)
    if not ax_text.strip():
        logger.warning("[goofish_catcher][agent] login ax snapshot empty")
        return None
    prompt = _LOGIN_CHECK_PROMPT.format(ax_text=ax_text)

    try:
        response: str = await asyncio.wait_for(
            llm_call(prompt, _LOGIN_CHECK_SYSTEM),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        logger.warning("[goofish_catcher][agent] login check LLM timeout")
        return None
    except Exception as exc:
        logger.warning("[goofish_catcher][agent] login check LLM error: %s", exc)
        return None

    parsed = _extract_json_object(response)
    logged_in = parsed.get("logged_in")
    if not isinstance(logged_in, bool):
        return None
    logger.info("[goofish_catcher][agent] login check result: %s", logged_in)
    return logged_in


async def find_favorite_button_via_llm(
    page,
    *,
    llm_call,
    timeout_sec: int = 10,
) -> dict[str, Any] | None:
    """
    Return {"status": "favorited"|"not_favorited"|"unknown", "button_name": str}
    or None on failure.
    """
    import asyncio

    ax_text = await _get_ax_text(page)
    if not ax_text.strip():
        logger.warning("[goofish_catcher][agent] favorite ax snapshot empty")
        return None
    prompt = _FAVORITE_BUTTON_PROMPT.format(ax_text=ax_text)

    try:
        response: str = await asyncio.wait_for(
            llm_call(prompt, _FAVORITE_BUTTON_SYSTEM),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        logger.warning("[goofish_catcher][agent] favorite LLM timeout")
        return None
    except Exception as exc:
        logger.warning("[goofish_catcher][agent] favorite LLM error: %s", exc)
        return None

    parsed = _extract_json_object(response)
    status = parsed.get("status")
    if status not in ("favorited", "not_favorited", "unknown"):
        return None
    return {"status": status, "button_name": str(parsed.get("button_name") or "")}
