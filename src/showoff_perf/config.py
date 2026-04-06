from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    api_host: str
    api_port: int
    redis_url: str
    cache_ttl_seconds: int
    default_workers: int
    default_engine: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_host=getenv("PERF_API_HOST", "0.0.0.0"),
            api_port=int(getenv("PERF_API_PORT", "8000")),
            redis_url=getenv("PERF_REDIS_URL", "redis://localhost:6379/0"),
            cache_ttl_seconds=int(getenv("PERF_CACHE_TTL_SECONDS", "300")),
            default_workers=int(getenv("PERF_DEFAULT_WORKERS", "2")),
            default_engine=getenv("PERF_DEFAULT_ENGINE", "auto"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
