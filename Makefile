.PHONY: install test lint format run docker-build docker-run

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run black --check .
	poetry run isort --check .
	poetry run mypy .

format:
	poetry run black .
	poetry run isort .

run:
	poetry run python main.py

docker-build:
	docker build -t speed-test-internet .

docker-run:
	docker run --rm speed-test-internet
