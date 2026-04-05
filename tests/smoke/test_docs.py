from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_queue.app import create_app
from showoff_queue.config import QueueSettings


class FakeRedis:
    def get(self, key: str) -> None:
        return None

    def close(self) -> None:
        return None


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available() -> None:
    settings = QueueSettings(
        broker_url="memory://",
        result_backend="cache+memory://",
        redis_url="redis://redis:6379/2",
        heartbeat_key="queue:heartbeat",
        heartbeat_seconds=3,
        retry_max=2,
        host="127.0.0.1",
        port=8000,
    )

    with TestClient(create_app(settings, redis_client=FakeRedis())) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")
        health = client.get("/health")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Report Generation Queue"
    assert health.json() == {"status": "ok"}
