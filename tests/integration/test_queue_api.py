from __future__ import annotations

import time

import pytest
from celery.contrib.testing.worker import start_worker
from fastapi.testclient import TestClient

from showoff_queue.app import create_app
from showoff_queue.config import QueueSettings
from showoff_queue.queue import (
    TASK_HEARTBEAT,
    TASK_REPORT,
    TransientReportError,
    create_celery,
)


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.closed = False

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def close(self) -> None:
        self.closed = True


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


def make_queue() -> object:
    queue = create_celery(make_settings())
    queue.conf.update(task_store_eager_result=True)
    return queue


@pytest.mark.integration
def test_submit_job_and_read_success_status() -> None:
    queue = make_queue()
    redis_client = FakeRedis()

    with start_worker(queue, perform_ping_check=False):
        with TestClient(create_app(make_settings(), queue, redis_client)) as client:
            created = client.post(
                "/jobs/reports",
                json={"report_id": "demo", "content": "one two\nthree"},
            )
            assert created.status_code == 202
            task_id = created.json()["task_id"]

            deadline = time.time() + 5
            while True:
                result = client.get(f"/jobs/{task_id}")
                if result.json()["status"] == "SUCCESS":
                    break
                if time.time() >= deadline:
                    raise AssertionError("task did not complete")
                time.sleep(0.05)

            assert result.json() == {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": {
                    "report_id": "demo",
                    "line_count": 2,
                    "word_count": 3,
                    "checksum": (
                        "2e2bf529d7cf77cec165d750c66d6d1617d14adf8e9f4e483864ed0b6c89a221"
                    ),
                },
            }


@pytest.mark.integration
def test_report_task_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    queue = make_queue()
    attempts = {"count": 0}
    task = queue.tasks[TASK_REPORT]

    def flaky(payload: dict[str, str]) -> dict[str, int | str]:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TransientReportError("retry")
        return {
            "report_id": payload["report_id"],
            "line_count": 1,
            "word_count": 1,
            "checksum": "ok",
        }

    monkeypatch.setattr("showoff_queue.queue.build_report", flaky)
    result = task.apply(args=[{"report_id": "demo", "content": "x"}], throw=False)

    assert result.status == "SUCCESS"
    assert result.result == {
        "report_id": "demo",
        "line_count": 1,
        "word_count": 1,
        "checksum": "ok",
    }
    assert attempts["count"] == 2


@pytest.mark.integration
def test_heartbeat_endpoint_reads_scheduled_value() -> None:
    queue = make_queue()
    redis_client = FakeRedis()
    heartbeat = queue.tasks[TASK_HEARTBEAT]

    heartbeat.delay()
    redis_client.set("queue:heartbeat", "2026-04-05T20:00:00+00:00")

    with TestClient(create_app(make_settings(), queue, redis_client)) as client:
        response = client.get("/schedules/heartbeat")

    assert response.json() == {"last_run": "2026-04-05T20:00:00+00:00"}
