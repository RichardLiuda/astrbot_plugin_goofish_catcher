"""平台注册表：item_id 平台归属解析与商品 URL 构建（纯函数，无外部依赖）。

规则（阶段 0.2 确立）：
- 存储用 item_id 形如 ``{platform}:{raw_id}``；**无前缀一律视为 goofish**，
  以此兼容全部存量数据（items / price_history / notifications /
  item_deep_analysis 里的裸数字 ID）。
- goofish 的 item_id 维持裸数字不加前缀（``make_item_id`` 对 goofish 原样返回），
  新平台必须经 ``make_item_id`` 生成带前缀的 ID，避免与闲鱼数字 ID 空间撞号。
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from ..types import DEFAULT_PLATFORM

PLATFORM_GOOFISH = DEFAULT_PLATFORM
PLATFORM_TAOBAO = "taobao"

# 平台商品页 URL 模板，{raw_id} 为不带平台前缀的原始 ID。
_ITEM_URL_TEMPLATES: dict[str, str] = {
    PLATFORM_GOOFISH: "https://www.goofish.com/item?id={raw_id}",
    PLATFORM_TAOBAO: "https://item.taobao.com/item.htm?id={raw_id}",
}

_PLATFORM_DISPLAY_NAMES: dict[str, str] = {
    PLATFORM_GOOFISH: "闲鱼",
    PLATFORM_TAOBAO: "淘宝",
}

_KNOWN_PLATFORMS = frozenset(_ITEM_URL_TEMPLATES)


def split_item_id(item_id: str) -> tuple[str, str]:
    """把 item_id 拆成 (platform, raw_id)；无前缀或前缀未知时视为 goofish。"""
    text = (item_id or "").strip()
    prefix, sep, raw = text.partition(":")
    if sep and prefix in _KNOWN_PLATFORMS and raw:
        return prefix, raw
    return PLATFORM_GOOFISH, text


def make_item_id(platform: str, raw_id: str) -> str:
    """平台 + 原始 ID → 存储用 item_id。goofish 保持裸 ID 以兼容存量数据。"""
    raw = str(raw_id).strip()
    if not raw:
        raise ValueError("raw_id must not be empty")
    if platform == PLATFORM_GOOFISH:
        return raw
    if platform not in _KNOWN_PLATFORMS:
        raise ValueError(f"unknown platform: {platform}")
    return f"{platform}:{raw}"


def build_item_url(item_id: str, *, platform: str | None = None) -> str:
    """由 item_id 构建平台商品页 URL；可用 platform 显式覆盖 ID 内前缀。"""
    resolved_platform, raw_id = split_item_id(item_id)
    if platform:
        resolved_platform = platform
    template = _ITEM_URL_TEMPLATES.get(resolved_platform)
    if template is None:
        raise ValueError(f"unknown platform: {resolved_platform}")
    return template.format(raw_id=raw_id)


def platform_display_name(platform: str) -> str:
    """平台中文显示名（通知文案用）；未知平台原样返回标识。"""
    return _PLATFORM_DISPLAY_NAMES.get(platform, platform)


def normalize_url(url: object, base_url: str) -> str | None:
    """把相对/协议相对 URL 归一成绝对 URL；无法归一返回 None。

    与 provider_playwright 原 _normalize_url 逐字一致（0.3a 后下沉到此共享）。
    """
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


def extract_item_id_from_url(url: str) -> str | None:
    """从商品 URL 提取原始数字 ID（query 的 id/item_id/itemId/auctionId，
    或路径 item[=/]数字）。与 provider_playwright 原实现逐字一致。"""
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
