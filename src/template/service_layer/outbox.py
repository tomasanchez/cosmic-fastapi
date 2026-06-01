"""Broker-neutral transactional outbox relay use case."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Protocol

from template.service_layer.integration_messagebus import IntegrationMessageBus


@dataclass(frozen=True)
class OutboxMessage:
    """Represent one durable integration event awaiting publication."""

    id: str
    event_type: str
    aggregate_id: str
    payload: dict[str, Any]


class OutboxRepository(Protocol):
    """Describe persistence required by the outbox relay."""

    def list_pending(self, limit: int = 100) -> list[OutboxMessage]:
        """Return unpublished events in occurrence order."""

    def mark_attempted(self, message: OutboxMessage) -> None:
        """Record one broker publication attempt."""

    def mark_published(self, message: OutboxMessage) -> None:
        """Record a successful broker publication."""


class AbstractOutboxUnitOfWork(ABC):
    """Provide the transaction boundary required by the outbox relay."""

    outbox: OutboxRepository

    def __enter__(self) -> AbstractOutboxUnitOfWork:
        """Enter the relay transaction boundary."""
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Roll back work that did not explicitly commit."""
        self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """Commit relay bookkeeping."""

    @abstractmethod
    def rollback(self) -> None:
        """Roll back uncommitted relay bookkeeping."""


OutboxUnitOfWorkFactory = Callable[[], AbstractOutboxUnitOfWork]


def relay_pending_events(
    uow_factory: OutboxUnitOfWorkFactory,
    message_bus: IntegrationMessageBus,
    batch_size: int = 100,
) -> int:
    """Publish pending outbox events with at-least-once delivery.

    Args:
        uow_factory: Factory for a relay-owned transaction boundary.
        message_bus: Broker-neutral external message bus.
        batch_size: Maximum number of events to publish in one relay pass.

    Returns:
        Number of successfully published events.
    """
    published = 0
    with uow_factory() as uow:
        for message in uow.outbox.list_pending(batch_size):
            uow.outbox.mark_attempted(message)
            try:
                message_bus.publish(message.event_type, message.aggregate_id, message.payload)
            except Exception:
                uow.commit()
                raise
            uow.outbox.mark_published(message)
            uow.commit()
            published += 1
    return published
