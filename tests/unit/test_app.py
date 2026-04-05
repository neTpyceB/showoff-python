from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient

from showoff_pipeline.app import create_app
from showoff_pipeline.config import Settings
from showoff_pipeline.pipeline import PipelineService


def make_client(tmp_path) -> TestClient:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "pipeline.db"),
        insert_batch_size=2,
    )
    return TestClient(create_app(settings=settings, service=PipelineService(settings)))


def test_health_endpoint(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_run_returns_not_found(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/pipeline/runs/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found"}


def test_invalid_upload_returns_bad_request(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/pipeline/runs",
            files={
                "file": (
                    "broken.csv",
                    BytesIO(b"wrong,columns\n1,2\n"),
                    "text/csv",
                )
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "CSV columns must be exactly: timestamp,account,amount"
    }
