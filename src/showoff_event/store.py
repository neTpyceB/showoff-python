from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import AuditEntry, EventEnvelope, FeedEntry, NotificationEntry

CREATE_FEED_TABLE = """
CREATE TABLE IF NOT EXISTS feed_entries (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

CREATE_NOTIFICATION_TABLE = """
CREATE TABLE IF NOT EXISTS notifications (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

CREATE_AUDIT_TABLE = """
CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class FeedStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(CREATE_FEED_TABLE)

    def add_event(self, event: EventEnvelope) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO feed_entries (
                    event_id, user_id, title, detail, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.user_id,
                    event.title,
                    event.detail,
                    event.created_at,
                ),
            )

    def list_entries(self, user_id: str) -> list[FeedEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, title, detail, created_at
                FROM feed_entries
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [FeedEntry.model_validate(dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection


class NotificationStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(CREATE_NOTIFICATION_TABLE)

    def add_event(self, event: EventEnvelope) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO notifications (
                    event_id, user_id, message, created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.user_id,
                    f"Activity recorded: {event.title}",
                    event.created_at,
                ),
            )

    def list_entries(self, user_id: str) -> list[NotificationEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, message, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [NotificationEntry.model_validate(dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection


class AuditStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(CREATE_AUDIT_TABLE)

    def add_event(self, event: EventEnvelope) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO audit_events (
                    event_id, type, user_id, title, detail, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.type.value,
                    event.user_id,
                    event.title,
                    event.detail,
                    event.created_at,
                ),
            )

    def list_entries(self) -> list[AuditEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, type, user_id, title, detail, created_at
                FROM audit_events
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [AuditEntry.model_validate(dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection
