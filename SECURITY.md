# Security Audit

## Audit Date

- 2026-04-05

## Findings

- No network access is used by the application runtime.
- No secrets, tokens, or credentials are required.
- File writes are limited to the paths passed on the CLI.
- Rename and format commands mutate files directly by design.

## Dependency Posture

- Runtime dependencies: none outside Python standard library.
- Development dependencies are pinned to exact versions in `pyproject.toml`.
