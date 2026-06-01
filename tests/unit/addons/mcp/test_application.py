"""Test suite for MCP-facing application operations."""

from uuid import UUID

import pytest

from template.addons.mcp.application import McpUserNotFound, get_user_profile, onboard_user
from template.bootstrap import bootstrap
from template.settings.database_settings import DatabaseSettings


@pytest.fixture(name="container")
def fixture_container():
    """Create an initialized application container."""
    container = bootstrap(DatabaseSettings(URL="sqlite+pysqlite://", AUTO_CREATE_SCHEMA=True))
    container.startup()
    try:
        yield container
    finally:
        container.shutdown()


class TestMcpApplication:
    """Test cases for agent-facing application operations."""

    def test_onboards_a_user_and_exposes_a_resource(self, container):
        """
        GIVEN an initialized MCP application adapter
        WHEN an agent onboards a user
        THEN it receives the persisted profile and a durable resource URI
        """
        # WHEN
        result = onboard_user(
            name="Ada Lovelace",
            email="ada@example.com",
            theme="dark",
            marketing_enabled=True,
            container=container,
        )

        # THEN
        assert result.resource_uri == f"users://{result.profile.id}"
        assert result.profile.settings.theme == "dark"
        assert result.model_dump(mode="json")["resourceUri"] == f"users://{result.profile.id}"

    def test_rejects_an_unknown_profile_resource(self, container):
        """
        GIVEN an initialized MCP application adapter
        WHEN an agent reads an unknown profile resource
        THEN the adapter reports that the user does not exist
        """
        # GIVEN
        user_id = UUID("00000000-0000-0000-0000-000000000000")

        # WHEN / THEN
        with pytest.raises(McpUserNotFound, match=f"User not found: {user_id}"):
            get_user_profile(user_id, container)
