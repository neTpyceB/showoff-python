from __future__ import annotations

import socket
from threading import Thread
from time import monotonic, sleep
from urllib import request

import httpx
import pytest
import uvicorn

from showoff_micro.config import Settings
from showoff_micro.data_app import create_data_app
from showoff_micro.data_client import DataClient
from showoff_micro.store import JobStore
from showoff_micro.worker_service import WorkerService


class FakeAuthClient:
    def validate(self, authorization: str) -> str:
        return authorization.removeprefix("Bearer ")


def get_open_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(url: str) -> None:
    deadline = monotonic() + 5
    while monotonic() < deadline:
        try:
            with request.urlopen(f"{url}/health", timeout=1):
                return
        except OSError:
            sleep(0.05)
    raise AssertionError("Server did not start")


@pytest.mark.e2e
def test_job_is_processed_by_worker(tmp_path) -> None:
    port = get_open_port()
    data_service_url = f"http://127.0.0.1:{port}"
    settings = Settings(
        auth_host="0.0.0.0",
        auth_port=8000,
        data_host="127.0.0.1",
        data_port=port,
        data_db_path=str(tmp_path / "micro.db"),
        auth_service_url="http://auth:8000",
        data_service_url=data_service_url,
        worker_service_name="worker",
        worker_poll_seconds=1,
    )
    store = JobStore(settings.data_db_path)
    app = create_data_app(settings=settings, store=store, auth_client=FakeAuthClient())
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=settings.data_host,
            port=settings.data_port,
            log_level="error",
        )
    )
    server_thread = Thread(target=server.run, daemon=True)
    server_thread.start()
    wait_for_server(data_service_url)
    try:
        with httpx.Client(base_url=data_service_url, timeout=5) as client:
            created = client.post(
                "/jobs",
                headers={"Authorization": "Bearer alice"},
                json={"payload": "hello distributed world"},
            )
            worker = WorkerService(DataClient(data_service_url), poll_seconds=1)
            thread = Thread(target=worker.run_once)
            thread.start()
            thread.join()
            loaded = client.get(
                f"/jobs/{created.json()['id']}",
                headers={"Authorization": "Bearer alice"},
            )
    finally:
        server.should_exit = True
        server_thread.join(timeout=5)

    assert created.status_code == 201
    assert loaded.status_code == 200
    assert loaded.json()["status"] == "done"
    assert loaded.json()["result"] == "word_count:3"
