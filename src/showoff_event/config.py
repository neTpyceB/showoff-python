from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv


@dataclass(frozen=True, slots=True)
class Settings:
    platform_host: str
    platform_port: int
    feed_host: str
    feed_port: int
    feed_db_path: str
    notification_host: str
    notification_port: int
    notification_db_path: str
    audit_host: str
    audit_port: int
    audit_db_path: str
    redis_url: str
    event_channel: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            platform_host=getenv("EVENT_PLATFORM_HOST", "0.0.0.0"),
            platform_port=int(getenv("EVENT_PLATFORM_PORT", "8000")),
            feed_host=getenv("EVENT_FEED_HOST", "0.0.0.0"),
            feed_port=int(getenv("EVENT_FEED_PORT", "8001")),
            feed_db_path=getenv("EVENT_FEED_DB_PATH", "data/feed.db"),
            notification_host=getenv("EVENT_NOTIFICATION_HOST", "0.0.0.0"),
            notification_port=int(getenv("EVENT_NOTIFICATION_PORT", "8002")),
            notification_db_path=getenv(
                "EVENT_NOTIFICATION_DB_PATH",
                "data/notifications.db",
            ),
            audit_host=getenv("EVENT_AUDIT_HOST", "0.0.0.0"),
            audit_port=int(getenv("EVENT_AUDIT_PORT", "8003")),
            audit_db_path=getenv("EVENT_AUDIT_DB_PATH", "data/audit.db"),
            redis_url=getenv("EVENT_REDIS_URL", "redis://redis:6379/0"),
            event_channel=getenv("EVENT_CHANNEL", "platform.events"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
