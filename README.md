# CLI Productivity Toolkit

Minimal Python CLI for filesystem productivity tasks.

## Features

- Recursive file search
- Batch rename
- JSON formatting
- CSV formatting
- CLI-driven configuration through flags

## Stack

- Python 3.14.3
- `argparse`
- `pathlib`
- `json`
- `csv`
- Docker Compose

## Local Run

```bash
docker compose run --rm toolkit showoff --help
docker compose run --rm toolkit showoff search /workspace "*.py"
docker compose run --rm toolkit showoff rename /workspace old new --glob "*.txt"
docker compose run --rm toolkit showoff format json /workspace/data.json
docker compose run --rm toolkit showoff format csv /workspace/data.csv --output /workspace/formatted.csv
```

## Local Checks

```bash
docker compose run --rm checks
```

## Native Checks

```bash
make install
make check
```
