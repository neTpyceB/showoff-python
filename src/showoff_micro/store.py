from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .models import JobStatus

CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    owner_user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


class JobStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def ensure_schema(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(CREATE_JOBS_TABLE)

    def create_job(self, owner_user_id: str, payload: str) -> dict[str, str]:
        job_id = str(uuid4())
        created_at = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, owner_user_id, payload, status, result, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, NULL, ?, ?)
                """,
                (
                    job_id,
                    owner_user_id,
                    payload,
                    JobStatus.QUEUED.value,
                    created_at,
                    created_at,
                ),
            )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id, owner_user_id, payload, status, result, created_at, updated_at
                FROM jobs
                WHERE id = ?
                """,
                (job_id,),
            ).fetchone()
        return None if row is None else dict(row)

    def claim_next_job(self) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM jobs
                WHERE status = ?
                ORDER BY created_at
                LIMIT 1
                """,
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if row is None:
                return None
            updated_at = _now()
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (JobStatus.PROCESSING.value, updated_at, row["id"]),
            )
        return self.get_job(row["id"])

    def complete_job(self, job_id: str, result: str) -> dict[str, str]:
        updated_at = _now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE jobs
                SET status = ?, result = ?, updated_at = ?
                WHERE id = ?
                """,
                (JobStatus.DONE.value, result, updated_at, job_id),
            )
        return self.get_job(job_id)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection


def _now() -> str:
    return datetime.now(UTC).isoformat()
