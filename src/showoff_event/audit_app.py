from __future__ import annotations

from fastapi import FastAPI

from .bus import consume_events
from .config import Settings
from .lifespan import create_consumer_lifespan
from .models import AuditEntry, EventEnvelope, HealthResponse
from .store import AuditStore


def create_audit_app(
    settings: Settings,
    store: AuditStore | None = None,
    consumer=None,
) -> FastAPI:
    resolved_store = store or AuditStore(settings.audit_db_path)

    async def project(event: EventEnvelope) -> None:
        resolved_store.add_event(event)

    resolved_consumer = consumer or (
        lambda: consume_events(settings.redis_url, settings.event_channel, project)
    )
    app = FastAPI(
        title="Audit Service",
        version="0.10.0",
        lifespan=create_consumer_lifespan(
            resolved_store.ensure_schema,
            resolved_consumer,
        ),
    )

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/events", response_model=list[AuditEntry])
    def read_events() -> list[AuditEntry]:
        return resolved_store.list_entries()

    return app
