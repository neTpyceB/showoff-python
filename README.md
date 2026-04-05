# Report Generation Queue

Minimal production-ready queue system with FastAPI, Celery, and Redis.

## Features

- Background report jobs
- Celery retries
- Celery Beat scheduling
- Job status API
- Docker-first local run

## Stack

- Python 3.14.3
- FastAPI 0.135.2
- Celery 5.6.3
- Redis 6.4.0 client
- Redis 8.6.2-alpine server
- Uvicorn 0.42.0

## Run

```bash
docker compose up --build
```

API:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## Example

```bash
curl -X POST http://localhost:8000/jobs/reports \
  -H "Content-Type: application/json" \
  -d '{"report_id":"demo","content":"celery jobs run in the background"}'
```

## Checks

```bash
docker compose run --rm checks
```
