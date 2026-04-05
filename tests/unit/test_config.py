from __future__ import annotations

from pathlib import Path

import pytest

from showoff_api.config import Settings


@pytest.mark.unit
def test_settings_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_API_TOKEN", "token")
    monkeypatch.delenv("APP_DATABASE_PATH", raising=False)
    monkeypatch.delenv("APP_HOST", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)

    settings = Settings.from_env()

    assert settings == Settings(Path("data/notes.db"), "token", "0.0.0.0", 8000)


@pytest.mark.unit
def test_settings_from_env_uses_explicit_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("APP_API_TOKEN", "token")
    monkeypatch.setenv("APP_DATABASE_PATH", str(tmp_path / "notes.db"))
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("APP_PORT", "9000")

    settings = Settings.from_env()

    assert settings == Settings(tmp_path / "notes.db", "token", "127.0.0.1", 9000)


@pytest.mark.unit
def test_settings_from_env_requires_api_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_API_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="APP_API_TOKEN is required"):
        Settings.from_env()
