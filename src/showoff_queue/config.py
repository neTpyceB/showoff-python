from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class QueueSettings:
    broker_url: str
    result_backend: str
    redis_url: str
    heartbeat_key: str
    heartbeat_seconds: int
    retry_max: int
    host: str = "0.0.0.0"
    port: int = 8000

    @classmethod
    def from_env(cls) -> "QueueSettings":
        return cls(
            broker_url=os.environ.get("QUEUE_BROKER_URL", "redis://redis:6379/0"),
            result_backend=os.environ.get(
                "QUEUE_RESULT_BACKEND",
                "redis://redis:6379/1",
            ),
            redis_url=os.environ.get("QUEUE_REDIS_URL", "redis://redis:6379/2"),
            heartbeat_key=os.environ.get("QUEUE_HEARTBEAT_KEY", "queue:heartbeat"),
            heartbeat_seconds=int(os.environ.get("QUEUE_HEARTBEAT_SECONDS", "3")),
            retry_max=int(os.environ.get("QUEUE_RETRY_MAX", "2")),
            host=os.environ.get("QUEUE_API_HOST", "0.0.0.0"),
            port=int(os.environ.get("QUEUE_API_PORT", "8000")),
        )
