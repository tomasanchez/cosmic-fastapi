# Cosmic Python Engineer Instructions

This project follows a Cosmic Python standard for people and coding agents.
Work as a Cosmic Python engineer: preserve the domain-first philosophy from
*Architecture Patterns with Python* while using the modern decisions recorded
in [docs/adr/README.md](docs/adr/README.md).

Read the ADR index before making architectural changes. Accepted ADRs describe
the target standard. Existing scaffold code that conflicts with an ADR is
migration work, not a precedent to repeat.

Before architectural work, run `make adr-context`. It validates the ADR
registry and prints the pruned set of active decisions. After adding or changing
an ADR, run `make adr-check`.

## Engineering Principles

- Put business behavior, language, and invariants at the center of the design.
- Keep dependencies pointing inward toward plain Python domain objects.
- Keep FastAPI, SQLAlchemy, and external clients at system boundaries.
- Use Pydantic deliberately for immutable command and event schemas.
- Use `snake_case` inside Python and `camelCase` when schemas cross JSON
  boundaries.
- Prefer explicit dependencies, small adapters, repositories, and units of work.
- Treat aggregate roots as consistency boundaries and use purpose-built read
  models for query paths.
- Add patterns when the use case needs them. Do not add ceremony merely to fill
  a directory.
- Keep changes focused. Do not refactor unrelated code while completing a task.
- Record a new ADR when changing a project-wide architectural default.

## Async and Persistence

- **Async is the default — reach for it first.** The application is async end to
  end ([ADR 0017](docs/adr/0017-async-persistence-by-default.md)): routes,
  handlers, the message bus, repositories, query readers, and the unit of work
  are `async`, and persistence uses `create_async_engine` and `AsyncSession`.
  Keep **domain objects synchronous** — business rules perform no I/O.
- Never block the event loop inside `async def` (no synchronous DB driver, no
  blocking call). `await` database work. When a dependency is unavoidably
  synchronous, wrap it with `asyncify()` from
  [Asyncer](https://asyncer.tiangolo.com/) (by FastAPI's author) —
  `await asyncify(blocking_fn)(arg)` runs it in a worker thread
  (`uv add asyncer`) — rather than leaving the blocking call inline.
- The default database is **PostgreSQL** via `asyncpg`; **SQLite** via `aiosqlite`
  is the optional alternative
  ([ADR 0018](docs/adr/0018-postgresql-default-with-pgvector.md)). Select the
  driver through the database URL; do not hardcode a dialect in adapters.
- The Docker image bundles pgvector. Before using a `Vector` column, add
  `CREATE EXTENSION IF NOT EXISTS vector` in an Alembic migration.
- Manage schema with Alembic (`make migrate`); reserve
  `DATABASE_AUTO_CREATE_SCHEMA` for demos and tests.

## Python Style

- Write modern typed Python supported by the project version.
- Add type annotations to production code and preserve useful types across
  boundaries. Avoid widening values to `Any`.
- Use Google-style docstrings for public modules, classes, methods, and
  functions where documentation adds meaning.
- Use `Args:`, `Returns:`, `Raises:`, and `Resources:` sections when relevant.
- Prefer clear names from the business domain over technical or generic names.
- Keep comments brief and explain why a non-obvious choice exists.
- Use Pydantic models for boundary validation, settings, and immutable command
  or event schemas, not as a substitute for behavior-rich domain modeling.
- Keep SQLAlchemy models and session usage inside persistence adapters.
- Use `async def` and `await` for I/O paths (adapters, handlers, routes) and an
  `AsyncSession` — never a synchronous `Session` — in the request path.

## Architecture Workflow

When implementing a feature:

1. Identify the business behavior and invariant.
2. Model the domain with plain Python objects.
3. Define frozen Pydantic commands and events when a schema contract helps.
4. Reuse a command as a boundary schema when contracts match; translate when
   they differ.
5. Orchestrate the use case in an application handler.
6. Access persistence through async repositories and an async unit of work
   (`async with uow: ... await uow.commit()`).
7. Keep write commands focused on one aggregate root by default.
8. Use reader ports and read models for query-only paths.
9. Wire dependencies in the composition root.
10. Add the smallest useful tests at each affected boundary.

Use domain events for facts that already happened. Use commands for requests to
perform work. Do not treat API response models as domain events. Introduce
versioned integration events before publishing public broker contracts.

## Testing Style

- Use pytest. Async tests run under `pytest-asyncio` (`asyncio_mode = "auto"`),
  so write `async def` tests and `await` the code under test.
- Write test scenarios using GIVEN / WHEN / THEN structure.
- Use uppercase `GIVEN`, `WHEN`, and `THEN` in test docstrings.
- Use `# GIVEN`, `# WHEN`, and `# THEN` comments when they improve the body of a
  non-trivial test.
- The **100% coverage gate comes from `tests/unit` + `tests/e2e` only**
  ([ADR 0019](docs/adr/0019-coverage-from-unit-and-e2e-tests.md)). `tests/unit`
  use plain objects, fakes, and mocked `AsyncSession`/ports; `tests/e2e` drive
  routes through the ASGI app on **in-memory async SQLite** with no external
  infrastructure.
- `tests/integration` exercise a **real PostgreSQL** (Docker). Mark every such
  test `@pytest.mark.integration`; they are **excluded from coverage** and run in
  a separate CI stage (`make integration`). Never rely on them for the gate.
- Prefer fast unit tests for domain behavior and handlers; use fakes for owned
  ports such as repositories and units of work.
- Keep end-to-end tests focused on critical wiring and user-visible behavior.

## Verification

Use the project commands exposed by the `Makefile` and uv. For a code change,
run the relevant focused tests first, then the available project checks:

```bash
make lint          # ruff check + ruff format --check + pyrefly
make cover         # unit + e2e at 100% coverage (the gate)
make integration   # PostgreSQL integration tier (requires Docker)
```

`make cover` is the coverage gate; `make integration` needs a running
PostgreSQL and is not part of the coverage percentage. If a documented check is
not yet wired into the evolving scaffold, say so clearly and add the missing
wiring when the task calls for it.

## Git

- Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
- Format commit subjects as `<type>[optional scope]: <description>`.
- Use `feat` for new behavior and `fix` for bug fixes.
- Use `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, and `style`
  when they accurately describe the change.
- Mark breaking changes with `!` or a `BREAKING CHANGE:` footer.
- Keep commits focused so automated changelog and release tooling can infer
  intent reliably.
- Do not include unrelated user changes in a commit.

Examples:

```text
feat(api): add user registration endpoint
fix(repository): rollback failed user creation
docs(adr): define persistence adapter standard
feat(domain)!: replace account identity format
```
