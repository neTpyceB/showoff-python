from __future__ import annotations

from showoff_event import audit_main, feed_main, notification_main, platform_main
from showoff_event.config import Settings


def capture_run(captured: dict[str, object]):
    def runner(app, host, port) -> None:
        captured.update({"app": app, "host": host, "port": port})

    return runner


def make_settings() -> Settings:
    return Settings(
        platform_host="0.0.0.0",
        platform_port=8000,
        feed_host="0.0.0.0",
        feed_port=8001,
        feed_db_path="/tmp/feed.db",
        notification_host="0.0.0.0",
        notification_port=8002,
        notification_db_path="/tmp/notifications.db",
        audit_host="0.0.0.0",
        audit_port=8003,
        audit_db_path="/tmp/audit.db",
        redis_url="redis://redis:6379/0",
        event_channel="platform.events",
    )


def test_platform_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(platform_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        platform_main.uvicorn,
        "run",
        capture_run(captured),
    )

    platform_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8000
    assert captured["app"].title == "Platform API"


def test_feed_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(feed_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        feed_main.uvicorn,
        "run",
        capture_run(captured),
    )

    feed_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8001
    assert captured["app"].title == "Feed Service"


def test_notification_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(notification_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        notification_main.uvicorn,
        "run",
        capture_run(captured),
    )

    notification_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8002
    assert captured["app"].title == "Notification Service"


def test_audit_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(audit_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        audit_main.uvicorn,
        "run",
        capture_run(captured),
    )

    audit_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8003
    assert captured["app"].title == "Audit Service"
