# ADR 0013: Aggregates Define Consistency Boundaries

- Status: Accepted
- Date: 2026-05-31

## Context

Repositories and units of work are useful only when they preserve meaningful
business boundaries. An aggregate is a cluster of entities and value objects
that must remain consistent together. The aggregate root is the only object
loaded and saved directly by application code.

Without an explicit rule, handlers can load unrelated rows, update several
roots in one transaction, and gradually turn the domain layer into a thin
wrapper around a relational schema.

## Decision

Treat aggregate roots as consistency and transaction boundaries.

- Repositories expose aggregate roots, not arbitrary child entities.
- Commands target one aggregate root by default.
- A unit of work commits changes to one aggregate boundary by default.
- Enforce invariants inside the aggregate before persistence.
- Coordinate changes across aggregate boundaries with domain events and
  eventual consistency when the business allows it.
- Use a dedicated process manager or saga when a multi-step workflow spans
  aggregates and requires compensation or durable progress.
- Add optimistic locking when a mutable aggregate can receive competing
  updates. A persisted version counter is the default strategy.
- Use a database uniqueness constraint when an invariant is naturally global,
  such as a unique email address.

The sample `User` model is an intentionally small aggregate root. Registration
normalizes its state and raises `UserRegistered`. The repository persists the
root as one unit and the database enforces global email uniqueness.

## Consequences

Aggregate boundaries make transaction scope visible and keep domain behavior
focused. Cross-aggregate workflows may become eventually consistent and need
idempotent handlers. Optimistic locking adds a conflict path only when the use
case needs concurrent mutation protection.

## Agent Guidance

- Name the aggregate root before adding a write-side repository method.
- Do not expose repositories for child entities merely for CRUD convenience.
- Keep one aggregate boundary per command unless a business invariant requires
  a wider atomic transaction.
- Prefer events for cross-aggregate coordination.
- Add and test a version counter before introducing mutable concurrent writes.
- Keep database constraints for global invariants even when handlers perform a
  friendly pre-check.

## References

- [Cosmic Python: Aggregates and Consistency Boundaries](https://www.cosmicpython.com/book/chapter_07_aggregate.html)
- [Cosmic Python: Commands and Message Bus](https://www.cosmicpython.com/book/chapter_10_commands.html)
