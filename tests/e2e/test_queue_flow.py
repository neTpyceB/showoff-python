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
def test_end_to_end_queue_flow() -> None:
    port = free_port()
    env = {
        **os.environ,
        "QUEUE_API_HOST": "127.0.0.1",
        "QUEUE_API_PORT": str(port),
        "QUEUE_BROKER_URL": "memory://",
        "QUEUE_RESULT_BACKEND": "cache+memory://",
        "QUEUE_REDIS_URL": "redis://redis:6379/2",
        "QUEUE_HEARTBEAT_KEY": "queue:heartbeat",
        "QUEUE_HEARTBEAT_SECONDS": "3",
        "QUEUE_RETRY_MAX": "2",
        "PYTHONPATH": str(Path.cwd() / "src"),
    }
    process = subprocess.Popen(
        [sys.executable, "-m", "showoff_queue"],
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

        response = httpx.post(
            f"http://127.0.0.1:{port}/jobs/reports",
            json={"report_id": "demo", "content": "celery makes jobs async"},
            timeout=5,
        )

        assert response.status_code == 202
        task_id = response.json()["task_id"]

        status = httpx.get(f"http://127.0.0.1:{port}/jobs/{task_id}", timeout=5)
        assert status.status_code == 200
        assert status.json()["status"] == "PENDING"
    finally:
        process.terminate()
        process.wait(timeout=10)
