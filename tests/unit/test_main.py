from __future__ import annotations

import runpy
import sys

import pytest

from showoff_queue.__main__ import main
from showoff_queue.config import QueueSettings


@pytest.mark.unit
def test_main_runs_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = QueueSettings(
        broker_url="memory://",
        result_backend="cache+memory://",
        redis_url="redis://redis:6379/2",
        heartbeat_key="queue:heartbeat",
        heartbeat_seconds=3,
        retry_max=2,
        host="127.0.0.1",
        port=9000,
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr("showoff_queue.config.QueueSettings.from_env", lambda: settings)
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host, port: captured.update(app=app, host=host, port=port),
    )

    assert main() == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9000


@pytest.mark.unit
def test_package_entrypoint_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    sys.modules.pop("showoff_queue.__main__", None)
    monkeypatch.setattr(sys, "argv", ["showoff-queue-api"])
    monkeypatch.setattr(
        "showoff_queue.config.QueueSettings.from_env",
        lambda: QueueSettings(
            broker_url="memory://",
            result_backend="cache+memory://",
            redis_url="redis://redis:6379/2",
            heartbeat_key="queue:heartbeat",
            heartbeat_seconds=3,
            retry_max=2,
            host="127.0.0.1",
            port=9000,
        ),
    )
    monkeypatch.setattr("uvicorn.run", lambda app, host, port: None)

    with pytest.raises(SystemExit) as error:
        runpy.run_module("showoff_queue", run_name="__main__")

    assert error.value.code == 0
