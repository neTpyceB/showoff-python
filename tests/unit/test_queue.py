from __future__ import annotations

import pytest
from celery import Celery

from showoff_queue.config import QueueSettings
from showoff_queue.queue import (
    TASK_HEARTBEAT,
    TASK_REPORT,
    build_report,
    create_celery,
    write_heartbeat,
)


def make_settings() -> QueueSettings:
    return QueueSettings(
        broker_url="memory://",
        result_backend="cache+memory://",
        redis_url="redis://redis:6379/2",
        heartbeat_key="queue:heartbeat",
        heartbeat_seconds=3,
        retry_max=2,
        host="127.0.0.1",
        port=8000,
    )


@pytest.mark.unit
def test_build_report_returns_summary() -> None:
    assert build_report({"report_id": "demo", "content": "one two\nthree"}) == {
        "report_id": "demo",
        "line_count": 2,
        "word_count": 3,
        "checksum": "2e2bf529d7cf77cec165d750c66d6d1617d14adf8e9f4e483864ed0b6c89a221",
    }


@pytest.mark.unit
def test_create_celery_registers_tasks() -> None:
    queue = create_celery(make_settings())

    assert isinstance(queue, Celery)
    assert TASK_REPORT in queue.tasks
    assert TASK_HEARTBEAT in queue.tasks


@pytest.mark.unit
def test_write_heartbeat_writes_value(monkeypatch: pytest.MonkeyPatch) -> None:
    written: dict[str, str] = {}

    class FakeRedis:
        def set(self, key: str, value: str) -> None:
            written[key] = value

        def close(self) -> None:
            written["closed"] = "yes"

    monkeypatch.setattr(
        "showoff_queue.queue.Redis.from_url",
        lambda url, decode_responses: FakeRedis(),
    )

    timestamp = write_heartbeat("redis://redis:6379/2", "queue:heartbeat")

    assert written["queue:heartbeat"] == timestamp
    assert written["closed"] == "yes"


@pytest.mark.unit
def test_heartbeat_task_returns_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    queue = create_celery(make_settings())
    monkeypatch.setattr(
        "showoff_queue.queue.write_heartbeat",
        lambda url, key: "2026-04-05T20:00:00+00:00",
    )

    result = queue.tasks[TASK_HEARTBEAT].apply()

    assert result.result == {"last_run": "2026-04-05T20:00:00+00:00"}
