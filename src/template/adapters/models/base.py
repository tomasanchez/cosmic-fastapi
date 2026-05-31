"""Shared SQLAlchemy persistence model helpers."""

from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import JSON, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Provide the declarative base for persistence records."""

    def model_dump(self) -> dict[str, Any]:
        """Return mapped column values as a dictionary."""
        result = {}
        for column in self.__table__.columns:  # type: ignore[attr-defined]
            result[column.name] = self._dump_value(getattr(self, column.name))
        return result

    def _dump_value(self, value: Any) -> Any:
        """Recursively dump nested Pydantic values."""
        if value is None:
            return None
        if isinstance(value, BaseModel):
            return value.model_dump(exclude_none=True)
        if isinstance(value, list):
            return [self._dump_value(item) for item in value]
        return value


class BasePydanticField(TypeDecorator):
    """Store Pydantic models in a JSON column."""

    impl = JSON().with_variant(JSONB(), "postgresql")
    cache_ok = True

    def __init__(self, model_class: type[BaseModel], *args, **kwargs):
        """Initialize the field for one Pydantic model class."""
        if not issubclass(model_class, BaseModel):
            raise TypeError
        super().__init__(*args, **kwargs)
        self.model_class = model_class

    def _validate_and_dump_model(self, model: BaseModel) -> dict[str, Any]:
        """Validate and serialize one Pydantic model."""
        if not isinstance(model, self.model_class):
            raise TypeError
        return model.model_dump(exclude_none=True)

    def _validate_and_load_model(self, data: dict[str, Any]) -> BaseModel:
        """Validate and deserialize one Pydantic model."""
        try:
            return self.model_class.model_validate(data)
        except ValidationError as error:
            raise ValueError(error) from error


class PydanticModelField(BasePydanticField):
    """Store one Pydantic model in a JSON column."""

    def process_bind_param(self, value: BaseModel | None, dialect: Dialect) -> dict[str, Any] | None:
        """Serialize a value before persistence."""
        return None if value is None else self._validate_and_dump_model(value)

    def process_result_value(self, value: dict[str, Any] | None, dialect: Dialect) -> BaseModel | None:
        """Deserialize a value loaded from persistence."""
        return None if value is None else self._validate_and_load_model(value)


class PydanticModelListField(BasePydanticField):
    """Store a list of Pydantic models in a JSON column."""

    def process_bind_param(self, value: list[BaseModel] | None, dialect: Dialect) -> list[dict[str, Any]] | None:
        """Serialize values before persistence."""
        if value is None:
            return None
        if not isinstance(value, list):
            raise TypeError
        return [self._validate_and_dump_model(item) for item in value]

    def process_result_value(self, value: list[dict[str, Any]] | None, dialect: Dialect) -> list[BaseModel] | None:
        """Deserialize values loaded from persistence."""
        if value is None:
            return None
        if not isinstance(value, list):
            raise TypeError
        return [self._validate_and_load_model(item) for item in value]
