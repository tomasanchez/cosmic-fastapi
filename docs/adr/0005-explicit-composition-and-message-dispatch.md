# ADR 0005: Explicit Composition and Message Dispatch

- Status: Accepted
- Date: 2026-05-31

## Context

Application handlers need repositories, units of work, publishers, clocks, and
other adapters. Hidden construction inside handlers makes tests brittle and
couples business workflows to infrastructure.

Commands and events also have different semantics. A command asks the system to
perform work. An event records a fact and may trigger additional work.

## Decision

Use explicit dependency injection and a small composition root.

- `bootstrap.py` assembles settings, adapters, factories, and handler maps.
- Command handlers receive explicit dependencies and have exactly one handler
  per command type.
- Event handlers receive explicit dependencies and may have zero or more
  handlers per event type.
- An internal message bus dispatches commands and drains events raised by
  aggregates.
- External message brokers are optional adapters introduced only when work must
  cross a process boundary.
- External publishing reliability requirements must be addressed explicitly,
  typically with an outbox pattern.

The composition root may use straightforward factories, closures, or
`functools.partial`. A dependency injection framework is not the default.

## Consequences

Use cases remain callable from HTTP routes, tests, workers, and scripts. The
message bus adds a small amount of indirection, but only where commands and
events provide value.

## Agent Guidance

- Keep orchestration in handlers and business decisions in aggregates.
- Inject dependencies instead of importing configured global clients.
- Do not add Redis, Kafka, or a task queue merely to implement in-process
  dispatch.
- Define delivery guarantees before publishing events externally.

## References

- [Cosmic Python: Events and Message Bus](https://www.cosmicpython.com/book/chapter_08_events_and_message_bus.html)
- [Cosmic Python: Commands](https://www.cosmicpython.com/book/chapter_10_commands.html)
- [Cosmic Python: Dependency Injection](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)
