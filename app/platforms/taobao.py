"""淘宝站点档案：平台特数据与钩子实现（阶段 1.1 起；1.3 接入详情页解析）。

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

详情页（阶段 1.3，实证 local_data/probe_*_item_htm_*.html，天猫店/C 店各一份）：
- 详情页同为 SSR，payload 只有埋点，商品数据嵌在 HTML 的
  window.__ICE_APP_CONTEXT__（var b = {BIG_JSON}）里 → parse_detail_page 钩子解析。
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any
from urllib.parse import quote, urlparse

from ..types import DeepAnalysisResult, NormalizedItem
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


# ---------------------------------------------------------------------------
# 详情页解析（阶段 1.3）
#
# 实证（2026-07-24，local_data/probe_*_item_htm_*.html，天猫店 + 淘宝 C 店各一份）：
# 淘宝详情页是 SSR 页面，XHR 只有埋点/监控，无详情 mtop 接口；商品数据嵌在 HTML 的
# `window.__ICE_APP_CONTEXT__ || {};var b = {BIG_JSON}` 里，路径
# loaderData.home.data.res → seller / item / skuBase / skuCore。
# ---------------------------------------------------------------------------

# 内嵌 JSON 定位标记：主路径用 "var b = "，兜底用紧凑形态（无空格）的 loaderData 键
_VAR_B_MARKER = "var b = "
_LOADER_DATA_MARKER = '"loaderData":{"home"'

_PARSE_FAIL_REASON = "详情页结构解析失败，仅基础信息"

# DSR 三项（宝贝描述/卖家服务/物流服务）的 type / title 标记
_DSR_TYPES = ("desc", "serv", "post")
_DSR_TITLES = ("宝贝描述", "卖家服务", "物流服务")


def _extract_balanced_json(text: str, start: int) -> str | None:
    """从 text[start]（必须为 "{"）起大括号配平提取 JSON 子串；配平失败返回 None。

    扫描跳过双引号字符串字面量（含转义），避免字符串里的花括号干扰计数。
    """
    if start < 0 or start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_string = False
    escaped = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _navigate_loader_res(data: Any) -> dict[str, Any] | None:
    """JSON 对象 → loaderData.home.data.res；路径缺失或 res 非 dict 返回 None。"""
    try:
        res = data["loaderData"]["home"]["data"]["res"]
    except (KeyError, TypeError):
        return None
    return res if isinstance(res, dict) else None


def _extract_loader_res(html: str) -> dict[str, Any] | None:
    """从详情页 HTML 提取 loaderData.home.data.res；任一失败返回 None。

    兜底顺序：先试 `var b = {`（SSR 标准形态），落空再直接定位
    `"loaderData":{"home"` 并反向配平找到其外层 `{` 后正向提取。
    """
    text = str(html or "")
    # 主路径：window.__ICE_APP_CONTEXT__ || {};var b = {BIG_JSON}
    idx = text.find(_VAR_B_MARKER)
    if idx >= 0:
        start = text.find("{", idx + len(_VAR_B_MARKER))
        blob = _extract_balanced_json(text, start)
        if blob:
            try:
                res = _navigate_loader_res(json.loads(blob))
            except (ValueError, TypeError):
                res = None
            if res is not None:
                return res
    # 兜底：定位紧凑形态的 loaderData 键，反向找到包含它的外层 `{`
    idx = text.find(_LOADER_DATA_MARKER)
    if idx < 0:
        return None
    depth = 0
    start = -1
    for pos in range(idx - 1, -1, -1):
        ch = text[pos]
        if ch == "}":
            depth += 1
        elif ch == "{":
            if depth == 0:
                start = pos
                break
            depth -= 1
    blob = _extract_balanced_json(text, start)
    if not blob:
        return None
    try:
        return _navigate_loader_res(json.loads(blob))
    except (ValueError, TypeError):
        return None


def _conservative_detail_result(item: NormalizedItem, reason: str) -> DeepAnalysisResult:
    """解析失败时的保守结果：只用搜索卡片已有的基础信息。"""
    title = str(item.title or "")
    price_text = f"¥{item.price:g}" if item.price else "价格未知"
    summary = f"{title}，{price_text}" if title else price_text
    return DeepAnalysisResult(
        item_id=item.item_id,
        analyzed_at=int(time.time()),
        status="ok",
        credit_status="unknown",
        credit_reason=reason,
        summary=summary,
        risk="",
        image_urls=[],
        seller_name="未知",
    )


def _classify_shop(seller_nick: str, url: str) -> str:
    """店铺类型：nick 含"旗舰"/"官方" → 品牌旗舰店；天猫 host → 天猫店；否则淘宝 C 店。"""
    if "旗舰" in seller_nick or "官方" in seller_nick:
        return "品牌旗舰店"
    host = urlparse(str(url or "").lower()).netloc
    if "detail.tmall.com" in host:
        return "天猫店"
    return "淘宝C店"


def _parse_scores(evaluates: Any, dsr_only: bool) -> list[float]:
    """evaluates 列表 → 前三个 float 分数；dsr_only 时按 type/title 过滤出 DSR 三项。"""
    entries = [e for e in evaluates if isinstance(e, dict)] if isinstance(evaluates, list) else []
    if dsr_only:
        picked = [e for e in entries if e.get("type") in _DSR_TYPES or e.get("title") in _DSR_TITLES]
        entries = picked or entries
    scores: list[float] = []
    for entry in entries:
        try:
            scores.append(float(str(entry.get("score") or "").strip()))
        except ValueError:
            continue
        if len(scores) >= 3:
            break
    return scores


def _parse_experience_score(res: dict[str, Any]) -> dict[str, Any] | None:
    """体验分组（res.componentsVO.storeCardVO：宝贝质量/物流速度/服务保障），有则提取。"""
    components = res.get("componentsVO")
    store_card = components.get("storeCardVO") if isinstance(components, dict) else None
    if not isinstance(store_card, dict):
        return None
    scores = _parse_scores(store_card.get("evaluates"), dsr_only=False)
    overall = None
    try:
        overall = float(str(store_card.get("overallScore") or "").strip())
    except ValueError:
        pass
    if overall is None and not scores:
        return None
    return {"overall": overall, "scores": scores}


def _build_prop_maps(props: Any) -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    """skuBase.props → (pid → 维度名, (pid, vid) → 值名)；valueMap 与 values 都兼容。"""
    prop_names: dict[str, str] = {}
    value_names: dict[tuple[str, str], str] = {}
    for prop in props if isinstance(props, list) else []:
        if not isinstance(prop, dict):
            continue
        pid = str(prop.get("pid") or "")
        if not pid:
            continue
        prop_names[pid] = str(prop.get("name") or pid)
        value_map = prop.get("valueMap")
        entries = list(value_map.values()) if isinstance(value_map, dict) else (prop.get("values") or [])
        for entry in entries if isinstance(entries, list) else []:
            if not isinstance(entry, dict):
                continue
            vid = str(entry.get("vid") or "")
            if vid:
                value_names[(pid, vid)] = str(entry.get("name") or vid)
    return prop_names, value_names


def _sku_label(prop_path: Any, prop_names: dict[str, str], value_names: dict[tuple[str, str], str]) -> str:
    """propPath（pid:vid;pid:vid）→ "显存容量=8GB / 显卡名称=RTX5070Ti"；解不出的维度跳过。"""
    parts = []
    for pair in str(prop_path or "").split(";"):
        if ":" not in pair:
            continue
        pid, vid = pair.split(":", 1)
        value_name = value_names.get((pid, vid))
        if value_name is not None:
            parts.append(f"{prop_names.get(pid, pid)}={value_name}")
    return " / ".join(parts)


def _parse_sku_table(res: dict[str, Any]) -> list[dict[str, Any]]:
    """skuCore.sku2info + skuBase → SKU 档位表（price 无效项已过滤，含无货标注）。

    sku2info 的键 "0"/"1"... 对应 skuBase.skus 下标（天猫实证）；C 店页面混有
    以 skuId 为键的条目，先按下标解析、落空再按 skuId 匹配，并按 skuId 去重。
    """
    sku_base = res.get("skuBase") if isinstance(res.get("skuBase"), dict) else {}
    sku_core = res.get("skuCore") if isinstance(res.get("skuCore"), dict) else {}
    sku2info = sku_core.get("sku2info")
    if not isinstance(sku2info, dict):
        return []
    skus = sku_base.get("skus") if isinstance(sku_base.get("skus"), list) else []
    prop_names, value_names = _build_prop_maps(sku_base.get("props"))
    table: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key, info in sku2info.items():
        if not isinstance(info, dict):
            continue
        sku: dict[str, Any] | None = None
        key_text = str(key)
        if key_text.isdigit():
            index = int(key_text)
            if 0 <= index < len(skus) and isinstance(skus[index], dict):
                sku = skus[index]
        if sku is None:
            for candidate in skus:
                if isinstance(candidate, dict) and str(candidate.get("skuId") or "") == key_text:
                    sku = candidate
                    break
        sku = sku if isinstance(sku, dict) else {}
        sku_id = str(sku.get("skuId") or "")
        dedupe_key = sku_id or f"key:{key_text}"
        if dedupe_key in seen:
            continue
        price_info = info.get("price")
        price = None
        if isinstance(price_info, dict):
            try:
                price = float(str(price_info.get("priceText") or "").strip())
            except ValueError:
                price = None
        if price is None or price <= 0:
            continue
        seen.add(dedupe_key)
        quantity = info.get("quantity")
        quantity_text = str(info.get("quantityText") or "")
        available = "无货" not in quantity_text
        if isinstance(quantity, (int, float)) and quantity <= 0:
            available = False
        label = _sku_label(sku.get("propPath"), prop_names, value_names)
        if not label:
            label = f"SKU {sku_id}" if sku_id else "默认规格"
        table.append(
            {
                "label": label,
                "price": price,
                "quantity": quantity,
                "quantityText": quantity_text,
                "logisticsTime": str(info.get("logisticsTime") or ""),
                "available": available,
            }
        )
    return table


def _judge_credit(dsr_scores: list[float], shop_type: str) -> tuple[str, str]:
    """DSR 三项均 ≥4.8 → good；任一 <4.5 → bad；其余 unknown（品牌旗舰店均 ≥4.6 上调 good）。"""
    dsr_text = "/".join(f"{s:g}" for s in dsr_scores)
    if len(dsr_scores) < 3:
        return "unknown", "缺少 DSR 三项评分，无法判定店铺信用"
    if all(s >= 4.8 for s in dsr_scores):
        return "good", f"DSR 三项 {dsr_text} 均 ≥4.8，店铺评分良好"
    if any(s < 4.5 for s in dsr_scores):
        return "bad", f"DSR 三项 {dsr_text} 含 <4.5 分项，店铺评分偏低"
    if shop_type == "品牌旗舰店" and all(s >= 4.6 for s in dsr_scores):
        return "good", f"品牌旗舰店，DSR 三项 {dsr_text} 均 ≥4.6"
    return "unknown", f"DSR 三项 {dsr_text} 介于 4.5~4.8 之间，无明确信用信号"


def _parse_taobao_detail_page(
    html: str, payloads: list, item: NormalizedItem
) -> DeepAnalysisResult:
    """淘宝详情页解析钩子（阶段 1.3）：解析 HTML 内嵌 JSON，永不抛异常。

    淘宝详情页为 SSR，payloads 只有埋点故不使用；任何解析失败都返回保守结果。
    """
    del payloads  # SSR 页面 XHR 只有埋点/监控，商品数据全在 HTML 内嵌 JSON
    try:
        res = _extract_loader_res(html)
        seller = res.get("seller") if isinstance(res, dict) else None
        if not isinstance(seller, dict):
            return _conservative_detail_result(item, _PARSE_FAIL_REASON)

        # 店铺：nick / 类型 / DSR / 等级 / 体验分
        nick = str(seller.get("sellerNick") or seller.get("shopName") or "").strip() or "未知"
        shop_type = _classify_shop(nick, item.url)
        dsr_scores = _parse_scores(seller.get("evaluates"), dsr_only=True)
        experience = _parse_experience_score(res)
        credit_parts = [shop_type]
        if dsr_scores:
            credit_parts.append("DSR " + "/".join(f"{s:g}" for s in dsr_scores))
        credit_level = str(seller.get("creditLevel") or "").strip()
        if credit_level:
            credit_parts.append(f"等级{credit_level}")
        if experience and experience.get("overall") is not None:
            credit_parts.append(f"体验分{experience['overall']:g}")
        seller_id = str(seller.get("userId") or seller.get("sellerId") or "") or None
        shop_url = normalize_url(seller.get("pcShopUrl") or seller.get("shopUrl"), _BASE_URL)

        # SKU 档位表与价格区间
        sku_table = _parse_sku_table(res)
        prices = [entry["price"] for entry in sku_table]
        price_min = min(prices) if prices else None
        price_max = max(prices) if prices else None

        credit_status, credit_reason = _judge_credit(dsr_scores, shop_type)

        risk_parts: list[str] = []
        if shop_type == "淘宝C店" and any(s < 4.5 for s in dsr_scores):
            risk_parts.append("店铺评分偏低，谨慎交易")
        if price_min and price_max and price_max / price_min > 3:
            risk_parts.append("SKU 价差巨大（低价档引流），认准型号再拍")
        if any(not entry["available"] for entry in sku_table):
            risk_parts.append("部分档位无货")

        dsr_text = "/".join(f"{s:g}" for s in dsr_scores) if dsr_scores else "未知"
        if price_min is not None and price_max is not None:
            sku_text = f"SKU {len(sku_table)} 档 ¥{price_min:g}~¥{price_max:g}"
        else:
            sku_text = "SKU 价格信息缺失"
        summary = f"{nick}（{shop_type}），DSR {dsr_text}，{sku_text}"

        item_info = res.get("item")
        images = item_info.get("images") if isinstance(item_info, dict) else None
        image_urls = [str(u) for u in images[:6] if u] if isinstance(images, list) else []

        return DeepAnalysisResult(
            item_id=item.item_id,
            analyzed_at=int(time.time()),
            status="ok",
            credit_status=credit_status,
            credit_reason=credit_reason,
            summary=summary,
            risk="；".join(risk_parts),
            image_urls=image_urls,
            seller_name=nick,
            seller_id=seller_id,
            seller_credit=" · ".join(credit_parts),
            raw={
                "sku_table": sku_table[:8],
                "sku_total": len(sku_table),
                "price_min": price_min,
                "price_max": price_max,
                "dsr": dsr_scores,
                "experience": experience,
                "shop_url": shop_url,
                "shop_type": shop_type,
            },
        )
    except Exception:
        logger.exception("淘宝详情页解析异常，降级为保守结果")
        return _conservative_detail_result(item, _PARSE_FAIL_REASON)


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
    # 详情接口标记：实测（2026-07-24 两份真实详情页）为 SSR，payload 只有埋点，
    # 无详情 mtop 接口 → 走 HTML 内嵌 JSON 解析（parse_detail_page）；标记仅留作日志兼容。
    detail_api_marker="mtop.taobao.pcdetail.data.get",
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
    # 淘宝详情页为 SSR（阶段 1.3 已实测）：深度分析走 parse_detail_page 解析 HTML 内嵌 JSON。
    supports_item_detail=True,
    parse_detail_page=_parse_taobao_detail_page,
    # 淘宝访客态下 mini_login iframe 本就不存在，"iframe gone=成功"启发式会误判，
    # 一键登录捷径整体禁用（login_session.try_quick_login 与 provider 侧同修）。
    quick_login_enabled=False,
    # 登录落地页是纯登录页，validate_login 不能回那里（会把已登录用户拖回登录页，
    # 且 getusersimple 只在内容页触发）。探测页用搜索页——实测该页必发
    # mtop.user.getusersimple，未登录 SESSION_EXPIRED、登录后 SUCCESS。
    validate_probe_url="https://s.taobao.com/search?q=%E6%89%8B%E6%9C%BA",
    # 淘宝访客搜索合法：次要接口（getusersimple 等）的 SESSION_EXPIRED 不代表被墙，
    # payload 登录标记不判 AUTH_REQUIRED，只认 login.taobao.com 重定向。
    auth_on_payload_markers=False,
)
