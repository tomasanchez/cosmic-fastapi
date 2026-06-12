# ADR 0011: Pydantic Message Schemas With Plain Domain Aggregates

- Status: Accepted
- Date: 2026-05-31

## Context

The original Cosmic Python examples use standard-library dataclasses for
commands and events. That remains a sound dependency-minimizing choice, but
this template targets modern Python services where messages commonly cross
HTTP, worker, broker, CLI, and test boundaries.

Commands and events are immutable data carriers. Pydantic 2 gives those data
carriers runtime validation, serialization, JSON Schema generation, and a
consistent contract for adapters. Requiring separate dataclass and Pydantic
representations for every message adds translation code without always buying
meaningful independence.

The important architectural boundary is narrower: transport frameworks,
persistence details, and external contract concerns must not shape
behavior-rich domain aggregates.

## Decision

Use a hybrid model:

- Keep entities, aggregates, and behavior-rich domain objects as plain Python
  classes or standard-library dataclasses by default.
- Allow immutable commands and events to inherit from Pydantic `BaseModel`.
- Treat Pydantic as a schema dependency for messages, not as the domain
  framework or persistence model.
- Reuse a Pydantic command directly as an inbound adapter schema when its
  public contract and application contract are intentionally identical.
- Keep a separate HTTP, broker, or external DTO when the external contract has
  different fields, naming, versioning, authorization rules, or lifecycle.
- Translate domain events into versioned integration events before publishing
  them externally when the public event contract needs independent evolution.

FastAPI remains an entrypoint adapter. SQLAlchemy remains a persistence
adapter. Neither belongs in domain aggregates or application messages.

## Consequences

Application code has fewer mechanical DTO copies for simple use cases.
Commands and events can be validated and serialized consistently across
entrypoints and workers. Agents can still introduce a separate boundary DTO
when it protects an external contract.

The domain now accepts a deliberate dependency on Pydantic for message
schemas. This is a pragmatic tradeoff rather than strict adherence to the
book's implementation details. Aggregates remain independently testable and
must not inherit from Pydantic merely to reduce typing.

## Agent Guidance

- Use frozen Pydantic models for commands and events unless a plain dataclass
  has a clear local advantage.
- Keep entities, aggregates, and behavior-rich value objects plain Python by
  default.
- Do not create a second DTO mechanically. Reuse a command at an entrypoint
  when the contracts intentionally match.
- Add a boundary DTO and explicit translation when external and application
  contracts differ.
- Do not import `fastapi`, `sqlalchemy`, or adapter modules from `domain`.
- Do not use a Pydantic message schema as a SQLAlchemy record or return domain
  entities directly from HTTP endpoints.
- Version integration events independently when they leave the process.

## References

- [Cosmic Python: Commands and Message Bus](https://www.cosmicpython.com/book/chapter_10_commands.html)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/)
