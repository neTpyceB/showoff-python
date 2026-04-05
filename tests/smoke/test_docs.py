from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from showoff_api.app import create_app
from showoff_api.config import Settings


@pytest.mark.smoke
def test_docs_and_openapi_are_available(tmp_path: Path) -> None:
    client = TestClient(
        create_app(
            Settings(
                database_path=tmp_path / "notes.db",
                api_token="smoke-token",
                host="127.0.0.1",
                port=8000,
            ),
        ),
    )

    docs = client.get("/docs")
    openapi = client.get("/openapi.json")

    assert docs.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Notes REST API Service"
