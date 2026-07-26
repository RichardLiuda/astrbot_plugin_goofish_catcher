"""app/platforms/taobao.py 详情页解析钩子（_parse_taobao_detail_page）的单元测试。

页面结构实证来源：local_data/probe_*_item_htm_*.html（2026-07-24，天猫店/C 店各一份）——
淘宝详情页是 SSR，商品数据嵌在 `window.__ICE_APP_CONTEXT__ || {};var b = {BIG_JSON}`
里，路径 loaderData.home.data.res → seller / item / skuBase / skuCore；
sku2info 的键 "0"/"1"... 对应 skuBase.skus 下标（C 店页面混有以 skuId 为键的条目）。
"""
from __future__ import annotations

import json
import unittest

from app.platforms import TAOBAO_PROFILE
from app.platforms.taobao import _parse_taobao_detail_page
from app.types import NormalizedItem


def _item(
    url: str = "https://detail.tmall.com/item.htm?id=692309345346",
    title: str = "索泰 RTX5070Ti 显卡",
    price: float = 3549.0,
) -> NormalizedItem:
    return NormalizedItem(
        item_id="taobao:692309345346", title=title, price=price, url=url, platform="taobao"
    )


def _dsr(desc: object, serv: object, post: object) -> list[dict]:
    return [
        {"score": str(desc), "level": "1", "levelText": "高", "title": "宝贝描述", "type": "desc"},
        {"score": str(serv), "level": "1", "levelText": "高", "title": "卖家服务", "type": "serv"},
        {"score": str(post), "level": "1", "levelText": "高", "title": "物流服务", "type": "post"},
    ]


def _res(**overrides) -> dict:
    """精简版 res：天猫旗舰店（索泰旗舰店），2 个 SKU 档（3549 有货 / 10999 无货）。"""
    res = {
        "seller": {
            "sellerNick": "索泰旗舰店",
            "evaluates": _dsr("4.9 ", "4.9 ", "4.9 "),
            "creditLevel": "11",
            "userId": "2091996333",
            "sellerId": "2091996333",
            "pcShopUrl": "//shop111306835.taobao.com",
        },
        "item": {
            "vagueSellCount": "8000+",
            "images": [f"https://img.alicdn.com/pic{i}.jpg" for i in range(8)],
        },
        "componentsVO": {
            "storeCardVO": {
                "overallScore": "4.5",
                "evaluates": [
                    {"score": "5.0", "title": "宝贝质量"},
                    {"score": "4.8", "title": "物流速度"},
                    {"score": "3.8", "title": "服务保障"},
                ],
            }
        },
        "skuBase": {
            "props": [
                {
                    "pid": "30308",
                    "name": "显存容量",
                    "values": [{"vid": "41420", "name": "8GB"}, {"vid": "16915352", "name": "12GB"}],
                    "valueMap": {
                        "41420": {"vid": "41420", "name": "8GB"},
                        "16915352": {"vid": "16915352", "name": "12GB"},
                    },
                },
                {
                    "pid": "1627207",
                    "name": "显卡名称",
                    "values": [
                        {"vid": "42355091863", "name": "RTX5070Ti"},
                        {"vid": "39155826514", "name": "RTX5080"},
                    ],
                    "valueMap": {
                        "42355091863": {"vid": "42355091863", "name": "RTX5070Ti"},
                        "39155826514": {"vid": "39155826514", "name": "RTX5080"},
                    },
                },
            ],
            "skus": [
                {"propPath": "30308:41420;1627207:42355091863", "skuId": "6265307815706"},
                {"propPath": "30308:16915352;1627207:39155826514", "skuId": "6034913873932"},
            ],
        },
        "skuCore": {
            "sku2info": {
                "0": {
                    "price": {
                        "priceTitle": "优惠前",
                        "priceText": "3549",
                        "priceMoney": "354900",
                        "priceDesc": "起",
                    },
                    "quantity": 5,
                    "quantityText": "即将售罄(限购1件)",
                    "logisticsTime": "预计1小时内发货",
                },
                "1": {
                    "price": {"priceText": "10999", "priceMoney": "1099900"},
                    "quantity": 0,
                    "quantityText": "无货(限购1件)",
                    "logisticsTime": "预计3天内发货",
                },
            }
        },
    }
    res.update(overrides)
    return res


