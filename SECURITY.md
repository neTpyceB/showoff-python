# Security Audit

## Audit Date

- 2026-04-06

## Findings

- Public traffic is limited to the documented platform, feed, notification, and audit ports.
- Redis is restricted to internal Docker-network traffic for event fan-out.
- Each projection keeps its own SQLite volume for local persistence.
- No secrets or external credentials are required for local runtime.
