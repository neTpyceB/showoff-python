from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    api_token: str
    host: str = "0.0.0.0"
    port: int = 8000

    @classmethod
    def from_env(cls) -> "Settings":
        api_token = os.environ.get("APP_API_TOKEN")
        if api_token is None:
            raise RuntimeError("APP_API_TOKEN is required")
        return cls(
            database_path=Path(os.environ.get("APP_DATABASE_PATH", "data/notes.db")),
            api_token=api_token,
            host=os.environ.get("APP_HOST", "0.0.0.0"),
            port=int(os.environ.get("APP_PORT", "8000")),
        )
