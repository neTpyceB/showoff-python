# Architecture

## Structure

- `src/showoff_cli/cli.py`: CLI parser and command handlers.
- `src/showoff_cli/core.py`: pure filesystem and formatting operations.
- `tests/`: unit, integration, smoke, and end-to-end coverage.
- `Dockerfile`: multi-stage container build.
- `compose.yaml`: local runtime and check services.

## Command Model

- `search`: recursive filename search from a root path.
- `rename`: recursive file rename by string replacement inside file names.
- `format`: in-place or redirected JSON/CSV normalization.

## Design Constraints

- Standard library only at runtime.
- Single package, single CLI entrypoint.
- No fallback branches or unused abstractions.
