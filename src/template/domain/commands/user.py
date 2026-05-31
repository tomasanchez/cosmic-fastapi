"""Commands handled by user application services."""

from uuid import UUID, uuid4

from pydantic import Field

from template.domain.messages import Command
from template.domain.models.user import UserSettings


class RegisterUser(Command):
    """Request registration of one user."""

    name: str
    email: str
    settings: UserSettings = Field(default_factory=UserSettings)
    user_id: UUID = Field(default_factory=uuid4)
