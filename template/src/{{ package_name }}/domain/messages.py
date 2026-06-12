"""Shared schema behavior for application messages."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Message(BaseModel):
    """Provide immutable camel-case schemas for commands and events."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
        populate_by_name=True,
        serialize_by_alias=True,
        str_strip_whitespace=True,
    )


class Command(Message):
    """Represent a request for the application to perform work."""


class Event(Message):
    """Represent a fact that already happened."""
