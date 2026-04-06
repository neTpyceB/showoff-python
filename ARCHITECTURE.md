# Architecture

## Services

- `auth`: token issuance and validation service.
- `data`: job storage and public read/write API.
- `worker`: background processor polling the data service.

## Communication

- Clients call `auth` for tokens.
- Clients call `data` with `Authorization: Bearer <token>`.
- `data` validates tokens by calling `auth /validate`.
- `worker` claims and completes jobs through `data` internal endpoints.

## Service Discovery

- `auth /discovery` and `data /discovery` expose the configured service addresses.
- Docker service names provide the runtime lookup mechanism: `auth`, `data`, `worker`.
- Compose health checks gate startup so the worker starts only after the APIs are live.
- The worker uses an on-failure restart policy so it recovers if the data service restarts.

## Structure

- `src/showoff_micro/config.py`: environment-driven service settings.
- `src/showoff_micro/auth_app.py`: auth service API.
- `src/showoff_micro/data_app.py`: data service API.
- `src/showoff_micro/store.py`: SQLite job storage.
- `src/showoff_micro/auth_client.py`: auth-service HTTP client.
- `src/showoff_micro/data_client.py`: data-service HTTP client for the worker.
- `src/showoff_micro/worker_service.py`: worker loop and job processing.
- `src/showoff_micro/auth_main.py`: auth entrypoint.
- `src/showoff_micro/data_main.py`: data entrypoint.
- `src/showoff_micro/worker_main.py`: worker entrypoint.
