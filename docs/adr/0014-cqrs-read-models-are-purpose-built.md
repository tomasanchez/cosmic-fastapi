# ADR 0014: CQRS Read Models Are Purpose Built

- Status: Accepted
- Date: 2026-05-31

## Context

Write-side aggregates protect invariants. Read paths answer questions. Loading
an aggregate through its repository for every query couples API responses to
the write model and can produce unnecessary joins, mapping, and transaction
work.

Cosmic Python presents CQRS as a spectrum rather than a requirement for
separate databases or services. A small project can separate read code from
write code while using the same relational database.

## Decision

Separate read paths from write-side aggregate repositories when a feature
needs query behavior.

- Command handlers use repositories and a unit of work.
- Query services use purpose-built reader ports.
- SQLAlchemy readers select persistence records or projections directly.
- Read models contain the fields required by consumers and do not expose
  aggregate behavior.
- Read models may be dataclasses or Pydantic schemas depending on whether they
  cross a serialization boundary.
- Use the same database by default. Separate projections, stores, or services
  are optional optimizations introduced for demonstrated needs.

The sample user query uses `UserReader` and `SqlAlchemyUserReader` to return a
`UserReadModel` without rehydrating the `User` aggregate.

## Consequences

Queries can evolve for consumer needs without weakening aggregate boundaries.
The application has a small amount of extra read-side code. Eventual
consistency becomes relevant only when a separate projection store is added.

## Agent Guidance

- Do not route read-only endpoints through a write-side unit of work by habit.
- Define a small reader port for consumer-focused query behavior.
- Return read models rather than mutable aggregates from query services.
- Keep the same database until scale, latency, or ownership requires a
  separate projection.
- Document projection lag and rebuild strategy before introducing an
  eventually consistent read store.

## References

- [Cosmic Python: Command-Query Responsibility Segregation](https://www.cosmicpython.com/book/chapter_12_cqrs.html)
