from __future__ import annotations

from showoff_event.config import Settings, get_settings


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("EVENT_PLATFORM_HOST", "127.0.0.1")
    monkeypatch.setenv("EVENT_PLATFORM_PORT", "9000")
    monkeypatch.setenv("EVENT_FEED_HOST", "127.0.0.1")
    monkeypatch.setenv("EVENT_FEED_PORT", "9001")
    monkeypatch.setenv("EVENT_FEED_DB_PATH", "/tmp/feed.db")
    monkeypatch.setenv("EVENT_NOTIFICATION_HOST", "127.0.0.1")
    monkeypatch.setenv("EVENT_NOTIFICATION_PORT", "9002")
    monkeypatch.setenv("EVENT_NOTIFICATION_DB_PATH", "/tmp/notifications.db")
    monkeypatch.setenv("EVENT_AUDIT_HOST", "127.0.0.1")
    monkeypatch.setenv("EVENT_AUDIT_PORT", "9003")
    monkeypatch.setenv("EVENT_AUDIT_DB_PATH", "/tmp/audit.db")
    monkeypatch.setenv("EVENT_REDIS_URL", "redis://localhost:6380/0")
    monkeypatch.setenv("EVENT_CHANNEL", "custom.events")

    assert Settings.from_env() == Settings(
        platform_host="127.0.0.1",
        platform_port=9000,
        feed_host="127.0.0.1",
        feed_port=9001,
        feed_db_path="/tmp/feed.db",
        notification_host="127.0.0.1",
        notification_port=9002,
        notification_db_path="/tmp/notifications.db",
        audit_host="127.0.0.1",
        audit_port=9003,
        audit_db_path="/tmp/audit.db",
        redis_url="redis://localhost:6380/0",
        event_channel="custom.events",
    )


def test_get_settings_is_cached(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("EVENT_FEED_DB_PATH", "/tmp/first.db")

    first = get_settings()
    monkeypatch.setenv("EVENT_FEED_DB_PATH", "/tmp/second.db")
    second = get_settings()

    assert first is second
    assert second.feed_db_path == "/tmp/first.db"
    get_settings.cache_clear()
