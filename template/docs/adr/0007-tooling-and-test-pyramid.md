# ADR 0007: Tooling and Test Pyramid

- Status: Accepted
- Date: 2026-05-31

## Context

A reusable standard needs a small, reliable toolchain and a clear testing
strategy. Agents should be able to discover the expected commands without
inventing project-specific workflows.

## Decision

Use:

- `pyproject.toml` as the primary Python project configuration file.
- uv for Python installation alignment, dependency management, environments,
  command execution, and locking.
- A committed `uv.lock` file for reproducible application builds.
- Ruff for linting, import sorting, and formatting.
- Pyrefly for static type checking.
- pytest for tests.
- Alembic for relational database migrations.
- A `Makefile` as a discoverable convenience layer for common commands.
- Conventional Commits for machine-readable Git history and automated
  changelogs.

Organize tests by feedback speed and infrastructure requirements:

- `tests/unit`: domain and handler tests using plain objects and fakes.
- `tests/integration`: repository, unit of work, migration, and adapter tests
  against real infrastructure where behavior depends on it.
- `tests/e2e`: a small number of tests through deployed-style entrypoints.

CI runs lockfile validation, linting, static type checking, tests, and the
production image build.

## Consequences

Local and CI workflows stay reproducible and easy to discover. The suite favors
fast tests while still checking infrastructure integration where substitutes
would hide important behavior.

## Agent Guidance

- Use `uv add` and `uv remove` instead of editing dependency lists alone.
- Commit `pyproject.toml` and `uv.lock` changes together.
- Prefer a fast domain or handler test for business behavior.
- Add integration coverage for SQL dialect behavior, transaction semantics, and
  external adapters.
- Keep e2e coverage small and focused on critical wiring.
- Use Conventional Commits and keep commits focused.

## References

- [uv projects](https://docs.astral.sh/uv/concepts/projects/)
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
