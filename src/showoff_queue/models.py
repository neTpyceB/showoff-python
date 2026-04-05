from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, StringConstraints

ReportId = Annotated[str, StringConstraints(min_length=1, max_length=64)]
Content = Annotated[str, StringConstraints(min_length=1, max_length=5000)]


class ReportJobRequest(BaseModel):
    report_id: ReportId
    content: Content


class ReportResult(BaseModel):
    report_id: ReportId
    line_count: int
    word_count: int
    checksum: str


class JobSubmission(BaseModel):
    task_id: str


class JobStatus(BaseModel):
    task_id: str
    status: str
    result: ReportResult | None = None


class HeartbeatStatus(BaseModel):
    last_run: str | None = None
