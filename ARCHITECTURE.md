# Architecture

## Services

- `api`: FastAPI service exposing the optimization endpoint.
- `redis`: cache store for repeated computations.

## Domain

- Workload: sum of primes up to `upper_bound`.
- Engines: `python`, `cython`, `auto`.
- Cache key: `upper_bound + workers + engine request`.
- Profile output: CPU seconds, peak memory bytes, and hottest function name.

## Structure

- `src/showoff_perf/config.py`: environment-driven runtime settings.
- `src/showoff_perf/cache.py`: Redis cache adapter.
- `src/showoff_perf/kernels.py`: pure Python prime kernel.
- `src/showoff_perf/cykernels.pyx`: Cython prime kernel.
- `src/showoff_perf/compute.py`: profiling, caching, engine selection, and multiprocessing orchestration.
- `src/showoff_perf/app.py`: FastAPI routes.
- `src/showoff_perf/__main__.py`: API process entrypoint.

## Execution Model

- Requests are profiled with `cProfile` and `tracemalloc`.
- Work is split into numeric chunks and executed with `multiprocessing.Pool`.
- Cache hits return the stored result payload with `cached=true`.
- `auto` prefers Cython when the extension is available.
