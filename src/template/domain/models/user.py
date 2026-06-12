"""User aggregate and value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from template.domain.events.user import UserDeactivated, UserRegistered
from template.domain.messages import Event


@dataclass(frozen=True)
class UserSettings:
    """Represent user-specific preferences."""

    theme: Literal["light", "dark"] = "light"
    language: str = "en"
    marketing_enabled: bool = False
    backup_email: str | None = None


@dataclass
class User:
    """Represent a registered user aggregate."""

    name: str
    email: str
    settings: UserSettings = field(default_factory=UserSettings)
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    events: list[Event] = field(default_factory=list, compare=False)

    @classmethod
    def register(
        cls,
        name: str,
        email: str,
        settings: UserSettings | None = None,
        user_id: UUID | None = None,
    ) -> User:
        """Register a user and record the resulting domain event.

        Args:
            name: User display name.
            email: Unique user email address.
            settings: Optional user preferences.
            user_id: Optional identity supplied by the caller.

        Returns:
            The newly registered user.
        """
        user = cls(
            id=user_id or uuid4(),
            name=name.strip(),
            email=email.strip().lower(),
            settings=settings or UserSettings(),
        )
        user.events.append(UserRegistered(user_id=user.id, email=user.email))
        return user

    def deactivate(self) -> None:
        """Deactivate the user and record the resulting domain event.

        Deactivation is idempotent: deactivating an already-inactive user
        leaves the aggregate unchanged and records no further event.
        """
        if not self.is_active:
            return
        self.is_active = False
        self.events.append(UserDeactivated(user_id=self.id))
