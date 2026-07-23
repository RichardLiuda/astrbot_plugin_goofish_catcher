"""闲鱼（Goofish）站点档案：平台特数据与钩子实现。

阶段 0.3a 行为保持型重构：钩子函数实现逐字搬自 app/provider_playwright.py，
登录态相关常量（login_url / embedded_login_markers / login_status_api_markers）
统一收口于此，app/login_session.py 经本档案取数。
"""

from __future__ import annotations

import logging
from urllib.parse import quote, urlparse

from ..types import DEFAULT_PLATFORM
from .base import SiteProfile

logger = logging.getLogger("astrbot_plugin_goofish_catcher")

_BASE_URL = "https://www.goofish.com"
# 登录会话落地页（原 app/login_session.py 的 DEFAULT_LOGIN_URL）。
_LOGIN_URL = "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC"

# 页面 HTML 内嵌登录框标记。
_EMBEDDED_LOGIN_MARKERS = (
    "passport.goofish.com/mini_login.htm",
    "alibaba-login-box",
)
# 登录态校验必须成功的 mtop 接口。
_LOGIN_STATUS_API_MARKERS = (
    "mtop.taobao.idlemessage.pc.loginuser.get",
    "mtop.idle.web.user.page.nav",
)
# 响应日志白名单。
_LOG_RESPONSE_URL_MARKERS = (
    "mtop.taobao.idle.pc.detail",
    "mtop.taobao.idlemessage.pc.loginuser.get",
    "mtop.taobao.idle.collect.item",
    "com.taobao.idle.unfavor.item",
    "passport.goofish.com/mini_login.htm",
    "mtop.idle.web.user.page.nav",
)


def _build_search_url(
    keyword: str,
    price_lower: float | None,
    price_upper: float | None,
) -> str:
    url = f"{_BASE_URL}/search?q={quote(keyword)}"
    if price_lower is not None and price_lower > 0:
        url += f"&priceLower={int(price_lower)}"
    if price_upper is not None and price_upper > 0:
        url += f"&priceUpper={int(price_upper)}"
    return url


def _is_auth_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    if "passport.goofish.com" in host and (
        "mini_login.htm" in path or path == "/login" or path.startswith("/login/")
    ):
        return True
    if "goofish.com" in host and "mini_login.htm" in path:
        return True
    if "goofish.com" in host and "member/login" in path:
        return True
    return False


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
    if text.endswith("_闲鱼"):
        text = text[: -len("_闲鱼")].strip()
    if text.endswith(" - 闲不住？上闲鱼！"):
        text = ""
    return text


GOOFISH_PROFILE = SiteProfile(
    platform=DEFAULT_PLATFORM,
    display_name="闲鱼",
    base_url=_BASE_URL,
    login_url=_LOGIN_URL,
    embedded_login_markers=_EMBEDDED_LOGIN_MARKERS,
    login_status_api_markers=_LOGIN_STATUS_API_MARKERS,
    favorite_button_selector="div[class*='buttons--'] div[class*='right--']",
    favorite_hint_text="收藏",
    favorited_hint_text="已收藏",
    detail_api_marker="mtop.taobao.idle.pc.detail",
    log_response_url_markers=_LOG_RESPONSE_URL_MARKERS,
    dom_card_link_selector="a[href*='item']",
    pagination_box_selector="div[class*='search-pagination-page-box']",
    pagination_active_selector="div[class*='search-pagination-page-box-active']",
    pagination_input_selector="input[class*='search-pagination-to-page-input']",
    pagination_confirm_selector="button[class*='search-pagination-to-page-confirm-button']",
    filter_label_new_publish="新发布",
    filter_label_personal_only="个人闲置",
    filter_label_free_shipping="包邮",
    filter_label_region="区域",
    build_search_url=_build_search_url,
    is_auth_url=_is_auth_url,
    is_captcha_url=_is_captcha_url,
    normalize_item_page_title=_normalize_item_page_title,
    supports_item_detail=True,
    quick_login_enabled=True,
)
