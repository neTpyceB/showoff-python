from __future__ import annotations

import cProfile
import json
import multiprocessing
import pstats
import tracemalloc
from math import ceil

from .cache import Cache
from .config import Settings
from .kernels import sum_primes_in_range as py_sum_primes_in_range
from .models import Engine, PrimeSumRequest, PrimeSumResponse, ProfileResponse

try:
    from .cykernels import sum_primes_in_range as cy_sum_primes_in_range

    CYTHON_AVAILABLE = True  # pragma: no cover
except ImportError:  # pragma: no cover
    CYTHON_AVAILABLE = False
    cy_sum_primes_in_range = None


class CythonUnavailableError(RuntimeError):
    """Raised when Cython execution is requested but unavailable."""


def _chunk_ranges(upper_bound: int, workers: int) -> list[tuple[int, int]]:
    if upper_bound < 2:
        return [(2, 2)]
    span = upper_bound - 1
    chunk_size = max(1, ceil(span / workers))
    chunks: list[tuple[int, int]] = []
    start = 2
    while start <= upper_bound:
        stop = min(start + chunk_size, upper_bound + 1)
        chunks.append((start, stop))
        start = stop
    return chunks


def _sum_chunk(start: int, stop: int, engine: Engine) -> int:
    if engine is Engine.CYTHON:
        if not CYTHON_AVAILABLE:
            raise CythonUnavailableError("Cython optimization is not available")
        return int(cy_sum_primes_in_range(start, stop))  # pragma: no cover
    return py_sum_primes_in_range(start, stop)


def _pool_runner(
    chunks: list[tuple[int, int]],
    workers: int,
    engine: Engine,
) -> list[int]:
    with multiprocessing.Pool(processes=workers) as pool:
        payload = [(start, stop, engine) for start, stop in chunks]
        return pool.starmap(_sum_chunk, payload)


class PrimeService:
    def __init__(
        self,
        settings: Settings,
        cache: Cache,
        pool_runner=_pool_runner,
    ) -> None:
        self._settings = settings
        self._cache = cache
        self._pool_runner = pool_runner

    def health(self) -> dict[str, str | bool]:
        return {
            "status": "ok",
            "cache": "ok" if self._cache.ping() else "down",
            "cython_available": CYTHON_AVAILABLE,
        }

    def analyze(self, payload: PrimeSumRequest) -> PrimeSumResponse:
        workers = payload.workers or self._settings.default_workers
        engine_requested = payload.engine or Engine(self._settings.default_engine)
        engine_used = self._resolve_engine(engine_requested)
        cache_key = (
            f"prime-sum:{payload.upper_bound}:{workers}:{engine_requested.value}"
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            document = json.loads(cached)
            document["cached"] = True
            return PrimeSumResponse.model_validate(document)

        response = self._profile_compute(
            upper_bound=payload.upper_bound,
            workers=workers,
            engine_requested=engine_requested,
            engine_used=engine_used,
        )
        self._cache.set(
            cache_key,
            response.model_dump_json(),
            ex=self._settings.cache_ttl_seconds,
        )
        return response

    def _profile_compute(
        self,
        upper_bound: int,
        workers: int,
        engine_requested: Engine,
        engine_used: Engine,
    ) -> PrimeSumResponse:
        profiler = cProfile.Profile()
        tracemalloc.start()
        prime_sum = profiler.runcall(self._compute, upper_bound, workers, engine_used)
        _, peak_memory_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        stats = pstats.Stats(profiler)
        top_entry = max(stats.stats.items(), key=lambda entry: entry[1][3])
        top_function = top_entry[0][2]
        cpu_seconds = round(sum(item[3] for item in stats.stats.values()), 6)
        return PrimeSumResponse(
            upper_bound=upper_bound,
            workers=workers,
            engine_requested=engine_requested,
            engine_used=engine_used,
            cached=False,
            prime_sum=prime_sum,
            profile=ProfileResponse(
                cpu_seconds=cpu_seconds,
                peak_memory_bytes=peak_memory_bytes,
                top_function=top_function,
            ),
        )

    def _compute(self, upper_bound: int, workers: int, engine: Engine) -> int:
        chunks = _chunk_ranges(upper_bound, workers)
        return sum(self._pool_runner(chunks, workers, engine))

    def _resolve_engine(self, engine: Engine) -> Engine:
        if engine is Engine.AUTO:
            return Engine.CYTHON if CYTHON_AVAILABLE else Engine.PYTHON
        if engine is Engine.CYTHON and not CYTHON_AVAILABLE:
            raise CythonUnavailableError("Cython optimization is not available")
        return engine
