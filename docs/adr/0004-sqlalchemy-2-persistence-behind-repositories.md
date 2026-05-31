# ADR 0004: SQLAlchemy 2 Persistence Stays Behind Repositories

- Status: Accepted
- Date: 2026-05-31

## Context

Cosmic Python demonstrates imperative ORM mapping so SQLAlchemy depends on the
domain model. SQLAlchemy 2 still supports that approach through
`registry.map_imperatively()`, but its documentation recommends declarative
mapping for new users and modern typing support.

We want both a framework-independent domain and idiomatic SQLAlchemy 2 adapter
code.

## Decision

The default persistence adapter uses:

- SQLAlchemy 2 typed declarative persistence models under `adapters`.
- SQLAlchemy 2 `select()` statements and `Session` usage.
- Repositories that translate between persistence models and domain objects.
- Repository interfaces expressed as `typing.Protocol` where practical.
- A unit of work that owns the session, repositories, commit, and rollback.
- Explicit commit on successful command handling and rollback by default.
- Alembic migration files committed with schema changes.

Imperative mapping with `registry.map_imperatively()` is allowed when direct
domain object persistence has a demonstrated advantage. It must remain inside
the persistence adapter and must not add SQLAlchemy imports to the domain.

## Consequences

The default introduces mapping code between persistence and domain objects. In
exchange, the domain remains plain Python and persistence models receive
SQLAlchemy 2 typing and tooling support. Repositories and units of work can be
replaced with in-memory fakes in unit tests.

## Agent Guidance

- Do not put `DeclarativeBase`, `Mapped`, or `mapped_column()` in `domain`.
- Do not call a SQLAlchemy session from an HTTP route or domain object.
- Put query-specific read models behind a query service when CQRS is useful.
- Add or update an Alembic migration whenever relational schema changes.
- Test commit and rollback behavior at the adapter boundary.

## References

- [SQLAlchemy 2 mapping styles](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
- [SQLAlchemy 2 session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Python protocols](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Cosmic Python: Unit of Work](https://www.cosmicpython.com/book/chapter_06_uow.html)
