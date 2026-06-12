# ADR 0001: Modern Cosmic Python Standard

- Status: Accepted
- Date: 2026-05-31

## Context

This project follows a modern Cosmic Python standard for people and coding
agents. It is inspired by *Architecture Patterns with Python*, also known as
Cosmic Python. The book's central goal is to keep business logic easy to understand,
fast to test, and independent of delivery and infrastructure choices.

Python application tooling has moved forward. FastAPI, Pydantic 2, SQLAlchemy
2, Alembic, Ruff, and uv let us express the same architectural intent with
better typing, validation, packaging, and developer ergonomics.

## Decision

We preserve these principles:

1. Domain behavior is the center of the application.
2. Dependencies point inward.
3. Entrypoints translate external requests into application messages.
4. Application handlers orchestrate use cases.
5. Repositories abstract persistence.
6. A unit of work defines the transaction boundary.
7. Domain events describe facts that already happened.
8. Infrastructure is replaceable and tested at its boundaries.

We modernize the implementation:

- FastAPI replaces Flask as the HTTP adapter.
- Pydantic 2 validates external data, settings, and immutable message schemas,
  not core domain behavior.
- SQLAlchemy 2 typed declarative models are persistence adapter details.
- Alembic versions relational schema changes.
- uv manages the project environment and lockfile.
- Ruff and pytest provide a compact quality toolchain.

These are defaults, not ceremony requirements. A simple read-only endpoint does
not need a command or aggregate merely to resemble a diagram.

## Consequences

Projects receive a consistent architecture without forcing every Cosmic Python
pattern into every feature. Code may be slightly more explicit than a direct
CRUD application, but domain rules remain isolated and tests remain focused.

## Agent Guidance

- Prefer the smallest design that preserves the dependency direction.
- Add layers because a use case needs them, not because a folder exists.
- Do not let framework convenience APIs leak into the domain.
- Record a new ADR before changing a project-wide default.

## References

- [Cosmic Python overview](https://www.cosmicpython.com/book/preface.html)
- [Cosmic Python architecture summary](https://www.cosmicpython.com/book/appendix_ds1_table.html)
