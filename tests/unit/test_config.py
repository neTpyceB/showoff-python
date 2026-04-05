from __future__ import annotations

import pytest

from showoff_queue.config import QueueSettings


@pytest.mark.unit
def test_settings_from_env_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QUEUE_BROKER_URL", raising=False)
    monkeypatch.delenv("QUEUE_RESULT_BACKEND", raising=False)
    monkeypatch.delenv("QUEUE_REDIS_URL", raising=False)
    monkeypatch.delenv("QUEUE_HEARTBEAT_KEY", raising=False)
    monkeypatch.delenv("QUEUE_HEARTBEAT_SECONDS", raising=False)
    monkeypatch.delenv("QUEUE_RETRY_MAX", raising=False)
    monkeypatch.delenv("QUEUE_API_HOST", raising=False)
    monkeypatch.delenv("QUEUE_API_PORT", raising=False)

    assert QueueSettings.from_env() == QueueSettings(
        broker_url="redis://redis:6379/0",
        result_backend="redis://redis:6379/1",
        redis_url="redis://redis:6379/2",
        heartbeat_key="queue:heartbeat",
        heartbeat_seconds=3,
        retry_max=2,
        host="0.0.0.0",
        port=8000,
    )


@pytest.mark.unit
def test_settings_from_env_uses_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUEUE_BROKER_URL", "redis://example/0")
    monkeypatch.setenv("QUEUE_RESULT_BACKEND", "redis://example/1")
    monkeypatch.setenv("QUEUE_REDIS_URL", "redis://example/2")
    monkeypatch.setenv("QUEUE_HEARTBEAT_KEY", "custom:heartbeat")
    monkeypatch.setenv("QUEUE_HEARTBEAT_SECONDS", "5")
    monkeypatch.setenv("QUEUE_RETRY_MAX", "4")
    monkeypatch.setenv("QUEUE_API_HOST", "127.0.0.1")
    monkeypatch.setenv("QUEUE_API_PORT", "9000")

    assert QueueSettings.from_env() == QueueSettings(
        broker_url="redis://example/0",
        result_backend="redis://example/1",
        redis_url="redis://example/2",
        heartbeat_key="custom:heartbeat",
        heartbeat_seconds=5,
        retry_max=4,
        host="127.0.0.1",
        port=9000,
    )
