"""SQLAlchemy read-side query adapters."""

from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from template.adapters.models.user import UserRecord
from template.domain.models.user import UserSettings
from template.service_layer.read_models import UserReadModel


class SqlAlchemyUserReader:
    """Read user projections without rehydrating write-side aggregates."""

    def __init__(self, session_factory: sessionmaker[Session]):
        """Initialize the reader.

        Args:
            session_factory: Factory used to create SQLAlchemy sessions.
        """
        self.session_factory = session_factory

    def get(self, user_id: UUID) -> UserReadModel | None:
        """Return a user projection by identity."""
        with self.session_factory() as session:
            record = session.get(UserRecord, str(user_id))
            if record is None:
                return None
            return UserReadModel(
                id=UUID(record.id),
                name=record.name,
                email=record.email,
                is_active=record.is_active,
                settings=UserSettings(**record.settings),
            )
