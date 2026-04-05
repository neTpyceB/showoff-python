from __future__ import annotations

from io import BytesIO

import pytest
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


@pytest.mark.integration
def test_stream_pipeline_api_flow(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/pipeline/runs?mode=stream",
            files={
                "file": (
                    "stream.csv",
                    BytesIO(
                        b"timestamp,account,amount\n"
                        b"2026-01-01T10:00:00+00:00, ACME ,10.50\n"
                        b"2026-01-01T11:00:00+00:00,Globex,2.00\n"
                    ),
                    "text/csv",
                )
            },
        )
        assert response.status_code == 201
        body = response.json()

        lookup = client.get(f"/pipeline/runs/{body['run_id']}")
        monitoring = client.get("/monitoring")

    assert body["status"] == "success"
    assert body["stored_rows"] == 2
    assert lookup.status_code == 200
    assert lookup.json()["run_id"] == body["run_id"]
    assert monitoring.status_code == 200
    assert monitoring.json()["successful_runs"] == 1


@pytest.mark.integration
def test_batch_pipeline_api_flow(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/pipeline/runs?mode=batch",
            files={
                "file": (
                    "batch.csv",
                    BytesIO(
                        b"timestamp,account,amount\n"
                        b"2026-01-02T10:00:00+00:00,Acme,1.25\n"
                        b"2026-01-02T12:00:00+00:00,Acme,2.75\n"
                    ),
                    "text/csv",
                )
            },
        )

    assert response.status_code == 201
    assert response.json()["mode"] == "batch"
    assert response.json()["total_amount_cents"] == 400
