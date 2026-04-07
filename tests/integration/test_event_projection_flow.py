from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from showoff_event.audit_app import create_audit_app
from showoff_event.config import Settings
from showoff_event.feed_app import create_feed_app
from showoff_event.notification_app import create_notification_app
from showoff_event.platform_app import create_platform_app
from showoff_event.store import AuditStore, FeedStore, NotificationStore


class FakePublisher:
    def __init__(self) -> None:
        self.events = []

    async def publish(self, event) -> None:
        self.events.append(event)


async def idle_consumer() -> None:
    await asyncio.Future()


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


@pytest.mark.integration
def test_published_event_can_be_projected_across_services(tmp_path) -> None:
    settings = make_settings(tmp_path)
    feed_store = FeedStore(settings.feed_db_path)
    notification_store = NotificationStore(settings.notification_db_path)
    audit_store = AuditStore(settings.audit_db_path)
    feed_store.ensure_schema()
    notification_store.ensure_schema()
    audit_store.ensure_schema()
    publisher = FakePublisher()

    platform_app = create_platform_app(settings, publisher=publisher)
    feed_app = create_feed_app(settings, store=feed_store, consumer=idle_consumer)
    notification_app = create_notification_app(
        settings,
        store=notification_store,
        consumer=idle_consumer,
    )
    audit_app = create_audit_app(settings, store=audit_store, consumer=idle_consumer)

    with TestClient(platform_app) as platform_client:
        event = platform_client.post(
            "/events/activities",
            json={
                "user_id": "alice",
                "title": "Trip completed",
                "detail": "Berlin airport pickup",
            },
        ).json()

    feed_store.add_event(publisher.events[0])
    notification_store.add_event(publisher.events[0])
    audit_store.add_event(publisher.events[0])

    with TestClient(feed_app) as feed_client:
        feed = feed_client.get("/users/alice/feed")
    with TestClient(notification_app) as notification_client:
        notifications = notification_client.get("/users/alice/notifications")
    with TestClient(audit_app) as audit_client:
        audit = audit_client.get("/events")

    assert event["event_id"] == publisher.events[0].event_id
    assert feed.json()[0]["title"] == "Trip completed"
    assert notifications.json()[0]["message"] == "Activity recorded: Trip completed"
    assert audit.json()[0]["detail"] == "Berlin airport pickup"
