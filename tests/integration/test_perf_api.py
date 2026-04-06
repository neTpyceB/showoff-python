from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_perf.app import create_app
from showoff_perf.compute import PrimeService
from showoff_perf.config import Settings


class FakeCache:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.storage.get(key)

    def set(self, key: str, value: str, ex: int) -> None:
        self.storage[key] = value

    def ping(self) -> bool:
        return True


def make_client(pool_runner) -> TestClient:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        redis_url="redis://cache:6379/0",
        cache_ttl_seconds=300,
        default_workers=2,
        default_engine="auto",
    )
    service = PrimeService(
        settings=settings,
        cache=FakeCache(),
        pool_runner=pool_runner,
    )
    return TestClient(create_app(settings=settings, service=service))


@pytest.mark.integration
def test_python_engine_and_cache_flow() -> None:
    with make_client(lambda chunks, workers, engine: [17]) as client:
        first = client.post(
            "/prime-sums",
            json={"upper_bound": 10, "workers": 1, "engine": "python"},
        )
        second = client.post(
            "/prime-sums",
            json={"upper_bound": 10, "workers": 1, "engine": "python"},
        )

    assert first.status_code == 200
    assert first.json()["engine_used"] == "python"
    assert second.status_code == 200
    assert second.json()["cached"] is True


@pytest.mark.integration
def test_auto_engine_uses_available_optimizer() -> None:
    with make_client(lambda chunks, workers, engine: [17]) as client:
        response = client.post("/prime-sums", json={"upper_bound": 10})

    assert response.status_code == 200
    assert response.json()["engine_used"] in {"python", "cython"}
