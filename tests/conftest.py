"""
Pytest Fixtures.
"""
import pytest
from starlette.testclient import TestClient

from template.main import app


@pytest.fixture(name="test_client")
def fixture_test_client() -> TestClient:
    """
    Create a test client for the FastAPI application.

    Returns:
        TestClient: A test client for the app.
    """
    return TestClient(app)
