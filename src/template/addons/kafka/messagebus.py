"""Kafka implementation of the external integration message bus."""

import json
from collections.abc import Callable
from typing import Any, Protocol

from confluent_kafka import KafkaError, Producer


class KafkaPublishFailed(RuntimeError):
    """Raised when Kafka does not acknowledge an integration event."""


class KafkaProducer(Protocol):
    """Describe the Confluent producer methods used by this adapter."""

    def produce(
        self,
        topic: str,
        *,
        key: str,
        value: bytes,
        on_delivery: Callable[[KafkaError | None, Any], None],
    ) -> None:
        """Queue one Kafka message."""

    def flush(self, timeout: float | None = None) -> int:
        """Wait for queued messages and return the number still pending."""


class KafkaIntegrationMessageBus:
    """Publish JSON integration events through Kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        timeout: float = 10.0,
        producer: KafkaProducer | None = None,
    ):
        """Initialize the publisher.

        Args:
            bootstrap_servers: Comma-separated Kafka broker addresses.
            topic: Destination topic for user integration events.
            timeout: Maximum flush wait in seconds.
            producer: Optional producer override for tests.
        """
        self.topic = topic
        self.timeout = timeout
        self.producer = producer or Producer({"bootstrap.servers": bootstrap_servers})

    def publish(self, event_type: str, key: str, payload: dict[str, Any]) -> None:
        """Publish one JSON event and wait for acknowledgement."""
        errors: list[KafkaError] = []

        def capture_delivery(error: KafkaError | None, _: Any) -> None:
            if error is not None:
                errors.append(error)

        self.producer.produce(
            self.topic,
            key=key,
            value=json.dumps(payload).encode(),
            on_delivery=capture_delivery,
        )
        remaining = self.producer.flush(self.timeout)
        if remaining or errors:
            raise KafkaPublishFailed
