from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_saas.app import create_app
from showoff_saas.config import Settings
from showoff_saas.repository import SaaSRepository
from showoff_saas.service import SaaSService


@pytest.mark.smoke
def test_docs_openapi_and_health_are_available(tmp_path) -> None:
    settings = Settings(
        api_host="127.0.0.1",
        api_port=8000,
        db_path=str(tmp_path / "saas.db"),
    )
    app = create_app(settings=settings, service=SaaSService(SaaSRepository(settings)))

    with TestClient(app) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")
        health = client.get("/health")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Multi-tenant SaaS Backend"
    assert health.json() == {"status": "ok"}
