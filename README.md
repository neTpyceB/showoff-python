# Async Data Aggregator

Minimal production-ready async aggregation service.

## Features

- Concurrent upstream HTTP calls
- Merged response payload
- Explicit timeout handling
- Explicit retry handling
- Docker-first local run

## Stack

- Python 3.14.3
- FastAPI 0.135.2
- HTTPX 0.28.1
- Uvicorn 0.41.0
- `asyncio.TaskGroup`

## Run

```bash
docker compose up --build
```

Aggregator:

- `http://localhost:8000/docs`
- `http://localhost:8000/aggregate/ada`

Mock upstream:

- `http://localhost:9000/docs`

## Example

```bash
curl http://localhost:8000/aggregate/ada
```

## Checks

```bash
docker compose run --rm checks
```
