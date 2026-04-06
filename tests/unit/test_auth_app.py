from __future__ import annotations

from fastapi.testclient import TestClient

from showoff_micro.auth_app import create_auth_app
from showoff_micro.config import Settings


def make_settings() -> Settings:
    return Settings(
        auth_host="0.0.0.0",
        auth_port=8000,
        data_host="0.0.0.0",
        data_port=8000,
        data_db_path="/tmp/micro.db",
        auth_service_url="http://auth:8000",
        data_service_url="http://data:8000",
        worker_service_name="worker",
        worker_poll_seconds=1,
    )


def test_auth_endpoints() -> None:
    with TestClient(create_auth_app(make_settings())) as client:
        health = client.get("/health")
        discovery = client.get("/discovery")
        token = client.post("/tokens", json={"user_id": "alice"})
        validate = client.get(
            "/validate",
            headers={"Authorization": f"Bearer {token.json()['access_token']}"},
        )

    assert health.json() == {"status": "ok"}
    assert discovery.json()["service"] == "auth"
    assert token.json() == {"access_token": "alice"}
    assert validate.json() == {"user_id": "alice"}


def test_validate_rejects_invalid_header() -> None:
    with TestClient(create_auth_app(make_settings())) as client:
        response = client.get("/validate", headers={"Authorization": "alice"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