def _html(res: dict, *, var_b: bool = True) -> str:
    # 真实页面为压缩 JSON（无空格），fixture 同样用紧凑分隔符
    payload = {"appData": None, "loaderData": {"home": {"data": {"res": res}}}}
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if var_b:
        return (
            "<html><body><script>(function(){window.__ICE_APP_CONTEXT__ || {};"
            f"var b = {blob};window.__ICE_APP_CONTEXT__=b;"
            "})();</script></body></html>"
        )
    return f"<html><body><script>var pageData = {blob};</script></body></html>"


def _parse(res: dict | None = None, html: str | None = None, **item_kwargs):
    if html is None:
        html = _html(res if res is not None else _res())
    return _parse_taobao_detail_page(html, [], _item(**item_kwargs))


class FullParseTest(unittest.TestCase):
    def test_full_parse(self) -> None:
        r = _parse()
        self.assertEqual(r.status, "ok")
        self.assertEqual(r.credit_status, "good")
        self.assertEqual(r.seller_name, "索泰旗舰店")
        self.assertEqual(r.seller_id, "2091996333")
        assert r.seller_credit is not None
        self.assertIn("品牌旗舰店", r.seller_credit)
        self.assertIn("DSR 4.9/4.9/4.9", r.seller_credit)
        self.assertIn("等级11", r.seller_credit)

    def test_sku_table_labels_and_prices(self) -> None:
        r = _parse()
        raw = r.raw or {}
        table = raw["sku_table"]
        self.assertEqual(raw["sku_total"], 2)
        # propPath 经 props.valueMap 解成 "维度=值"，多维度以 " / " 连接
        self.assertEqual(table[0]["label"], "显存容量=8GB / 显卡名称=RTX5070Ti")
        self.assertEqual(table[1]["label"], "显存容量=12GB / 显卡名称=RTX5080")
        self.assertEqual(table[0]["price"], 3549.0)
        self.assertEqual(table[0]["quantityText"], "即将售罄(限购1件)")
        self.assertEqual(table[0]["logisticsTime"], "预计1小时内发货")
        self.assertEqual(raw["price_min"], 3549.0)
        self.assertEqual(raw["price_max"], 10999.0)

    def test_images_cut_to_six(self) -> None:
        r = _parse()
        self.assertEqual(len(r.image_urls), 6)
        self.assertEqual(r.image_urls[0], "https://img.alicdn.com/pic0.jpg")

    def test_summary_format(self) -> None:
        r = _parse()
        self.assertEqual(
            r.summary, "索泰旗舰店（品牌旗舰店），DSR 4.9/4.9/4.9，SKU 2 档 ¥3549~¥10999"
        )

    def test_raw_fields(self) -> None:
        r = _parse()
        raw = r.raw or {}
        self.assertEqual(raw["dsr"], [4.9, 4.9, 4.9])
        self.assertEqual(raw["shop_url"], "https://shop111306835.taobao.com")
        self.assertEqual(raw["shop_type"], "品牌旗舰店")

    def test_experience_score_used(self) -> None:
        # 第二组评分（体验分：宝贝质量/物流速度/服务保障）有则提取，但不混入 DSR 判定
        r = _parse()
        raw = r.raw or {}
        self.assertEqual(raw["experience"]["overall"], 4.5)
        self.assertEqual(raw["experience"]["scores"], [5.0, 4.8, 3.8])
        assert r.seller_credit is not None
        self.assertIn("体验分4.5", r.seller_credit)
        self.assertEqual(r.credit_status, "good")  # 体验分 3.8 不影响 DSR 判定

    def test_sku_id_keyed_sku2info(self) -> None:
        # C 店实证：sku2info 混有以 skuId 为键的条目，按 skuId 匹配解析
        res = _res()
        res["skuCore"]["sku2info"] = {
            "6034913873932": {
                "price": {"priceText": "10999"},
                "quantity": 3,
                "quantityText": "有货",
                "logisticsTime": "",
            }
        }
        r = _parse(res)
        table = (r.raw or {})["sku_table"]
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0]["label"], "显存容量=12GB / 显卡名称=RTX5080")
        self.assertEqual(table[0]["price"], 10999.0)

    def test_invalid_price_filtered(self) -> None:
        res = _res()
        res["skuCore"]["sku2info"]["1"]["price"]["priceText"] = "N/A"
        r = _parse(res)
        raw = r.raw or {}
        self.assertEqual(raw["sku_total"], 1)
        self.assertEqual(raw["price_min"], 3549.0)
        self.assertEqual(raw["price_max"], 3549.0)


