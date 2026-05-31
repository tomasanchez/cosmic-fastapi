"""Events raised by the user aggregate."""

from uuid import UUID

from template.domain.messages import Event


class UserRegistered(Event):
    """Record that a user completed registration."""

    user_id: UUID
    email: str
