from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_micro.auth_app import create_auth_app
from showoff_micro.config import Settings
from showoff_micro.data_app import create_data_app
from showoff_micro.store import JobStore


class FakeAuthClient:
    def validate(self, authorization: str) -> str:
        return "alice"


def make_settings(tmp_path) -> Settings:
    return Settings(
        auth_host="127.0.0.1",
        auth_port=8000,
        data_host="127.0.0.1",
        data_port=8000,
        data_db_path=str(tmp_path / "micro.db"),
        auth_service_url="http://auth:8000",
        data_service_url="http://data:8000",
        worker_service_name="worker",
        worker_poll_seconds=1,
    )


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available(tmp_path) -> None:
    settings = make_settings(tmp_path)
    auth_app = create_auth_app(settings)
    data_app = create_data_app(
        settings=settings,
        store=JobStore(settings.data_db_path),
        auth_client=FakeAuthClient(),
    )

    with TestClient(auth_app) as auth_client:
        auth_docs = auth_client.get("/docs")
        auth_openapi = auth_client.get("/openapi.json")
        auth_health = auth_client.get("/health")

    with TestClient(data_app) as data_client:
        data_docs = data_client.get("/docs")
        data_openapi = data_client.get("/openapi.json")
        data_health = data_client.get("/health")

    assert auth_docs.status_code == 200
    assert auth_openapi.json()["info"]["title"] == "Auth Service"
    assert auth_health.json() == {"status": "ok"}
    assert data_docs.status_code == 200
    assert data_openapi.json()["info"]["title"] == "Data Service"
    assert data_health.json() == {"status": "ok"}
