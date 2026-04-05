# Security Audit

## Audit Date

- 2026-04-05

## Findings

- All CRUD endpoints require a bearer token.
- Default local token is provided through Docker Compose for local development only.
- No secrets are stored in the repository.
- SQLite writes are limited to the configured database path.

## Notes

- Replace `APP_API_TOKEN` in non-local environments.
