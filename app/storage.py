from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import aiosqlite

from .admin_types import (
    FetchRunSummary,
    ItemSummary,
    NotificationRecord,
    OverviewAlert,
    PriceHistoryPoint,
    RelatedSubscription,
    TrendBucket,
)
from .types import ExistingItem, NormalizedItem, Subscription


class SubscriptionStorage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None
        self._write_lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path.as_posix())
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA foreign_keys=ON;")
        await self._apply_migrations()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    def _conn_or_raise(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("storage is not initialized")
        return self._conn

    async def _apply_migrations(self) -> None:
        conn = self._conn_or_raise()
        row = await (await conn.execute("PRAGMA user_version")).fetchone()
        version = int(row[0]) if row else 0

        if version < 1:
            await conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
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
                    updated_at INTEGER NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_umo_keyword
                    ON subscriptions (umo, keyword);
                CREATE INDEX IF NOT EXISTS idx_subscriptions_due
                    ON subscriptions (enabled, next_run_at);

                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    publish_time INTEGER DEFAULT NULL,
                    first_seen_at INTEGER NOT NULL,
                    last_seen_at INTEGER NOT NULL,
                    last_price REAL DEFAULT NULL,
                    FOREIGN KEY(sub_id) REFERENCES subscriptions(id) ON DELETE CASCADE
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_items_sub_item
                    ON items (sub_id, item_id);
                CREATE INDEX IF NOT EXISTS idx_items_item_id
                    ON items (item_id);
                CREATE INDEX IF NOT EXISTS idx_items_sub_last_seen
                    ON items (sub_id, last_seen_at);

                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    observed_at INTEGER NOT NULL,
                    source TEXT DEFAULT '',
                    FOREIGN KEY(sub_id) REFERENCES subscriptions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_price_history_item_time
                    ON price_history (item_id, observed_at DESC);

                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    sent_at INTEGER NOT NULL,
                    meta_json TEXT DEFAULT NULL,
                    FOREIGN KEY(sub_id) REFERENCES subscriptions(id) ON DELETE CASCADE
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_unique
                    ON notifications (sub_id, item_id, event_type, payload_hash);
                CREATE INDEX IF NOT EXISTS idx_notifications_latest
                    ON notifications (sub_id, item_id, event_type, sent_at DESC);

                CREATE TABLE IF NOT EXISTS fetch_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_id INTEGER NOT NULL,
                    started_at INTEGER NOT NULL,
                    finished_at INTEGER DEFAULT NULL,
                    status TEXT NOT NULL,
                    err_type TEXT DEFAULT NULL,
                    err_msg TEXT DEFAULT NULL,
                    items_count INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(sub_id) REFERENCES subscriptions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_fetch_runs_sub_started
                    ON fetch_runs (sub_id, started_at DESC);
                """
            )
            await conn.execute("PRAGMA user_version = 1;")
            await conn.commit()
            version = 1

        if version < 2:
            await conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS filtered_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    publish_time INTEGER DEFAULT NULL,
                    first_filtered_at INTEGER NOT NULL,
                    last_filtered_at INTEGER NOT NULL,
                    FOREIGN KEY(sub_id) REFERENCES subscriptions(id) ON DELETE CASCADE
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_filtered_items_sub_item
                    ON filtered_items (sub_id, item_id);
                CREATE INDEX IF NOT EXISTS idx_filtered_items_sub_last_filtered
                    ON filtered_items (sub_id, last_filtered_at DESC);
                """
            )
            await conn.execute("PRAGMA user_version = 2;")
            await conn.commit()

    @staticmethod
    def _row_to_subscription(row: aiosqlite.Row) -> Subscription:
        return Subscription(
            id=int(row["id"]),
            umo=str(row["umo"]),
            keyword=str(row["keyword"]),
            interval_sec=int(row["interval_sec"]),
            pages=int(row["pages"]),
            drop_abs=float(row["drop_abs"]),
            drop_pct=float(row["drop_pct"]),
            new_window_sec=int(row["new_window_sec"]),
            cooldown_sec=int(row["cooldown_sec"]),
            enabled=bool(row["enabled"]),
            paused_reason=row["paused_reason"],
            last_run_at=row["last_run_at"],
            next_run_at=row["next_run_at"],
            consecutive_failures=int(row["consecutive_failures"]),
        )

    @staticmethod
    def _row_to_normalized_item(row: aiosqlite.Row) -> NormalizedItem:
        return NormalizedItem(
            item_id=str(row["item_id"]),
            title=str(row["title"]),
            price=float(row["last_price"]) if row["last_price"] is not None else 0.0,
            url=str(row["url"]),
            publish_time=row["publish_time"],
        )

    async def get_subscription(self, umo: str, keyword: str) -> Subscription | None:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT * FROM subscriptions
                WHERE umo = ? AND keyword = ?
                """,
                (umo, keyword),
            )
        ).fetchone()
        return self._row_to_subscription(row) if row else None

    async def get_subscription_by_id(self, sub_id: int) -> Subscription | None:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT * FROM subscriptions
                WHERE id = ?
                """,
                (sub_id,),
            )
        ).fetchone()
        return self._row_to_subscription(row) if row else None

    async def upsert_subscription(
        self,
        *,
        umo: str,
        keyword: str,
        interval_sec: int,
        pages: int,
        drop_abs: float,
        drop_pct: float,
        new_window_sec: int,
        cooldown_sec: int,
    ) -> tuple[Subscription, bool]:
        conn = self._conn_or_raise()
        now_ts = int(time.time())
        async with self._write_lock:
            existing = await (
                await conn.execute(
                    """
                    SELECT id FROM subscriptions
                    WHERE umo = ? AND keyword = ?
                    LIMIT 1
                    """,
                    (umo, keyword),
                )
            ).fetchone()
            created = existing is None
            await conn.execute(
                """
                INSERT INTO subscriptions (
                    umo, keyword, interval_sec, pages, drop_abs, drop_pct,
                    new_window_sec, cooldown_sec, enabled, paused_reason,
                    last_run_at, next_run_at, consecutive_failures,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, NULL, NULL, ?, 0, ?, ?)
                ON CONFLICT(umo, keyword) DO UPDATE SET
                    interval_sec = excluded.interval_sec,
                    pages = excluded.pages,
                    drop_abs = excluded.drop_abs,
                    drop_pct = excluded.drop_pct,
                    new_window_sec = excluded.new_window_sec,
                    cooldown_sec = excluded.cooldown_sec,
                    enabled = 1,
                    paused_reason = NULL,
                    next_run_at = excluded.next_run_at,
                    updated_at = excluded.updated_at
                """,
                (
                    umo,
                    keyword,
                    interval_sec,
                    pages,
                    drop_abs,
                    drop_pct,
                    new_window_sec,
                    cooldown_sec,
                    now_ts,
                    now_ts,
                    now_ts,
                ),
            )
            await conn.commit()
            row = await (
                await conn.execute(
                    """
                    SELECT * FROM subscriptions
                    WHERE umo = ? AND keyword = ?
                    LIMIT 1
                    """,
                    (umo, keyword),
                )
            ).fetchone()

        if row is None:
            raise RuntimeError("failed to upsert subscription")
        return self._row_to_subscription(row), created

    async def delete_subscription(self, umo: str, keyword: str) -> bool:
        conn = self._conn_or_raise()
        async with self._write_lock:
            cursor = await conn.execute(
                """
                DELETE FROM subscriptions
                WHERE umo = ? AND keyword = ?
                """,
                (umo, keyword),
            )
            await conn.commit()
        return cursor.rowcount > 0

    async def list_subscriptions_by_umo(self, umo: str) -> list[Subscription]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT * FROM subscriptions
                WHERE umo = ?
                ORDER BY keyword ASC
                """,
                (umo,),
            )
        ).fetchall()
        return [self._row_to_subscription(row) for row in rows]

    async def list_subscriptions(self) -> list[Subscription]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT * FROM subscriptions
                ORDER BY id ASC
                """
            )
        ).fetchall()
        return [self._row_to_subscription(row) for row in rows]

    async def get_due_subscriptions(
        self, now_ts: int, limit: int = 100
    ) -> list[Subscription]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT * FROM subscriptions
                WHERE enabled = 1
                AND (next_run_at IS NULL OR next_run_at <= ?)
                ORDER BY COALESCE(next_run_at, 0) ASC
                LIMIT ?
                """,
                (now_ts, limit),
            )
        ).fetchall()
        return [self._row_to_subscription(row) for row in rows]

    async def pause_subscription(self, sub_id: int, reason: str) -> None:
        conn = self._conn_or_raise()
        now_ts = int(time.time())
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE subscriptions
                SET enabled = 0,
                    paused_reason = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (reason, now_ts, sub_id),
            )
            await conn.commit()

    async def resume_subscription(self, sub_id: int, now_ts: int) -> None:
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE subscriptions
                SET enabled = 1,
                    paused_reason = NULL,
                    consecutive_failures = 0,
                    next_run_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (now_ts, now_ts, sub_id),
            )
            await conn.commit()

    async def update_schedule_success(
        self, sub_id: int, now_ts: int, interval_sec: int
    ) -> None:
        conn = self._conn_or_raise()
        next_run_at = now_ts + max(1, interval_sec)
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE subscriptions
                SET last_run_at = ?,
                    next_run_at = ?,
                    consecutive_failures = 0,
                    updated_at = ?
                WHERE id = ?
                """,
                (now_ts, next_run_at, now_ts, sub_id),
            )
            await conn.commit()

    async def update_schedule_failure(
        self, sub_id: int, now_ts: int, retry_after_sec: int
    ) -> None:
        conn = self._conn_or_raise()
        next_run_at = now_ts + max(1, retry_after_sec)
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE subscriptions
                SET last_run_at = ?,
                    next_run_at = ?,
                    consecutive_failures = consecutive_failures + 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (now_ts, next_run_at, now_ts, sub_id),
            )
            await conn.commit()

    async def create_fetch_run(self, sub_id: int, started_at: int) -> int:
        conn = self._conn_or_raise()
        async with self._write_lock:
            cursor = await conn.execute(
                """
                INSERT INTO fetch_runs (
                    sub_id, started_at, status, items_count
                ) VALUES (?, ?, 'running', 0)
                """,
                (sub_id, started_at),
            )
            await conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("failed to create fetch_run")
            return int(cursor.lastrowid)

    async def finish_fetch_run(
        self,
        run_id: int,
        *,
        finished_at: int,
        status: str,
        err_type: str | None = None,
        err_msg: str | None = None,
        items_count: int = 0,
    ) -> None:
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE fetch_runs
                SET finished_at = ?,
                    status = ?,
                    err_type = ?,
                    err_msg = ?,
                    items_count = ?
                WHERE id = ?
                """,
                (finished_at, status, err_type, err_msg, items_count, run_id),
            )
            await conn.commit()

    async def get_item(self, sub_id: int, item_id: str) -> ExistingItem | None:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT sub_id, item_id, title, url, publish_time, first_seen_at, last_seen_at, last_price
                FROM items
                WHERE sub_id = ? AND item_id = ?
                """,
                (sub_id, item_id),
            )
        ).fetchone()
        if not row:
            return None
        return ExistingItem(
            sub_id=int(row["sub_id"]),
            item_id=str(row["item_id"]),
            title=str(row["title"]),
            url=str(row["url"]),
            publish_time=row["publish_time"],
            first_seen_at=int(row["first_seen_at"]),
            last_seen_at=int(row["last_seen_at"]),
            last_price=float(row["last_price"])
            if row["last_price"] is not None
            else None,
        )

    async def get_items_by_ids(
        self, sub_id: int, item_ids: list[str]
    ) -> dict[str, ExistingItem]:
        if not item_ids:
            return {}
        conn = self._conn_or_raise()
        deduped_ids = list(dict.fromkeys(item_ids))
        placeholders = ",".join("?" for _ in deduped_ids)
        rows = await (
            await conn.execute(
                f"""
                SELECT sub_id, item_id, title, url, publish_time, first_seen_at, last_seen_at, last_price
                FROM items
                WHERE sub_id = ? AND item_id IN ({placeholders})
                """,
                (sub_id, *deduped_ids),
            )
        ).fetchall()
        result: dict[str, ExistingItem] = {}
        for row in rows:
            item_id = str(row["item_id"])
            result[item_id] = ExistingItem(
                sub_id=int(row["sub_id"]),
                item_id=item_id,
                title=str(row["title"]),
                url=str(row["url"]),
                publish_time=row["publish_time"],
                first_seen_at=int(row["first_seen_at"]),
                last_seen_at=int(row["last_seen_at"]),
                last_price=float(row["last_price"])
                if row["last_price"] is not None
                else None,
            )
        return result

    async def get_filtered_item_ids(self, sub_id: int, item_ids: list[str]) -> set[str]:
        if not item_ids:
            return set()
        conn = self._conn_or_raise()
        deduped_ids = list(dict.fromkeys(item_ids))
        placeholders = ",".join("?" for _ in deduped_ids)
        rows = await (
            await conn.execute(
                f"""
                SELECT item_id
                FROM filtered_items
                WHERE sub_id = ? AND item_id IN ({placeholders})
                """,
                (sub_id, *deduped_ids),
            )
        ).fetchall()
        return {str(row["item_id"]) for row in rows}

    async def list_items_by_snapshot(
        self,
        *,
        sub_id: int,
        snapshot_ts: int,
        limit: int = 30,
    ) -> tuple[list[NormalizedItem], int]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT item_id, title, url, publish_time, last_price
                FROM items
                WHERE sub_id = ? AND last_seen_at = ?
                ORDER BY
                    CASE WHEN last_price IS NULL THEN 1 ELSE 0 END ASC,
                    last_price ASC,
                    COALESCE(publish_time, 0) DESC,
                    item_id DESC
                LIMIT ?
                """,
                (sub_id, snapshot_ts, limit),
            )
        ).fetchall()
        count_row = await (
            await conn.execute(
                """
                SELECT COUNT(*) AS cnt
                FROM items
                WHERE sub_id = ? AND last_seen_at = ?
                """,
                (sub_id, snapshot_ts),
            )
        ).fetchone()
        total = int(count_row["cnt"]) if count_row else 0
        return [self._row_to_normalized_item(row) for row in rows], total

    async def insert_item(self, sub_id: int, item: NormalizedItem, now_ts: int) -> None:
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.execute(
                """
                INSERT INTO items (
                    sub_id, item_id, title, url, publish_time,
                    first_seen_at, last_seen_at, last_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sub_id, item_id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    publish_time = COALESCE(excluded.publish_time, items.publish_time),
                    last_seen_at = excluded.last_seen_at,
                    last_price = excluded.last_price
                """,
                (
                    sub_id,
                    item.item_id,
                    item.title,
                    item.url,
                    item.publish_time,
                    now_ts,
                    now_ts,
                    item.price,
                ),
            )
            await conn.commit()

    async def upsert_items_bulk(
        self,
        sub_id: int,
        items: list[NormalizedItem],
        now_ts: int,
    ) -> None:
        if not items:
            return
        conn = self._conn_or_raise()
        records = [
            (
                sub_id,
                item.item_id,
                item.title,
                item.url,
                item.publish_time,
                now_ts,
                now_ts,
                item.price,
            )
            for item in items
        ]
        async with self._write_lock:
            await conn.executemany(
                """
                INSERT INTO items (
                    sub_id, item_id, title, url, publish_time,
                    first_seen_at, last_seen_at, last_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sub_id, item_id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    publish_time = COALESCE(excluded.publish_time, items.publish_time),
                    last_seen_at = excluded.last_seen_at,
                    last_price = excluded.last_price
                """,
                records,
            )
            await conn.commit()

    async def upsert_filtered_items_bulk(
        self,
        sub_id: int,
        items: list[NormalizedItem],
        now_ts: int,
    ) -> None:
        if not items:
            return
        conn = self._conn_or_raise()
        records = [
            (
                sub_id,
                item.item_id,
                item.title,
                item.url,
                item.publish_time,
                now_ts,
                now_ts,
            )
            for item in items
        ]
        async with self._write_lock:
            await conn.executemany(
                """
                INSERT INTO filtered_items (
                    sub_id, item_id, title, url, publish_time,
                    first_filtered_at, last_filtered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sub_id, item_id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    publish_time = COALESCE(excluded.publish_time, filtered_items.publish_time),
                    last_filtered_at = excluded.last_filtered_at
                """,
                records,
            )
            await conn.commit()

    async def update_item(self, sub_id: int, item: NormalizedItem, now_ts: int) -> None:
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE items
                SET title = ?,
                    url = ?,
                    publish_time = COALESCE(?, publish_time),
                    last_seen_at = ?,
                    last_price = ?
                WHERE sub_id = ? AND item_id = ?
                """,
                (
                    item.title,
                    item.url,
                    item.publish_time,
                    now_ts,
                    item.price,
                    sub_id,
                    item.item_id,
                ),
            )
            await conn.commit()

    async def insert_price_history(
        self,
        sub_id: int,
        item_id: str,
        price: float,
        observed_at: int,
        source: str,
    ) -> None:
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.execute(
                """
                INSERT INTO price_history (
                    sub_id, item_id, price, observed_at, source
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (sub_id, item_id, price, observed_at, source),
            )
            await conn.commit()

    async def insert_price_history_bulk(
        self,
        rows: list[tuple[int, str, float, int, str]],
    ) -> None:
        if not rows:
            return
        conn = self._conn_or_raise()
        async with self._write_lock:
            await conn.executemany(
                """
                INSERT INTO price_history (
                    sub_id, item_id, price, observed_at, source
                ) VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            await conn.commit()

    async def notification_hash_exists(
        self,
        sub_id: int,
        item_id: str,
        event_type: str,
        payload_hash: str,
    ) -> bool:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT 1 FROM notifications
                WHERE sub_id = ? AND item_id = ? AND event_type = ? AND payload_hash = ?
                LIMIT 1
                """,
                (sub_id, item_id, event_type, payload_hash),
            )
        ).fetchone()
        return row is not None

    async def get_last_notification_sent_at(
        self,
        sub_id: int,
        item_id: str,
        event_type: str,
    ) -> int | None:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT sent_at FROM notifications
                WHERE sub_id = ? AND item_id = ? AND event_type = ?
                ORDER BY sent_at DESC
                LIMIT 1
                """,
                (sub_id, item_id, event_type),
            )
        ).fetchone()
        return int(row["sent_at"]) if row else None

    async def get_last_notification_sent_map(
        self,
        sub_id: int,
        item_ids: list[str],
        event_type: str,
    ) -> dict[str, int]:
        if not item_ids:
            return {}
        conn = self._conn_or_raise()
        deduped_ids = list(dict.fromkeys(item_ids))
        placeholders = ",".join("?" for _ in deduped_ids)
        rows = await (
            await conn.execute(
                f"""
                SELECT item_id, MAX(sent_at) AS last_sent_at
                FROM notifications
                WHERE sub_id = ? AND event_type = ? AND item_id IN ({placeholders})
                GROUP BY item_id
                """,
                (sub_id, event_type, *deduped_ids),
            )
        ).fetchall()
        return {
            str(row["item_id"]): int(row["last_sent_at"])
            for row in rows
            if row["last_sent_at"] is not None
        }

    async def insert_notification(
        self,
        *,
        sub_id: int,
        item_id: str,
        event_type: str,
        payload_hash: str,
        sent_at: int,
        meta: dict | None = None,
    ) -> None:
        conn = self._conn_or_raise()
        meta_json = json.dumps(meta, ensure_ascii=False) if meta is not None else None
        async with self._write_lock:
            await conn.execute(
                """
                INSERT OR IGNORE INTO notifications (
                    sub_id, item_id, event_type, payload_hash, sent_at, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sub_id, item_id, event_type, payload_hash, sent_at, meta_json),
            )
            await conn.commit()

    async def insert_notifications_bulk(
        self,
        rows: list[tuple[int, str, str, str, int, dict | None]],
    ) -> None:
        if not rows:
            return
        conn = self._conn_or_raise()
        records = [
            (
                sub_id,
                item_id,
                event_type,
                payload_hash,
                sent_at,
                json.dumps(meta, ensure_ascii=False) if meta is not None else None,
            )
            for sub_id, item_id, event_type, payload_hash, sent_at, meta in rows
        ]
        async with self._write_lock:
            await conn.executemany(
                """
                INSERT OR IGNORE INTO notifications (
                    sub_id, item_id, event_type, payload_hash, sent_at, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                records,
            )
            await conn.commit()

    async def count_enabled_subscriptions(self) -> int:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                "SELECT COUNT(*) AS cnt FROM subscriptions WHERE enabled = 1"
            )
        ).fetchone()
        return int(row["cnt"]) if row else 0

    async def count_subscriptions(self) -> int:
        conn = self._conn_or_raise()
        row = await (await conn.execute("SELECT COUNT(*) AS cnt FROM subscriptions")).fetchone()
        return int(row["cnt"]) if row else 0

    async def count_paused_subscriptions(self) -> int:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute("SELECT COUNT(*) AS cnt FROM subscriptions WHERE enabled = 0")
        ).fetchone()
        return int(row["cnt"]) if row else 0

    async def list_subscriptions_paginated(
        self,
        *,
        keyword: str = "",
        umo: str = "",
        enabled: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Subscription], int]:
        conn = self._conn_or_raise()
        where_parts: list[str] = []
        params: list[object] = []
        if keyword.strip():
            where_parts.append("keyword LIKE ?")
            params.append(f"%{keyword.strip()}%")
        if umo.strip():
            where_parts.append("umo LIKE ?")
            params.append(f"%{umo.strip()}%")
        if enabled is not None:
            where_parts.append("enabled = ?")
            params.append(1 if enabled else 0)
        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

        count_row = await (
            await conn.execute(
                f"SELECT COUNT(*) AS cnt FROM subscriptions {where_sql}",
                tuple(params),
            )
        ).fetchone()
        rows = await (
            await conn.execute(
                f"""
                SELECT * FROM subscriptions
                {where_sql}
                ORDER BY enabled DESC, COALESCE(next_run_at, 0) ASC, id DESC
                LIMIT ? OFFSET ?
                """,
                (*params, max(1, limit), max(0, offset)),
            )
        ).fetchall()
        total = int(count_row["cnt"]) if count_row else 0
        return [self._row_to_subscription(row) for row in rows], total

    async def update_subscription(
        self,
        *,
        sub_id: int,
        umo: str,
        keyword: str,
        interval_sec: int,
        pages: int,
        drop_abs: float,
        drop_pct: float,
        new_window_sec: int,
        cooldown_sec: int,
    ) -> Subscription | None:
        conn = self._conn_or_raise()
        now_ts = int(time.time())
        async with self._write_lock:
            await conn.execute(
                """
                UPDATE subscriptions
                SET umo = ?,
                    keyword = ?,
                    interval_sec = ?,
                    pages = ?,
                    drop_abs = ?,
                    drop_pct = ?,
                    new_window_sec = ?,
                    cooldown_sec = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    umo,
                    keyword,
                    interval_sec,
                    pages,
                    drop_abs,
                    drop_pct,
                    new_window_sec,
                    cooldown_sec,
                    now_ts,
                    sub_id,
                ),
            )
            await conn.commit()
        return await self.get_subscription_by_id(sub_id)

    async def delete_subscription_by_id(self, sub_id: int) -> bool:
        conn = self._conn_or_raise()
        async with self._write_lock:
            cursor = await conn.execute(
                "DELETE FROM subscriptions WHERE id = ?",
                (sub_id,),
            )
            await conn.commit()
        return cursor.rowcount > 0

    async def list_item_summaries(
        self,
        *,
        search: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ItemSummary], int]:
        conn = self._conn_or_raise()
        text = search.strip()
        where_sql = ""
        params: list[object] = []
        if text:
            where_sql = """
                WHERE item_id LIKE ?
                   OR title LIKE ?
                   OR url LIKE ?
            """
            like = f"%{text}%"
            params.extend([like, like, like])

        count_row = await (
            await conn.execute(
                f"""
                SELECT COUNT(*) AS cnt
                FROM (
                    SELECT item_id
                    FROM items
                    {where_sql}
                    GROUP BY item_id
                ) grouped
                """,
                tuple(params),
            )
        ).fetchone()
        rows = await (
            await conn.execute(
                f"""
                SELECT
                    base.item_id AS item_id,
                    (
                        SELECT i2.title
                        FROM items i2
                        WHERE i2.item_id = base.item_id
                        ORDER BY i2.last_seen_at DESC, i2.id DESC
                        LIMIT 1
                    ) AS title,
                    (
                        SELECT i2.url
                        FROM items i2
                        WHERE i2.item_id = base.item_id
                        ORDER BY i2.last_seen_at DESC, i2.id DESC
                        LIMIT 1
                    ) AS url,
                    COALESCE(
                        (
                            SELECT i2.last_price
                            FROM items i2
                            WHERE i2.item_id = base.item_id
                            ORDER BY i2.last_seen_at DESC, i2.id DESC
                            LIMIT 1
                        ),
                        0
                    ) AS price,
                    (
                        SELECT i2.publish_time
                        FROM items i2
                        WHERE i2.item_id = base.item_id
                        ORDER BY i2.last_seen_at DESC, i2.id DESC
                        LIMIT 1
                    ) AS publish_time,
                    MIN(base.first_seen_at) AS first_seen_at,
                    MAX(base.last_seen_at) AS last_seen_at,
                    COUNT(DISTINCT base.sub_id) AS subscription_count,
                    (
                        SELECT n.event_type
                        FROM notifications n
                        WHERE n.item_id = base.item_id
                        ORDER BY n.sent_at DESC, n.id DESC
                        LIMIT 1
                    ) AS latest_event_type
                FROM items base
                {where_sql}
                GROUP BY base.item_id
                ORDER BY MAX(base.last_seen_at) DESC, base.item_id DESC
                LIMIT ? OFFSET ?
                """,
                (*params, max(1, limit), max(0, offset)),
            )
        ).fetchall()
        total = int(count_row["cnt"]) if count_row else 0
        items = [
            ItemSummary(
                item_id=str(row["item_id"]),
                title=str(row["title"]),
                url=str(row["url"]),
                price=float(row["price"] or 0.0),
                publish_time=row["publish_time"],
                first_seen_at=int(row["first_seen_at"]),
                last_seen_at=int(row["last_seen_at"]),
                subscription_count=int(row["subscription_count"]),
                latest_event_type=row["latest_event_type"],
            )
            for row in rows
        ]
        return items, total

    async def get_item_summary(self, item_id: str) -> ItemSummary | None:
        items, _ = await self.list_item_summaries(search=item_id, limit=200, offset=0)
        for item in items:
            if item.item_id == item_id:
                return item
        return None

    async def list_related_subscriptions_for_item(
        self,
        item_id: str,
    ) -> list[RelatedSubscription]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    s.id AS sub_id,
                    s.keyword AS keyword,
                    s.umo AS umo,
                    s.enabled AS enabled,
                    s.paused_reason AS paused_reason,
                    i.last_seen_at AS last_seen_at,
                    i.last_price AS last_price
                FROM items i
                JOIN subscriptions s ON s.id = i.sub_id
                WHERE i.item_id = ?
                ORDER BY i.last_seen_at DESC, s.id DESC
                """,
                (item_id,),
            )
        ).fetchall()
        return [
            RelatedSubscription(
                sub_id=int(row["sub_id"]),
                keyword=str(row["keyword"]),
                umo=str(row["umo"]),
                enabled=bool(row["enabled"]),
                paused_reason=row["paused_reason"],
                last_seen_at=int(row["last_seen_at"]),
                last_price=float(row["last_price"]) if row["last_price"] is not None else None,
            )
            for row in rows
        ]

    async def list_price_history_for_item(
        self,
        item_id: str,
        *,
        limit: int = 120,
    ) -> list[PriceHistoryPoint]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    p.sub_id AS sub_id,
                    s.keyword AS keyword,
                    s.umo AS umo,
                    p.item_id AS item_id,
                    p.price AS price,
                    p.observed_at AS observed_at,
                    p.source AS source
                FROM price_history p
                JOIN subscriptions s ON s.id = p.sub_id
                WHERE p.item_id = ?
                ORDER BY p.observed_at DESC, p.id DESC
                LIMIT ?
                """,
                (item_id, max(1, limit)),
            )
        ).fetchall()
        return [
            PriceHistoryPoint(
                sub_id=int(row["sub_id"]),
                keyword=str(row["keyword"]),
                umo=str(row["umo"]),
                item_id=str(row["item_id"]),
                price=float(row["price"]),
                observed_at=int(row["observed_at"]),
                source=str(row["source"] or ""),
            )
            for row in rows
        ]

    async def list_notifications_for_item(
        self,
        item_id: str,
        *,
        limit: int = 50,
    ) -> list[NotificationRecord]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    n.sub_id AS sub_id,
                    s.keyword AS keyword,
                    s.umo AS umo,
                    n.item_id AS item_id,
                    n.event_type AS event_type,
                    n.sent_at AS sent_at,
                    n.meta_json AS meta_json
                FROM notifications n
                JOIN subscriptions s ON s.id = n.sub_id
                WHERE n.item_id = ?
                ORDER BY n.sent_at DESC, n.id DESC
                LIMIT ?
                """,
                (item_id, max(1, limit)),
            )
        ).fetchall()
        results: list[NotificationRecord] = []
        for row in rows:
            meta_json = row["meta_json"]
            meta = None
            if meta_json:
                try:
                    meta = json.loads(meta_json)
                except json.JSONDecodeError:
                    meta = {"raw": meta_json}
            results.append(
                NotificationRecord(
                    sub_id=int(row["sub_id"]),
                    keyword=str(row["keyword"]),
                    umo=str(row["umo"]),
                    item_id=str(row["item_id"]),
                    event_type=str(row["event_type"]),
                    sent_at=int(row["sent_at"]),
                    meta=meta,
                )
            )
        return results

    async def list_fetch_runs(
        self,
        *,
        status: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[FetchRunSummary], int]:
        conn = self._conn_or_raise()
        where_sql = ""
        params: list[object] = []
        if status.strip():
            where_sql = "WHERE f.status = ?"
            params.append(status.strip())
        count_row = await (
            await conn.execute(
                f"""
                SELECT COUNT(*) AS cnt
                FROM fetch_runs f
                {where_sql}
                """,
                tuple(params),
            )
        ).fetchone()
        rows = await (
            await conn.execute(
                f"""
                SELECT
                    f.id AS id,
                    f.sub_id AS sub_id,
                    s.keyword AS keyword,
                    s.umo AS umo,
                    f.started_at AS started_at,
                    f.finished_at AS finished_at,
                    f.status AS status,
                    f.err_type AS err_type,
                    f.err_msg AS err_msg,
                    f.items_count AS items_count
                FROM fetch_runs f
                JOIN subscriptions s ON s.id = f.sub_id
                {where_sql}
                ORDER BY f.started_at DESC, f.id DESC
                LIMIT ? OFFSET ?
                """,
                (*params, max(1, limit), max(0, offset)),
            )
        ).fetchall()
        total = int(count_row["cnt"]) if count_row else 0
        results = [
            FetchRunSummary(
                id=int(row["id"]),
                sub_id=int(row["sub_id"]),
                keyword=str(row["keyword"]),
                umo=str(row["umo"]),
                started_at=int(row["started_at"]),
                finished_at=int(row["finished_at"]) if row["finished_at"] is not None else None,
                status=str(row["status"]),
                err_type=row["err_type"],
                err_msg=row["err_msg"],
                items_count=int(row["items_count"]),
            )
            for row in rows
        ]
        return results, total

    async def list_fetch_runs_for_item(
        self,
        item_id: str,
        *,
        limit: int = 30,
    ) -> list[FetchRunSummary]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    f.id AS id,
                    f.sub_id AS sub_id,
                    s.keyword AS keyword,
                    s.umo AS umo,
                    f.started_at AS started_at,
                    f.finished_at AS finished_at,
                    f.status AS status,
                    f.err_type AS err_type,
                    f.err_msg AS err_msg,
                    f.items_count AS items_count
                FROM fetch_runs f
                JOIN subscriptions s ON s.id = f.sub_id
                WHERE f.sub_id IN (
                    SELECT DISTINCT sub_id
                    FROM items
                    WHERE item_id = ?
                )
                ORDER BY f.started_at DESC, f.id DESC
                LIMIT ?
                """,
                (item_id, max(1, limit)),
            )
        ).fetchall()
        return [
            FetchRunSummary(
                id=int(row["id"]),
                sub_id=int(row["sub_id"]),
                keyword=str(row["keyword"]),
                umo=str(row["umo"]),
                started_at=int(row["started_at"]),
                finished_at=int(row["finished_at"]) if row["finished_at"] is not None else None,
                status=str(row["status"]),
                err_type=row["err_type"],
                err_msg=row["err_msg"],
                items_count=int(row["items_count"]),
            )
            for row in rows
        ]

    async def get_recent_run_stats(
        self,
        *,
        since_ts: int,
    ) -> tuple[int, int]:
        conn = self._conn_or_raise()
        row = await (
            await conn.execute(
                """
                SELECT
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
                    SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) AS failed_count
                FROM fetch_runs
                WHERE started_at >= ?
                """,
                (since_ts,),
            )
        ).fetchone()
        if row is None:
            return 0, 0
        return int(row["success_count"] or 0), int(row["failed_count"] or 0)

    async def list_notification_trends(
        self,
        *,
        since_ts: int,
        limit_days: int = 7,
    ) -> list[TrendBucket]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    date(sent_at, 'unixepoch', 'localtime') AS bucket_day,
                    SUM(CASE WHEN event_type = 'NEW' THEN 1 ELSE 0 END) AS new_count,
                    SUM(CASE WHEN event_type = 'PRICE_DROP' THEN 1 ELSE 0 END) AS price_drop_count
                FROM notifications
                WHERE sent_at >= ?
                GROUP BY bucket_day
                ORDER BY bucket_day DESC
                LIMIT ?
                """,
                (since_ts, max(1, limit_days)),
            )
        ).fetchall()
        return [
            TrendBucket(
                day=str(row["bucket_day"]),
                new_count=int(row["new_count"] or 0),
                price_drop_count=int(row["price_drop_count"] or 0),
            )
            for row in reversed(rows)
        ]

    async def list_recent_alerts(self, *, limit: int = 8) -> list[OverviewAlert]:
        conn = self._conn_or_raise()
        rows = await (
            await conn.execute(
                """
                SELECT
                    s.id AS sub_id,
                    s.keyword AS keyword,
                    COALESCE(f.err_msg, s.paused_reason, '') AS message,
                    COALESCE(f.finished_at, s.last_run_at, s.next_run_at) AS occurred_at,
                    COALESCE(f.err_type, s.paused_reason, 'UNKNOWN') AS err_type
                FROM subscriptions s
                LEFT JOIN fetch_runs f
                    ON f.id = (
                        SELECT f2.id
                        FROM fetch_runs f2
                        WHERE f2.sub_id = s.id AND f2.status != 'success'
                        ORDER BY COALESCE(f2.finished_at, f2.started_at) DESC, f2.id DESC
                        LIMIT 1
                    )
                WHERE s.paused_reason IS NOT NULL
                   OR f.id IS NOT NULL
                ORDER BY COALESCE(f.finished_at, s.last_run_at, s.next_run_at, 0) DESC, s.id DESC
                LIMIT ?
                """,
                (max(1, limit),),
            )
        ).fetchall()
        alerts: list[OverviewAlert] = []
        for row in rows:
            err_type = str(row["err_type"] or "UNKNOWN")
            level = "error" if err_type in {"AUTH_REQUIRED", "CAPTCHA", "DEPENDENCY_MISSING"} else "warning"
            alerts.append(
                OverviewAlert(
                    level=level,
                    keyword=str(row["keyword"]),
                    message=str(row["message"] or err_type),
                    occurred_at=int(row["occurred_at"]) if row["occurred_at"] is not None else None,
                    subscription_id=int(row["sub_id"]),
                )
            )
        return alerts
