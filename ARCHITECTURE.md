# Architecture

## Services

- `api`: public FastAPI service for submitting jobs and reading status.
- `worker`: Celery worker for background processing.
- `beat`: Celery beat scheduler for periodic tasks.
- `redis`: broker, result backend, and shared state store.

## Domain

- Job type: report generation.
- Input: `report_id`, `content`.
- Output: `report_id`, `line_count`, `word_count`, `checksum`.

## Structure

- `src/showoff_queue/config.py`: environment-driven runtime settings.
- `src/showoff_queue/queue.py`: Celery app, tasks, retry policy, and scheduling.
- `src/showoff_queue/app.py`: FastAPI routes and dependency wiring.
- `src/showoff_queue/models.py`: request and response models.
- `src/showoff_queue/__main__.py`: API process entrypoint.

## Scheduling

- Celery Beat runs `showoff_queue.record_heartbeat` on a fixed interval.
- The task writes the latest heartbeat timestamp into Redis.
- The API exposes the latest timestamp at `/schedules/heartbeat`.
