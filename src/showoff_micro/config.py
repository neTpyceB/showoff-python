from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    auth_host: str
    auth_port: int
    data_host: str
    data_port: int
    data_db_path: str
    auth_service_url: str
    data_service_url: str
    worker_service_name: str
    worker_poll_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            auth_host=getenv("MICRO_AUTH_HOST", "0.0.0.0"),
            auth_port=int(getenv("MICRO_AUTH_PORT", "8000")),
            data_host=getenv("MICRO_DATA_HOST", "0.0.0.0"),
            data_port=int(getenv("MICRO_DATA_PORT", "8000")),
            data_db_path=getenv("MICRO_DATA_DB_PATH", "data/micro.db"),
            auth_service_url=getenv("MICRO_AUTH_SERVICE_URL", "http://auth:8000"),
            data_service_url=getenv("MICRO_DATA_SERVICE_URL", "http://data:8000"),
            worker_service_name=getenv("MICRO_WORKER_SERVICE_NAME", "worker"),
            worker_poll_seconds=int(getenv("MICRO_WORKER_POLL_SECONDS", "1")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
