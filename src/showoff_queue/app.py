from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from celery import Celery
from celery.result import AsyncResult
from fastapi import Depends, FastAPI, Request, status
from redis import Redis

from showoff_queue import __version__
from showoff_queue.config import QueueSettings
from showoff_queue.models import (
    HeartbeatStatus,
    JobStatus,
    JobSubmission,
    ReportJobRequest,
    ReportResult,
)
from showoff_queue.queue import TASK_REPORT, celery_app


def get_settings(request: Request) -> QueueSettings:
    return request.app.state.settings


def get_queue(request: Request) -> Celery:
    return request.app.state.queue


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def create_app(
    settings: QueueSettings,
    queue_app: Celery | None = None,
    redis_client: Redis | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        owned_redis = redis_client is None
        app.state.settings = settings
        app.state.queue = queue_app or celery_app
        app.state.redis = redis_client or Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        try:
            yield
        finally:
            if owned_redis:
                app.state.redis.close()

    app = FastAPI(
        title="Report Generation Queue",
        version=__version__,
        summary="Background report jobs with Celery and Redis.",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/jobs/reports",
        response_model=JobSubmission,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def submit_report(
        payload: ReportJobRequest,
        queue: Annotated[Celery, Depends(get_queue)],
    ) -> JobSubmission:
        task = queue.tasks[TASK_REPORT].delay(payload.model_dump())
        return JobSubmission(task_id=task.id)

    @app.get("/jobs/{task_id}", response_model=JobStatus)
    def job_status(
        task_id: str,
        queue: Annotated[Celery, Depends(get_queue)],
    ) -> JobStatus:
        result = AsyncResult(task_id, app=queue)
        payload = (
            ReportResult.model_validate(result.result) if result.successful() else None
        )
        return JobStatus(task_id=task_id, status=result.status, result=payload)

    @app.get("/schedules/heartbeat", response_model=HeartbeatStatus)
    def heartbeat_status(
        settings: Annotated[QueueSettings, Depends(get_settings)],
        redis_client: Annotated[Redis, Depends(get_redis)],
    ) -> HeartbeatStatus:
        return HeartbeatStatus(last_run=redis_client.get(settings.heartbeat_key))

    return app
