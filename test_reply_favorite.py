from __future__ import annotations

import unittest

from app.reply_favorite import (
    extract_non_reply_text,
    extract_reply_context_from_outline,
    extract_reply_text,
    format_reply_index_range,
    map_reply_selection,
    parse_reply_selection,
    parse_reply_target,
    recommendation_reply_hint,
)

from astrbot.api.message_components import Plain, Reply


class ReplyFavoriteParserTests(unittest.TestCase):
    def test_extract_non_reply_text_ignores_quoted_message_segment(self) -> None:
        reply = Reply(id="quoted-1", message_str="【查询推荐】关键词：macstudio96g")
        text = extract_non_reply_text([reply, Plain(" 2 ")])

        self.assertEqual(text, "2")

    def test_extract_reply_context_from_outline_parses_aiocqhttp_style_outline(
        self,
    ) -> None:
        reply_text, selection_text = extract_reply_context_from_outline(
            "[引用消息(神户理香子: 【查询推荐】关键词：macmini\n1. [95.0] test\n   链接：https://www.goofish.com/item?id=1)] 1"
        )

        self.assertEqual(selection_text, "1")
        self.assertIsNotNone(reply_text)
        assert reply_text is not None
        self.assertTrue(reply_text.startswith("【查询推荐】关键词：macmini"))

    def test_parse_reply_selection_supports_multiple_separators_and_dedupes(
        self,
    ) -> None:
        self.assertEqual(parse_reply_selection("1 2,2、3，4"), [1, 2, 3, 4])

    def test_parse_reply_selection_rejects_non_numeric_reply(self) -> None:
        self.assertIsNone(parse_reply_selection("收藏 1"))
        self.assertIsNone(parse_reply_selection(""))

    def test_parse_reply_target_extracts_items_from_recommendation_message(
        self,
    ) -> None:
        target = parse_reply_target(
            "\n".join(
                [
                    "【查询推荐】关键词：富士 相机",
                    "抓取页数：1 | 原始结果：2 | 初筛后：2",
                    "1. [9.1] Fujifilm X-T5",
                    "   价格：￥8999.00",
                    "   理由：成色好",
                    "   风险：价格略高",
                    "   链接：https://www.goofish.com/item?id=123456",
                    "2. [8.4] Fujifilm X-S20",
                    "   价格：￥4999.00",
                    "   理由：配置均衡",
                    "   风险：暂无",
                    "   链接：https://www.goofish.com/item?id=789012",
                    recommendation_reply_hint(),
                ]
            )
        )

        self.assertIsNotNone(target)
        assert target is not None
        self.assertIsNone(target.error_message)
        self.assertEqual([item.index for item in target.items], [1, 2])
        self.assertEqual(target.items[0].title, "Fujifilm X-T5")
        self.assertEqual(target.items[0].item_id, "123456")
        self.assertEqual(target.items[1].url, "https://www.goofish.com/item?id=789012")

    def test_parse_reply_target_rejects_batch_manual_check_summary(self) -> None:
        target = parse_reply_target("【立即检查】共执行 2 个订阅，结果如下：")

        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual(target.source, "batch_manual_check")
        self.assertIn("暂不支持", target.error_message or "")

    def test_parse_reply_target_ignores_non_plugin_quote(self) -> None:
        self.assertIsNone(parse_reply_target("普通聊天消息"))

    def test_map_reply_selection_returns_invalid_indexes(self) -> None:
        target = parse_reply_target(
            "\n".join(
                [
                    "【闲鱼建议】关键词：镜头",
                    "1. [8.8] Sony 20-70",
                    "   链接：https://www.goofish.com/item?id=111",
                    "2. [8.3] Sony 24-105",
                    "   链接：https://www.goofish.com/item?id=222",
                ]
            )
        )

        assert target is not None
        selected, invalid = map_reply_selection(target, [2, 3, 1])

        self.assertEqual([item.index for item in selected], [2, 1])
        self.assertEqual(invalid, [3])

    def test_parse_reply_target_accepts_link_glued_to_image_label(self) -> None:
        target = parse_reply_target(
            "\n".join(
                [
                    "【闲鱼建议】关键词：ad200pro",
                    "候选数：9 | 推荐数：3",
                    "1. [78.0] 低价出神牛AD200pro闪光灯",
                    "   链接：https://www.goofish.com/item?id=1070796089956",
                    "2. [73.0] ad200pro 1代，只有灯和充电器",
                    "   价格：￥900.00",
                    "   主图：链接：https://www.goofish.com/item?id=1092446536865",
                    "3. [68.0] 神牛AD200Pro外拍灯",
                    "   链接：https://www.goofish.com/item?id=1095508844229",
                ]
            )
        )

        assert target is not None
        self.assertIsNone(target.error_message)
        self.assertEqual([item.index for item in target.items], [1, 2, 3])
        self.assertEqual(target.items[1].item_id, "1092446536865")
        selected, invalid = map_reply_selection(target, [2])
        self.assertEqual(invalid, [])
        self.assertEqual([item.index for item in selected], [2])

    def test_extract_reply_text_prefers_chain_over_flattened_message_str(self) -> None:
        reply = Reply(
            id="quoted-2",
            message_str=(
                "【闲鱼建议】关键词：ad200pro\n"
                "2. [73.0] ad200pro 1代\n"
                "主图：链接：https://www.goofish.com/item?id=1092446536865"
            ),
            chain=[
                Plain("2. [73.0] ad200pro 1代\n主图："),
                Plain("链接：https://www.goofish.com/item?id=1092446536865"),
            ],
        )

        text = extract_reply_text([reply, Plain("2")])

        assert text is not None
        self.assertIn(
            "主图：\n链接：https://www.goofish.com/item?id=1092446536865", text
        )
        self.assertNotIn("主图：链接：", text)

    def test_format_reply_index_range_lists_gaps(self) -> None:
        target = parse_reply_target(
            "\n".join(
                [
                    "【闲鱼建议】关键词：镜头",
                    "1. [8.8] Sony 20-70",
                    "   链接：https://www.goofish.com/item?id=111",
                    "3. [8.3] Sony 24-105",
                    "   链接：https://www.goofish.com/item?id=333",
                ]
            )
        )

        assert target is not None
        self.assertEqual(format_reply_index_range(target.items), "1、3")
