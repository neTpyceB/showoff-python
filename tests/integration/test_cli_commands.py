from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "showoff_cli", *args],
        capture_output=True,
        check=True,
        cwd=cwd,
        text=True,
    )


@pytest.mark.integration
def test_search_command_lists_matches(tmp_path: Path) -> None:
    target = tmp_path / "match.txt"
    target.write_text("content", encoding="utf-8")

    result = run_cli("search", str(tmp_path), "*.txt", cwd=tmp_path)

    assert result.stdout.strip() == str(target)


@pytest.mark.integration
def test_rename_command_renames_files_with_glob(tmp_path: Path) -> None:
    source = tmp_path / "old-name.txt"
    source.write_text("content", encoding="utf-8")

    result = run_cli(
        "rename",
        str(tmp_path),
        "old",
        "new",
        "--glob",
        "*.txt",
        cwd=tmp_path,
    )

    assert result.stdout.strip() == f"{source} -> {tmp_path / 'new-name.txt'}"
    assert not source.exists()
    assert (tmp_path / "new-name.txt").exists()


@pytest.mark.integration
def test_format_command_writes_output_file(tmp_path: Path) -> None:
    source = tmp_path / "data.json"
    output = tmp_path / "formatted.json"
    source.write_text('{"value":1}', encoding="utf-8")

    result = run_cli(
        "format",
        "json",
        str(source),
        "--output",
        str(output),
        cwd=tmp_path,
    )

    assert result.stdout.strip() == str(output)
    assert output.read_text(encoding="utf-8") == '{\n  "value": 1\n}\n'
