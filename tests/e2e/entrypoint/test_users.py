"""End-to-end tests for user entrypoints."""

from collections.abc import Iterator

import pytest
from fastapi import status
from starlette.testclient import TestClient

from template.asgi import get_application
from template.bootstrap import bootstrap
from template.domain.events.user import UserRegistered
from template.settings.database_settings import DatabaseSettings


@pytest.fixture(name="user_client")
def fixture_user_client() -> Iterator[tuple[TestClient, list[UserRegistered]]]:
    """Create an API client with isolated in-memory persistence."""
    published: list[UserRegistered] = []
    container = bootstrap(DatabaseSettings(URL="sqlite+pysqlite://", AUTO_CREATE_SCHEMA=True), publish=published.append)
    with TestClient(get_application(container)) as client:
        yield client, published


class TestUsersEntryPoint:
    """Test cases for user HTTP workflows."""

    def test_registers_and_queries_a_user(self, user_client: tuple[TestClient, list[UserRegistered]]):
        """
        GIVEN a running FastAPI application
        WHEN a user is registered and queried
        THEN the API returns the persisted user and publishes the event
        """
        # GIVEN
        client, published = user_client

        # WHEN
        create_response = client.post("/api/v1/users", json={"name": "Ada Lovelace", "email": "ada@example.com"})
        user_id = create_response.json()["data"]["id"]
        query_response = client.get(f"/api/v1/users/{user_id}")

        # THEN
        assert create_response.status_code == status.HTTP_201_CREATED
        assert query_response.status_code == status.HTTP_200_OK
        assert query_response.json()["data"]["email"] == "ada@example.com"
        assert published == [UserRegistered(user_id=published[0].user_id, email="ada@example.com")]

    def test_rejects_a_duplicate_email(self, user_client: tuple[TestClient, list[UserRegistered]]):
        """
        GIVEN a registered user
        WHEN another registration uses the same email
        THEN the API returns a conflict response
        """
        # GIVEN
        client, _ = user_client
        payload = {"name": "Ada Lovelace", "email": "ada@example.com"}
        client.post("/api/v1/users", json=payload)

        # WHEN
        response = client.post("/api/v1/users", json=payload)

        # THEN
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_returns_not_found_for_an_unknown_user(self, user_client: tuple[TestClient, list[UserRegistered]]):
        """
        GIVEN a running FastAPI application
        WHEN an unknown user is queried
        THEN the API returns a not-found response
        """
        # GIVEN
        client, _ = user_client

        # WHEN
        response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

        # THEN
        assert response.status_code == status.HTTP_404_NOT_FOUND
