from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace


astrbot_module = types.ModuleType("astrbot")
astrbot_api_module = types.ModuleType("astrbot.api")
astrbot_api_module.logger = SimpleNamespace(
    warning=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
    debug=lambda *args, **kwargs: None,
)
astrbot_api_star_module = types.ModuleType("astrbot.api.star")
astrbot_api_star_module.Context = object
astrbot_api_star_module.StarTools = object

sys.modules.setdefault("astrbot", astrbot_module)
sys.modules["astrbot.api"] = astrbot_api_module
sys.modules["astrbot.api.star"] = astrbot_api_star_module

import aiosqlite

from app.storage import SubscriptionStorage


_UPSERT_KWARGS = dict(
    interval_sec=3600,
    pages=1,
    recommend_max_price=None,
    drop_abs=100.0,
    drop_pct=0.1,
    new_window_sec=86400,
    cooldown_sec=3600,
)


class StoragePlatformTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.storage = SubscriptionStorage(self.db_path)
        await self.storage.initialize()

    async def asyncTearDown(self) -> None:
        await self.storage.close()
        self._tmpdir.cleanup()

    async def test_fresh_db_has_v7_schema(self) -> None:
        async with aiosqlite.connect(self.db_path.as_posix()) as conn:
            row = await (await conn.execute("PRAGMA user_version")).fetchone()
            self.assertEqual(int(row[0]), 7)
            col_rows = await (
                await conn.execute("PRAGMA table_info(subscriptions)")
            ).fetchall()
            cols = {r[1] for r in col_rows}
            self.assertIn("platform", cols)
            mp_cols = await (
                await conn.execute("PRAGMA table_info(market_price)")
            ).fetchall()
            self.assertIn("platform", {r[1] for r in mp_cols})

    async def test_subscription_unique_per_platform(self) -> None:
        umo, kw = "umo-1", "macmini"
        _, created_g = await self.storage.upsert_subscription(
            umo=umo, keyword=kw, platform="goofish", **_UPSERT_KWARGS
        )
        _, created_t = await self.storage.upsert_subscription(
            umo=umo, keyword=kw, platform="taobao", **_UPSERT_KWARGS
        )
        self.assertTrue(created_g)
        self.assertTrue(created_t)

        _, created_again = await self.storage.upsert_subscription(
            umo=umo, keyword=kw, platform="taobao", **_UPSERT_KWARGS
        )
        self.assertFalse(created_again)

        async with aiosqlite.connect(self.db_path.as_posix()) as conn:
            row = await (
                await conn.execute("SELECT COUNT(*) FROM subscriptions")
            ).fetchone()
            self.assertEqual(int(row[0]), 2)

        taobao_sub = await self.storage.get_subscription(umo, kw, platform="taobao")
        self.assertIsNotNone(taobao_sub)
        assert taobao_sub is not None
        self.assertEqual(taobao_sub.platform, "taobao")

        deleted = await self.storage.delete_subscription(umo, kw)
        self.assertTrue(deleted)
        self.assertIsNone(await self.storage.get_subscription(umo, kw))
        self.assertIsNotNone(
            await self.storage.get_subscription(umo, kw, platform="taobao")
        )

    async def test_market_price_keyed_per_platform(self) -> None:
        now_ts = 1_700_000_000
        g = await self.storage.upsert_market_price(
            "RTX 5090", [100.0, 110.0, 120.0], now_ts, platform="goofish"
        )
        t = await self.storage.upsert_market_price(
            "RTX 5090", [200.0, 220.0], now_ts, platform="taobao"
        )
        self.assertEqual(g.ema_price, 110.0)
        self.assertEqual(t.ema_price, 210.0)
        self.assertEqual(g.platform, "goofish")
        self.assertEqual(t.platform, "taobao")

        # 默认平台是 goofish，且不受 taobao 数据影响
        default_mp = await self.storage.get_market_price("RTX 5090")
        self.assertIsNotNone(default_mp)
        assert default_mp is not None
        self.assertEqual(default_mp.ema_price, 110.0)
        self.assertEqual(default_mp.platform, "goofish")

        taobao_mp = await self.storage.get_market_price("RTX 5090", platform="taobao")
        self.assertIsNotNone(taobao_mp)
        assert taobao_mp is not None
        self.assertEqual(taobao_mp.ema_price, 210.0)

        # 再更新 taobao，goofish 的 EMA 不变
        await self.storage.upsert_market_price(
            "RTX 5090", [300.0], now_ts + 60, platform="taobao"
        )
        default_mp2 = await self.storage.get_market_price("RTX 5090")
        assert default_mp2 is not None
        self.assertEqual(default_mp2.ema_price, 110.0)

    async def test_migration_from_v6(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "v6.db"
            async with aiosqlite.connect(db_path.as_posix()) as conn:
                await conn.executescript(
                    """
                    CREATE TABLE subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        umo TEXT NOT NULL,
                        keyword TEXT NOT NULL,
                        interval_sec INTEGER NOT NULL,
                        pages INTEGER NOT NULL,
                        drop_abs REAL NOT NULL,
                        drop_pct REAL NOT NULL,
                        new_window_sec INTEGER NOT NULL,
                        cooldown_sec INTEGER NOT NULL,
                        enabled INTEGER NOT NULL DEFAULT 1,
                        paused_reason TEXT DEFAULT NULL,
                        last_run_at INTEGER DEFAULT NULL,
                        next_run_at INTEGER DEFAULT NULL,
                        consecutive_failures INTEGER NOT NULL DEFAULT 0,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        recommend_max_price REAL DEFAULT NULL,
                        price_min REAL DEFAULT NULL,
                        price_max REAL DEFAULT NULL,
                        personal_only INTEGER NOT NULL DEFAULT 0,
                        free_shipping INTEGER NOT NULL DEFAULT 0,
                        new_publish_option TEXT DEFAULT NULL,
                        region TEXT DEFAULT NULL
                    );
                    CREATE UNIQUE INDEX idx_subscriptions_umo_keyword
                        ON subscriptions (umo, keyword);
                    INSERT INTO subscriptions (
                        umo, keyword, interval_sec, pages, drop_abs, drop_pct,
                        new_window_sec, cooldown_sec, created_at, updated_at
                    ) VALUES ('umo-1', 'macmini', 3600, 1, 100.0, 0.1, 86400, 3600, 1, 1);

                    CREATE TABLE market_price (
                        keyword       TEXT PRIMARY KEY,
                        ema_price     REAL NOT NULL,
                        sample_count  INTEGER NOT NULL DEFAULT 0,
                        updated_at    INTEGER NOT NULL
                    );
                    INSERT INTO market_price (keyword, ema_price, sample_count, updated_at)
                        VALUES ('RTX 5090', 110.0, 3, 1);

                    PRAGMA user_version = 6;
                    """
                )
                await conn.commit()

            storage = SubscriptionStorage(db_path)
            await storage.initialize()
            try:
                async with aiosqlite.connect(db_path.as_posix()) as conn:
                    row = await (await conn.execute("PRAGMA user_version")).fetchone()
                    self.assertEqual(int(row[0]), 7)

                    row = await (
                        await conn.execute(
                            "SELECT platform FROM subscriptions WHERE umo = 'umo-1' AND keyword = 'macmini'"
                        )
                    ).fetchone()
                    self.assertEqual(row[0], "goofish")

                    idx_rows = await (
                        await conn.execute("PRAGMA index_list(subscriptions)")
                    ).fetchall()
                    idx_names = {r[1] for r in idx_rows}
                    self.assertIn("idx_subscriptions_umo_platform_keyword", idx_names)
                    self.assertNotIn("idx_subscriptions_umo_keyword", idx_names)

                    row = await (
                        await conn.execute(
                            "SELECT platform, ema_price, sample_count FROM market_price WHERE keyword = 'RTX 5090'"
                        )
                    ).fetchone()
                    self.assertEqual(row[0], "goofish")
                    self.assertEqual(float(row[1]), 110.0)
                    self.assertEqual(int(row[2]), 3)

                _, created = await storage.upsert_subscription(
                    umo="umo-1",
                    keyword="macmini",
                    platform="taobao",
                    **_UPSERT_KWARGS,
                )
                self.assertTrue(created)
                async with aiosqlite.connect(db_path.as_posix()) as conn:
                    row = await (
                        await conn.execute("SELECT COUNT(*) FROM subscriptions")
                    ).fetchone()
                    self.assertEqual(int(row[0]), 2)
            finally:
                await storage.close()


if __name__ == "__main__":
    unittest.main()
