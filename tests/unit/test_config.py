from __future__ import annotations

from showoff_pipeline.config import Settings, get_settings


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("PIPELINE_API_HOST", "127.0.0.1")
    monkeypatch.setenv("PIPELINE_API_PORT", "9000")
    monkeypatch.setenv("PIPELINE_DB_PATH", "/tmp/pipeline.db")
    monkeypatch.setenv("PIPELINE_INSERT_BATCH_SIZE", "25")

    assert Settings.from_env() == Settings(
        api_host="127.0.0.1",
        api_port=9000,
        db_path="/tmp/pipeline.db",
        insert_batch_size=25,
    )


def test_get_settings_is_cached(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("PIPELINE_DB_PATH", "/tmp/first.db")

    first = get_settings()
    monkeypatch.setenv("PIPELINE_DB_PATH", "/tmp/second.db")
    second = get_settings()

    assert first is second
    assert second.db_path == "/tmp/first.db"
    get_settings.cache_clear()
