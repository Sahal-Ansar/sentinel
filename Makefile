.PHONY: up down test lint simulate eval

up: ## step 0.4
	docker compose up -d --wait

down: ## step 0.4
	docker compose down

test:
	uv run --locked --all-packages pytest

lint:
	uv run --locked --all-packages ruff check .
	uv run --locked --all-packages ruff format --check .

simulate eval:
	@echo "make $@ is not built yet (simulate: step 1.6, eval: step 3.4)" >&2; exit 1
