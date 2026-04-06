from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Engine(StrEnum):
    AUTO = "auto"
    PYTHON = "python"
    CYTHON = "cython"


class HealthResponse(BaseModel):
    status: str
    cache: str
    cython_available: bool


class PrimeSumRequest(BaseModel):
    upper_bound: int
    workers: int | None = None
    engine: Engine | None = None


class ProfileResponse(BaseModel):
    cpu_seconds: float
    peak_memory_bytes: int
    top_function: str


class PrimeSumResponse(BaseModel):
    upper_bound: int
    workers: int
    engine_requested: Engine
    engine_used: Engine
    cached: bool
    prime_sum: int
    profile: ProfileResponse
