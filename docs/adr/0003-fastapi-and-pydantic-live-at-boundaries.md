# ADR 0003: FastAPI and Pydantic Live at Boundaries

- Status: Superseded
- Superseded by: [0011](0011-pydantic-message-schemas-with-plain-domain-aggregates.md)
- Date: 2026-05-31

## Context

FastAPI and Pydantic 2 provide excellent HTTP parsing, serialization, OpenAPI
generation, and configuration loading. They are most useful at the edges of the
system. Treating them as the domain model would couple business behavior to a
transport and validation framework.

## Decision

FastAPI is a primary adapter. Pydantic models are boundary data transfer
objects.

- Define request and response schemas near HTTP entrypoints or in a boundary
  schema module.
- Translate validated request schemas into commands or query arguments.
- Translate handler results into response schemas.
- Use `pydantic-settings` for environment-derived configuration.
- Use FastAPI `lifespan` for process-lifetime resources and cleanup.
- Use FastAPI dependency injection for request-scoped boundary dependencies.

FastAPI dependency injection is not the application's composition root. It is
an HTTP adapter mechanism that calls dependencies assembled by application
bootstrap code.

## Consequences

OpenAPI and runtime validation stay strong while the domain remains usable from
HTTP, a CLI, tests, workers, and event consumers. Some explicit translation is
required.

## Agent Guidance

- Do not pass a Pydantic request model deep into a domain aggregate.
- Do not return domain entities directly from HTTP endpoints.
- Keep route functions thin: parse, translate, dispatch, serialize.
- Put startup and shutdown resource management in `lifespan`.

## References

- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI lifespan events](https://fastapi.tiangolo.com/advanced/events/)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic settings](https://docs.pydantic.dev/latest/api/pydantic_settings/)
