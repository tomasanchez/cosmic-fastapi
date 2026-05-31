# ADR 0012: Camel-Case JSON Message Contracts

- Status: Accepted
- Date: 2026-05-31

## Context

Commands can enter the application through HTTP, Kafka, RabbitMQ, SQS, a CLI,
or an internal caller. Events may remain in-process or leave the process
through a broker adapter. JSON is the common interchange format for several of
these adapters.

Python code conventionally uses `snake_case`, while JSON APIs and messages
commonly use `camelCase`. Without a project default, adapters serialize the
same message differently and consumers receive inconsistent contracts.

HTTP responses, domain events, and integration events are related but not
identical concepts:

- An HTTP response describes the immediate result of one request.
- A domain event records a business fact inside the application.
- An integration event is a public, versioned message published for external
  consumers.

## Decision

Use `snake_case` names inside Python and `camelCase` aliases in JSON.

- Commands and domain events inherit from a shared frozen Pydantic message
  base.
- Message adapters accept camel-case JSON and serialize JSON-safe camel-case
  payloads.
- HTTP responses also serialize JSON using camel-case aliases.
- Broker adapters translate domain events into versioned integration-event
  contracts when a message leaves the process.
- Integration envelopes should identify at least the event type, schema
  version, event identity, occurrence time, and payload.
- Do not use HTTP response envelopes as broker event envelopes.

For an intentionally small application, an adapter may initially publish a
domain event payload directly. Before external consumers depend on that
payload, introduce a versioned integration event and treat it as a public
contract.

## Consequences

Python remains idiomatic while HTTP and broker consumers receive consistent
JSON. Commands can be validated from multiple transports without mechanical
schema copies. External event contracts can evolve independently from internal
domain events and HTTP responses.

Adapters must call JSON-mode serialization when sending messages outside the
process, for example:

```python
payload = event.model_dump(mode="json")
```

## Agent Guidance

- Use `snake_case` in Python and `camelCase` in JSON message payloads.
- Parse incoming broker commands through their Pydantic command schema.
- Serialize outgoing messages with `model_dump(mode="json")` or
  `model_dump_json()`.
- Keep HTTP response schemas, domain events, and integration events distinct
  when their contracts or lifecycles differ.
- Add a versioned integration event before a broker payload becomes a public
  contract.
- Document delivery guarantees, retries, idempotency, and ordering when adding
  a broker adapter.

## References

- [Pydantic alias generators](https://docs.pydantic.dev/latest/api/alias_generators/)
- [Pydantic serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [CloudEvents specification](https://cloudevents.io/)
