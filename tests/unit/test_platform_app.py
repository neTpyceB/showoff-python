from __future__ import annotations

from fastapi.testclient import TestClient

from showoff_event.config import Settings
from showoff_event.platform_app import create_platform_app


class FakePublisher:
    def __init__(self) -> None:
        self.published = []

    async def publish(self, event) -> None:
        self.published.append(event)


def make_settings() -> Settings:
    return Settings(
        platform_host="127.0.0.1",
        platform_port=8000,
        feed_host="127.0.0.1",
        feed_port=8001,
        feed_db_path="/tmp/feed.db",
        notification_host="127.0.0.1",
        notification_port=8002,
        notification_db_path="/tmp/notifications.db",
        audit_host="127.0.0.1",
        audit_port=8003,
        audit_db_path="/tmp/audit.db",
        redis_url="redis://redis:6379/0",
        event_channel="platform.events",
    )


def test_publish_activity_emits_event() -> None:
    publisher = FakePublisher()

    app = create_platform_app(make_settings(), publisher=publisher)
    with TestClient(app) as client:
        response = client.post(
            "/events/activities",
            json={
                "user_id": "alice",
                "title": "Ride completed",
                "detail": "Airport to city center",
            },
        )
        health = client.get("/health")

    assert response.status_code == 202
    assert response.json()["type"] == "activity.created"
    assert response.json()["user_id"] == "alice"
    assert response.json()["title"] == "Ride completed"
    assert publisher.published[0].detail == "Airport to city center"
    assert health.json() == {"status": "ok"}
