"""Transactional outbox persistence adapter."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from template.adapters.models.outbox import OutboxRecord
from template.domain.events.user import UserRegistered
from template.domain.messages import Event
from template.integration_events.user import UserRegisteredV1
from template.service_layer.outbox import AbstractOutboxUnitOfWork, OutboxMessage


def stage_integration_event(session: Session, event: Event) -> None:
    """Translate and stage a supported domain event in the current transaction."""
    if isinstance(event, UserRegistered):
        integration_event = UserRegisteredV1.from_domain(event)
        session.add(
            OutboxRecord(
                id=str(integration_event.event_id),
                event_type=integration_event.event_type,
                aggregate_id=str(integration_event.payload.user_id),
                payload=integration_event.model_dump(mode="json"),
                occurred_at=integration_event.occurred_at,
                published_at=None,
                attempts=0,
            )
        )


class SqlAlchemyOutboxRepository:
    """Load and update integration events waiting for publication."""

    def __init__(self, session: Session):
        """Initialize the repository with its transaction-owned session."""
        self.session = session

    def list_pending(self, limit: int = 100) -> list[OutboxMessage]:
        """Return unpublished events in occurrence order."""
        statement = (
            select(OutboxRecord)
            .where(OutboxRecord.published_at.is_(None))
            .order_by(OutboxRecord.occurred_at)
            .limit(limit)
        )
        return [self._to_message(record) for record in self.session.scalars(statement)]

    def mark_attempted(self, message: OutboxMessage) -> None:
        """Record one broker publication attempt."""
        self._get_record(message).attempts += 1

    def mark_published(self, message: OutboxMessage) -> None:
        """Record a successful broker publication."""
        self._get_record(message).published_at = datetime.now(UTC)

    def _get_record(self, message: OutboxMessage) -> OutboxRecord:
        """Return the persistence record for one relay message."""
        record = self.session.get(OutboxRecord, message.id)
        if record is None:  # pragma: no cover - defensive transaction guard
            raise LookupError(message.id)
        return record

    @staticmethod
    def _to_message(record: OutboxRecord) -> OutboxMessage:
        """Translate persistence state into an application message."""
        return OutboxMessage(
            id=record.id,
            event_type=record.event_type,
            aggregate_id=record.aggregate_id,
            payload=record.payload,
        )


class SqlAlchemyOutboxUnitOfWork(AbstractOutboxUnitOfWork):
    """Manage relay bookkeeping through a SQLAlchemy session."""

    def __init__(self, session_factory: sessionmaker[Session]):
        """Initialize the unit of work."""
        self.session_factory = session_factory

    def __enter__(self) -> "SqlAlchemyOutboxUnitOfWork":
        """Open the relay session and repository."""
        self.session = self.session_factory()
        self.outbox = SqlAlchemyOutboxRepository(self.session)
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback,
    ) -> None:
        """Roll back unfinished work and close the relay session."""
        super().__exit__(exception_type, exception, traceback)
        self.session.close()

    def commit(self) -> None:
        """Commit relay bookkeeping."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back relay bookkeeping."""
        self.session.rollback()
