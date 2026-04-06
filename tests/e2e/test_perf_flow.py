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


@pytest.mark.e2e
def test_real_multiprocessing_flow() -> None:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        redis_url="redis://cache:6379/0",
        cache_ttl_seconds=300,
        default_workers=2,
        default_engine="python",
    )
    service = PrimeService(settings=settings, cache=FakeCache())
    app = create_app(settings=settings, service=service)

    with TestClient(app) as client:
        response = client.post(
            "/prime-sums",
            json={"upper_bound": 1000, "workers": 2, "engine": "python"},
        )

    assert response.status_code == 200
    assert response.json()["prime_sum"] == 76127
    assert response.json()["profile"]["peak_memory_bytes"] > 0
