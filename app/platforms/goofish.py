"""闲鱼（Goofish）站点档案：平台特数据与钩子实现。

阶段 0.3a 行为保持型重构：钩子函数实现逐字搬自 app/provider_playwright.py，
登录态相关常量（login_url / embedded_login_markers / login_status_api_markers）
统一收口于此，app/login_session.py 经本档案取数。

阶段 0.3b 行为保持型重构：闲鱼详情页解析（_build_deep_analysis_result 及其
专用辅助函数）逐字搬自 app/provider_playwright.py，接成
GOOFISH_PROFILE.parse_detail_page；_payload_indicates_captcha 为搜索路径的
8 标记共享版（登录校验 app/login_session.py 用私有 3 标记窄口径，
避免 mtop 限流被误判 CAPTCHA）。
"""

from __future__ import annotations

import json
import logging
import re
import time
from html import unescape
from typing import Any
from urllib.parse import quote, urlparse

from ..types import DEFAULT_PLATFORM, DeepAnalysisResult, NormalizedItem
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


# ──────────────────────────────────────────────────────────────────────────
# 0.3b：闲鱼详情页解析，逐字搬自 app/provider_playwright.py。
# _pick_first_text / _payload_ret_summary 是与引擎同份的逐字副本（引擎搜索
# 路径与 app/browser_agent.py 仍用引擎版；档案不能反向 import 引擎，故各自持有）。
# ──────────────────────────────────────────────────────────────────────────


def _payload_ret_summary(payload: dict[str, Any]) -> str:
    ret = payload.get("ret")
    if isinstance(ret, list):
        return " | ".join(str(item) for item in ret[:3]) or "-"
    text = str(ret or "").strip()
    return text or "-"


def _payload_indicates_captcha(payload: dict[str, Any]) -> bool:
    ret = payload.get("ret")
    ret_text = " ".join(str(item) for item in ret) if isinstance(ret, list) else str(ret)
    lowered = ret_text.lower()
    return any(
        marker in lowered
        for marker in (
            "captcha",
            "验证码",
            "滑块",
            "fail_sys_user_validate",
            "rgv587_error",
            "被挤爆",
            "punish",
            "baxia",
        )
    )


