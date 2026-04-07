# AGENTS

## Operating Rules

- Keep scope limited to the event-platform requirements.
- Keep implementation minimal and production-ready.
- Use pinned current stable versions only.
- Run lint, tests, build, and Docker validation after every change.
- Keep repository docs aligned with the running distributed system.

## Project

- Name: Event-driven Platform
- Stack: FastAPI, Redis pub/sub, SQLite, Docker multi-container
- Services: platform, feed, notifications, audit
- Features: notification system, activity feed, audit/event log, eventual consistency
