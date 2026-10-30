"""Per-subscription chat allow/deny lists."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import MethodType, SimpleNamespace

from app.chat_access import (
    event_allowed_for_subscription,
    subscription_chat_allowed,
)
from app.storage import SubscriptionStorage


def _event(umo: str, *, group_id: str = "", sender_id: str = "", private: bool = False):
    return SimpleNamespace(
        unified_msg_origin=umo,
        get_group_id=lambda: group_id,
        get_sender_id=lambda: sender_id,
        is_private_chat=lambda: private,
    )


def _sub(allow=(), deny=()):
    return SimpleNamespace(allow_umos=tuple(allow), deny_umos=tuple(deny))


class SubscriptionChatAllowedTest(unittest.TestCase):
    def test_empty_lists_allow_everything(self) -> None:
        self.assertTrue(subscription_chat_allowed(_sub(), unified_msg_origin="a:GroupMessage:1"))

    def test_allow_list_hit_and_miss(self) -> None:
        sub = _sub(allow=["111"])
        self.assertTrue(subscription_chat_allowed(sub, unified_msg_origin="a:GroupMessage:111"))
        self.assertFalse(subscription_chat_allowed(sub, unified_msg_origin="a:GroupMessage:222"))

    def test_deny_list_blocks(self) -> None:
        sub = _sub(deny=["333"])
        self.assertFalse(subscription_chat_allowed(sub, unified_msg_origin="a:GroupMessage:333"))
        self.assertTrue(subscription_chat_allowed(sub, unified_msg_origin="a:GroupMessage:444"))

    def test_deny_wins_over_allow(self) -> None:
        sub = _sub(allow=["555"], deny=["555"])
        self.assertFalse(subscription_chat_allowed(sub, unified_msg_origin="a:GroupMessage:555"))

    def test_group_id_token_matches(self) -> None:
        sub = _sub(allow=["group:777"])
        self.assertTrue(
            subscription_chat_allowed(sub, group_id="777", unified_msg_origin="a:GroupMessage:777")
        )

    def test_event_helper_reads_group_id(self) -> None:
        sub = _sub(deny=["888"])
        allowed = event_allowed_for_subscription(
            _event("a:GroupMessage:888", group_id="888"), sub
        )
        self.assertFalse(allowed)
        self.assertTrue(
            event_allowed_for_subscription(
                _event("a:GroupMessage:999", group_id="999"), sub
            )
        )

    def test_private_sender_token_matches(self) -> None:
        sub = _sub(allow=["user-1"])
        event = _event("a:FriendMessage:user-1", sender_id="user-1", private=True)
        self.assertTrue(event_allowed_for_subscription(event, sub))


class SubscriptionChatListStorageTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.storage = SubscriptionStorage(Path(self._tmp.name) / "chat_lists.db")
        await self.storage.initialize()

    async def asyncTearDown(self) -> None:
        await self.storage.close()
        self._tmp.cleanup()

    async def _upsert(self, **kwargs):
        payload = {
            "umo": "aiocqhttp:GroupMessage:100",
            "keyword": "相机",
            "interval_sec": 600,
            "pages": 1,
            "recommend_max_price": None,
            "drop_abs": 0.0,
            "drop_pct": 0.0,
            "new_window_sec": 3600,
            "cooldown_sec": 60,
        }
        payload.update(kwargs)
        return await self.storage.upsert_subscription(**payload)

    async def test_roundtrip_preserves_entries(self) -> None:
        sub, created = await self._upsert(
            allow_umos=["group:200", "201"], deny_umos=["300"]
        )
        self.assertTrue(created)
        self.assertEqual(sub.allow_umos, ("group:200", "201"))
        self.assertEqual(sub.deny_umos, ("300",))

        reloaded = await self.storage.get_subscription_by_id(sub.id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.allow_umos, ("group:200", "201"))
        self.assertEqual(reloaded.deny_umos, ("300",))

    async def test_default_is_unrestricted(self) -> None:
        sub, _ = await self._upsert()
        self.assertEqual(sub.allow_umos, ())
        self.assertEqual(sub.deny_umos, ())
        self.assertTrue(subscription_chat_allowed(sub, unified_msg_origin=sub.umo))

    async def test_update_replaces_lists(self) -> None:
        sub, _ = await self._upsert()
        updated = await self.storage.update_subscription(
            sub_id=sub.id,
            umo=sub.umo,
            keyword=sub.keyword,
            interval_sec=sub.interval_sec,
            pages=sub.pages,
            recommend_max_price=sub.recommend_max_price,
            drop_abs=sub.drop_abs,
            drop_pct=sub.drop_pct,
            new_window_sec=sub.new_window_sec,
            cooldown_sec=sub.cooldown_sec,
            allow_umos=["400"],
            deny_umos=[],
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.allow_umos, ("400",))
        self.assertEqual(updated.deny_umos, ())

    async def test_legacy_rows_default_to_empty(self) -> None:
        sub, _ = await self._upsert(allow_umos=["500"], deny_umos=["501"])
        # Simulate a row written before the v8 columns existed.
        conn = self.storage._conn_or_raise()
        await conn.execute(
            "UPDATE subscriptions SET allow_umos = '', deny_umos = '' WHERE id = ?",
            (sub.id,),
        )
        await conn.commit()
        reloaded = await self.storage.get_subscription_by_id(sub.id)
        self.assertEqual(reloaded.allow_umos, ())
        self.assertEqual(reloaded.deny_umos, ())


class SubscriptionChatGuardTest(unittest.IsolatedAsyncioTestCase):
    """The tool-side guard rejects operations from chats outside the lists."""

    async def asyncSetUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.storage = SubscriptionStorage(Path(self._tmp.name) / "guard.db")
        await self.storage.initialize()
        sub, _ = await self.storage.upsert_subscription(
            umo="aiocqhttp:GroupMessage:100",
            keyword="相机",
            interval_sec=600,
            pages=1,
            recommend_max_price=None,
            drop_abs=0.0,
            drop_pct=0.0,
            new_window_sec=3600,
            cooldown_sec=60,
            allow_umos=["group:200"],
        )
        self.sub = sub

        from test_scheduler_platform_routing import _load_plugin_main

        plugin_cls = _load_plugin_main().GoofishCatcherPlugin

        plugin = SimpleNamespace(storage=self.storage)
        plugin._subscription_chat_guard = MethodType(
            plugin_cls._subscription_chat_guard, plugin
        )
        self.plugin = plugin

    async def asyncTearDown(self) -> None:
        await self.storage.close()
        self._tmp.cleanup()

    async def test_blocks_chat_outside_lists(self) -> None:
        message = await self.plugin._subscription_chat_guard(
            _event("aiocqhttp:GroupMessage:999", group_id="999"), self.sub.id
        )
        self.assertIsNotNone(message)
        self.assertIn("未对当前会话开放", message)

    async def test_allows_chat_inside_lists(self) -> None:
        message = await self.plugin._subscription_chat_guard(
            _event("aiocqhttp:GroupMessage:200", group_id="200"), self.sub.id
        )
        self.assertIsNone(message)

    async def test_unknown_subscription_defers_to_caller(self) -> None:
        message = await self.plugin._subscription_chat_guard(
            _event("aiocqhttp:GroupMessage:200", group_id="200"), 99999
        )
        self.assertIsNone(message)


if __name__ == "__main__":
    unittest.main()
