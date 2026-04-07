# Event-driven Platform

Minimal production-ready event-driven backend with Redis pub/sub and async projections.

## Features

- Platform API publishing events
- Notification service
- Activity feed service
- Audit log service
- Eventual consistency through async projections
- Docker multi-container runtime
- Redis event bus

## Stack

- Python 3.14.3
- FastAPI 0.135.3
- redis-py 7.4.0
- Uvicorn 0.44.0
- SQLite (stdlib)
- Redis 8.6.2

## Run

```bash
docker compose up --build
```

Service docs:

- Platform API: `http://localhost:8000/docs`
- Feed Service: `http://localhost:8001/docs`
- Notification Service: `http://localhost:8002/docs`
- Audit Service: `http://localhost:8003/docs`

## Example

```bash
curl -X POST http://localhost:8000/events/activities \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","title":"Trip completed","detail":"Airport pickup"}'
```

```bash
curl http://localhost:8001/users/alice/feed
```

```bash
curl http://localhost:8002/users/alice/notifications
```

```bash
curl http://localhost:8003/events
```

## Checks

```bash
docker compose run --rm checks
```
