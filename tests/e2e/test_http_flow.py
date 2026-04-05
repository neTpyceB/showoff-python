from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.mark.e2e
def test_end_to_end_http_flow(tmp_path: Path) -> None:
    port = free_port()
    database_path = tmp_path / "notes.db"
    env = {
        **os.environ,
        "APP_API_TOKEN": "e2e-token",
        "APP_DATABASE_PATH": str(database_path),
        "APP_HOST": "127.0.0.1",
        "APP_PORT": str(port),
        "PYTHONPATH": str(Path.cwd() / "src"),
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "showoff_api"],
        cwd=Path.cwd(),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.time() + 10
        while True:
            try:
                docs = httpx.get(f"http://127.0.0.1:{port}/docs", timeout=0.2)
                if docs.status_code == 200:
                    break
            except httpx.HTTPError:
                if time.time() >= deadline:
                    raise
                time.sleep(0.1)

        headers = {"Authorization": "Bearer e2e-token"}
        created = httpx.post(
            f"http://127.0.0.1:{port}/notes",
            headers=headers,
            json={"title": "First note", "content": "FastAPI with SQLite."},
            timeout=5,
        )
        assert created.status_code == 201
        note_id = created.json()["id"]

        listed = httpx.get(f"http://127.0.0.1:{port}/notes", headers=headers, timeout=5)
        assert listed.status_code == 200
        assert listed.json() == [
            {"id": note_id, "title": "First note", "content": "FastAPI with SQLite."},
        ]

        updated = httpx.put(
            f"http://127.0.0.1:{port}/notes/{note_id}",
            headers=headers,
            json={"title": "Updated note", "content": "Still production-ready."},
            timeout=5,
        )
        assert updated.status_code == 200
        assert updated.json() == {
            "id": note_id,
            "title": "Updated note",
            "content": "Still production-ready.",
        }

        deleted = httpx.delete(
            f"http://127.0.0.1:{port}/notes/{note_id}",
            headers=headers,
            timeout=5,
        )
        assert deleted.status_code == 204
    finally:
        process.terminate()
        process.wait(timeout=10)
