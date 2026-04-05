from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AggregatorSettings:
    profile_url: str
    activity_url: str
    status_url: str
    timeout_seconds: float
    retries: int
    host: str = "0.0.0.0"
    port: int = 8000

    @classmethod
    def from_env(cls) -> "AggregatorSettings":
        return cls(
            profile_url=_required_env("AGGREGATOR_PROFILE_URL"),
            activity_url=_required_env("AGGREGATOR_ACTIVITY_URL"),
            status_url=_required_env("AGGREGATOR_STATUS_URL"),
            timeout_seconds=float(os.environ.get("AGGREGATOR_TIMEOUT_SECONDS", "0.5")),
            retries=int(os.environ.get("AGGREGATOR_RETRIES", "2")),
            host=os.environ.get("AGGREGATOR_HOST", "0.0.0.0"),
            port=int(os.environ.get("AGGREGATOR_PORT", "8000")),
        )


@dataclass(frozen=True)
class MockSettings:
    host: str = "0.0.0.0"
    port: int = 9000

    @classmethod
    def from_env(cls) -> "MockSettings":
        return cls(
            host=os.environ.get("MOCK_API_HOST", "0.0.0.0"),
            port=int(os.environ.get("MOCK_API_PORT", "9000")),
        )


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"{name} is required")
    return value
