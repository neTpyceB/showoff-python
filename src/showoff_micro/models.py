from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"


class HealthResponse(BaseModel):
    status: str


class DiscoveryResponse(BaseModel):
    service: str
    auth_url: str
    data_url: str
    worker_service: str


class TokenRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)


class TokenResponse(BaseModel):
    access_token: str


class ValidationResponse(BaseModel):
    user_id: str


class JobCreateRequest(BaseModel):
    payload: str = Field(min_length=1, max_length=2000)


class JobResponse(BaseModel):
    id: str
    owner_user_id: str
    payload: str
    status: JobStatus
    result: str | None
    created_at: str
    updated_at: str


class JobCompletionRequest(BaseModel):
    result: str
