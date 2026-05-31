"""tests/unit/domain/models/test_base.py
Unit test cases for BaseModel
"""

from typing import Any, cast

import pytest
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

from template.adapters.models.base import Base, BasePydanticField, PydanticModelField, PydanticModelListField
from template.domain.models.base import BaseEnum


class TestBase:
    def test_dumps_to_dict(self):
        """
        GIVEN a Base class with columns
        AND an instance of the class
        WHEN model_dump is called
        THEN it maps to dict
        """

        # GIVEN
        class TestModel(Base):
            __tablename__ = "test_model"
            test_id: Mapped[int] = mapped_column(primary_key=True)
            foo: Mapped[str]
            bar: Mapped[int]
            foobar: Mapped[bool]

        instance = TestModel(test_id=1, foo="foo", bar=1, foobar=True)

        # WHEN
        result = instance.model_dump()

        # THEN
        assert result == {"test_id": 1, "foo": "foo", "bar": 1, "foobar": True}

    def test_dumps_recursively(self):
        """
        GIVEN a pydantic model field
        AND a Base class with nested PydanticModel fields
        AND an instance of the class
        WHEN model_dump is called
        THEN it maps to dict with pydantic dicts
        """

        class TestPydanticField(BaseModel):
            foo: str = "foo"
            bar: int = 0

        # AND
        class NestedTestModel(Base):
            __tablename__ = "test_pydantic_model"
            test_id: Mapped[int] = mapped_column(primary_key=True)
            foobar: Mapped[TestPydanticField] = mapped_column(PydanticModelField(TestPydanticField))
            foobars: Mapped[list[TestPydanticField]] = mapped_column(PydanticModelListField(TestPydanticField))
            nullable: Mapped[str | None]

        # AND
        instance = NestedTestModel(test_id=1, foobar=TestPydanticField(), foobars=[TestPydanticField()], nullable=None)

        # WHEN
        result = instance.model_dump()

        # THEN
        assert result == {
            "test_id": 1,
            "foobar": {"foo": "foo", "bar": 0},
            "foobars": [{"foo": "foo", "bar": 0}],
            "nullable": None,
        }

    def test_validates_pydantic_json_fields(self):
        """
        GIVEN SQLAlchemy Pydantic JSON field adapters
        WHEN values are bound and loaded
        THEN models are serialized, restored, and invalid values are rejected
        """

        # GIVEN
        class TestPydanticField(BaseModel):
            foo: str

        class OtherPydanticField(BaseModel):
            bar: str

        single_field = PydanticModelField(TestPydanticField)
        list_field = PydanticModelListField(TestPydanticField)
        model = TestPydanticField(foo="foo")

        # WHEN / THEN
        assert single_field.process_bind_param(None, None) is None  # type: ignore[arg-type]
        assert single_field.process_bind_param(model, None) == {"foo": "foo"}  # type: ignore[arg-type]
        assert single_field.process_result_value(None, None) is None  # type: ignore[arg-type]
        assert single_field.process_result_value({"foo": "foo"}, None) == model  # type: ignore[arg-type]
        assert list_field.process_bind_param(None, None) is None  # type: ignore[arg-type]
        assert list_field.process_bind_param([model], None) == [{"foo": "foo"}]  # type: ignore[arg-type]
        assert list_field.process_result_value(None, None) is None  # type: ignore[arg-type]
        assert list_field.process_result_value([{"foo": "foo"}], None) == [model]  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            BasePydanticField(cast(Any, str))
        with pytest.raises(TypeError):
            single_field._validate_and_dump_model(OtherPydanticField(bar="bar"))
        with pytest.raises(TypeError):
            list_field.process_bind_param(model, None)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            list_field.process_result_value({"foo": "foo"}, None)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            single_field.process_result_value({}, None)  # type: ignore[arg-type]


class TestBaseEnum:
    def test_list_values(self):
        """
        GIVEN a BaseEnum class
        WHEN list_values is called
        THEN it returns a list of values
        """

        # GIVEN
        class TestEnum(BaseEnum):
            FOO = "foo"
            BAR = "bar"
            FOOBAR = "foobar"

        # WHEN
        result = TestEnum.list()

        # THEN
        assert result == ["foo", "bar", "foobar"]
