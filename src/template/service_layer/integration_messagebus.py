"""Broker-neutral external message bus port."""

from typing import Any, Protocol


class IntegrationMessageBus(Protocol):
    """Publish versioned integration events to an external message bus."""

    def publish(self, event_type: str, key: str, payload: dict[str, Any]) -> None:
        """Publish one integration event or raise an exception."""
