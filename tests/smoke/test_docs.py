from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from showoff_async.app import create_app
from showoff_async.config import AggregatorSettings
from showoff_async.mock_app import create_mock_app


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available() -> None:
    settings = AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.1,
        retries=1,
        host="127.0.0.1",
        port=8000,
    )
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_mock_app()),
        base_url="http://upstream.test",
    )
    test_client = TestClient(create_app(settings, client))

    docs = test_client.get("/docs")
    openapi = test_client.get("/openapi.json")
    health = test_client.get("/health")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Async Data Aggregator"
    assert health.json() == {"status": "ok"}
