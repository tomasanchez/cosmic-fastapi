"""Application command and event handlers."""

from collections.abc import Callable
from uuid import UUID

from template.domain.commands.user import DeactivateUser, RegisterUser
from template.domain.events.user import UserDeactivated, UserRegistered
from template.domain.models.user import User
from template.service_layer.unit_of_work import AbstractUnitOfWork, IntegrityConflict


class EmailAlreadyRegistered(ValueError):
    """Raised when a registration uses an existing email address."""


class UserNotFound(LookupError):
    """Raised when a command targets an unknown user identity."""

    def __init__(self, user_id: UUID):
        """Initialize the error for a missing user."""
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


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


def deactivate_user(command: DeactivateUser, uow: AbstractUnitOfWork) -> UUID:
    """Deactivate a user.

    Loads the aggregate through the unit of work, applies the deactivation
    behavior, and commits. The write-back on commit persists the mutated
    aggregate state even though the translation repository detaches it from
    SQLAlchemy change tracking.

    Args:
        command: User deactivation request.
        uow: Transaction boundary.

    Returns:
        The deactivated user identity.

    Raises:
        UserNotFound: If no user exists for the requested identity.
    """
    with uow:
        user = uow.users.get(command.user_id)
        if user is None:
            raise UserNotFound(command.user_id)
        user.deactivate()
        uow.commit()
    return command.user_id


def publish_user_registered(event: UserRegistered, publish: Callable[[UserRegistered], None]) -> None:
    """Publish user registration for interested external adapters."""
    publish(event)


def publish_user_deactivated(event: UserDeactivated, publish: Callable[[UserDeactivated], None]) -> None:
    """Publish user deactivation for interested external adapters."""
    publish(event)
