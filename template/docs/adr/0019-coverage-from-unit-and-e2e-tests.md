# ADR 0019: Coverage From Unit and E2E Tests; Integration Runs Separately

- Status: Accepted
- Date: 2026-06-12

## Context

[ADR 0007](0007-tooling-and-test-pyramid.md) defines the test pyramid
(`unit`, `integration`, `e2e`). With PostgreSQL as the default
([ADR 0018](0018-postgresql-default-with-pgvector.md)) and async persistence
([ADR 0017](0017-async-persistence-by-default.md)), the integration tier needs a
real PostgreSQL instance (Docker). Gating the 100% coverage requirement on tests
that require Docker couples the fast feedback loop — and the offline template
bake — to container infrastructure, which is slow and brittle in that role.

## Decision

Split the suite by what each tier needs and what it gates.

- **`tests/unit`** — pure unit tests with mocked sessions/queries and in-memory
  fakes; no database.
- **`tests/e2e`** — routes exercised through the ASGI app with an injected
  **in-memory async SQLite** (`aiosqlite`) container; no external infrastructure.
- **`tests/integration`** — repository, unit-of-work, dialect, and migration
  behavior against a **real PostgreSQL** (`asyncpg`) via a Docker service
  container.

The **100% coverage gate is computed from `unit` + `e2e` only.** These run
offline and deterministically, so adapter code must be reachable by a mocked
unit test or the in-memory e2e path to count. `tests/integration` is **excluded
from coverage** and runs as a **separate CI stage** with a PostgreSQL (pgvector)
service. `make cover` runs the offline gate; `make integration` runs the Docker
tier. The Copier bake matrix runs only the offline gate.

This extends [ADR 0007](0007-tooling-and-test-pyramid.md); 0007 remains Accepted.

## Consequences

Coverage feedback is fast, deterministic, and infrastructure-free, and the
template bakes offline. Real-PostgreSQL behavior (dialect specifics, migrations,
transaction semantics) is still verified, in a dedicated CI job that does not
block the coverage signal. The trade-off: code that only runs against PostgreSQL
must be covered by an integration test for confidence even though it does not
count toward the coverage percentage, so keep such Postgres-only branches thin.

## Agent Guidance

- Put fast behavior in `tests/unit` (mock the `AsyncSession`/reader) and critical
  wiring in `tests/e2e` (in-memory async SQLite container).
- Mark real-database tests with the `integration` marker and place them in
  `tests/integration`; never rely on them for coverage.
- Keep the offline gate at 100% via `make cover`.
- Verify dialect- or migration-specific behavior in the integration stage.
- Keep `concurrency = ["thread", "greenlet"]` in `[tool.coverage.run]`. SQLAlchemy's
  async support resumes coroutines across a greenlet boundary, so without it
  coverage misclassifies branches that continue after an awaited database call.

## References

- [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [coverage.py configuration](https://coverage.readthedocs.io/en/latest/config.html)
- [ADR 0007: Tooling and Test Pyramid](0007-tooling-and-test-pyramid.md)
- [ADR 0018: PostgreSQL by Default with a pgvector Image](0018-postgresql-default-with-pgvector.md)
