# Makefile
.PHONY: install run test lint format docker-up docker-down migrate

install:
	pip install -r requirements.txt

run:
	uvicorn main_updated:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black .
	isort .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

create-migration:
	alembic revision --autogenerate -m "$(message)"