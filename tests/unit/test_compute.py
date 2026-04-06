from __future__ import annotations

import json

import pytest

from showoff_perf.compute import (
    CYTHON_AVAILABLE,
    CythonUnavailableError,
    PrimeService,
    _chunk_ranges,
    _sum_chunk,
)
from showoff_perf.config import Settings
from showoff_perf.models import Engine, PrimeSumRequest


class FakeCache:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.storage.get(key)

    def set(self, key: str, value: str, ex: int) -> None:
        self.storage[key] = value

    def ping(self) -> bool:
        return True


def make_service(pool_runner) -> PrimeService:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        redis_url="redis://cache:6379/0",
        cache_ttl_seconds=300,
        default_workers=2,
        default_engine="auto",
    )
    return PrimeService(settings=settings, cache=FakeCache(), pool_runner=pool_runner)


def test_chunk_ranges_split_evenly() -> None:
    assert _chunk_ranges(10, 2) == [(2, 7), (7, 11)]
    assert _chunk_ranges(1, 2) == [(2, 2)]


def test_health_reports_cache_and_cython() -> None:
    service = make_service(lambda chunks, workers, engine: [17])

    assert service.health() == {
        "status": "ok",
        "cache": "ok",
        "cython_available": CYTHON_AVAILABLE,
    }


def test_analyze_computes_and_caches_result() -> None:
    captured: dict[str, object] = {}

    def fake_pool_runner(chunks, workers, engine):
        captured["chunks"] = chunks
        captured["workers"] = workers
        captured["engine"] = engine
        return [5, 12]

    service = make_service(fake_pool_runner)

    response = service.analyze(
        PrimeSumRequest(upper_bound=10, workers=2, engine=Engine.PYTHON)
    )

    assert response.prime_sum == 17
    assert response.cached is False
    assert response.engine_used is Engine.PYTHON
    assert captured["chunks"] == [(2, 7), (7, 11)]
    cached_document = json.loads(service._cache.storage["prime-sum:10:2:python"])
    assert cached_document["prime_sum"] == 17


def test_analyze_returns_cached_document() -> None:
    service = make_service(lambda chunks, workers, engine: [17])
    service._cache.storage["prime-sum:10:2:python"] = json.dumps(
        {
            "upper_bound": 10,
            "workers": 2,
            "engine_requested": "python",
            "engine_used": "python",
            "cached": False,
            "prime_sum": 17,
            "profile": {
                "cpu_seconds": 0.1,
                "peak_memory_bytes": 64,
                "top_function": "sum_primes_in_range",
            },
        }
    )

    response = service.analyze(
        PrimeSumRequest(upper_bound=10, workers=2, engine=Engine.PYTHON)
    )

    assert response.cached is True
    assert response.prime_sum == 17


def test_auto_engine_uses_cython_when_available() -> None:
    service = make_service(lambda chunks, workers, engine: [0])

    response = service.analyze(PrimeSumRequest(upper_bound=1, workers=1))

    expected_engine = Engine.CYTHON if CYTHON_AVAILABLE else Engine.PYTHON
    assert response.engine_used is expected_engine


def test_cython_request_fails_when_unavailable(monkeypatch) -> None:
    service = make_service(lambda chunks, workers, engine: [0])
    monkeypatch.setattr("showoff_perf.compute.CYTHON_AVAILABLE", False)

    with pytest.raises(CythonUnavailableError):
        service.analyze(
            PrimeSumRequest(upper_bound=10, workers=1, engine=Engine.CYTHON)
        )


def test_sum_chunk_uses_python_engine() -> None:
    assert _sum_chunk(2, 10, Engine.PYTHON) == 17


def test_sum_chunk_uses_cython_engine_when_available(monkeypatch) -> None:
    if CYTHON_AVAILABLE:
        assert _sum_chunk(2, 10, Engine.CYTHON) == 17
        return

    monkeypatch.setattr("showoff_perf.compute.CYTHON_AVAILABLE", False)
    with pytest.raises(CythonUnavailableError):
        _sum_chunk(2, 10, Engine.CYTHON)
