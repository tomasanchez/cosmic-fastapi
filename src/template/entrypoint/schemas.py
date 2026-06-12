"""Pydantic schemas used at application boundaries."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Provide camel-case serialization for API schemas."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        use_enum_values=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
    )


class ResponseModel[S: CamelCaseModel](CamelCaseModel):
    """Wrap successful API response data."""

    data: S | list[S] = Field(description="The response data.")


class LivenessProbed(CamelCaseModel):
    """Represent a successful application liveness probe."""

    status: Literal["Ok", "Error"] = Field(description="The status of the application.", default="Ok")


class ReadinessProbed(CamelCaseModel):
    """Represent a successful application readiness probe."""

    status: Literal["Ready", "Error"] = Field(description="The readiness probe of the application.", default="Ready")