class CreditRuleTest(unittest.TestCase):
    def test_all_above_48_good(self) -> None:
        r = _parse(_res(seller={**_res()["seller"], "evaluates": _dsr("4.8", "4.9", "5.0")}))
        self.assertEqual(r.credit_status, "good")

    def test_any_below_45_bad(self) -> None:
        r = _parse(_res(seller={**_res()["seller"], "evaluates": _dsr("4.9", "4.4", "4.9")}))
        self.assertEqual(r.credit_status, "bad")
        self.assertIn("<4.5", r.credit_reason)

    def test_flagship_46_upgraded_to_good(self) -> None:
        # 品牌旗舰店轻微上调：unknown 档（均 <4.8 且无 <4.5）但均 ≥4.6 → good
        r = _parse(_res(seller={**_res()["seller"], "evaluates": _dsr("4.6", "4.7", "4.7")}))
        self.assertEqual(r.credit_status, "good")
        self.assertIn("品牌旗舰店", r.credit_reason)

    def test_non_flagship_46_stays_unknown(self) -> None:
        # 同档分数但非旗舰店不上调
        seller = {**_res()["seller"], "sellerNick": "gdy119", "evaluates": _dsr("4.6", "4.7", "4.7")}
        r = _parse(_res(seller=seller), url="https://item.taobao.com/item.htm?id=1039174402349")
        self.assertEqual(r.credit_status, "unknown")

    def test_missing_dsr_unknown(self) -> None:
        r = _parse(_res(seller={**_res()["seller"], "evaluates": []}))
        self.assertEqual(r.credit_status, "unknown")


class RiskTest(unittest.TestCase):
    def test_price_spread_over_3x(self) -> None:
        # 默认 fixture：10999 / 3549 ≈ 3.10 > 3 → 低价档引流提示
        r = _parse()
        self.assertIn("价差巨大", r.risk)

    def test_no_spread_no_risk(self) -> None:
        res = _res()
        res["skuCore"]["sku2info"]["1"]["price"]["priceText"] = "3999"
        res["skuCore"]["sku2info"]["1"]["quantity"] = 3
        res["skuCore"]["sku2info"]["1"]["quantityText"] = "有货"
        r = _parse(res)
        self.assertEqual(r.risk, "")

    def test_out_of_stock_marked(self) -> None:
        r = _parse()
        table = (r.raw or {})["sku_table"]
        self.assertTrue(table[0]["available"])
        self.assertFalse(table[1]["available"])  # quantityText 含"无货"
        self.assertIn("部分档位无货", r.risk)

    def test_cshop_low_dsr_risk(self) -> None:
        seller = {**_res()["seller"], "sellerNick": "gdy119", "evaluates": _dsr("4.9", "4.4", "4.9")}
        r = _parse(_res(seller=seller), url="https://item.taobao.com/item.htm?id=1039174402349")
        self.assertEqual(r.credit_status, "bad")
        self.assertIn("店铺评分偏低，谨慎交易", r.risk)


