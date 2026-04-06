# High-performance Service

Minimal production-ready optimization service with profiling, Redis caching, multiprocessing, and a Cython execution path.

## Features

- CPU and memory profiling
- Redis-backed result caching
- Multiprocessing execution
- Python and Cython engines
- Docker-first local run

## Stack

- Python 3.14.3
- FastAPI 0.135.3
- Uvicorn 0.44.0
- redis-py 7.4.0
- Redis 8.6.2-alpine
- Cython 3.2.4

## Run

```bash
docker compose up --build
```

API:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## Example

```bash
curl -X POST http://localhost:8000/prime-sums \
  -H "Content-Type: application/json" \
  -d '{"upper_bound":100000,"workers":2,"engine":"auto"}'
```

## Checks

```bash
docker compose run --rm checks
```
