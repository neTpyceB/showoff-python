from __future__ import annotations

import csv
import io
import json
from pathlib import Path


def search_files(root: Path, pattern: str) -> list[Path]:
    return sorted(path for path in root.rglob(pattern) if path.is_file())


def batch_rename(
    root: Path,
    find: str,
    replace: str,
    glob: str = "*",
) -> list[tuple[Path, Path]]:
    renamed: list[tuple[Path, Path]] = []
    for path in sorted(
        (candidate for candidate in root.rglob(glob) if candidate.is_file()),
        key=str,
    ):
        if find not in path.name:
            continue
        target = path.with_name(path.name.replace(find, replace))
        path.rename(target)
        renamed.append((path, target))
    return renamed


def format_json(text: str) -> str:
    return f"{json.dumps(json.loads(text), indent=2, ensure_ascii=False)}\n"


def format_csv(text: str) -> str:
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(
        csv.reader(io.StringIO(text)),
    )
    return buffer.getvalue()


def format_file(kind: str, source: Path, output: Path | None = None) -> Path:
    text = source.read_text(encoding="utf-8")
    formatted = format_json(text) if kind == "json" else format_csv(text)
    destination = output or source
    destination.write_text(formatted, encoding="utf-8", newline="")
    return destination
