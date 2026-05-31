# ADR 0002: Domain Models Are Framework Independent

- Status: Superseded
- Superseded by: [0011](0011-pydantic-message-schemas-with-plain-domain-aggregates.md)
- Date: 2026-05-31

## Context

The domain model should express business language, behavior, and invariants.
When domain classes inherit from an ORM base class or double as HTTP schemas,
storage and transport decisions shape the business model.

## Decision

Domain entities, aggregates, value objects, commands, and events are plain
Python objects.

- Use normal classes or standard-library dataclasses.
- Prefer frozen dataclasses for immutable value objects, commands, and events.
- Keep aggregate methods responsible for enforcing invariants.
- Let aggregate roots collect domain events when a business fact matters to
  another handler.
- Keep infrastructure imports out of `domain`.

Domain events are not API response envelopes and do not imply event sourcing.
They are in-process facts unless a specific adapter publishes them externally.

## Consequences

Domain tests run without FastAPI, Pydantic, SQLAlchemy, a database, or a message
broker. Translation code exists at boundaries, but it makes dependencies and
representation changes explicit.

## Agent Guidance

- Do not import `fastapi`, `pydantic`, `sqlalchemy`, or adapter modules from
  `domain`.
- Name domain objects using the business language.
- Put validation of external shape at the boundary and business invariants in
  the domain.
- Add a value object when it gives a primitive value domain meaning or behavior.

## References

- [Cosmic Python: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
