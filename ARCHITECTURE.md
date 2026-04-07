# Architecture

## Services

- `platform`: accepts activity events over HTTP and publishes them to Redis.
- `feed`: subscribes to the bus and maintains a user activity feed projection.
- `notifications`: subscribes to the bus and maintains user notifications.
- `audit`: subscribes to the bus and persists the full event log.
- `redis`: event bus for fan-out delivery.

## Flow

- Clients publish `activity.created` events to `platform`.
- `platform` writes nothing locally and only emits to the bus.
- `feed`, `notifications`, and `audit` react asynchronously and persist their own SQLite read models.
- Reads are eventually consistent because projections update after publish.

## Structure

- `src/showoff_event/config.py`: environment-driven service settings.
- `src/showoff_event/bus.py`: Redis publisher and subscriber loop.
- `src/showoff_event/store.py`: SQLite projection stores.
- `src/showoff_event/platform_app.py`: event publishing API.
- `src/showoff_event/feed_app.py`: feed API plus subscriber.
- `src/showoff_event/notification_app.py`: notification API plus subscriber.
- `src/showoff_event/audit_app.py`: audit API plus subscriber.
