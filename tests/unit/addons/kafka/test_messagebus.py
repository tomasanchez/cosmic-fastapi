"""Test suite for the Kafka integration message bus adapter."""

import json
from collections.abc import Callable
from typing import Any

import pytest

pytest.importorskip("confluent_kafka")
from confluent_kafka import KafkaError

from template.addons.kafka.messagebus import KafkaIntegrationMessageBus, KafkaPublishFailed


class FakeProducer:
    """Simulate Confluent producer acknowledgements."""

    def __init__(self, remaining: int = 0, error: KafkaError | None = None):
        """Initialize acknowledgement behavior."""
        self.remaining = remaining
        self.error = error
        self.message: tuple[str, str, bytes] | None = None

    def produce(
        self,
        topic: str,
        *,
        key: str,
        value: bytes,
        on_delivery: Callable[[KafkaError | None, Any], None],
    ) -> None:
        """Capture a message and invoke its delivery callback."""
        self.message = (topic, key, value)
        on_delivery(self.error, None)

    def flush(self, timeout: float | None = None) -> int:
        """Return configured undelivered queue size."""
        return self.remaining


class TestKafkaIntegrationMessageBus:
    """Test cases for JSON publication acknowledgements."""

    def test_publishes_json_with_the_aggregate_key(self):
        """
        GIVEN an acknowledged Kafka producer
        WHEN an integration event is published
        THEN its JSON envelope is sent with the aggregate key
        """
        # GIVEN
        producer = FakeProducer()
        message_bus = KafkaIntegrationMessageBus("localhost:9092", "users.events", producer=producer)

        # WHEN
        message_bus.publish("user.registered", "user-1", {"schemaVersion": 1})

        # THEN
        assert producer.message is not None
        assert producer.message[:2] == ("users.events", "user-1")
        assert json.loads(producer.message[2]) == {"schemaVersion": 1}

    @pytest.mark.parametrize("producer", [FakeProducer(remaining=1), FakeProducer(error=KafkaError(1))])
    def test_rejects_unacknowledged_messages(self, producer: FakeProducer):
        """
        GIVEN a Kafka producer that cannot acknowledge an event
        WHEN an integration event is published
        THEN publication fails so the outbox row remains pending
        """
        # GIVEN
        message_bus = KafkaIntegrationMessageBus("localhost:9092", "users.events", producer=producer)

        # WHEN / THEN
        with pytest.raises(KafkaPublishFailed):
            message_bus.publish("user.registered", "user-1", {"schemaVersion": 1})
