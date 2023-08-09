"""
Test suite for ASGI Application
"""
from template.asgi import get_application


class TestASGI:
    """
    Unit test suite for ASGI Application
    """

    def test_get_application(self):
        """
        GIVEN a FastAPI application
        WHEN the application is initialized
        THEN the application is returned
        """
        assert get_application() is not None
