# ADR 0016: Aggregate Persistence Write-Back on Commit

- Status: Accepted
- Date: 2026-06-12

## Context

[ADR 0011](0011-pydantic-message-schemas-with-plain-domain-aggregates.md)
keeps domain aggregates as plain Python objects and isolates them from
SQLAlchemy. The repository therefore uses the *translation* pattern: it maps
between the `User` aggregate and the `UserRecord` SQLAlchemy model on the way
in and out of persistence.

That isolation has a sharp edge the book's classic mapper-based repository does
not have. The book maps the domain object onto the ORM, so the SQLAlchemy
identity map and unit of work track every mutation and flush it on commit. With
translation, a domain aggregate loaded via `repository.get(...)` is a fresh,
detached object. SQLAlchemy never sees it. Mutating that aggregate and calling
`uow.commit()` previously persisted **nothing** for loaded-then-mutated
aggregates: the only writes that reached the database were the explicit
`session.add(...)` calls made by `repository.add(...)` for brand-new
aggregates. Updates were silently lost.

The repository also tracked seen aggregates in a list, which appended
duplicates when the same row was loaded twice and offered no way to return the
same instance for the same identity within a transaction.

## Decision

Restore write-on-commit for the translation repository without coupling the
domain to SQLAlchemy.

- Track seen aggregates in an **identity map** keyed by aggregate id
  (`dict[UUID, User]`) instead of a list. `get(...)` returns the
  already-tracked instance for an identity, so callers mutate one shared
  aggregate per transaction and re-loading a row does not create duplicates.
- On `commit()`, the unit of work asks the repository to persist tracked
  changes. The repository writes each tracked aggregate back with
  `session.merge(self._to_record(user))`. `merge` upserts by primary key,
  which unifies inserts (new aggregates also added via `session.add`) and
  updates (aggregates loaded then mutated). The session then commits.
- Domain aggregates stay plain Python. The write-back lives entirely in the
  persistence adapter and the SQLAlchemy unit of work.

[ADR 0011](0011-pydantic-message-schemas-with-plain-domain-aggregates.md)
remains Accepted. This ADR extends its persistence implications; it does not
supersede it.

## Consequences

Mutations to loaded aggregates now persist on commit, matching the mental model
developers expect from the book and from ORM-backed repositories. The identity
map fixes duplicate tracking and guarantees one instance per identity per
transaction, which also keeps domain-event collection correct.

The cost is an explicit `merge` per tracked aggregate at commit time. `merge`
issues a primary-key lookup, so very large transactions touching many
aggregates pay for that lookup per aggregate. This is acceptable because
write commands target a single aggregate root by default
([ADR 0013](0013-aggregates-define-consistency-boundaries.md)). Unique-constraint
violations still surface at flush, so the check-then-commit duplicate-email
handling and the `IntegrityConflict` to `EmailAlreadyRegistered` translation in
the handlers continue to work unchanged.

Query-only paths must keep using purpose-built read models
([ADR 0014](0014-cqrs-read-models-are-purpose-built.md)) rather than loading
write-side aggregates, so this write-back cost only applies to genuine command
handling.

## Agent Guidance

- Load an aggregate through `uow.users.get(...)`, mutate it with domain
  behavior, and call `uow.commit()`. Do not reach into the SQLAlchemy session
  to update rows by hand.
- Keep aggregate state translation inside the repository
  (`_to_record` / `_to_domain`). Do not leak SQLAlchemy records into handlers
  or the domain.
- Keep write commands focused on one aggregate root by default.
- For query paths, use a reader port and read model instead of loading an
  aggregate just to read it.
- When adding a new aggregate type, give its repository an identity map and a
  `persist_changes`-style write-back, and call it from the unit of work's
  `commit`.

## References

- [ADR 0011: Pydantic Message Schemas With Plain Domain Aggregates](0011-pydantic-message-schemas-with-plain-domain-aggregates.md)
- [ADR 0013: Aggregates Define Consistency Boundaries](0013-aggregates-define-consistency-boundaries.md)
- [ADR 0014: CQRS Read Models Are Purpose Built](0014-cqrs-read-models-are-purpose-built.md)
- [Cosmic Python: Unit of Work](https://www.cosmicpython.com/book/chapter_06_uow.html)
- [SQLAlchemy: Session.merge](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#merging)
