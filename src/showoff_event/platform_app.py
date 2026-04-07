from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI

from .bus import EventPublisher, RedisPublisher
from .config import Settings
from .models import EventEnvelope, EventType, HealthResponse, PublishActivityRequest


def create_platform_app(
    settings: Settings,
    publisher: EventPublisher | None = None,
) -> FastAPI:
    resolved_publisher = publisher or RedisPublisher(
        settings.redis_url,
        settings.event_channel,
    )
    app = FastAPI(title="Platform API", version="0.10.0")

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/events/activities", response_model=EventEnvelope, status_code=202)
    async def publish_activity(payload: PublishActivityRequest) -> EventEnvelope:
        event = EventEnvelope(
            event_id=str(uuid4()),
            type=EventType.ACTIVITY_CREATED,
            user_id=payload.user_id,
            title=payload.title,
            detail=payload.detail,
            created_at=datetime.now(UTC).isoformat(),
        )
        await resolved_publisher.publish(event)
        return event

    return app
