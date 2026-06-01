"""Test suite for the broker-neutral outbox relay."""

from typing import Any

from template.service_layer.outbox import AbstractOutboxUnitOfWork, OutboxMessage, relay_pending_events


class FakeOutboxRepository:
    """Record relay bookkeeping without persistence infrastructure."""

    def __init__(self, messages: list[OutboxMessage]):
        """Initialize pending messages."""
        self.messages = messages
        self.attempted: list[OutboxMessage] = []
        self.published: list[OutboxMessage] = []

    def list_pending(self, limit: int = 100) -> list[OutboxMessage]:
        """Return pending messages up to the requested limit."""
        return self.messages[:limit]

    def mark_attempted(self, message: OutboxMessage) -> None:
        """Record one publication attempt."""
        self.attempted.append(message)

    def mark_published(self, message: OutboxMessage) -> None:
        """Record a successful publication."""
        self.published.append(message)


class FakeOutboxUnitOfWork(AbstractOutboxUnitOfWork):
    """Provide relay bookkeeping without SQLAlchemy."""

    def __init__(self, messages: list[OutboxMessage]):
        """Initialize fake persistence."""
        self.repository = FakeOutboxRepository(messages)
        self.outbox = self.repository
        self.commits = 0
        self.rolled_back = False

    def commit(self) -> None:
        """Record one commit."""
        self.commits += 1

    def rollback(self) -> None:
        """Record a rollback."""
        self.rolled_back = True


class FakeIntegrationMessageBus:
    """Record external events without a broker SDK."""

    def __init__(self):
        """Initialize published messages."""
        self.published: list[tuple[str, str, dict[str, Any]]] = []

    def publish(self, event_type: str, key: str, payload: dict[str, Any]) -> None:
        """Record one external event."""
        self.published.append((event_type, key, payload))


class TestRelayPendingEvents:
    """Test broker-neutral relay orchestration."""

    def test_publishes_through_the_external_message_bus_port(self):
        """
        GIVEN an outbox unit of work and an external message bus
        WHEN pending events are relayed
        THEN orchestration needs neither SQLAlchemy nor a broker SDK
        """
        # GIVEN
        message = OutboxMessage(
            id="event-1",
            event_type="user.registered",
            aggregate_id="user-1",
            payload={"schemaVersion": 1},
        )
        uow = FakeOutboxUnitOfWork([message])
        message_bus = FakeIntegrationMessageBus()

        # WHEN
        published = relay_pending_events(lambda: uow, message_bus)

        # THEN
        assert published == 1
        assert message_bus.published == [("user.registered", "user-1", {"schemaVersion": 1})]
        assert uow.repository.attempted == [message]
        assert uow.repository.published == [message]
        assert uow.commits == 1
        assert uow.rolled_back
