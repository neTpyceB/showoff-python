# Microservices System

Minimal production-ready distributed backend with auth, data, and worker services.

## Features

- Auth service
- Data service
- Worker service
- Service-to-service HTTP communication
- Basic service discovery endpoints
- Docker multi-container runtime
- Health-gated startup ordering
- Worker auto-restart on failure

## Stack

- Python 3.14.3
- FastAPI 0.135.3
- Uvicorn 0.44.0
- SQLite (stdlib)

## Run

```bash
docker compose up --build
```

Service docs:

- Auth: `http://localhost:8001/docs`
- Data: `http://localhost:8002/docs`

## Example

```bash
curl -X POST http://localhost:8001/tokens \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice"}'
```

```bash
curl -X POST http://localhost:8002/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer alice" \
  -d '{"payload":"hello distributed world"}'
```

## Checks

```bash
docker compose run --rm checks
```
