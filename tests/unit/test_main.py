from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from showoff_api.__main__ import main
from showoff_api.config import Settings


@pytest.mark.unit
def test_main_runs_uvicorn(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    settings = Settings(tmp_path / "notes.db", "token", "127.0.0.1", 9000)
    captured: dict[str, object] = {}

    monkeypatch.setattr("showoff_api.__main__.Settings.from_env", lambda: settings)

    def fake_run(app: object, host: str, port: int) -> None:
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port

    monkeypatch.setattr("showoff_api.__main__.uvicorn.run", fake_run)

    assert main() == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9000
    assert captured["app"].title == "Notes REST API Service"


@pytest.mark.unit
def test_module_entrypoint_exits_with_main_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(sys, "argv", ["showoff-api"])
    sys.modules.pop("showoff_api.__main__", None)
    settings = Settings(tmp_path / "notes.db", "token", "127.0.0.1", 9000)
    monkeypatch.setattr("showoff_api.config.Settings.from_env", lambda: settings)
    monkeypatch.setattr("uvicorn.run", lambda app, host, port: None)

    with pytest.raises(SystemExit) as error:
        runpy.run_module("showoff_api.__main__", run_name="__main__")

    assert error.value.code == 0
