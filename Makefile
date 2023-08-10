
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

.PHONY: build
build: ## Creates a virtual environment and installs development dependencies
	poetry install

.PHONY: test
test: ## Executes tests cases
	poetry run pytest

.PHONY: cover
cover: ## Executes tests cases with coverage reports
	poetry run pytest --cov . --junitxml reports/xunit.xml \
	--cov-report xml:reports/coverage.xml --cov-report term-missing

.PHONY: lint
lint: ## Applies static analysis, checks and code formatting
	poetry run pre-commit run --all-files

.PHONY: ci-prebuild
ci-prebuild: ## Install build tools and prepare project directory for the CI pipeline
	pip install --disable-pip-version-check poetry
	cat /dev/null > requirements.txt

.PHONY: help
help: ## Show make target documentation
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)