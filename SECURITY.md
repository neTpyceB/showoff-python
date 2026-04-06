# Security Audit

## Audit Date

- 2026-04-06

## Findings

- Public traffic is limited to the auth and data services.
- Token validation is delegated from data to auth over the internal Docker network.
- SQLite storage is mounted only into the data container.
- Worker-only endpoints are exposed only on the internal data service port.
- No secrets or external credentials are required for local runtime.
