# Notes REST API Service

Minimal production-ready FastAPI backend for personal notes.

## Features

- CRUD endpoints for notes
- Pydantic request validation
- OpenAPI and Swagger docs
- Bearer token authentication
- SQLite persistence
- Docker-first local run

## Stack

- Python 3.14.3
- FastAPI 0.135.2
- Uvicorn 0.41.0
- SQLite

## Run

```bash
docker compose up --build api
```

API:

- `http://localhost:8000/docs`
- `http://localhost:8000/openapi.json`

Default local bearer token:

- `local-token`

## Example Requests

```bash
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer local-token" \
  -H "Content-Type: application/json" \
  -d '{"title":"First note","content":"Production-ready FastAPI."}'

curl http://localhost:8000/notes \
  -H "Authorization: Bearer local-token"
```

## Checks

```bash
docker compose run --rm checks
```
