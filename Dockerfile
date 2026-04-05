FROM python:3.14.0-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install build==1.4.2 && \
    python -m build

FROM python:3.14.0-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install /tmp/*.whl && \
    rm -rf /tmp/*.whl

EXPOSE 8000

CMD ["showoff-pipeline-api"]

FROM python:3.14.0-slim AS dev

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY . .

RUN python -m pip install --upgrade pip==26.0.1 && \
    python -m pip install -e .[dev]

CMD ["sh", "-lc", "ruff check . && ruff format --check . && coverage run -m pytest && coverage report --fail-under=100 && python -m build"]
