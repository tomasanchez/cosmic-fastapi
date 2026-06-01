"""Application-facing operations exposed by the optional MCP adapter."""

from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field

from template.bootstrap import ApplicationContainer
from template.domain.commands.user import RegisterUser, RegisterUserSettings
from template.entrypoint.schemas import CamelCaseModel
from template.service_layer.handlers import EmailAlreadyRegistered
from template.service_layer.queries import get_user
from template.service_layer.read_models import UserReadModel


class McpUserSettings(CamelCaseModel):
    """Represent user preferences returned to an MCP client."""

    theme: Literal["light", "dark"]
    language: str
    marketing_enabled: bool
    backup_email: EmailStr | None


class McpUserProfile(CamelCaseModel):
    """Represent an agent-readable user profile."""

    id: UUID
    name: str
    email: EmailStr
    is_active: bool
    settings: McpUserSettings

    @classmethod
    def from_read_model(cls, user: UserReadModel) -> "McpUserProfile":
        """Translate an application read model into an MCP profile."""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            settings=McpUserSettings(
                theme=user.settings.theme,
                language=user.settings.language,
                marketing_enabled=user.settings.marketing_enabled,
                backup_email=user.settings.backup_email,
            ),
        )


class OnboardUserResult(CamelCaseModel):
    """Return an onboarded profile and its durable MCP resource URI."""

    profile: McpUserProfile
    resource_uri: str
    next_step: str = Field(
        default="Read the profile resource before making decisions that depend on this user's preferences."
    )


class McpUserNotFound(LookupError):
    """Raised when an MCP resource references an unknown user."""

    def __init__(self, user_id: UUID):
        """Initialize the error for an unknown user identity."""
        super().__init__(f"User not found: {user_id}")


def onboard_user(
    *,
    name: str,
    email: EmailStr,
    container: ApplicationContainer,
    theme: Literal["light", "dark"] = "light",
    language: str = "en",
    marketing_enabled: bool = False,
    backup_email: EmailStr | None = None,
) -> OnboardUserResult:
    """Register a user and return agent-oriented follow-up context.

    Args:
        name: User display name.
        email: Unique user email address.
        container: Application dependencies.
        theme: Preferred display theme.
        language: Preferred user language.
        marketing_enabled: Whether the user accepts marketing communication.
        backup_email: Optional recovery email address.

    Returns:
        The persisted user profile and its MCP resource URI.

    Raises:
        EmailAlreadyRegistered: If the primary email is already registered.
    """
    command = RegisterUser(
        name=name,
        email=email,
        settings=RegisterUserSettings(
            theme=theme,
            language=language,
            marketing_enabled=marketing_enabled,
            backup_email=backup_email,
        ),
    )
    user_id = container.bus.handle(command)
    return OnboardUserResult(profile=get_user_profile(user_id, container), resource_uri=f"users://{user_id}")


def get_user_profile(user_id: UUID, container: ApplicationContainer) -> McpUserProfile:
    """Return an agent-readable user profile resource.

    Args:
        user_id: Registered user identity.
        container: Application dependencies.

    Returns:
        A profile shaped for an MCP consumer.

    Raises:
        McpUserNotFound: If the user identity is unknown.
    """
    user = get_user(user_id, container.user_reader)
    if user is None:
        raise McpUserNotFound(user_id)
    return McpUserProfile.from_read_model(user)


__all__ = ["EmailAlreadyRegistered", "McpUserNotFound", "get_user_profile", "onboard_user"]
