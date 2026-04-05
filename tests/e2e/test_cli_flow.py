from __future__ import annotations

import json
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


@pytest.mark.e2e
def test_end_to_end_flow(tmp_path: Path) -> None:
    json_file = tmp_path / "draft-report.json"
    csv_file = tmp_path / "draft-data.csv"
    formatted_csv = tmp_path / "clean-data.csv"

    json_file.write_text('{"name":"Ada","skills":["python","cli"]}', encoding="utf-8")
    csv_file.write_text("name,age\r\nAda,36\r\n", encoding="utf-8")

    search = run_cli("search", str(tmp_path), "*.json", cwd=tmp_path)
    assert str(json_file) in search.stdout

    rename = run_cli(
        "rename",
        str(tmp_path),
        "draft",
        "final",
        "--glob",
        "*.json",
        cwd=tmp_path,
    )
    renamed_file = tmp_path / "final-report.json"
    assert f"{json_file} -> {renamed_file}" in rename.stdout

    formatted_json = run_cli("format", "json", str(renamed_file), cwd=tmp_path)
    assert str(renamed_file) in formatted_json.stdout
    assert json.loads(renamed_file.read_text(encoding="utf-8")) == {
        "name": "Ada",
        "skills": ["python", "cli"],
    }

    formatted = run_cli(
        "format",
        "csv",
        str(csv_file),
        "--output",
        str(formatted_csv),
        cwd=tmp_path,
    )
    assert str(formatted_csv) in formatted.stdout
    assert formatted_csv.read_text(encoding="utf-8") == "name,age\nAda,36\n"
