from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

import showoff_event.notification_app as notification_app_module
from showoff_event.config import Settings
from showoff_event.models import EventEnvelope, EventType
from showoff_event.notification_app import create_notification_app
from showoff_event.store import NotificationStore


def make_settings(tmp_path) -> Settings:
    return Settings(
        platform_host="127.0.0.1",
        platform_port=8000,
        feed_host="127.0.0.1",
        feed_port=8001,
        feed_db_path=str(tmp_path / "feed.db"),
        notification_host="127.0.0.1",
        notification_port=8002,
        notification_db_path=str(tmp_path / "notifications.db"),
        audit_host="127.0.0.1",
        audit_port=8003,
        audit_db_path=str(tmp_path / "audit.db"),
        redis_url="redis://redis:6379/0",
        event_channel="platform.events",
    )


def make_event() -> EventEnvelope:
    return EventEnvelope(
        event_id="event-1",
        type=EventType.ACTIVITY_CREATED,
        user_id="alice",
        title="Ride completed",
        detail="Airport to city center",
        created_at="2026-04-06T16:00:00+00:00",
    )


def test_notification_app_reads_projected_entries_and_manages_consumer(
    tmp_path,
) -> None:
    state = {"started": False, "stopped": False}

    async def consumer() -> None:
        state["started"] = True
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            state["stopped"] = True
            raise

    settings = make_settings(tmp_path)
    store = NotificationStore(settings.notification_db_path)
    app = create_notification_app(settings=settings, store=store, consumer=consumer)

    with TestClient(app) as client:
        store.add_event(make_event())
        response = client.get("/users/alice/notifications")
        health = client.get("/health")

    assert response.status_code == 200
    assert response.json()[0]["message"] == "Activity recorded: Ride completed"
    assert health.json() == {"status": "ok"}
    assert state == {"started": True, "stopped": True}


def test_notification_app_default_consumer_projects_event(
    tmp_path,
    monkeypatch,
) -> None:
    settings = make_settings(tmp_path)
    store = NotificationStore(settings.notification_db_path)

    async def fake_consume_events(redis_url: str, channel: str, on_event) -> None:
        await on_event(make_event())
        await asyncio.Future()

    monkeypatch.setattr(
        notification_app_module,
        "consume_events",
        fake_consume_events,
    )

    with TestClient(create_notification_app(settings=settings, store=store)) as client:
        response = client.get("/users/alice/notifications")

    assert response.json()[0]["event_id"] == "event-1"
