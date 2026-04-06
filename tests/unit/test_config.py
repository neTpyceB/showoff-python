from __future__ import annotations

from showoff_micro.config import Settings, get_settings


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("MICRO_AUTH_HOST", "127.0.0.1")
    monkeypatch.setenv("MICRO_AUTH_PORT", "9001")
    monkeypatch.setenv("MICRO_DATA_HOST", "127.0.0.1")
    monkeypatch.setenv("MICRO_DATA_PORT", "9002")
    monkeypatch.setenv("MICRO_DATA_DB_PATH", "/tmp/micro.db")
    monkeypatch.setenv("MICRO_AUTH_SERVICE_URL", "http://auth.local")
    monkeypatch.setenv("MICRO_DATA_SERVICE_URL", "http://data.local")
    monkeypatch.setenv("MICRO_WORKER_SERVICE_NAME", "worker-local")
    monkeypatch.setenv("MICRO_WORKER_POLL_SECONDS", "5")

    assert Settings.from_env() == Settings(
        auth_host="127.0.0.1",
        auth_port=9001,
        data_host="127.0.0.1",
        data_port=9002,
        data_db_path="/tmp/micro.db",
        auth_service_url="http://auth.local",
        data_service_url="http://data.local",
        worker_service_name="worker-local",
        worker_poll_seconds=5,
    )


def test_get_settings_is_cached(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("MICRO_DATA_DB_PATH", "/tmp/first.db")

    first = get_settings()
    monkeypatch.setenv("MICRO_DATA_DB_PATH", "/tmp/second.db")
    second = get_settings()

    assert first is second
    assert second.data_db_path == "/tmp/first.db"
    get_settings.cache_clear()
