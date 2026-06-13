# ADR 0017: Async Persistence and Application Code by Default

- Status: Accepted
- Date: 2026-06-12

## Context

[ADR 0006](0006-async-is-an-explicit-end-to-end-choice.md) made synchronous code
the default and treated async as an explicit, per-use-case opt-in. It also
stated that changing the default persistence mode to async requires a new ADR —
this is that ADR.

FastAPI is an async-first framework, and the services this template scaffolds
are I/O-bound (database, HTTP, brokers). Running async end to end lets a single
worker serve many concurrent requests while awaiting I/O, and SQLAlchemy 2's
asyncio extension is now mature and well documented. Maintaining a synchronous
default plus an async opt-in also means two persistence styles to teach and
test. Standardizing on async removes that fork.

## Decision

The template is **async end to end by default**, and ships only the async path.

- Persistence uses `create_async_engine`, `AsyncSession`, and
  `async_sessionmaker`.
- The unit of work is an async context manager (`async with uow:`) with
  `await uow.commit()` / `await uow.rollback()` and async write-back.
- Repositories and query readers are async and use
  `await session.execute(select(...))`.
- Command and event handlers are `async def`; the message bus awaits them.
- FastAPI routes and the application lifespan are async; startup/shutdown await
  container hooks.
- Database drivers are async: `asyncpg` for PostgreSQL, `aiosqlite` for SQLite
  (`greenlet` is pulled in transitively by SQLAlchemy's async support).

Domain objects stay plain synchronous Python — business rules must not perform
I/O ([ADR 0002](0002-domain-models-are-framework-independent.md)), so they never
become coroutines.

This **supersedes [ADR 0006](0006-async-is-an-explicit-end-to-end-choice.md)**.

## Consequences

The code matches idiomatic modern FastAPI and there is a single persistence
style to learn, maintain, and test. The cost is that async correctness now
matters everywhere: handlers must never block the event loop, tests need an
async runner (`pytest-asyncio`), and contributors must understand `await`
semantics. The domain layer is unaffected and remains trivially unit-testable.

## Agent Guidance

- Reach for async first: a new adapter, handler, route, or client is `async` by
  default. Make every adapter, service-layer, and entrypoint I/O path
  `async`/`await`.
- Never call blocking I/O inside an `async def`. When a dependency is
  unavoidably synchronous, wrap the call with `asyncify()` from
  [Asyncer](https://asyncer.tiangolo.com/) (by FastAPI's author) — e.g.
  `await asyncify(blocking_fn)(arg)` — which runs it in a worker thread instead
  of blocking the event loop (`uv add asyncer`). Do not paper over a blocking
  call by leaving it inline.
- Keep domain methods synchronous and free of I/O.
- Use `AsyncSession` and `await` commits/queries; do not mix a sync `Session`
  into the request path.
- Write async tests; cover the async paths.

## References

- [SQLAlchemy asyncio extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI: async and await](https://fastapi.tiangolo.com/async/)
- [Asyncer: `asyncify`](https://asyncer.tiangolo.com/tutorial/asyncify/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [ADR 0006: Async Is an Explicit End-to-End Choice](0006-async-is-an-explicit-end-to-end-choice.md)
