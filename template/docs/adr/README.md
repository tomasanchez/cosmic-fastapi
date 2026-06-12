# Architecture Decision Records

This directory records the architectural defaults for this project. The standard
modernizes the intent of
[Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html)
instead of copying its implementation line for line.

The standard is designed for people and coding agents. An agent should read
these records before adding a feature, persistence model, background worker, or
new infrastructure dependency.

## Status

The current source tree is an evolving scaffold. Accepted ADRs describe the
target standard. Existing code that conflicts with an accepted ADR should be
treated as migration work, not as a precedent to repeat.

## Decision Records

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](0001-modern-cosmic-python-standard.md) | Modern Cosmic Python Standard | Accepted |
| [0002](0002-domain-models-are-framework-independent.md) | Domain Models Are Framework Independent | Superseded |
| [0003](0003-fastapi-and-pydantic-live-at-boundaries.md) | FastAPI and Pydantic Live at Boundaries | Superseded |
| [0004](0004-sqlalchemy-2-persistence-behind-repositories.md) | SQLAlchemy 2 Persistence Stays Behind Repositories | Accepted |
| [0005](0005-explicit-composition-and-message-dispatch.md) | Explicit Composition and Message Dispatch | Accepted |
| [0006](0006-async-is-an-explicit-end-to-end-choice.md) | Async Is an Explicit End-to-End Choice | Superseded |
| [0007](0007-tooling-and-test-pyramid.md) | Tooling and Test Pyramid | Accepted |
| [0008](0008-static-typing-with-pyrefly.md) | Static Typing With Pyrefly | Accepted |
| [0009](0009-conventional-commits.md) | Conventional Commits | Accepted |
| [0010](0010-adr-lifecycle-and-decision-pruning.md) | ADR Lifecycle and Decision Pruning | Accepted |
| [0011](0011-pydantic-message-schemas-with-plain-domain-aggregates.md) | Pydantic Message Schemas With Plain Domain Aggregates | Accepted |
| [0012](0012-camel-case-json-message-contracts.md) | Camel-Case JSON Message Contracts | Accepted |
| [0013](0013-aggregates-define-consistency-boundaries.md) | Aggregates Define Consistency Boundaries | Accepted |
| [0014](0014-cqrs-read-models-are-purpose-built.md) | CQRS Read Models Are Purpose Built | Accepted |
| [0016](0016-aggregate-persistence-write-back.md) | Aggregate Persistence Write-Back on Commit | Accepted |
| [0017](0017-async-persistence-by-default.md) | Async Persistence and Application Code by Default | Accepted |
| [0018](0018-postgresql-default-with-pgvector.md) | PostgreSQL by Default with a pgvector Image; SQLite Optional | Accepted |
| [0019](0019-coverage-from-unit-and-e2e-tests.md) | Coverage From Unit and E2E Tests; Integration Runs Separately | Accepted |

## Agent Checklist

Before writing code:

1. Identify the domain behavior and invariant.
2. Put business rules in plain Python domain objects.
3. Use frozen Pydantic models for commands and events when they benefit from a schema contract.
4. Add separate boundary DTOs only when the external contract differs from the application message.
5. Use `snake_case` in Python and `camelCase` when messages cross JSON boundaries.
6. Access persistence through a repository and transaction boundary.
7. Treat aggregate roots as consistency boundaries and keep commands focused on one root by default.
8. Use purpose-built read models for query paths instead of loading write-side aggregates by habit.
9. Wire dependencies in the composition root.
10. Add the highest useful test that does not require infrastructure.
11. Add integration tests where adapters meet real infrastructure.
12. Record a new ADR when changing an accepted default.
13. Use Conventional Commits when creating Git history.

## Decision Pruner

Run the decision pruner before architectural work:

```bash
make adr-context
```

This validates the ADR registry and prints only active guidance. After changing
an ADR, run:

```bash
make adr-check
```

## Creating an ADR

Copy [template.md](template.md), assign the next four-digit number, and keep the
decision focused. An ADR should explain both the chosen default and when an
exception is justified.
