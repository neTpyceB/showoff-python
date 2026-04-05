from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from showoff_queue.app import create_app, get_queue, get_redis, get_settings
from showoff_queue.config import QueueSettings
from showoff_queue.queue import create_celery


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.closed = False

    def get(self, key: str) -> str | None:
        return self.values.get(key)

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


@pytest.mark.unit
def test_dependencies_return_state_objects() -> None:
    settings = make_settings()
    queue = create_celery(settings)
    redis_client = FakeRedis()
    app = create_app(settings, queue, redis_client)
    app.state.settings = settings
    app.state.queue = queue
    app.state.redis = redis_client
    request = Request({"type": "http", "app": app})

    assert get_settings(request) == settings
    assert get_queue(request) == queue
    assert get_redis(request) == redis_client


@pytest.mark.unit
def test_app_closes_owned_redis_on_shutdown() -> None:
    with TestClient(create_app(make_settings())) as client:
        assert client.get("/health").json() == {"status": "ok"}
