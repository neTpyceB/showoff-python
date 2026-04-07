from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from showoff_event.audit_app import create_audit_app
from showoff_event.config import Settings
from showoff_event.feed_app import create_feed_app
from showoff_event.notification_app import create_notification_app
from showoff_event.platform_app import create_platform_app


async def idle_consumer() -> None:
    await asyncio.Future()


class FakePublisher:
    async def publish(self, event) -> None:
        return None


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


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available(tmp_path) -> None:
    settings = make_settings(tmp_path)
    platform_app = create_platform_app(settings, publisher=FakePublisher())
    feed_app = create_feed_app(settings, consumer=idle_consumer)
    notification_app = create_notification_app(settings, consumer=idle_consumer)
    audit_app = create_audit_app(settings, consumer=idle_consumer)

    with TestClient(platform_app) as client:
        platform_docs = client.get("/docs")
        platform_openapi = client.get("/openapi.json")
        platform_health = client.get("/health")

    with TestClient(feed_app) as client:
        feed_docs = client.get("/docs")
        feed_openapi = client.get("/openapi.json")
        feed_health = client.get("/health")

    with TestClient(notification_app) as client:
        notification_docs = client.get("/docs")
        notification_openapi = client.get("/openapi.json")
        notification_health = client.get("/health")

    with TestClient(audit_app) as client:
        audit_docs = client.get("/docs")
        audit_openapi = client.get("/openapi.json")
        audit_health = client.get("/health")

    assert platform_docs.status_code == 200
    assert platform_openapi.json()["info"]["title"] == "Platform API"
    assert platform_health.json() == {"status": "ok"}
    assert feed_docs.status_code == 200
    assert feed_openapi.json()["info"]["title"] == "Feed Service"
    assert feed_health.json() == {"status": "ok"}
    assert notification_docs.status_code == 200
    assert notification_openapi.json()["info"]["title"] == "Notification Service"
    assert notification_health.json() == {"status": "ok"}
    assert audit_docs.status_code == 200
    assert audit_openapi.json()["info"]["title"] == "Audit Service"
    assert audit_health.json() == {"status": "ok"}