def _pick_first_text(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        if key not in data:
            continue
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _build_deep_analysis_result(
    *,
    item: NormalizedItem,
    payloads: list[dict[str, Any] | list[Any]],
    page_title: str,
) -> DeepAnalysisResult:
    detail_payload = _find_item_detail_payload(payloads)
    detail_payload_found = detail_payload is not None
    if detail_payload is not None:
        item_do = detail_payload.get("itemDO")
        seller_do = detail_payload.get("sellerDO")
        if not isinstance(item_do, dict):
            item_do = _find_first_nested_dict(
                detail_payload, ("itemDO", "item", "itemInfo", "auction")
            )
        if not isinstance(seller_do, dict):
            seller_do = _find_first_nested_dict(
                detail_payload, ("sellerDO", "seller", "sellerInfo")
            )
    else:
        merged = _merge_detail_payloads(payloads)
        item_do = _find_first_nested_dict(merged, ("itemDO", "item", "itemInfo", "auction"))
        # Avoid generic ``user`` here: detail pages also load recommendation feeds
        # whose cardData.user is not the current item's seller.
        seller_do = _find_first_nested_dict(merged, ("sellerDO", "seller", "sellerInfo"))

    item_do = item_do if isinstance(item_do, dict) else None
    seller_do = seller_do if isinstance(seller_do, dict) else None
    detail_source: dict[str, Any] = {}
    if isinstance(item.raw, dict):
        detail_source.update(item.raw)
    if item_do:
        detail_source.update(item_do)
    if seller_do:
        detail_source["seller"] = seller_do

    title = _pick_first_text(item_do or {}, ("title", "itemTitle", "subject")) if item_do else None
    seller_name = _pick_first_text(
        seller_do or {},
        ("nick", "nickName", "sellerNick", "userNick", "nickname"),
    ) if seller_do else None
    seller_id = _pick_first_text(
        seller_do or {},
        ("sellerId", "userId", "id"),
    ) if seller_do else None
    seller_credit = _pick_first_text(
        seller_do or {},
        ("zhimaLevel", "zhimaLevelName", "levelName", "creditLevel", "creditText"),
    ) if seller_do else None
    if seller_do and not seller_credit:
        zhima_info = seller_do.get("zhimaLevelInfo")
        if isinstance(zhima_info, dict):
            seller_credit = _pick_first_text(zhima_info, ("levelName", "name", "text"))
    if seller_do:
        structured_seller_credit = _extract_structured_seller_credit(seller_do)
        if seller_credit and structured_seller_credit:
            seller_credit = _join_unique_credit_parts(
                seller_credit,
                structured_seller_credit,
            )
        elif structured_seller_credit:
            seller_credit = structured_seller_credit

    image_urls = _extract_image_urls(detail_source)
    want_count = _parse_optional_int(_pick_first_text(item_do or {}, ("wantCnt", "wantCount", "want_count"))) if item_do else None
    browse_count = _parse_optional_int(_pick_first_text(item_do or {}, ("browseCnt", "browseCount", "browse_count"))) if item_do else None

    credit_status, credit_reason = _classify_credit(
        seller_credit=seller_credit,
        seller_payload=seller_do or {},
        item_payload=item_do or {},
    )
    logger.info(
        "[goofish_catcher] detail parse item_id=%s payloads=%s detail_payload=%s item_do=%s item_do_item_id=%s seller_do=%s seller_keys=%s seller_name=%s seller_id=%s seller_credit=%s credit_status=%s credit_reason=%s want=%s browse=%s page_title=%r",
        item.item_id,
        len(payloads),
        detail_payload_found,
        bool(item_do),
        _pick_first_text(item_do or {}, ("itemId", "item_id", "id", "auctionId", "targetId")),
        bool(seller_do),
        list((seller_do or {}).keys())[:25],
        seller_name or "-",
        seller_id or "-",
        seller_credit or "-",
        credit_status,
        credit_reason,
        want_count,
        browse_count,
        page_title,
    )
    status = "rejected" if credit_status == "bad" else "passed"
    risk = "信用风险较高" if status == "rejected" else "未发现明确低信用风险"
    summary_parts = [
        f"信用：{seller_credit or credit_status}",
        credit_reason,
    ]
    if want_count is not None:
        summary_parts.append(f"想要 {want_count}")
    if browse_count is not None:
        summary_parts.append(f"浏览 {browse_count}")
    if seller_name:
        summary_parts.append(f"卖家 {seller_name}")

    return DeepAnalysisResult(
        item_id=item.item_id,
        analyzed_at=int(time.time()),
        status=status,
        credit_status=credit_status,
        credit_reason=credit_reason,
        summary="；".join(part for part in summary_parts if part),
        risk=risk,
        image_urls=image_urls,
        seller_name=seller_name,
        seller_id=seller_id,
        seller_credit=seller_credit,
        want_count=want_count,
        browse_count=browse_count,
        raw={
            "title": title or page_title or item.title,
            "payload_count": len(payloads),
            "item": _safe_jsonable(item_do or {}),
            "seller": _safe_jsonable(seller_do or {}),
        },
    )


def _merge_detail_payloads(payloads: list[dict[str, Any] | list[Any]]) -> dict[str, Any]:
    return {"payloads": payloads}


def _find_item_detail_payload(
    payloads: list[dict[str, Any] | list[Any]],
) -> dict[str, Any] | None:
    """Return the data object from the current item's detail API response.

    A detail page can load several unrelated JSON payloads after the item
    response, especially recommendation feeds.  Those feeds contain
    ``cardData.user`` objects for other sellers.  Deep analysis must bind seller
    info to the mtop.taobao.idle.pc.detail payload instead of globally taking
    the first nested seller/user-like object.
    """

    candidates: list[dict[str, Any]] = []
    saw_detail_api = False
    stack: list[Any] = list(payloads)
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            data = current.get("data")
            if isinstance(data, dict):
                api = str(current.get("api") or "").lower()
                has_detail_shape = isinstance(data.get("itemDO"), dict) or isinstance(
                    data.get("sellerDO"), dict
                )
                if api == "mtop.taobao.idle.pc.detail":
                    saw_detail_api = True
                    logger.info(
                        "[goofish_catcher] detail payload candidate api=%s ret=%s has_detail_shape=%s data_keys=%s",
                        current.get("api") or "-",
                        _payload_ret_summary(current),
                        has_detail_shape,
                        list(data.keys())[:30],
                    )
                if api == "mtop.taobao.idle.pc.detail" and has_detail_shape:
                    return data
                if isinstance(data.get("itemDO"), dict) and isinstance(data.get("sellerDO"), dict):
                    candidates.append(data)
            stack.extend(value for value in current.values() if isinstance(value, (dict, list)))
        elif isinstance(current, list):
            stack.extend(value for value in current if isinstance(value, (dict, list)))
    if candidates:
        logger.info(
            "[goofish_catcher] detail payload fallback using shaped candidate, count=%s",
            len(candidates),
        )
        return candidates[0]
    logger.info(
        "[goofish_catcher] detail payload not found payloads=%s saw_detail_api=%s",
        len(payloads),
        saw_detail_api,
    )
    return None


def _find_first_nested_dict(node: Any, keys: tuple[str, ...]) -> dict[str, Any] | None:
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key in keys:
                value = current.get(key)
                if isinstance(value, dict):
                    return value
            stack.extend(value for value in current.values() if isinstance(value, (dict, list)))
        elif isinstance(current, list):
            stack.extend(value for value in current if isinstance(value, (dict, list)))
    return None


def _extract_image_urls(node: Any, *, limit: int = 6) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add_url(value: Any) -> None:
        if len(urls) >= limit:
            return
        text = str(value or "").strip()
        if not text:
            return
        if text.startswith("//"):
            text = "https:" + text
        if not (text.startswith("http://") or text.startswith("https://")):
            return
        lowered = text.lower()
        if not any(marker in lowered for marker in (".jpg", ".jpeg", ".png", ".webp", "alicdn", "img")):
            return
        if text in seen:
            return
        seen.add(text)
        urls.append(text)

    def add_structured_image_list(value: Any) -> None:
        if len(urls) >= limit or not isinstance(value, list):
            return
        image_entries = [entry for entry in value if isinstance(entry, dict)]
        image_entries.sort(key=lambda entry: 0 if entry.get("major") is True else 1)
        for entry in image_entries:
            if len(urls) >= limit:
                return
            add_url(
                entry.get("url")
                or entry.get("image")
                or entry.get("imageUrl")
                or entry.get("picUrl")
                or entry.get("src")
            )

    def add_priority_images(current: Any) -> None:
        stack_for_priority = [current]
        while stack_for_priority and len(urls) < limit:
            node = stack_for_priority.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    lowered_key = str(key).lower()
                    if lowered_key in {"imageinfos", "image_infos", "images", "image_list"}:
                        add_structured_image_list(value)
                    if isinstance(value, (dict, list)):
                        stack_for_priority.append(value)
            elif isinstance(node, list):
                stack_for_priority.extend(
                    value for value in reversed(node) if isinstance(value, (dict, list))
                )

    add_priority_images(node)

    stack = [node]
    while stack and len(urls) < limit:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                lowered_key = str(key).lower()
                if lowered_key in {"url", "image", "imageurl", "picurl", "src"} or "image" in lowered_key or "pic" in lowered_key:
                    if isinstance(value, str):
                        add_url(value)
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(
                value
                for value in reversed(current)
                if isinstance(value, (dict, list, str))
            )
        elif isinstance(current, str):
            add_url(current)
    return urls


def _extract_structured_seller_credit(seller_payload: dict[str, Any]) -> str | None:
    parts: list[str] = []

    good_ratio = _pick_first_text(
        seller_payload,
        ("newGoodRatioRate", "goodRatioRate", "goodRate", "positiveRate", "goodRatio"),
    )
    if good_ratio:
        parts.append(f"好评率{good_ratio}")

    sold_count = _parse_optional_int(
        _pick_first_text(
            seller_payload,
            ("hasSoldNumInteger", "soldCnt", "soldCount", "sellCount"),
        )
    )
    if sold_count is not None:
        parts.append(f"卖出{sold_count}件")

    reg_days = _parse_optional_int(seller_payload.get("userRegDay"))
    if reg_days:
        if reg_days >= 365:
            parts.append(f"来闲鱼{max(1, reg_days // 365)}年")
        else:
            parts.append(f"来闲鱼{reg_days}天")

    level = _extract_seller_level(seller_payload)
    if level is not None:
        parts.append(f"闲鱼信用等级{level}")

    if seller_payload.get("zhimaAuth") is True:
        parts.append("已芝麻认证")

    identity_tags = seller_payload.get("identityTags")
    if isinstance(identity_tags, list):
        for tag in identity_tags:
            if not isinstance(tag, dict):
                continue
            text = _pick_first_text(tag, ("text", "title", "name"))
            if text and "认证" in text:
                parts.append(text)

    return "，".join(parts) if parts else None


def _join_unique_credit_parts(*values: str | None) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        for part in re.split(r"[，,；;]", value):
            normalized = part.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            parts.append(normalized)
    return "，".join(parts)


def _classify_credit(
    *,
    seller_credit: str | None,
    seller_payload: dict[str, Any],
    item_payload: dict[str, Any],
) -> tuple[str, str]:
    seller_text = " ".join(
        str(value)
        for value in (
            seller_credit,
            json.dumps(seller_payload, ensure_ascii=False)[:1200],
        )
        if value
    )
    item_text = json.dumps(item_payload, ensure_ascii=False)[:800].lower()
    lowered = seller_text.lower()
    bad_markers = (
        "信用较差",
        "信用差",
        "芝麻较差",
        "较差",
        "差评很多",
        "风险卖家",
        "严重违规",
        "骗子",
        "诈骗",
    )
    good_markers = (
        "信用极好",
        "信用优秀",
        "芝麻信用优秀",
        "优秀",
        "极好",
        "良好",
    )
    severe_item_markers = ("风险卖家", "严重违规", "骗子", "诈骗")
    if any(marker in lowered for marker in bad_markers) or any(
        marker in item_text for marker in severe_item_markers
    ):
        return "bad", "检测到明确低信用或严重负面风险标记"
    if any(marker in lowered for marker in good_markers):
        return "good", "卖家信用信息良好"

    seller_level = _extract_seller_level(seller_payload)
    good_ratio = _parse_percent(
        _pick_first_text(
            seller_payload,
            ("newGoodRatioRate", "goodRatioRate", "goodRate", "positiveRate", "goodRatio"),
        )
    )
    sold_count = _parse_optional_int(
        _pick_first_text(
            seller_payload,
            ("hasSoldNumInteger", "soldCnt", "soldCount", "sellCount"),
        )
    )
    remark_do = seller_payload.get("remarkDO")
    bad_remarks = None
    good_remarks = None
    if isinstance(remark_do, dict):
        bad_remarks = _parse_optional_int(remark_do.get("sellerBadRemarkCnt"))
        good_remarks = _parse_optional_int(remark_do.get("sellerGoodRemarkCnt"))

    if seller_level is not None and seller_level <= 2:
        return "bad", f"卖家闲鱼信用等级偏低：{seller_level}"
    if (
        good_ratio is not None
        and good_ratio < 90
        and (sold_count or 0) >= 10
    ):
        return "bad", f"卖家好评率偏低：{good_ratio:.0f}%"
    if (
        bad_remarks is not None
        and bad_remarks >= 3
        and bad_remarks > (good_remarks or 0)
    ):
        return "bad", "卖家负面评价数量偏高"

    if seller_level is not None and seller_level >= 4:
        return "good", f"卖家闲鱼信用等级较好：{seller_level}"
    if good_ratio is not None and good_ratio >= 95:
        return "good", f"卖家好评率较高：{good_ratio:.0f}%"
    if (
        good_ratio is not None
        and good_ratio >= 90
        and (sold_count or 0) >= 10
    ):
        return "good", f"卖家交易评价较稳定：好评率{good_ratio:.0f}%"

    if seller_credit:
        return "unknown", f"卖家信用信息：{seller_credit}"
    return "unknown", "未获取到明确卖家信用信息，按保守规则不过滤"


def _extract_seller_level(seller_payload: dict[str, Any]) -> int | None:
    level_tag = seller_payload.get("idleFishCreditTag")
    if isinstance(level_tag, dict):
        track_params = level_tag.get("trackParams")
        if isinstance(track_params, dict):
            level = _parse_optional_int(track_params.get("sellerLevel"))
            if level is not None:
                return level

    for tag in seller_payload.get("levelTags") or ():
        if not isinstance(tag, dict):
            continue
        track_params = tag.get("trackParams")
        if isinstance(track_params, dict):
            level = _parse_optional_int(track_params.get("sellerLevel"))
            if level is not None:
                return level
    return None


def _parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def _safe_jsonable(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except Exception:
        return str(value)


def _parse_goofish_detail_page(html, payloads, item) -> DeepAnalysisResult:
    # page_title 原由引擎传入 await page.title()（经 _normalize_item_page_title
    # 归一化）；搬家后改为从 html 提取 <title>，经同一归一化钩子处理，保持输出一致。
    # page.title() 返回的是已解码文本，正则截取到的是原始实体（&amp; 等），
    # 须 unescape 才与 master 输出一致。
    title = ""
    match = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.IGNORECASE | re.DOTALL)
    if match:
        title = unescape(match.group(1))
    return _build_deep_analysis_result(
        item=item,
        payloads=payloads,
        page_title=_normalize_item_page_title(title),
    )


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
    parse_detail_page=_parse_goofish_detail_page,
)
