"""SiteProfile：平台站点档案。通用抓取引擎经此读取全部平台特数据。"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True, slots=True)
class SiteProfile:
    platform: str                    # 与 types.DEFAULT_PLATFORM 对齐
    display_name: str                # 中文显示名
    base_url: str                    # 如 https://www.goofish.com
    login_url: str                   # 登录会话落地页
    embedded_login_markers: tuple[str, ...]     # 页面 HTML 内嵌登录框标记
    login_status_api_markers: tuple[str, ...]   # 登录态校验必须成功的 mtop 接口
    favorite_button_selector: str
    favorite_hint_text: str          # "收藏"
    favorited_hint_text: str         # "已收藏"
    detail_api_marker: str           # 详情 payload 的 api 名
    log_response_url_markers: tuple[str, ...]   # 日志白名单
    dom_card_link_selector: str      # DOM 提取层的卡片链接选择器
    pagination_box_selector: str
    pagination_active_selector: str
    pagination_input_selector: str
    pagination_confirm_selector: str
    filter_label_new_publish: str
    filter_label_personal_only: str
    filter_label_free_shipping: str
    filter_label_region: str
    # 钩子函数（逻辑无法干净数据化的部分）
    build_search_url: Callable[[str, float | None, float | None], str]   # (keyword, price_lower, price_upper)
    is_auth_url: Callable[[str], bool]
    is_captcha_url: Callable[[str], bool]
    normalize_item_page_title: Callable[[str], str]
    # 可选：DOM 提取层定制（None = 引擎默认的 {href, text, title} 提取 + 首行标题/全文价解析）。
    # dom_card_extractor_js：eval_on_selector_all 的 JS 体，返回平台定制的卡片 dict 列表。
    # parse_dom_card：把卡片 dict 转成 NormalizedItem（含广告过滤、ID 前缀），失败返回 None。
    dom_card_extractor_js: str | None = None
    parse_dom_card: Callable[[dict, str], "NormalizedItem | None"] | None = None
    # 是否支持商品详情页深度分析；False 时 analyze_item_detail 直接短路返回保守结果。
    supports_item_detail: bool = True
    # 是否允许「快速进入/一键登录」捷径（login_session.try_quick_login 与
    # provider._try_quick_login）；淘宝访客态下 iframe-gone 启发式会误判成功，置 False。
    quick_login_enabled: bool = True
    # 登录态校验探测页（None = 用 login_url）。登录落地页是纯登录页的平台必须设置：
    # validate_login 会 goto 该页检查登录态接口——若指回登录页，会把已登录用户拖回登录页。
    validate_probe_url: str | None = None
    # payload 里的登录失效标记（FAIL_SYS_SESSION_EXPIRED 等）是否判 AUTH_REQUIRED。
    # 访客可用平台（淘宝）应关闭：次要接口的 SESSION_EXPIRED 不代表搜索被墙，
    # 只认 login.* 重定向才是真登录墙。
    auth_on_payload_markers: bool = True
