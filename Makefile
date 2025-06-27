
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

.PHONY: cover
cover: ## Executes tests cases with coverage reports
	uv run pytest --cov . --cov-fail-under=100 --junitxml reports/xunit.xml \
	--cov-report xml:reports/coverage.xml --cov-report term-missing

.PHONY: format
format: ## Formats the code using Ruff
	uv run ruff format ./src ./tests

.PHONY: pre-commit
pre-commit: ## Runs pre-commit hooks on all files
	uv run pre-commit run --all-files

.PHONY: lint
lint: ## Applies static analysis and type checks
	uv run ruff check ./src
	uv run ruff format --check ./src

.PHONY: fix
fix:  ## Fix lint errors
	uv run ruff check --fix ./src

.PHONY: help
help: ## Show make target documentation
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
