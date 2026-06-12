# ADR 0018: PostgreSQL by Default with a pgvector Image; SQLite Optional

- Status: Accepted
- Date: 2026-06-12

## Context

The template historically defaulted to file-based SQLite, which is excellent for
zero-setup demos but is not what most production services run. Real services
want PostgreSQL: concurrent writers, real types (JSONB, arrays), and increasingly
vector search for embeddings via the `pgvector` extension. A template should
default to the realistic target while still offering a frictionless,
infrastructure-free option.

## Decision

PostgreSQL is the **default** database; SQLite remains a selectable option.

- A Copier `database` question chooses `postgres` (default) or `sqlite`.
- **PostgreSQL**: the `asyncpg` driver and a default URL of the form
  `postgresql+asyncpg://…`. `docker-compose` bundles a **pgvector-capable
  image** (`pgvector/pgvector:pg17`) as a `db` service with a healthcheck and a
  named volume; the `app` service depends on it.
- **SQLite**: the `aiosqlite` driver and a file URL; no database service is
  added to `docker-compose`.
- Async drivers only, per [ADR 0017](0017-async-persistence-by-default.md).
- Alembic runs against the async engine.

The pgvector **image** is provided so the extension is available, but the
example domain ships **no vector column**. Projects that need vectors add a
`CREATE EXTENSION IF NOT EXISTS vector` step in a migration and a `Vector`
column in a persistence model when the requirement is real.

## Consequences

New projects start on a production-shaped database and can adopt pgvector without
changing infrastructure. SQLite stays available for quick experiments and is the
substrate for the fast offline test tier
([ADR 0019](0019-coverage-from-unit-and-e2e-tests.md)). The cost is that the
Postgres default expects a running database for local runs; `docker-compose up`
provides one, and `DATABASE_AUTO_CREATE_SCHEMA`/Alembic handle the schema.

## Agent Guidance

- Select the driver through the database URL (`postgresql+asyncpg` /
  `sqlite+aiosqlite`); do not hardcode a dialect in adapters.
- Before using a `Vector` column, add `CREATE EXTENSION IF NOT EXISTS vector` in
  an Alembic migration.
- Keep persistence-model SQL portable where practical; put genuinely
  Postgres-specific behavior behind an integration test
  ([ADR 0019](0019-coverage-from-unit-and-e2e-tests.md)).
- Manage schema with Alembic; reserve `AUTO_CREATE_SCHEMA` for demos and tests.

## References

- [pgvector](https://github.com/pgvector/pgvector)
- [asyncpg](https://magicstack.github.io/asyncpg/)
- [aiosqlite](https://aiosqlite.omnilib.dev/)
- [Alembic with async engines](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic)
- [ADR 0017: Async Persistence and Application Code by Default](0017-async-persistence-by-default.md)
