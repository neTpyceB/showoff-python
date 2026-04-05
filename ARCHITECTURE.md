# Architecture

## Services

- `aggregator`: public FastAPI service exposing `/aggregate/{user_id}`.
- `mock-api`: local upstream service exposing `/profile/{user_id}`, `/activity/{user_id}`, and `/status/{user_id}`.

## Structure

- `src/showoff_async/config.py`: environment-driven runtime settings.
- `src/showoff_async/service.py`: concurrent fetch, retry, timeout, and merge logic.
- `src/showoff_async/app.py`: aggregator FastAPI app.
- `src/showoff_async/mock_app.py`: local upstream FastAPI app for runtime validation.
- `src/showoff_async/models.py`: request and response models.
- `src/showoff_async/__main__.py`: aggregator process entrypoint.
- `src/showoff_async/mock_main.py`: mock upstream process entrypoint.

## Concurrency Model

- One request fans out to three upstream HTTP calls.
- `asyncio.TaskGroup` runs the calls concurrently.
- Each upstream call uses an `httpx.AsyncClient` with explicit timeout.
- Retries are handled in the aggregator, not by the HTTP client.

## Failure Model

- If any source still fails after retry exhaustion, the whole aggregation fails.
- Timeout exhaustion returns `504`.
- Other upstream failures return `502`.
