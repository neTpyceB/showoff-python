FROM python:3.14.3-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md setup.py MANIFEST.in ./
COPY src ./src

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install build==1.4.2 && \
    python -m build

FROM python:3.14.3-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install /tmp/*.whl && \
    rm -rf /tmp/*.whl

EXPOSE 8000

CMD ["showoff-perf-api"]

FROM python:3.14.3-slim AS dev

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY . .

RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install -e .[dev]

CMD ["sh", "-lc", "ruff check . && ruff format --check . && coverage run -m pytest && coverage report --fail-under=100 && python -m build"]
