# ETL Pipeline System

Minimal production-ready ETL service with FastAPI and SQLite.

## Features

- Ingest CSV datasets
- Transform rows into normalized records
- Store transformed data in SQLite
- Streaming and batch execution modes
- Logging and monitoring endpoint
- Docker-first local run

## Stack

- Python 3.14.0
- FastAPI 0.135.3
- Uvicorn 0.43.0
- python-multipart 0.0.24
- SQLite (stdlib)

## Run

```bash
docker compose up --build
```

API:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`
- `http://localhost:8000/monitoring`

## Example

```bash
curl -X POST "http://localhost:8000/pipeline/runs?mode=stream" \
  -F "file=@sample.csv"
```

Expected CSV columns:

```csv
timestamp,account,amount
2026-01-01T10:00:00+00:00,Acme,10.50
```

## Checks

```bash
docker compose run --rm checks
```
