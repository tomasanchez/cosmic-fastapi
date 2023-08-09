"""
Test suite for Schemas
"""
from template.domain.schemas import CamelCaseModel, ResponseModel


class TestSchemas:
    """
    Test cases for Schemas
    """

    def test_camel_case_model(self):
        """
        GIVEN a CamelCaseModel
        WHEN the model is dumped default to camel case json compatible
        THEN the result is camel case
        """

        class DummyModel(CamelCaseModel):
            """
            A dummy model
            """

            foo: str
            bar: int
            foo_bar: str

        model = DummyModel(foo="foo", bar=1, foo_bar="foo_bar")

        assert model.model_dump() == {"foo": "foo", "bar": 1, "fooBar": "foo_bar"}

    def test_response_model(self):
        """
        GIVEN a CamelCaseModel
        WHEN the model is included in a ResponseModel
        THEN data includes a camel case json compatible model
        """

        class DummyModel(CamelCaseModel):
            """
            A dummy model
            """

            foo: str
            bar: int
            foo_bar: str

        model = ResponseModel[DummyModel](data=DummyModel(foo="foo", bar=1, foo_bar="foo_bar"))

        data = model.model_dump().get("data")

        assert data == {"foo": "foo", "bar": 1, "fooBar": "foo_bar"}

    def test_response_model_list(self):
        """
        GIVEN many CamelCaseModel instances
        WHEN the models are included in a ResponseModel
        THEN data includes a list of camel case json compatible models
        """

        class DummyModel(CamelCaseModel):
            """
            A dummy model
            """

            foo: str
            bar: int
            foo_bar: str

        model = ResponseModel[list[DummyModel]](
            data=[
                DummyModel(foo="foo", bar=1, foo_bar="foo_bar"),
                DummyModel(foo="foo", bar=1, foo_bar="foo_bar"),
            ]
        )

        data = model.model_dump().get("data")

        assert data == [
            {"foo": "foo", "bar": 1, "fooBar": "foo_bar"},
            {"foo": "foo", "bar": 1, "fooBar": "foo_bar"},
        ]
