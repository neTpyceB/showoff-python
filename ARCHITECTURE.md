# Architecture

## Services

- `api`: public FastAPI service for ingesting datasets and reading pipeline state.
- `sqlite`: local file-backed storage mounted into the API container.

## Domain

- Dataset type: CSV.
- Required columns: `timestamp`, `account`, `amount`.
- Transform: normalize `account`, parse `timestamp`, convert `amount` to cents.
- Storage: `pipeline_runs` metadata table plus `etl_records` transformed row table.

## Structure

- `src/showoff_pipeline/config.py`: environment-driven runtime settings.
- `src/showoff_pipeline/pipeline.py`: schema management, ingest, transform, and store logic.
- `src/showoff_pipeline/app.py`: FastAPI routes and dependency wiring.
- `src/showoff_pipeline/models.py`: API response models and execution modes.
- `src/showoff_pipeline/__main__.py`: API process entrypoint.

## Execution Modes

- `stream`: reads and inserts rows in bounded batches for stable memory usage.
- `batch`: materializes the dataset before insert to expose the batch tradeoff explicitly.

## Monitoring

- `/monitoring` returns run totals, success and failure counts, stored row totals, and the latest completion time.
- Application logging emits run start, success, and failure events.