class ShopTypeTest(unittest.TestCase):
    def test_cshop_by_nick(self) -> None:
        # C 店实证：sellerNick 为个人号（无旗舰/官方字样），item.taobao.com host
        seller = {**_res()["seller"], "sellerNick": "gdy119"}
        r = _parse(_res(seller=seller), url="https://item.taobao.com/item.htm?id=1039174402349")
        assert r.seller_credit is not None
        self.assertIn("淘宝C店", r.seller_credit)
        self.assertEqual((r.raw or {})["shop_type"], "淘宝C店")

    def test_tmall_without_flagship_nick(self) -> None:
        seller = {**_res()["seller"], "sellerNick": "某某数码专营店"}
        r = _parse(_res(seller=seller))
        self.assertEqual((r.raw or {})["shop_type"], "天猫店")

    def test_official_nick_is_flagship(self) -> None:
        seller = {**_res()["seller"], "sellerNick": "索泰官方企业店"}
        r = _parse(_res(seller=seller), url="https://item.taobao.com/item.htm?id=1")
        self.assertEqual((r.raw or {})["shop_type"], "品牌旗舰店")


class LoaderDataFallbackTest(unittest.TestCase):
    def test_fallback_without_var_b(self) -> None:
        # 无 "var b = " 标记时兜底：定位紧凑形态 "loaderData":{"home" 并从外层 { 配平
        r = _parse(html=_html(_res(), var_b=False))
        self.assertEqual(r.seller_name, "索泰旗舰店")
        self.assertEqual(r.credit_status, "good")

    def test_brace_inside_string_not_misbalanced(self) -> None:
        # JSON 字符串值里的花括号不得干扰配平
        res = _res()
        res["item"]["vagueSellCount"] = "8000+{ weird }"
        r = _parse(res)
        self.assertEqual(r.seller_name, "索泰旗舰店")


class ConservativeResultTest(unittest.TestCase):
    def _assert_conservative(self, r) -> None:
        self.assertEqual(r.status, "ok")
        self.assertEqual(r.credit_status, "unknown")
        self.assertEqual(r.credit_reason, "详情页结构解析失败，仅基础信息")
        self.assertEqual(r.seller_name, "未知")
        self.assertEqual(r.image_urls, [])
        self.assertIn("索泰 RTX5070Ti 显卡", r.summary)  # 回退用 item.title/price
        self.assertIn("¥3549", r.summary)

    def test_no_marker_html(self) -> None:
        self._assert_conservative(_parse(html="<html><body>plain page</body></html>"))

    def test_broken_json(self) -> None:
        self._assert_conservative(_parse(html="<script>var b = {oops, not json};</script>"))

    def test_unbalanced_braces(self) -> None:
        self._assert_conservative(
            _parse(html='<script>var b = {"loaderData":{"home":{"data":{"res":')
        )

    def test_missing_res(self) -> None:
        payload = {"loaderData": {"home": {"data": {"other": 1}}}}
        blob = json.dumps(payload, separators=(",", ":"))
        self._assert_conservative(_parse(html=f"<script>var b = {blob};</script>"))

    def test_seller_not_dict(self) -> None:
        self._assert_conservative(_parse(_res(seller="gdy119")))

    def test_empty_html_no_raise(self) -> None:
        self._assert_conservative(_parse(html=""))


class ProfileWiringTest(unittest.TestCase):
    def test_parse_detail_page_wired(self) -> None:
        self.assertIs(TAOBAO_PROFILE.parse_detail_page, _parse_taobao_detail_page)

    def test_supports_item_detail_enabled(self) -> None:
        self.assertTrue(TAOBAO_PROFILE.supports_item_detail)

    def test_profile_hook_end_to_end(self) -> None:
        hook = TAOBAO_PROFILE.parse_detail_page
        assert hook is not None
        r = hook(_html(_res()), [], _item())
        self.assertEqual(r.seller_name, "索泰旗舰店")


if __name__ == "__main__":
    unittest.main()
