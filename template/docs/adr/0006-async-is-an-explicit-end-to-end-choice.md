# ADR 0006: Async Is an Explicit End-to-End Choice

- Status: Superseded
- Superseded by: [0017](0017-async-persistence-by-default.md)
- Date: 2026-05-31

## Context

FastAPI supports both synchronous and asynchronous callables. Async code is
valuable for workloads that spend time awaiting async I/O, but it is not an
automatic improvement. Mixing blocking database access into `async def`
handlers can reduce throughput and make behavior harder to reason about.

## Decision

Use synchronous application and persistence code by default.

Choose async for a use case only when its I/O path is async end to end:

- async route or consumer
- async handler where needed
- async SQLAlchemy session or async client
- async unit of work and repositories
- tests that exercise the async path

Do not create both sync and async implementations preemptively. Domain objects
remain synchronous because business rules should not perform I/O.

## Consequences

The default stays simple, predictable, and easy to test. Projects can opt into
async where measured requirements justify it without spreading async syntax
through the domain.

## Agent Guidance

- Do not perform blocking I/O directly inside `async def`.
- Keep I/O out of domain methods.
- Make an end-to-end choice per adapter path and document exceptions.
- Add a new ADR if the project changes its default persistence mode to async.

## References

- [FastAPI: async and await](https://fastapi.tiangolo.com/async/)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy asyncio extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
