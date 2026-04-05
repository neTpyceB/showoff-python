from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_pipeline.app import create_app
from showoff_pipeline.config import Settings
from showoff_pipeline.pipeline import PipelineService


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available(tmp_path) -> None:
    settings = Settings(
        api_host="127.0.0.1",
        api_port=8000,
        db_path=str(tmp_path / "pipeline.db"),
        insert_batch_size=10,
    )

    with TestClient(
        create_app(settings=settings, service=PipelineService(settings))
    ) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")
        health = client.get("/health")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "ETL Pipeline System"
    assert health.json() == {"status": "ok"}
