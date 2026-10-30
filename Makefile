PYTHON=python3

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
	$(PYTHON) -m pytest -q
frontend-build:
	cd frontend && npm ci && npm run build

format:
	$(PYTHON) -m isort backend scripts
	$(PYTHON) -m yapf -i -r backend scripts --exclude "**/generated/*"

check-format:
	$(PYTHON) -m isort --check-only backend scripts
	$(PYTHON) -m yapf --diff -r backend scripts --exclude "**/generated/*"
