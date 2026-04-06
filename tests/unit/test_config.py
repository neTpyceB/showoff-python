from __future__ import annotations

from showoff_saas.config import Settings, get_settings


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("SAAS_API_HOST", "127.0.0.1")
    monkeypatch.setenv("SAAS_API_PORT", "9000")
    monkeypatch.setenv("SAAS_DB_PATH", "/tmp/saas.db")

    assert Settings.from_env() == Settings(
        api_host="127.0.0.1",
        api_port=9000,
        db_path="/tmp/saas.db",
    )


def test_get_settings_is_cached(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("SAAS_DB_PATH", "/tmp/first.db")

    first = get_settings()
    monkeypatch.setenv("SAAS_DB_PATH", "/tmp/second.db")
    second = get_settings()

    assert first is second
    assert second.db_path == "/tmp/first.db"
    get_settings.cache_clear()
