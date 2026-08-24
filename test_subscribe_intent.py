"""Deterministic subscribe-intent parser — the path that must not fall to LLM."""

from __future__ import annotations

import unittest

from app.intent.subscribe import (
    KIND_KNOWN_COMMAND,
    KIND_NONE,
    KIND_SUBSCRIBE,
    KIND_UNKNOWN_PREFIX,
    classify_goofish_message,
    parse_subscribe_command,
    parse_subscribe_text,
)
from app.platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO


class ParseSubscribeTextTest(unittest.TestCase):
    def test_reported_taobao_natural_language(self) -> None:
        intent = parse_subscribe_text("订阅淘宝的 总统黄油")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_quoted_readme_style(self) -> None:
        intent = parse_subscribe_text("「订阅淘宝的 总统黄油」")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_glued_without_space(self) -> None:
        intent = parse_subscribe_text("订阅淘宝的总统黄油")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_help_me_prefix(self) -> None:
        intent = parse_subscribe_text("帮我订阅一下淘宝的 总统黄油")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_default_platform_is_goofish(self) -> None:
        intent = parse_subscribe_text("订阅 总统黄油")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_GOOFISH)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_does_not_steal_taobao_inside_product_word(self) -> None:
        intent = parse_subscribe_command("淘宝店专用包装")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_GOOFISH)
        self.assertEqual(intent.keyword, "淘宝店专用包装")

    def test_blocklist_and_questions(self) -> None:
        self.assertIsNone(parse_subscribe_text("订阅会员"))
        self.assertIsNone(parse_subscribe_text("如何订阅淘宝的总统黄油"))
        self.assertIsNone(parse_subscribe_text("闲鱼玩偶"))


class ParseSubscribeCommandTest(unittest.TestCase):
    def test_platform_then_keyword(self) -> None:
        intent = parse_subscribe_command("淘宝 总统黄油")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")

    def test_de_particle_and_trailing_ints(self) -> None:
        intent = parse_subscribe_command("淘宝的 总统黄油 1800 1")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(intent.keyword, "总统黄油")
        self.assertEqual(intent.interval_sec, 1800)
        self.assertEqual(intent.pages, 1)

    def test_legacy_positional_interval(self) -> None:
        intent = parse_subscribe_command("总统黄油 600")
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.platform, PLATFORM_GOOFISH)
        self.assertEqual(intent.keyword, "总统黄油")
        self.assertEqual(intent.interval_sec, 600)
        self.assertEqual(intent.pages, 0)


class ClassifyGoofishMessageTest(unittest.TestCase):
    def test_natural_language_subscribe_is_intercepted(self) -> None:
        classified = classify_goofish_message("订阅淘宝的 总统黄油")
        self.assertEqual(classified.kind, KIND_SUBSCRIBE)
        assert classified.intent is not None
        self.assertEqual(classified.intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(classified.intent.keyword, "总统黄油")

    def test_quoted_natural_language_subscribe(self) -> None:
        classified = classify_goofish_message("「订阅淘宝的 总统黄油」")
        self.assertEqual(classified.kind, KIND_SUBSCRIBE)
        assert classified.intent is not None
        self.assertEqual(classified.intent.keyword, "总统黄油")

    def test_glued_command_prefix_is_intercepted(self) -> None:
        # `/闲鱼 订阅淘宝的 总统黄油` — no space after 订阅, command filter misses it
        classified = classify_goofish_message("闲鱼 订阅淘宝的 总统黄油")
        self.assertEqual(classified.kind, KIND_SUBSCRIBE)
        assert classified.intent is not None
        self.assertEqual(classified.intent.platform, PLATFORM_TAOBAO)
        self.assertEqual(classified.intent.keyword, "总统黄油")

    def test_slash_prefix_variants(self) -> None:
        for text in (
            "/闲鱼 订阅淘宝的 总统黄油",
            "／闲鱼 订阅淘宝的 总统黄油",
        ):
            classified = classify_goofish_message(text)
            self.assertEqual(classified.kind, KIND_SUBSCRIBE, text)

    def test_spaced_subscribe_command_left_to_handler(self) -> None:
        classified = classify_goofish_message("闲鱼 订阅 淘宝的 总统黄油")
        self.assertEqual(classified.kind, KIND_KNOWN_COMMAND)
        self.assertIsNone(classified.intent)

    def test_other_commands_left_to_handler(self) -> None:
        for text in (
            "闲鱼 列表",
            "闲鱼 状态",
            "闲鱼 登录 淘宝",
            "闲鱼 立即检查 总统黄油",
            "闲鱼 查询 总统黄油",
        ):
            classified = classify_goofish_message(text)
            self.assertEqual(classified.kind, KIND_KNOWN_COMMAND, text)

    def test_unknown_prefix_does_not_fall_to_llm(self) -> None:
        classified = classify_goofish_message("闲鱼 订阅淘宝总统黄油吗")
        # 订阅淘宝总统黄油吗 — NL regex may or may not parse; unknown is also fine
        self.assertIn(classified.kind, {KIND_SUBSCRIBE, KIND_UNKNOWN_PREFIX})

    def test_unknown_prefix_plain_garbage(self) -> None:
        classified = classify_goofish_message("闲鱼 随便聊聊")
        self.assertEqual(classified.kind, KIND_UNKNOWN_PREFIX)

    def test_unrelated_chat_ignored(self) -> None:
        classified = classify_goofish_message("今天天气怎么样")
        self.assertEqual(classified.kind, KIND_NONE)


if __name__ == "__main__":
    unittest.main()
