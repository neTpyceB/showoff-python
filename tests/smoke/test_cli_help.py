from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.smoke
def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "showoff_cli", "--help"],
        capture_output=True,
        check=True,
        text=True,
    )

    assert "search" in result.stdout
    assert "rename" in result.stdout
    assert "format" in result.stdout
