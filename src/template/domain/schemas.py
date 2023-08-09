"""Schemas

"Schemas" refers to the data models or data structures that are used to define the shape or structure of data
that your API receives or returns.

FastAPI relies on Pydantic, a data validation and settings management library, to define and use these schemas.

By defining schemas for your data, you can ensure that the data is correctly validated and formatted,
making your API more robust and reliable. Schemas can also be used to generate OpenAPI documentation automatically,
which can help both developers and consumers of your API understand its capabilities.
"""

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from template.utils.formatting import to_camel


class CamelCaseModel(BaseModel):
    """
    A base which attributes can be translated to camel case.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        use_enum_values=True,
        alias_generator=to_camel,
    )

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "json",
        include=None,
        exclude=None,
        by_alias: bool = True,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


S = TypeVar("S", bound=CamelCaseModel)


class ResponseModel(CamelCaseModel, Generic[S]):
    """A message model."""

    data: S | list[S] = Field(description="The response data.")
