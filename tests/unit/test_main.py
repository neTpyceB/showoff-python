from __future__ import annotations

import runpy
import sys

import pytest

from showoff_async.__main__ import main as aggregator_main
from showoff_async.config import AggregatorSettings, MockSettings
from showoff_async.mock_main import main as mock_main


@pytest.mark.unit
def test_aggregator_main_runs_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.1,
        retries=1,
        host="127.0.0.1",
        port=9000,
    )
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "showoff_async.config.AggregatorSettings.from_env",
        lambda: settings,
    )
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host, port: captured.update(app=app, host=host, port=port),
    )

    assert aggregator_main() == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9000


@pytest.mark.unit
def test_mock_main_runs_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = MockSettings(host="127.0.0.1", port=9010)
    captured: dict[str, object] = {}
    monkeypatch.setattr("showoff_async.config.MockSettings.from_env", lambda: settings)
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host, port: captured.update(app=app, host=host, port=port),
    )

    assert mock_main() == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9010


@pytest.mark.unit
def test_package_entrypoint_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    sys.modules.pop("showoff_async.__main__", None)
    monkeypatch.setattr(sys, "argv", ["showoff-aggregator"])
    monkeypatch.setattr(
        "showoff_async.config.AggregatorSettings.from_env",
        lambda: AggregatorSettings(
            profile_url="http://upstream.test/profile",
            activity_url="http://upstream.test/activity",
            status_url="http://upstream.test/status",
            timeout_seconds=0.1,
            retries=1,
            host="127.0.0.1",
            port=9000,
        ),
    )
    monkeypatch.setattr("uvicorn.run", lambda app, host, port: None)

    with pytest.raises(SystemExit) as error:
        runpy.run_module("showoff_async", run_name="__main__")

    assert error.value.code == 0


@pytest.mark.unit
def test_mock_entrypoint_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    sys.modules.pop("showoff_async.mock_main", None)
    monkeypatch.setattr(sys, "argv", ["showoff-mock-api"])
    monkeypatch.setattr(
        "showoff_async.config.MockSettings.from_env",
        lambda: MockSettings(host="127.0.0.1", port=9010),
    )
    monkeypatch.setattr("uvicorn.run", lambda app, host, port: None)

    with pytest.raises(SystemExit) as error:
        runpy.run_module("showoff_async.mock_main", run_name="__main__")

    assert error.value.code == 0
