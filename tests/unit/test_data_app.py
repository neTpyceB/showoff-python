from __future__ import annotations

from fastapi.testclient import TestClient

from showoff_micro.config import Settings
from showoff_micro.data_app import create_data_app
from showoff_micro.store import JobStore


class FakeAuthClient:
    def validate(self, authorization: str) -> str:
        if authorization != "Bearer alice":
            raise PermissionError("Unauthorized")
        return "alice"


def make_settings(tmp_path) -> Settings:
    return Settings(
        auth_host="0.0.0.0",
        auth_port=8000,
        data_host="0.0.0.0",
        data_port=8000,
        data_db_path=str(tmp_path / "micro.db"),
        auth_service_url="http://auth:8000",
        data_service_url="http://data:8000",
        worker_service_name="worker",
        worker_poll_seconds=1,
    )


def test_create_and_read_job(tmp_path) -> None:
    settings = make_settings(tmp_path)
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())

    with TestClient(app) as client:
        created = client.post(
            "/jobs",
            headers={"Authorization": "Bearer alice"},
            json={"payload": "hello world"},
        )
        job_id = created.json()["id"]
        loaded = client.get(
            f"/jobs/{job_id}",
            headers={"Authorization": "Bearer alice"},
        )

    assert created.status_code == 201
    assert loaded.status_code == 200
    assert loaded.json()["payload"] == "hello world"


def test_internal_claim_and_complete(tmp_path) -> None:
    settings = make_settings(tmp_path)
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())

    with TestClient(app) as client:
        created = client.post(
            "/jobs",
            headers={"Authorization": "Bearer alice"},
            json={"payload": "hello world"},
        )
        job_id = created.json()["id"]
        claimed = client.post("/internal/jobs/claim", json={})
        completed = client.post(
            f"/internal/jobs/{job_id}/complete",
            json={"result": "word_count:2"},
        )

    assert claimed.json()["status"] == "processing"
    assert completed.json()["status"] == "done"
    assert completed.json()["result"] == "word_count:2"


def test_read_missing_job_returns_not_found(tmp_path) -> None:
    settings = make_settings(tmp_path)
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())

    with TestClient(app) as client:
        response = client.get(
            "/jobs/missing",
            headers={"Authorization": "Bearer alice"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_create_job_requires_valid_token(tmp_path) -> None:
    settings = make_settings(tmp_path)
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())

    with TestClient(app) as client:
        response = client.post(
            "/jobs",
            headers={"Authorization": "Bearer bob"},
            json={"payload": "hello world"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_read_job_requires_valid_token_and_discovery_is_available(tmp_path) -> None:
    settings = make_settings(tmp_path)
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())

    with TestClient(app) as client:
        discovery = client.get("/discovery")
        response = client.get(
            "/jobs/job-1",
            headers={"Authorization": "Bearer bob"},
        )

    assert discovery.status_code == 200
    assert discovery.json()["service"] == "data"
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
