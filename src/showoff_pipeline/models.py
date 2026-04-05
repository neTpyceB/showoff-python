from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ProcessingMode(StrEnum):
    STREAM = "stream"
    BATCH = "batch"


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class HealthResponse(BaseModel):
    status: str


class PipelineRunResponse(BaseModel):
    run_id: str
    source_name: str
    mode: ProcessingMode
    status: RunStatus
    processed_rows: int
    stored_rows: int
    total_amount_cents: int
    started_at: str
    finished_at: str | None
    error_message: str | None


class MonitoringResponse(BaseModel):
    runs_total: int
    successful_runs: int
    failed_runs: int
    stored_rows_total: int
    total_amount_cents: int
    latest_finished_at: str | None
