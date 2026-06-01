
.DEFAULT_GOAL = help
.NOTPARALLEL: ; # Targets execute serially
.ONESHELL: ; # Recipes execute in the same shell

.PHONY: clean
clean: ## Removes all build and test artifacts
	rm -f .coverage
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf reports
	rm -f requirements.txt
	rm -rf $(SSAP_DIR)

.PHONY: dist-clean
dist-clean: clean ## Removes all build and test artifacts and virtual environment
	rm -rf .venv

.PHONY: install
install: ## Install dependencies
	uv sync

.PHONY: dev
dev: ## Install dev dependencies
	uv sync --dev

.PHONY: build
build: ## Creates a virtual environment
	uv venv

.PHONY: test
test: ## Executes tests cases
	uv run pytest

.PHONY: adr-check
adr-check: ## Validates the architecture decision registry
	uv run python scripts/prune_decisions.py check

.PHONY: adr-context
adr-context: ## Prints active architecture guidance for agents
	uv run python scripts/prune_decisions.py context

.PHONY: migrate
migrate: ## Applies relational database migrations
	uv run alembic upgrade head

.PHONY: mcp
mcp: ## Runs the optional MCP addon over Streamable HTTP
	uv run --extra mcp python -m template.addons.mcp.server

.PHONY: kafka-up
kafka-up: ## Starts the local Kafka broker
	docker compose up -d kafka

.PHONY: kafka-relay
kafka-relay: ## Relays transactional outbox events to Kafka
	uv run --extra kafka python -m template.addons.kafka.worker

.PHONY: kafka-consume
kafka-consume: ## Prints local user integration events from Kafka
	docker compose exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic users.events --from-beginning

.PHONY: kafka-ui-up
kafka-ui-up: ## Starts local Kafka with the optional Kafbat UI
	docker compose --profile observability up -d kafbat-ui

.PHONY: kafka-ui-down
kafka-ui-down: ## Stops the optional Kafbat UI
	docker compose --profile observability stop kafbat-ui

.PHONY: cover
cover: ## Executes tests cases with coverage reports
	uv run --extra mcp --extra kafka pytest --cov src/template --cov-fail-under=100 --junitxml reports/xunit.xml \
	--cov-report xml:reports/coverage.xml --cov-report term-missing

.PHONY: format
format: ## Formats the code using Ruff
	uv run ruff format ./src ./tests ./scripts ./migrations

.PHONY: pre-commit
pre-commit: ## Runs pre-commit hooks on all files
	uv run pre-commit run --all-files

.PHONY: lint
lint: ## Applies static analysis and type checks
	uv run ruff check ./src ./tests ./scripts ./migrations
	uv run ruff format --check ./src ./tests ./scripts ./migrations
	uv run --extra mcp --extra kafka pyrefly check

.PHONY: fix
fix:  ## Fix lint errors
	uv run ruff check --fix ./src ./tests ./scripts ./migrations

.PHONY: help
help: ## Show make target documentation
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
