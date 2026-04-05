from __future__ import annotations

import csv
import io
import logging
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from .config import Settings
from .models import MonitoringResponse, PipelineRunResponse, ProcessingMode, RunStatus

REQUIRED_COLUMNS = ("timestamp", "account", "amount")
CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    processed_rows INTEGER NOT NULL DEFAULT 0,
    total_amount_cents INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    error_message TEXT
)
"""
CREATE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS etl_records (
    run_id TEXT NOT NULL,
    event_at TEXT NOT NULL,
    event_date TEXT NOT NULL,
    account TEXT NOT NULL,
    amount_cents INTEGER NOT NULL
)
"""
INSERT_RECORD = """
INSERT INTO etl_records (run_id, event_at, event_date, account, amount_cents)
VALUES (?, ?, ?, ?, ?)
"""
SELECT_RUN = """
SELECT
    pipeline_runs.id AS run_id,
    pipeline_runs.source_name,
    pipeline_runs.mode,
    pipeline_runs.status,
    pipeline_runs.processed_rows,
    pipeline_runs.total_amount_cents,
    pipeline_runs.started_at,
    pipeline_runs.finished_at,
    pipeline_runs.error_message,
    COALESCE(
        (SELECT COUNT(*) FROM etl_records WHERE etl_records.run_id = pipeline_runs.id),
        0
    ) AS stored_rows
FROM pipeline_runs
WHERE pipeline_runs.id = ?
"""
SELECT_MONITORING = """
SELECT
    COUNT(*) AS runs_total,
    COALESCE(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END), 0) AS successful_runs,
    COALESCE(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END), 0) AS failed_runs,
    COALESCE((SELECT COUNT(*) FROM etl_records), 0) AS stored_rows_total,
    COALESCE(SUM(total_amount_cents), 0) AS total_amount_cents,
    MAX(finished_at) AS latest_finished_at
FROM pipeline_runs
"""


class PipelineInputError(ValueError):
    """Raised when pipeline input is invalid."""


@dataclass(frozen=True, slots=True)
class TransformedRecord:
    run_id: str
    event_at: str
    event_date: str
    account: str
    amount_cents: int


