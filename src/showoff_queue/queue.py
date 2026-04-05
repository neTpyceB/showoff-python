from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from celery import Celery
from redis import Redis

from showoff_queue.config import QueueSettings

TASK_REPORT = "showoff_queue.generate_report"
TASK_HEARTBEAT = "showoff_queue.record_heartbeat"


class TransientReportError(Exception):
    pass


def build_report(payload: dict[str, str]) -> dict[str, int | str]:
    content = payload["content"]
    return {
        "report_id": payload["report_id"],
        "line_count": len(content.splitlines()),
        "word_count": len(content.split()),
        "checksum": sha256(content.encode("utf-8")).hexdigest(),
    }


def write_heartbeat(redis_url: str, heartbeat_key: str) -> str:
    client = Redis.from_url(redis_url, decode_responses=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    client.set(heartbeat_key, timestamp)
    client.close()
    return timestamp


def create_celery(settings: QueueSettings) -> Celery:
    app = Celery(
        "showoff_queue",
        broker=settings.broker_url,
        backend=settings.result_backend,
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_track_started=True,
        beat_schedule={
            "heartbeat": {
                "task": TASK_HEARTBEAT,
                "schedule": settings.heartbeat_seconds,
            },
        },
    )

    @app.task(
        bind=True,
        name=TASK_REPORT,
        autoretry_for=(TransientReportError,),
        retry_kwargs={"max_retries": settings.retry_max},
        retry_backoff=False,
    )
    def generate_report(self, payload: dict[str, str]) -> dict[str, int | str]:
        return build_report(payload)

    @app.task(name=TASK_HEARTBEAT)
    def record_heartbeat() -> dict[str, str]:
        return {
            "last_run": write_heartbeat(settings.redis_url, settings.heartbeat_key),
        }

    return app


celery_app = create_celery(QueueSettings.from_env())
