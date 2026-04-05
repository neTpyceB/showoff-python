from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from showoff_cli.cli import main


@pytest.mark.unit
def test_main_runs_search_and_prints_matches(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / "match.txt"
    target.write_text("content", encoding="utf-8")

    result = main(["search", str(tmp_path), "*.txt"])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == str(target)


@pytest.mark.unit
def test_main_runs_rename_and_prints_changes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "old.txt"
    source.write_text("content", encoding="utf-8")

    result = main(["rename", str(tmp_path), "old", "new", "--glob", "*.txt"])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == f"{source} -> {tmp_path / 'new.txt'}"


@pytest.mark.unit
def test_main_runs_format_and_prints_destination(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = tmp_path / "data.json"
    output = tmp_path / "formatted.json"
    source.write_text('{"value":1}', encoding="utf-8")

    result = main(["format", "json", str(source), "--output", str(output)])

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == str(output)


@pytest.mark.unit
def test_module_entrypoint_exits_with_cli_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / "match.txt"
    target.write_text("content", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["showoff", "search", str(tmp_path), "*.txt"])

    with pytest.raises(SystemExit) as error:
        runpy.run_module("showoff_cli", run_name="__main__")

    captured = capsys.readouterr()
    assert error.value.code == 0
    assert captured.out.strip() == str(target)
