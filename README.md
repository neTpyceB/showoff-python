# Multi-tenant SaaS Backend

Minimal production-ready SaaS backend with organization scoping, RBAC, billing mock, and audit logs.

## Features

- Organizations
- Multi-tenant organization scoping
- Role-based access with `admin` and `member`
- Billing mock checkout flow
- Audit logs for mutating operations
- Docker-first local run

## Stack

- Python 3.14.3
- FastAPI 0.135.3
- Uvicorn 0.43.0
- SQLite (stdlib)

## Run

```bash
docker compose up --build
```

API:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

All tenant-scoped requests require the `X-User-Id` header.

## Example

```bash
curl -X POST http://localhost:8000/organizations \
  -H "Content-Type: application/json" \
  -H "X-User-Id: alice" \
  -d '{"name":"Acme"}'
```

## Checks

```bash
docker compose run --rm checks
```
