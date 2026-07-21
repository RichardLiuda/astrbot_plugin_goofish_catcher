"""app/platforms/registry.py 的单元测试。

核心契约：
- 裸 ID 一律视为 goofish（兼容存量数据）；
- 新平台 ID 必须带 "{platform}:" 前缀；
- build_item_url 是全项目拼商品 URL 的唯一收口。
"""
from __future__ import annotations

import unittest

from app.platforms import (
    build_item_url,
    make_item_id,
    platform_display_name,
    split_item_id,
)


class SplitItemIdTest(unittest.TestCase):
    def test_bare_id_defaults_to_goofish(self) -> None:
        self.assertEqual(split_item_id("1068936004280"), ("goofish", "1068936004280"))

    def test_prefixed_taobao_id(self) -> None:
        self.assertEqual(split_item_id("taobao:12345"), ("taobao", "12345"))

    def test_unknown_prefix_treated_as_goofish_bare_id(self) -> None:
        # "tb:" 不是注册平台前缀，整个串当作 goofish 裸 ID，避免静默错判平台
        self.assertEqual(split_item_id("tb:123"), ("goofish", "tb:123"))

    def test_empty_and_none(self) -> None:
        self.assertEqual(split_item_id(""), ("goofish", ""))
        self.assertEqual(split_item_id(None), ("goofish", ""))  # type: ignore[arg-type]

    def test_whitespace_stripped(self) -> None:
        self.assertEqual(split_item_id("  taobao:123  "), ("taobao", "123"))


class MakeItemIdTest(unittest.TestCase):
    def test_goofish_stays_bare(self) -> None:
        # 存量 items/price_history/notifications 全是裸 ID，goofish 绝不加前缀
        self.assertEqual(make_item_id("goofish", "123"), "123")

    def test_taobao_gets_prefix(self) -> None:
        self.assertEqual(make_item_id("taobao", "123"), "taobao:123")

    def test_round_trip(self) -> None:
        item_id = make_item_id("taobao", "963892247731")
        self.assertEqual(split_item_id(item_id), ("taobao", "963892247731"))

    def test_empty_raw_raises(self) -> None:
        with self.assertRaises(ValueError):
            make_item_id("taobao", "  ")

    def test_unknown_platform_raises(self) -> None:
        with self.assertRaises(ValueError):
            make_item_id("jd", "123")


class BuildItemUrlTest(unittest.TestCase):
    def test_goofish_bare_id(self) -> None:
        self.assertEqual(
            build_item_url("1068936004280"),
            "https://www.goofish.com/item?id=1068936004280",
        )

    def test_taobao_prefixed_id(self) -> None:
        self.assertEqual(
            build_item_url("taobao:963892247731"),
            "https://item.taobao.com/item.htm?id=963892247731",
        )

    def test_explicit_platform_override(self) -> None:
        self.assertEqual(
            build_item_url("963892247731", platform="taobao"),
            "https://item.taobao.com/item.htm?id=963892247731",
        )

    def test_unknown_platform_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_item_url("123", platform="pdd")


class PlatformDisplayNameTest(unittest.TestCase):
    def test_known(self) -> None:
        self.assertEqual(platform_display_name("goofish"), "闲鱼")
        self.assertEqual(platform_display_name("taobao"), "淘宝")

    def test_unknown_falls_back_to_id(self) -> None:
        self.assertEqual(platform_display_name("jd"), "jd")


if __name__ == "__main__":
    unittest.main()
