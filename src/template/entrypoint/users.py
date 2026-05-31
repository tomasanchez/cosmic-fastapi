"""FastAPI entrypoints for user use cases."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import EmailStr, Field

from template.bootstrap import ApplicationContainer
from template.domain.commands.user import RegisterUser
from template.domain.models.user import UserSettings
from template.entrypoint.schemas import CamelCaseModel, ResponseModel
from template.service_layer.handlers import EmailAlreadyRegistered
from template.service_layer.queries import get_user
from template.service_layer.read_models import UserReadModel

router = APIRouter(prefix="/users", tags=["Users"])


class UserSettingsSchema(CamelCaseModel):
    """Represent user preferences at an API boundary."""

    theme: Literal["light", "dark"] = Field(default="light")
    language: str = Field(default="en")
    marketing_enabled: bool = Field(default=False)
    backup_email: EmailStr | None = Field(default=None)

    def to_domain(self) -> UserSettings:
        """Translate boundary data into a domain value object."""
        return UserSettings(
            theme=self.theme,
            language=self.language,
            marketing_enabled=self.marketing_enabled,
            backup_email=str(self.backup_email) if self.backup_email else None,
        )


class RegisterUserRequest(CamelCaseModel):
    """Validate a user registration request."""

    name: str = Field(min_length=1)
    email: EmailStr
    settings: UserSettingsSchema = Field(default_factory=UserSettingsSchema)


class UserResponse(CamelCaseModel):
    """Serialize a user aggregate."""

    id: UUID
    name: str
    email: EmailStr
    is_active: bool
    settings: UserSettingsSchema

    @classmethod
    def from_read_model(cls, user: UserReadModel) -> "UserResponse":
        """Translate an application read model into an API response."""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            settings=UserSettingsSchema(
                theme=user.settings.theme,
                language=user.settings.language,
                marketing_enabled=user.settings.marketing_enabled,
                backup_email=user.settings.backup_email,
            ),
        )


def get_container(request: Request) -> ApplicationContainer:
    """Return application dependencies from FastAPI state."""
    return request.app.state.container


Container = Annotated[ApplicationContainer, Depends(get_container)]


@router.post("", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterUserRequest, container: Container) -> ResponseModel[UserResponse]:
    """Register a user."""
    try:
        user_id = container.bus.handle(
            RegisterUser(name=payload.name, email=str(payload.email), settings=payload.settings.to_domain())
        )
    except EmailAlreadyRegistered as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from error

    user = get_user(user_id, container.user_reader)
    if user is None:  # pragma: no cover - defensive adapter guard
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registered user not found")
    return ResponseModel(data=UserResponse.from_read_model(user))


@router.get("/{user_id}")
def query_user(user_id: UUID, container: Container) -> ResponseModel[UserResponse]:
    """Return a registered user."""
    user = get_user(user_id, container.user_reader)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=UserResponse.from_read_model(user))
