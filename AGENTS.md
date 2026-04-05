# AGENTS

## Operating Rules

- Keep scope limited to the async aggregation requirements.
- Keep implementation minimal and production-ready.
- Use pinned current stable versions only.
- Run lint, tests, build, and Docker validation after every change.
- Keep repository docs aligned with the running service.

## Project

- Name: Async Data Aggregator
- Stack: FastAPI, asyncio, httpx, Docker
- Features: concurrent API calls, merged result, timeout handling, retry handling
