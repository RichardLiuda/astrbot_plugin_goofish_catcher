"""app/platforms/taobao.py 的单元测试。

字段规则实证来源：local_data/sso_taobao.html（2026-07-20 实验快照）——
标题在 div[class*='title--'] 的 title 属性；价格拆 priceInt/priceFloat；
广告卡片链接为 click.simba.taobao.com，必须过滤。
"""
from __future__ import annotations

import unittest

from app.platforms import TAOBAO_PROFILE
from app.platforms.taobao import _parse_dom_card, _parse_price_from_card

BASE = TAOBAO_PROFILE.base_url


def _card(**overrides):
    card = {
        "href": "//item.taobao.com/item.htm?id=884639892324",
        "title": "ROG RTX5080白夜神/黄金夜神/5090D 华硕台式电脑电竞游戏显卡",
        "priceInt": "10999",
        "priceFloat": ".00",
        "priceDesc": "优惠后",
        "salesText": "400+人付款",
        "shopName": "ROG旗舰店",
    }
    card.update(overrides)
    return card


class ParseDomCardTest(unittest.TestCase):
    def test_full_card(self) -> None:
        item = _parse_dom_card(_card(), BASE)
        assert item is not None
        self.assertEqual(item.item_id, "taobao:884639892324")  # 平台前缀防撞号
        self.assertEqual(item.platform, "taobao")
        self.assertEqual(item.price, 10999.0)
        self.assertIn("ROG", item.title)
        self.assertEqual(item.url, "https://item.taobao.com/item.htm?id=884639892324")
        # 店铺/销量进 raw，供聚合层风险标签使用
        self.assertEqual((item.raw or {}).get("shopName"), "ROG旗舰店")
        self.assertEqual((item.raw or {}).get("salesText"), "400+人付款")

    def test_tmall_link_accepted(self) -> None:
        item = _parse_dom_card(
            _card(href="//detail.tmall.com/item.htm?id=1031641444605&skuId=123"), BASE
        )
        assert item is not None
        self.assertEqual(item.item_id, "taobao:1031641444605")

    def test_ad_link_filtered(self) -> None:
        # click.simba.taobao.com 广告跳转链接必须过滤（实证错配案例）
        item = _parse_dom_card(
            _card(href="https://click.simba.taobao.com/cc_im?p=RTX&id=891757958238"),
            BASE,
        )
        self.assertIsNone(item)

    def test_missing_price_rejected(self) -> None:
        self.assertIsNone(_parse_dom_card(_card(priceInt=""), BASE))

    def test_missing_title_rejected(self) -> None:
        self.assertIsNone(_parse_dom_card(_card(title=""), BASE))

    def test_missing_href_rejected(self) -> None:
        self.assertIsNone(_parse_dom_card(_card(href=""), BASE))

    def test_price_without_float_part(self) -> None:
        item = _parse_dom_card(_card(priceInt="2868", priceFloat=""), BASE)
        assert item is not None
        self.assertEqual(item.price, 2868.0)


class ParsePriceTest(unittest.TestCase):
    def test_int_plus_float(self) -> None:
        self.assertEqual(
            _parse_price_from_card({"priceInt": "10999", "priceFloat": ".99"}),
            10999.99,
        )

    def test_dirty_int_part(self) -> None:
        self.assertEqual(
            _parse_price_from_card({"priceInt": "10,999", "priceFloat": ""}),
            10999.0,
        )


class TaobaoProfileHooksTest(unittest.TestCase):
    def test_build_search_url(self) -> None:
        self.assertEqual(
            TAOBAO_PROFILE.build_search_url("RTX 5090", None, None),
            "https://s.taobao.com/search?q=RTX%205090",
        )

    def test_is_auth_url(self) -> None:
        self.assertTrue(TAOBAO_PROFILE.is_auth_url("https://login.taobao.com/member/login.jhtml"))
        self.assertFalse(TAOBAO_PROFILE.is_auth_url("https://s.taobao.com/search?q=x"))

    def test_is_captcha_url(self) -> None:
        self.assertTrue(TAOBAO_PROFILE.is_captcha_url("https://cf.aliyun.com/nocaptcha/a"))
        self.assertFalse(TAOBAO_PROFILE.is_captcha_url("https://www.taobao.com/"))

    def test_normalize_item_page_title(self) -> None:
        self.assertEqual(
            TAOBAO_PROFILE.normalize_item_page_title("华硕 RTX5090 显卡-淘宝网"),
            "华硕 RTX5090 显卡",
        )

    def test_dom_selector_excludes_ads(self) -> None:
        # 选择器要求 href 含 item.htm，广告 cc_im 链接在选择器层就被排除
        self.assertIn("item.htm", TAOBAO_PROFILE.dom_card_link_selector)


if __name__ == "__main__":
    unittest.main()
