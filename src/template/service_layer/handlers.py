"""Application command and event handlers."""

from collections.abc import Callable
from uuid import UUID

from template.domain.commands.user import RegisterUser
from template.domain.events.user import UserRegistered
from template.domain.models.user import User
from template.service_layer.unit_of_work import AbstractUnitOfWork, IntegrityConflict


class EmailAlreadyRegistered(ValueError):
    """Raised when a registration uses an existing email address."""


def register_user(command: RegisterUser, uow: AbstractUnitOfWork) -> UUID:
    """Register a user.

    Args:
        command: User registration request.
        uow: Transaction boundary.

    Returns:
        The registered user identity.

    Raises:
        EmailAlreadyRegistered: If the normalized email already exists.
    """
    with uow:
        if uow.users.get_by_email(command.email) is not None:
            raise EmailAlreadyRegistered(command.email)
        user = User.register(
            name=command.name,
            email=str(command.email),
            settings=command.settings.to_domain(),
            user_id=command.user_id,
        )
        uow.users.add(user)
        try:
            uow.commit()
        except IntegrityConflict as error:
            raise EmailAlreadyRegistered(command.email) from error
    return user.id


def publish_user_registered(event: UserRegistered, publish: Callable[[UserRegistered], None]) -> None:
    """Publish user registration for interested external adapters."""
    publish(event)
