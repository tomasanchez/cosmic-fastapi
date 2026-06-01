"""Versioned user integration events."""

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from template.domain.events.user import UserRegistered


class IntegrationEvent(BaseModel):
    """Provide a versioned camel-case public event envelope."""

    model_config = ConfigDict(alias_generator=to_camel, frozen=True, populate_by_name=True, serialize_by_alias=True)

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserRegisteredPayloadV1(BaseModel):
    """Describe the stable public payload for a registered user."""

    model_config = ConfigDict(alias_generator=to_camel, frozen=True, populate_by_name=True, serialize_by_alias=True)

    user_id: UUID
    email: str


class UserRegisteredV1(IntegrationEvent):
    """Notify external consumers that a user completed registration."""

    event_type: Literal["user.registered"] = "user.registered"
    schema_version: Literal[1] = 1
    payload: UserRegisteredPayloadV1

    @classmethod
    def from_domain(cls, event: UserRegistered) -> "UserRegisteredV1":
        """Translate an internal domain event into a public contract."""
        return cls(payload=UserRegisteredPayloadV1(user_id=event.user_id, email=event.email))
