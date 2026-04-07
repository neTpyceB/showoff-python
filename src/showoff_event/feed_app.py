from __future__ import annotations

from fastapi import FastAPI

from .bus import consume_events
from .config import Settings
from .lifespan import create_consumer_lifespan
from .models import EventEnvelope, FeedEntry, HealthResponse
from .store import FeedStore


def create_feed_app(
    settings: Settings,
    store: FeedStore | None = None,
    consumer=None,
) -> FastAPI:
    resolved_store = store or FeedStore(settings.feed_db_path)

    async def project(event: EventEnvelope) -> None:
        resolved_store.add_event(event)

    resolved_consumer = consumer or (
        lambda: consume_events(settings.redis_url, settings.event_channel, project)
    )
    app = FastAPI(
        title="Feed Service",
        version="0.10.0",
        lifespan=create_consumer_lifespan(
            resolved_store.ensure_schema,
            resolved_consumer,
        ),
    )

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/users/{user_id}/feed", response_model=list[FeedEntry])
    def read_feed(user_id: str) -> list[FeedEntry]:
        return resolved_store.list_entries(user_id)

    return app
