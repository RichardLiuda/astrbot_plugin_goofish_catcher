"""淘宝站点档案：平台特数据与钩子实现（阶段 1.1）。

实证来源（2026-07-20/21 本地实验，见 .kimi/gotchas.md 与 local_data/sso_taobao.html）：
- 淘宝搜索是 SSR 页面，XHR 只有埋点/监控，商品数据在 DOM 里 → 提取主路径是 DOM 层，
  本档案提供 dom_card_extractor_js + parse_dom_card 两个定制钩子。
- 卡片结构：a[href*='item.htm'] 包裹整卡；标题在 div[class*='title--'] 的 title 属性
  （关键词高亮把标题拆成多个 span，取 title 属性最稳）；价格拆成
  span[class*='unit--']（¥）+ div[class*='priceInt--'] + div[class*='priceFloat--']；
  销量 span[class*='realSales--']；店铺 span[class*='shopNameText--']。
- 广告卡片的链接是 click.simba.taobao.com 跳转，选择器层已被 item.htm 排除，
  parse_dom_card 里再做一次 host 白名单兜底。
- 闲鱼登录不会给 .taobao.com 播种 cookie；访客可搜索但新指纹必弹滑块。
  淘宝登录链路（阶段 P0）：login_url 指向淘宝登录页，登录态校验接口为
  mtop.user.getUserSimple（见下方 login_status_api_markers 注释）。
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import quote, urlparse

from ..types import NormalizedItem
from .base import SiteProfile
from .registry import PLATFORM_TAOBAO, extract_item_id_from_url, make_item_id, normalize_url

logger = logging.getLogger("astrbot_plugin_goofish_catcher")

_BASE_URL = "https://www.taobao.com"
_SEARCH_BASE = "https://s.taobao.com/search"

# 只接受这两个 host 的商品详情链接；click.simba.taobao.com 等广告跳转一律过滤
_ITEM_HOST_RE = re.compile(r"(item\.taobao\.com|detail\.tmall\.com)/item\.htm")

# DOM 卡片提取 JS：按淘宝卡片结构取结构化字段（实证类名，阿里改版时需跟进）
_DOM_CARD_EXTRACTOR_JS = """
(nodes) => {
  const pick = (node, sel) => {
    const el = node.querySelector(sel);
    return el ? (el.innerText || '').trim() : '';
  };
  return nodes.slice(0, 80).map((node) => {
    const titleEl = node.querySelector("div[class*='title--']");
    const title = titleEl
      ? (titleEl.getAttribute('title') || titleEl.innerText || '').trim()
      : '';
    return {
      href: node.href || node.getAttribute('href') || '',
      title,
      priceInt: pick(node, "div[class*='priceInt--']"),
      priceFloat: pick(node, "div[class*='priceFloat--']"),
      priceDesc: pick(node, "span[class*='priceDesc--']"),
      salesText: pick(node, "span[class*='realSales--']"),
      shopName: pick(node, "span[class*='shopNameText--']"),
    };
  });
}
"""


def _build_search_url(
    keyword: str,
    price_lower: float | None,
    price_upper: float | None,
) -> str:
    # 价格区间 URL 参数名 pending（待实测验证）；当前由调用方内存过滤兜底。
    return f"{_SEARCH_BASE}?q={quote(keyword)}"


def _is_auth_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    host = urlparse(lowered).netloc
    return "login.taobao.com" in host or "passport.taobao.com" in host


def _is_captcha_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    return bool(
        ("cf.aliyun.com" in host and "nocaptcha" in path)
        or "captcha" in path
    )


def _normalize_item_page_title(title: str) -> str:
    text = str(title or "").strip()
    for suffix in ("- 淘宝网", "-淘宝网", "_淘宝网"):
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text


def _parse_price_from_card(card: dict[str, Any]) -> float | None:
    """价格 = priceInt + priceFloat（如 "10999" + ".00"）；任一缺失/不可解析返回 None。"""
    int_part = re.sub(r"[^\d]", "", str(card.get("priceInt") or ""))
    if not int_part:
        return None
    float_match = re.search(r"(\.\d+)", str(card.get("priceFloat") or ""))
    text = int_part + (float_match.group(1) if float_match else "")
    try:
        return float(text)
    except ValueError:
        return None


def _parse_dom_card(card: dict[str, Any], base_url: str) -> NormalizedItem | None:
    """淘宝 DOM 卡片 dict → NormalizedItem；广告/字段不全返回 None。"""
    url = normalize_url(card.get("href"), base_url)
    if not url or not _ITEM_HOST_RE.search(url):
        return None
    raw_id = extract_item_id_from_url(url)
    title = str(card.get("title") or "").strip()
    price = _parse_price_from_card(card)
    if not raw_id or not title or price is None:
        return None
    return NormalizedItem(
        item_id=make_item_id(PLATFORM_TAOBAO, raw_id),
        title=title,
        price=price,
        url=url,
        publish_time=None,
        platform=PLATFORM_TAOBAO,
        raw={
            "salesText": str(card.get("salesText") or ""),
            "shopName": str(card.get("shopName") or ""),
            "priceDesc": str(card.get("priceDesc") or ""),
        },
    )


TAOBAO_PROFILE = SiteProfile(
    platform=PLATFORM_TAOBAO,
    display_name="淘宝",
    base_url=_BASE_URL,
    login_url="https://login.taobao.com/member/login.jhtml",
    # 淘宝访客搜索合法，页面头部常驻阿里登录组件，"alibaba-login-box" 会误报；
    # 且该检查先于 captcha HTML 检查执行，会把滑块惩罚页误分类为 AUTH_REQUIRED。
    # 故留空：仅依赖 URL 级判定（login.taobao.com 重定向）。
    embedded_login_markers=(),
    # 登录态校验接口：来自 2026-07-22 AstrBot 实测日志，mtop.user.getUserSimple
    # 未登录返回 FAIL_SYS_SESSION_EXPIRED，登录后应返回 SUCCESS。
    # 注意 URL 里 api 名是驼峰（api=mtop.user.getUserSimple），login_session 的
    # _match_login_status_api 匹配前会对 URL 与标记统一 lower()，此处保持小写即可。
    login_status_api_markers=("mtop.user.getusersimple",),
    favorite_button_selector="div[class*='buttons--'] div[class*='right--']",  # pending：淘宝收藏 UI 未验证（阶段 1.3）
    favorite_hint_text="收藏",
    favorited_hint_text="已收藏",
    detail_api_marker="mtop.taobao.pcdetail.data.get",  # pending：阶段 1.3 实测
    log_response_url_markers=("mtop.taobao.pcdetail.data.get",),
    dom_card_link_selector="a[href*='item.htm']",
    # 分页选择器 pending：淘宝分页 UI 未实测，MVP 仅支持单页搜索
    pagination_box_selector="div[class*='search-pagination-page-box']",
    pagination_active_selector="div[class*='search-pagination-page-box-active']",
    pagination_input_selector="input[class*='search-pagination-to-page-input']",
    pagination_confirm_selector="button[class*='search-pagination-to-page-confirm-button']",
    # 过滤器 label pending：淘宝过滤器语义不同（无个人闲置/新发布），SearchFilters 平台裁剪后续做
    filter_label_new_publish="",
    filter_label_personal_only="",
    filter_label_free_shipping="包邮",
    filter_label_region="",
    build_search_url=_build_search_url,
    is_auth_url=_is_auth_url,
    is_captcha_url=_is_captcha_url,
    normalize_item_page_title=_normalize_item_page_title,
    dom_card_extractor_js=_DOM_CARD_EXTRACTOR_JS,
    parse_dom_card=_parse_dom_card,
    # 淘宝详情页解析未实测（阶段 1.3），深度分析短路为保守结果，不启动浏览器。
    supports_item_detail=False,
    # 淘宝访客态下 mini_login iframe 本就不存在，"iframe gone=成功"启发式会误判，
    # 一键登录捷径整体禁用（login_session.try_quick_login 与 provider 侧同修）。
    quick_login_enabled=False,
    # 登录落地页是纯登录页，validate_login 不能回那里（会把已登录用户拖回登录页，
    # 且 getusersimple 只在内容页触发）。探测页用搜索页——实测该页必发
    # mtop.user.getusersimple，未登录 SESSION_EXPIRED、登录后 SUCCESS。
    validate_probe_url="https://s.taobao.com/search?q=%E6%89%8B%E6%9C%BA",
)
