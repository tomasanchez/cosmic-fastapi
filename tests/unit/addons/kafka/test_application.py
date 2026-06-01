"""Test suite for the broker-neutral outbox relay application service."""

from functools import partial
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from template.adapters.models.base import Base
from template.adapters.models.outbox import OutboxRecord
from template.adapters.outbox import SqlAlchemyOutboxUnitOfWork
from template.adapters.unit_of_work import SqlAlchemyUnitOfWork
from template.domain.models.user import User
from template.service_layer.outbox import relay_pending_events


class FakeIntegrationMessageBus:
    """Record integration events sent by the relay."""

    def __init__(self, error: Exception | None = None):
        """Initialize the fake publisher."""
        self.error = error
        self.published: list[tuple[str, str, dict[str, Any]]] = []

    def publish(self, event_type: str, key: str, payload: dict[str, Any]) -> None:
        """Publish or raise the configured error."""
        if self.error:
            raise self.error
        self.published.append((event_type, key, payload))


@pytest.fixture(name="session_factory")
def fixture_session_factory() -> sessionmaker[Session]:
    """Create an isolated in-memory session factory."""
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def stage_user(session_factory: sessionmaker[Session]) -> User:
    """Store one user and its outbox event."""
    user = User.register(name="Ada Lovelace", email="ada@example.com")
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        uow.users.add(user)
        uow.commit()
    return user


class TestRelayPendingEvents:
    """Test cases for relaying pending outbox rows."""

    def test_marks_acknowledged_events_as_published(self, session_factory: sessionmaker[Session]):
        """
        GIVEN a durable outbox event
        WHEN the relay publisher acknowledges it
        THEN the event is keyed by aggregate and marked as published
        """
        # GIVEN
        user = stage_user(session_factory)
        message_bus = FakeIntegrationMessageBus()

        # WHEN
        published = relay_pending_events(partial(SqlAlchemyOutboxUnitOfWork, session_factory), message_bus)

        # THEN
        with session_factory() as session:
            record = session.scalar(select(OutboxRecord))
        assert published == 1
        assert message_bus.published[0][1] == str(user.id)
        assert record is not None
        assert record.published_at is not None
        assert record.attempts == 1

    def test_keeps_failed_events_pending_for_retry(self, session_factory: sessionmaker[Session]):
        """
        GIVEN a durable outbox event
        WHEN broker publication fails
        THEN the event stays pending and records the attempt
        """
        # GIVEN
        stage_user(session_factory)

        # WHEN / THEN
        with pytest.raises(RuntimeError, match="Broker unavailable"):
            relay_pending_events(
                partial(SqlAlchemyOutboxUnitOfWork, session_factory),
                FakeIntegrationMessageBus(RuntimeError("Broker unavailable")),
            )
        with session_factory() as session:
            record = session.scalar(select(OutboxRecord))
        assert record is not None
        assert record.published_at is None
        assert record.attempts == 1
