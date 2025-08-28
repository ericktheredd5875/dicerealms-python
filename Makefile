# Makefile for DiceRealms

APP_NAME=dicerealms

.PHONY: test

SHELL := /bin/bash
PY := python3.13

test:
	uv run pytest

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

run:
	uv run ${APP_NAME} start

