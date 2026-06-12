# Cosmic Python Pattern Coverage

This template modernizes the patterns from
[Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html).
It provides a reusable baseline without forcing infrastructure choices into
every generated project.

## Included Baseline

| Book topic | Template implementation |
| --- | --- |
| Domain modeling | Plain Python aggregate and value-object examples under `domain/models` |
| Repository pattern | Write-side repository port and SQLAlchemy 2 adapter |
| Service layer | Command and event handlers under `service_layer` |
| Unit of work | Abstract transaction boundary and SQLAlchemy adapter |
| Aggregates | Aggregate-root repository rule and consistency policy in ADR 0013 |
| Domain events | Aggregates record immutable Pydantic events |
| Message bus | Generic `Command` and `Event` dispatch with event draining |
| Commands | Immutable Pydantic commands accepted from HTTP or broker adapters |
| CQRS | Purpose-built reader port, read model, and SQLAlchemy projection adapter |
| Dependency injection | Explicit `bootstrap.py` composition root |
| HTTP entrypoint | Thin FastAPI routes that dispatch commands or query readers |
| Schema management | Alembic migrations |

## Conditional Extensions

Add these patterns when a concrete use case requires them:

| Pattern | Introduce when |
| --- | --- |
| Optimistic locking | Mutable aggregates can receive competing writes |
| Versioned integration events | Broker payloads become public contracts |
| Transactional outbox | Database commits and broker publication must be reliable together |
| Broker consumer and publisher adapters | A project selects Kafka, RabbitMQ, SQS, or another transport |
| Idempotency storage | Commands or events can be delivered more than once |
| Process manager or saga | A durable workflow spans aggregate boundaries |
| Separate read projection store | Query scale, latency, or ownership differs from the write model |

## Deliberate Non-Defaults

- Event sourcing is not implied by domain events.
- Separate read and write databases are not required for CQRS.
- A message broker is not required for in-process event dispatch.
- Optimistic locking is not added to immutable or create-only sample flows.

Agents should run `make adr-context` before introducing an extension and add an
ADR when changing a project-wide default.
