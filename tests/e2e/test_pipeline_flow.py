from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from showoff_pipeline.app import create_app
from showoff_pipeline.config import Settings
from showoff_pipeline.pipeline import PipelineService


@pytest.mark.e2e
def test_large_stream_flow(tmp_path) -> None:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "pipeline.db"),
        insert_batch_size=50,
    )
    rows = ["timestamp,account,amount"]
    rows.extend(
        f"2026-01-03T10:{index % 60:02d}:00+00:00,account-{index},1.00"
        for index in range(1000)
    )
    payload = "\n".join(rows).encode()

    app = create_app(settings=settings, service=PipelineService(settings))
    with TestClient(app) as client:
        response = client.post(
            "/pipeline/runs?mode=stream",
            files={"file": ("large.csv", BytesIO(payload), "text/csv")},
        )
        assert response.status_code == 201
        run = response.json()
        monitoring = client.get("/monitoring")

    assert run["processed_rows"] == 1000
    assert run["stored_rows"] == 1000
    assert run["total_amount_cents"] == 100000
    assert monitoring.status_code == 200
    assert monitoring.json()["stored_rows_total"] == 1000
