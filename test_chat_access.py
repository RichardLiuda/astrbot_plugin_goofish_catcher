"""Chat allow/deny list matching."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.chat_access import (
    active_chat_allowed,
    is_chat_allowed,
    parse_chat_entries,
    set_active_chat_rules,
)
from app.config import load_plugin_settings


class ParseChatEntriesTest(unittest.TestCase):
    def test_splits_mixed_separators_and_strips_prefixes(self) -> None:
        entries = parse_chat_entries(
            " 123456, group:789\n群聊:555；umo:aiocqhttp:GroupMessage:42 "
        )
        self.assertEqual(
            entries,
            ("123456", "789", "555", "aiocqhttp:groupmessage:42"),
        )

    def test_list_items_and_dedup(self) -> None:
        self.assertEqual(
            parse_chat_entries(["123", " 123 ", "user:456"]),
            ("123", "456"),
        )

    def test_empty(self) -> None:
        self.assertEqual(parse_chat_entries(None), ())
        self.assertEqual(parse_chat_entries(""), ())
        self.assertEqual(parse_chat_entries([]), ())


class IsChatAllowedTest(unittest.TestCase):
    def test_empty_lists_allow_everything(self) -> None:
        self.assertTrue(
            is_chat_allowed(
                (),
                (),
                group_id="1",
                unified_msg_origin="aiocqhttp:GroupMessage:1",
            )
        )

    def test_whitelist_matches_group_id_or_full_session(self) -> None:
        whitelist = ["123456", "aiocqhttp:FriendMessage:999"]
        self.assertTrue(
            is_chat_allowed(
                whitelist,
                (),
                group_id="123456",
                unified_msg_origin="aiocqhttp:GroupMessage:123456",
            )
        )
        self.assertTrue(
            is_chat_allowed(
                whitelist,
                (),
                unified_msg_origin="aiocqhttp:FriendMessage:999",
                sender_id="999",
                is_private=True,
            )
        )
        self.assertFalse(
            is_chat_allowed(
                whitelist,
                (),
                group_id="777",
                unified_msg_origin="aiocqhttp:GroupMessage:777",
            )
        )

    def test_private_user_id_does_not_match_a_group_sender(self) -> None:
        self.assertFalse(
            is_chat_allowed(
                ["999"],
                (),
                group_id="123456",
                unified_msg_origin="aiocqhttp:GroupMessage:123456",
                sender_id="999",
                is_private=False,
            )
        )
        self.assertTrue(
            is_chat_allowed(
                ["999"],
                (),
                unified_msg_origin="aiocqhttp:FriendMessage:999",
                sender_id="999",
                is_private=True,
            )
        )

    def test_blacklist_wins_over_whitelist(self) -> None:
        self.assertFalse(
            is_chat_allowed(
                ["123456", "789"],
                ["group:123456"],
                group_id="123456",
                unified_msg_origin="aiocqhttp:GroupMessage:123456",
            )
        )
        self.assertTrue(
            is_chat_allowed(
                ["123456", "789"],
                ["group:123456"],
                group_id="789",
                unified_msg_origin="aiocqhttp:GroupMessage:789",
            )
        )

    def test_blacklist_only_denies_listed_chats(self) -> None:
        self.assertFalse(
            is_chat_allowed(
                (),
                ["GroupMessage:123456"],
                group_id="123456",
                unified_msg_origin="aiocqhttp:GroupMessage:123456",
            )
        )
        self.assertTrue(
            is_chat_allowed(
                (),
                ["GroupMessage:123456"],
                unified_msg_origin="aiocqhttp:FriendMessage:42",
                is_private=True,
            )
        )


class ActiveRulesTest(unittest.TestCase):
    def tearDown(self) -> None:
        set_active_chat_rules((), ())

    def test_event_uses_active_rules(self) -> None:
        set_active_chat_rules(["123456"], [])

        class _Event:
            unified_msg_origin = "aiocqhttp:GroupMessage:123456"

            def get_group_id(self) -> str:
                return "123456"

            def get_sender_id(self) -> str:
                return "1"

            def is_private_chat(self) -> bool:
                return False

        class _Other(_Event):
            unified_msg_origin = "aiocqhttp:GroupMessage:9"

            def get_group_id(self) -> str:
                return "9"

        self.assertTrue(active_chat_allowed(_Event()))
        self.assertFalse(active_chat_allowed(_Other()))


class LoadSettingsChatAccessTest(unittest.TestCase):
    def test_settings_keep_parsed_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = load_plugin_settings(
                {
                    "chat_whitelist": "123\ngroup:456",
                    "chat_blacklist": ["umo:aiocqhttp:FriendMessage:9"],
                },
                "astrbot_plugin_goofish_catcher",
                Path(tmp),
            )
        self.assertEqual(settings.chat_whitelist, ("123", "456"))
        self.assertEqual(
            settings.chat_blacklist,
            ("aiocqhttp:friendmessage:9",),
        )
