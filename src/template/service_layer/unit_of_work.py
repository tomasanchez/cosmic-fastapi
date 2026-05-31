"""Transaction boundaries for application handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from types import TracebackType

from template.domain.messages import Event
from template.service_layer.repository import UserRepository


class AbstractUnitOfWork(ABC):
    """Provide atomic persistence and event collection."""

    users: UserRepository

    def __enter__(self) -> AbstractUnitOfWork:
        """Enter the transaction boundary."""
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
        """Commit the current transaction."""

    @abstractmethod
    def rollback(self) -> None:
        """Roll back the current transaction."""

    def collect_new_events(self) -> Iterator[Event]:
        """Yield pending events from aggregates seen in this transaction."""
        for user in self.users.seen:
            while user.events:
                yield user.events.pop(0)
