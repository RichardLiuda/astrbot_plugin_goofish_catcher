from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import aiosqlite

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
