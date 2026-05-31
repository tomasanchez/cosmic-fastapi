"""SQLAlchemy transaction adapter."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from template.adapters.repository import SqlAlchemyUserRepository
from template.service_layer.unit_of_work import AbstractUnitOfWork, IntegrityConflict


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Manage a SQLAlchemy session as one atomic unit."""

    def __init__(self, session_factory: sessionmaker[Session]):
        """Initialize the unit of work.

        Args:
            session_factory: Factory used to create a SQLAlchemy session.
        """
        self.session_factory = session_factory

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        """Open a session and repositories."""
        self.session = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Roll back unfinished work and close the session."""
        super().__exit__(exception_type, exception, traceback)
        self.session.close()

    def commit(self) -> None:
        """Commit the SQLAlchemy transaction."""
        try:
            self.session.commit()
        except IntegrityError as error:
            raise IntegrityConflict from error

    def rollback(self) -> None:
        """Roll back the SQLAlchemy transaction."""
        self.session.rollback()
