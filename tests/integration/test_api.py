from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from showoff_api.app import create_app
from showoff_api.config import Settings


def make_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        database_path=tmp_path / "notes.db",
        api_token="test-token",
        host="127.0.0.1",
        port=8000,
    )
    return TestClient(create_app(settings))


@pytest.mark.integration
def test_crud_flow(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"Authorization": "Bearer test-token"}

    created = client.post(
        "/notes",
        headers=headers,
        json={"title": "First note", "content": "Backend foundation."},
    )
    assert created.status_code == 201
    note = created.json()

    listed = client.get("/notes", headers=headers)
    assert listed.status_code == 200
    assert listed.json() == [note]

    read = client.get(f"/notes/{note['id']}", headers=headers)
    assert read.status_code == 200
    assert read.json() == note

    updated = client.put(
        f"/notes/{note['id']}",
        headers=headers,
        json={"title": "Updated note", "content": "Clean FastAPI architecture."},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated note"

    deleted = client.delete(f"/notes/{note['id']}", headers=headers)
    assert deleted.status_code == 204


@pytest.mark.integration
def test_validation_and_not_found(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"Authorization": "Bearer test-token"}

    invalid = client.post(
        "/notes",
        headers=headers,
        json={"title": "", "content": "x"},
    )
    assert invalid.status_code == 422

    missing = client.get("/notes/999", headers=headers)
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Note not found"}

    missing_update = client.put(
        "/notes/999",
        headers=headers,
        json={"title": "Updated note", "content": "Missing record."},
    )
    assert missing_update.status_code == 404
    assert missing_update.json() == {"detail": "Note not found"}

    missing_delete = client.delete("/notes/999", headers=headers)
    assert missing_delete.status_code == 404
    assert missing_delete.json() == {"detail": "Note not found"}


@pytest.mark.integration
def test_auth_is_required(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    missing = client.get("/notes")
    assert missing.status_code == 401
    assert missing.json() == {"detail": "Invalid bearer token"}

    wrong = client.get("/notes", headers={"Authorization": "Bearer wrong"})
    assert wrong.status_code == 401
    assert wrong.headers["www-authenticate"] == "Bearer"
