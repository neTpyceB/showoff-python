from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    api_host: str
    api_port: int
    db_path: str
    insert_batch_size: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_host=getenv("PIPELINE_API_HOST", "0.0.0.0"),
            api_port=int(getenv("PIPELINE_API_PORT", "8000")),
            db_path=getenv("PIPELINE_DB_PATH", "data/pipeline.db"),
            insert_batch_size=int(getenv("PIPELINE_INSERT_BATCH_SIZE", "500")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
