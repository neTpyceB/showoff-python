# Architecture

## Domain

- Entity: `Note`
- Fields: `id`, `title`, `content`

## Structure

- `src/showoff_api/config.py`: environment-driven runtime settings.
- `src/showoff_api/auth.py`: bearer token enforcement.
- `src/showoff_api/repository.py`: SQLite persistence.
- `src/showoff_api/schemas.py`: request and response models.
- `src/showoff_api/app.py`: FastAPI application factory and routes.
- `src/showoff_api/__main__.py`: process entrypoint.

## Request Flow

1. FastAPI validates the request.
2. Bearer auth dependency verifies the token.
3. Route handler calls the repository.
4. Response model shapes the output.

## Persistence

- SQLite database file path comes from `APP_DATABASE_PATH`.
- Schema is created on startup if missing.
