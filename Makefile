# Makefile for DiceRealms

APP_NAME=dicerealms

.PHONY: test test-cov

SHELL := /bin/bash
PY := python3.13

pip-reset:
	uv pip install -e .

test:
	uv run pytest

test-cov:
	uv run pytest --cov=dicerealms --cov-report=term-missing --cov-report=html

test-cov-xml:
	uv run pytest --cov=dicerealms --cov-report=xml

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

fmt:
	uv run ruff format .

sec:
	uv run bandit -c pyproject.toml -r .

run:
	uv run ${APP_NAME} start

