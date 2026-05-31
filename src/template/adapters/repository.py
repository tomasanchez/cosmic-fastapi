"""Persistence repositories."""

from __future__ import annotations

from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from template.adapters.models.user import UserRecord
from template.domain.models.user import User, UserSettings


class SqlAlchemyUserRepository:
    """Persist user aggregates with SQLAlchemy."""

    def __init__(self, session: Session):
        """Initialize the repository.

        Args:
            session: SQLAlchemy session owned by the unit of work.
        """
        self.session = session
        self.seen: list[User] = []

    def add(self, user: User) -> None:
        """Persist a new user."""
        self.session.add(self._to_record(user))
        self.seen.append(user)

    def get(self, user_id: UUID) -> User | None:
        """Return a user by identity."""
        return self._remember(self.session.get(UserRecord, str(user_id)))

    def get_by_email(self, email: str) -> User | None:
        """Return a user by normalized email address."""
        record = self.session.scalar(select(UserRecord).where(UserRecord.email == email.strip().lower()))
        return self._remember(record)

    def _remember(self, record: UserRecord | None) -> User | None:
        """Translate and track a loaded aggregate."""
        if record is None:
            return None
        user = self._to_domain(record)
        self.seen.append(user)
        return user

    @staticmethod
    def _to_record(user: User) -> UserRecord:
        """Translate a domain aggregate into a persistence record."""
        return UserRecord(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            settings={
                "theme": user.settings.theme,
                "language": user.settings.language,
                "marketing_enabled": user.settings.marketing_enabled,
                "backup_email": user.settings.backup_email,
            },
            created_at=user.created_at,
        )

    @staticmethod
    def _to_domain(record: UserRecord) -> User:
        """Translate a persistence record into a domain aggregate."""
        created_at = record.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        return User(
            id=UUID(record.id),
            name=record.name,
            email=record.email,
            is_active=record.is_active,
            settings=UserSettings(**record.settings),
            created_at=created_at,
        )
