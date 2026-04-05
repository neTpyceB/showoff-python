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
def test_end_to_end_http_flow() -> None:
    aggregator_port = free_port()
    mock_port = free_port()
    env = {
        **os.environ,
        "AGGREGATOR_PROFILE_URL": f"http://127.0.0.1:{mock_port}/profile",
        "AGGREGATOR_ACTIVITY_URL": f"http://127.0.0.1:{mock_port}/activity",
        "AGGREGATOR_STATUS_URL": f"http://127.0.0.1:{mock_port}/status",
        "AGGREGATOR_TIMEOUT_SECONDS": "0.5",
        "AGGREGATOR_RETRIES": "1",
        "AGGREGATOR_HOST": "127.0.0.1",
        "AGGREGATOR_PORT": str(aggregator_port),
        "MOCK_API_HOST": "127.0.0.1",
        "MOCK_API_PORT": str(mock_port),
        "PYTHONPATH": str(Path.cwd() / "src"),
    }
    mock_process = subprocess.Popen(
        [sys.executable, "-m", "showoff_async.mock_main"],
        cwd=Path.cwd(),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    aggregator_process = subprocess.Popen(
        [sys.executable, "-m", "showoff_async"],
        cwd=Path.cwd(),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        deadline = time.time() + 10
        while True:
            try:
                docs = httpx.get(
                    f"http://127.0.0.1:{aggregator_port}/docs",
                    timeout=0.2,
                )
                if docs.status_code == 200:
                    break
            except httpx.HTTPError:
                if time.time() >= deadline:
                    raise
                time.sleep(0.1)

        response = httpx.get(
            f"http://127.0.0.1:{aggregator_port}/aggregate/ada",
            timeout=5,
        )

        assert response.status_code == 200
        assert response.json() == {
            "user_id": "ada",
            "profile": {"user_id": "ada", "name": "Ada", "role": "engineer"},
            "activity": {"user_id": "ada", "commits": 9, "reviews": 3},
            "status": {"user_id": "ada", "availability": "focused"},
        }
    finally:
        aggregator_process.terminate()
        aggregator_process.wait(timeout=10)
        mock_process.terminate()
        mock_process.wait(timeout=10)
