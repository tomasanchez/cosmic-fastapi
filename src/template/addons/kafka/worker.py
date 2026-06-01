"""Standalone transactional outbox relay worker."""

import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from template.adapters.outbox import SqlAlchemyOutboxUnitOfWork
from template.addons.kafka.messagebus import KafkaIntegrationMessageBus
from template.service_layer.outbox import relay_pending_events
from template.settings.database_settings import DatabaseSettings
from template.settings.kafka_settings import KafkaSettings

log = logging.getLogger(__name__)


def run_forever() -> None:
    """Publish pending outbox events until the process stops."""
    kafka_settings = KafkaSettings()
    engine = create_engine(DatabaseSettings().URL)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    message_bus = KafkaIntegrationMessageBus(
        bootstrap_servers=kafka_settings.BOOTSTRAP_SERVERS,
        topic=kafka_settings.USER_EVENTS_TOPIC,
        timeout=kafka_settings.PUBLISH_TIMEOUT,
    )
    try:
        while True:
            published = relay_pending_events(
                lambda: SqlAlchemyOutboxUnitOfWork(session_factory),
                message_bus,
                kafka_settings.BATCH_SIZE,
            )
            if published:
                log.info("Published %s integration events", published)
            time.sleep(kafka_settings.RELAY_INTERVAL)
    finally:
        engine.dispose()


if __name__ == "__main__":  # pragma: no cover - exercised by running the optional addon
    run_forever()
