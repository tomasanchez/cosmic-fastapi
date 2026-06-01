# ADR 0016: External Message Buses Use a Transactional Outbox

- Status: Accepted
- Date: 2026-05-31

## Context

Publishing directly to Kafka after a database commit can lose an event when
the process stops between the two writes. Publishing before commit can emit an
event for state that later rolls back. A distributed transaction between the
application database and Kafka adds complexity that most projects do not need.

## Decision

Define a broker-neutral `IntegrationMessageBus` port in the service layer and
provide Kafka as one opt-in secondary adapter. Back external publication with
a transactional outbox.

- Translate selected domain events into versioned public integration events.
- Store each integration event in `outbox_events` in the same database
  transaction as aggregate changes.
- Relay unpublished rows through `IntegrationMessageBus` in a separate worker
  process.
- Mark a row as published only after the configured broker acknowledges the
  event.
- In the Kafka adapter, publish with the aggregate identity as the key so events for one
  aggregate receive a stable partitioning default.
- Treat delivery as at least once. Consumers must be idempotent using
  `eventId`.
- Keep the in-process message bus for local reactions. The external
  `IntegrationMessageBus` is an integration boundary, not a replacement for
  domain events.

The sample translates `UserRegistered` into `UserRegisteredV1`. Its Kafka
adapter publishes to the `users.events` topic. Local Docker Compose provides a
single-node KRaft broker for development only. A project can replace Kafka with
RabbitMQ, SQS, or another adapter without changing the relay use case.

The optional `observability` Docker Compose profile adds Kafbat UI for local
inspection of topics, partitions, messages, keys, and consumer groups. It is a
developer tool, not an application dependency or production default.

## Consequences

A broker outage does not fail user registration after the database is
available. Events remain durable until the relay can publish them. A relay may
publish the same event more than once if it stops after Kafka acknowledges a
message but before the database records completion.

The example intentionally does not include a broker consumer. A project should
add one when it has a concrete downstream use case, together with idempotency
storage and retry policy.

## Agent Guidance

- Do not publish to an external bus inside an HTTP route, aggregate, or database
  transaction.
- Add versioned integration schemas before external consumers depend on an
  event.
- Keep domain events and public integration events distinct.
- Depend on `IntegrationMessageBus` in the service layer. Keep Kafka, RabbitMQ,
  SQS, and SDK-specific types inside secondary adapters.
- Use `eventId` for consumer deduplication and aggregate identity as the Kafka
  key unless ordering requirements justify another choice.
- Document dead-letter handling, retention, observability, and consumer retry
  policy before production deployment.
- Do not treat local Docker Compose settings as production Kafka guidance.
- Keep Kafbat UI and similar dashboards outside application code. Require
  production-specific access controls before deploying an operational UI.

## References

- [Cosmic Python: Events and the Message Bus](https://www.cosmicpython.com/book/chapter_08_events_and_message_bus.html)
- [Confluent Kafka Python client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Confluent KRaft overview](https://docs.confluent.io/platform/current/kafka-metadata/kraft.html)
