from __future__ import annotations

import pytest

from showoff_async.config import AggregatorSettings, MockSettings


@pytest.mark.unit
def test_aggregator_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGGREGATOR_PROFILE_URL", "http://example.test/profile")
    monkeypatch.setenv("AGGREGATOR_ACTIVITY_URL", "http://example.test/activity")
    monkeypatch.setenv("AGGREGATOR_STATUS_URL", "http://example.test/status")
    monkeypatch.setenv("AGGREGATOR_TIMEOUT_SECONDS", "0.2")
    monkeypatch.setenv("AGGREGATOR_RETRIES", "3")
    monkeypatch.setenv("AGGREGATOR_HOST", "127.0.0.1")
    monkeypatch.setenv("AGGREGATOR_PORT", "9001")

    settings = AggregatorSettings.from_env()

    assert settings == AggregatorSettings(
        profile_url="http://example.test/profile",
        activity_url="http://example.test/activity",
        status_url="http://example.test/status",
        timeout_seconds=0.2,
        retries=3,
        host="127.0.0.1",
        port=9001,
    )


@pytest.mark.unit
def test_aggregator_settings_require_upstream_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGGREGATOR_PROFILE_URL", raising=False)
    monkeypatch.delenv("AGGREGATOR_ACTIVITY_URL", raising=False)
    monkeypatch.delenv("AGGREGATOR_STATUS_URL", raising=False)

    with pytest.raises(RuntimeError, match="AGGREGATOR_PROFILE_URL is required"):
        AggregatorSettings.from_env()


@pytest.mark.unit
def test_mock_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOCK_API_HOST", "127.0.0.1")
    monkeypatch.setenv("MOCK_API_PORT", "9010")

    assert MockSettings.from_env() == MockSettings(host="127.0.0.1", port=9010)