class PipelineService:
    def __init__(
        self,
        settings: Settings,
        logger: logging.Logger | None = None,
    ) -> None:
        self._settings = settings
        self._logger = logger or logging.getLogger("showoff_pipeline")

    def ensure_schema(self) -> None:
        Path(self._settings.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(CREATE_RUNS_TABLE)
            connection.execute(CREATE_RECORDS_TABLE)

    def run(
        self,
        file_object: BinaryIO,
        source_name: str,
        mode: ProcessingMode,
    ) -> PipelineRunResponse:
        run_id = str(uuid4())
        started_at = _now()
        self._logger.info(
            "pipeline run started",
            extra={"run_id": run_id, "mode": mode},
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO pipeline_runs (
                    id,
                    source_name,
                    mode,
                    status,
                    processed_rows,
                    total_amount_cents,
                    started_at,
                    finished_at,
                    error_message
                ) VALUES (?, ?, ?, ?, 0, 0, ?, NULL, NULL)
                """,
                (run_id, source_name, mode.value, RunStatus.RUNNING.value, started_at),
            )
            connection.commit()
            try:
                processed_rows, total_amount_cents = self._process(
                    connection=connection,
                    file_object=file_object,
                    run_id=run_id,
                    mode=mode,
                )
            except PipelineInputError as error:
                finished_at = _now()
                connection.execute(
                    """
                    UPDATE pipeline_runs
                    SET status = ?, finished_at = ?, error_message = ?
                    WHERE id = ?
                    """,
                    (RunStatus.FAILED.value, finished_at, str(error), run_id),
                )
                connection.commit()
                self._logger.info(
                    "pipeline run failed",
                    extra={"run_id": run_id, "error": str(error)},
                )
                raise

            finished_at = _now()
            connection.execute(
                """
                UPDATE pipeline_runs
                SET status = ?,
                    processed_rows = ?,
                    total_amount_cents = ?,
                    finished_at = ?
                WHERE id = ?
                """,
                (
                    RunStatus.SUCCESS.value,
                    processed_rows,
                    total_amount_cents,
                    finished_at,
                    run_id,
                ),
            )
            connection.commit()
        self._logger.info(
            "pipeline run finished",
            extra={"run_id": run_id, "processed_rows": processed_rows},
        )
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> PipelineRunResponse:
        with self._connect() as connection:
            row = connection.execute(SELECT_RUN, (run_id,)).fetchone()
        if row is None:
            raise KeyError(run_id)
        return PipelineRunResponse.model_validate(dict(row))

    def get_monitoring(self) -> MonitoringResponse:
        with self._connect() as connection:
            row = connection.execute(SELECT_MONITORING).fetchone()
        return MonitoringResponse.model_validate(dict(row))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._settings.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _process(
        self,
        connection: sqlite3.Connection,
        file_object: BinaryIO,
        run_id: str,
        mode: ProcessingMode,
    ) -> tuple[int, int]:
        with connection:
            if mode is ProcessingMode.BATCH:
                return self._process_batch(connection, file_object, run_id)
            return self._process_stream(connection, file_object, run_id)

    def _process_batch(
        self,
        connection: sqlite3.Connection,
        file_object: BinaryIO,
        run_id: str,
    ) -> tuple[int, int]:
        rows = [
            self._transform_row(run_id, row) for row in self._iter_rows(file_object)
        ]
        self._insert_records(connection, rows)
        total_amount_cents = sum(row.amount_cents for row in rows)
        return len(rows), total_amount_cents

    def _process_stream(
        self,
        connection: sqlite3.Connection,
        file_object: BinaryIO,
        run_id: str,
    ) -> tuple[int, int]:
        processed_rows = 0
        total_amount_cents = 0
        buffer: list[TransformedRecord] = []
        for row in self._iter_rows(file_object):
            record = self._transform_row(run_id, row)
            buffer.append(record)
            processed_rows += 1
            total_amount_cents += record.amount_cents
            if len(buffer) == self._settings.insert_batch_size:
                self._insert_records(connection, buffer)
                buffer.clear()
        self._insert_records(connection, buffer)
        return processed_rows, total_amount_cents

    def _iter_rows(self, file_object: BinaryIO) -> Iterator[dict[str, str]]:
        file_object.seek(0)
        text_stream = io.TextIOWrapper(file_object, encoding="utf-8", newline="")
        try:
            reader = csv.DictReader(text_stream)
            if reader.fieldnames is None:
                raise PipelineInputError("CSV header is required")
            if tuple(reader.fieldnames) != REQUIRED_COLUMNS:
                raise PipelineInputError(
                    "CSV columns must be exactly: timestamp,account,amount"
                )
            for row in reader:
                yield row
        finally:
            text_stream.detach()

    def _transform_row(
        self,
        run_id: str,
        row: dict[str, str],
    ) -> TransformedRecord:
        try:
            event_at = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            amount_cents = int((Decimal(row["amount"]) * 100).quantize(Decimal("1")))
        except Exception as error:
            raise PipelineInputError(str(error)) from error
        account = row["account"].strip().lower()
        return TransformedRecord(
            run_id=run_id,
            event_at=event_at.isoformat(),
            event_date=event_at.date().isoformat(),
            account=account,
            amount_cents=amount_cents,
        )

    def _insert_records(
        self,
        connection: sqlite3.Connection,
        rows: list[TransformedRecord],
    ) -> None:
        if not rows:
            return
        connection.executemany(
            INSERT_RECORD,
            [
                (
                    row.run_id,
                    row.event_at,
                    row.event_date,
                    row.account,
                    row.amount_cents,
                )
                for row in rows
            ],
        )


def _now() -> str:
    return datetime.now(UTC).isoformat()
