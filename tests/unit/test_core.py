from __future__ import annotations

from pathlib import Path

import pytest

from showoff_cli.core import (
    batch_rename,
    format_csv,
    format_file,
    format_json,
    search_files,
)


@pytest.mark.unit
def test_search_files_returns_sorted_matches(tmp_path: Path) -> None:
    first = tmp_path / "b.txt"
    second = tmp_path / "a.txt"
    third = tmp_path / "a.md"
    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    third.write_text("", encoding="utf-8")

    assert search_files(tmp_path, "*.txt") == [second, first]


@pytest.mark.unit
def test_batch_rename_skips_non_matching_names(tmp_path: Path) -> None:
    source = tmp_path / "old.txt"
    untouched = tmp_path / "keep.txt"
    source.write_text("", encoding="utf-8")
    untouched.write_text("", encoding="utf-8")

    renamed = batch_rename(tmp_path, "old", "new", "*.txt")

    assert renamed == [(source, tmp_path / "new.txt")]
    assert not source.exists()
    assert untouched.exists()


@pytest.mark.unit
def test_format_json_pretty_prints() -> None:
    assert format_json('{"value":1}') == '{\n  "value": 1\n}\n'


@pytest.mark.unit
def test_format_csv_normalizes_newlines() -> None:
    assert format_csv("name,age\r\nAda,36\r\n") == "name,age\nAda,36\n"


@pytest.mark.unit
def test_format_file_rewrites_source_in_place(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("name,age\r\nAda,36\r\n", encoding="utf-8")

    destination = format_file("csv", source)

    assert destination == source
    assert source.read_text(encoding="utf-8") == "name,age\nAda,36\n"
