PYTHON := python

.PHONY: install lint format test build check docker-build docker-smoke docker-test

install:
	$(PYTHON) -m pip install --upgrade pip==26.0.1
	$(PYTHON) -m pip install -e .[dev]

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

test:
	coverage run -m pytest
	coverage report --fail-under=100

build:
	$(PYTHON) -m build

check: lint test build

docker-build:
	docker compose build

docker-smoke:
	docker compose run --rm toolkit showoff --help

docker-test:
	docker compose run --rm checks
