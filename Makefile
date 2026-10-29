.PHONY: up down logs test frontend-build proto format check-format
up:
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f gateway identity messaging video
proto:
	sh scripts/generate-proto.sh
test:
	python -m pytest -q
frontend-build:
	cd frontend && npm ci && npm run build

format:
	python -m isort backend scripts
	python -m yapf -i -r backend scripts --exclude "**/generated/*"

check-format:
	python -m isort --check-only backend scripts
	python -m yapf --diff -r backend scripts --exclude "**/generated/*"
