from __future__ import annotations

from showoff_micro import auth_main, data_main, worker_main
from showoff_micro.config import Settings


def capture_run(captured: dict[str, object]):
    def runner(app, host, port) -> None:
        captured.update({"app": app, "host": host, "port": port})

    return runner


def make_settings() -> Settings:
    return Settings(
        auth_host="0.0.0.0",
        auth_port=8000,
        data_host="0.0.0.0",
        data_port=8000,
        data_db_path="/tmp/micro.db",
        auth_service_url="http://auth:8000",
        data_service_url="http://data:8000",
        worker_service_name="worker",
        worker_poll_seconds=1,
    )


def test_auth_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(auth_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        auth_main.uvicorn,
        "run",
        capture_run(captured),
    )

    auth_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8000
    assert captured["app"].title == "Auth Service"


def test_data_main_starts_uvicorn(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    monkeypatch.setattr(data_main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        data_main.uvicorn,
        "run",
        capture_run(captured),
    )

    data_main.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8000
    assert captured["app"].title == "Data Service"


def test_worker_main_runs_forever(monkeypatch) -> None:
    settings = make_settings()
    captured: dict[str, object] = {}

    class FakeWorkerService:
        def __init__(self, data_client, poll_seconds: int) -> None:
            captured["data_client"] = data_client
            captured["poll_seconds"] = poll_seconds

        def run_forever(self) -> None:
            captured["started"] = True

    monkeypatch.setattr(worker_main, "get_settings", lambda: settings)
    monkeypatch.setattr(worker_main, "WorkerService", FakeWorkerService)

    worker_main.main()

    assert captured["poll_seconds"] == 1
    assert captured["started"] is True
