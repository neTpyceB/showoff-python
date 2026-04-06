from __future__ import annotations

from showoff_perf.config import Settings, get_settings


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("PERF_API_HOST", "127.0.0.1")
    monkeypatch.setenv("PERF_API_PORT", "9000")
    monkeypatch.setenv("PERF_REDIS_URL", "redis://cache:6379/0")
    monkeypatch.setenv("PERF_CACHE_TTL_SECONDS", "42")
    monkeypatch.setenv("PERF_DEFAULT_WORKERS", "4")
    monkeypatch.setenv("PERF_DEFAULT_ENGINE", "python")

    assert Settings.from_env() == Settings(
        api_host="127.0.0.1",
        api_port=9000,
        redis_url="redis://cache:6379/0",
        cache_ttl_seconds=42,
        default_workers=4,
        default_engine="python",
    )


def test_get_settings_is_cached(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("PERF_REDIS_URL", "redis://first:6379/0")

    first = get_settings()
    monkeypatch.setenv("PERF_REDIS_URL", "redis://second:6379/0")
    second = get_settings()

    assert first is second
    assert second.redis_url == "redis://first:6379/0"
    get_settings.cache_clear()
