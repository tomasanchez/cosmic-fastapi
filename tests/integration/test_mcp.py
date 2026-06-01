"""Integration tests for the optional MCP protocol adapter."""

import asyncio
import json

import pytest
from pydantic import AnyUrl

pytest.importorskip("mcp")
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextResourceContents

from template.addons.mcp.server import create_mcp_server
from template.bootstrap import bootstrap
from template.settings.database_settings import DatabaseSettings


class TestMcpServer:
    """Test cases for MCP client interactions."""

    def test_onboards_a_user_and_reads_the_profile_resource(self):
        """
        GIVEN an opt-in MCP server
        WHEN a client calls the onboarding tool and reads the returned resource
        THEN MCP exposes the selected Cosmic Python application operations
        """
        # GIVEN
        container = bootstrap(DatabaseSettings(URL="sqlite+pysqlite://", AUTO_CREATE_SCHEMA=True))
        container.startup()

        async def exercise_server():
            async with create_connected_server_and_client_session(create_mcp_server(container)) as session:
                tools = await session.list_tools()
                result = await session.call_tool(
                    "onboard_user",
                    {"name": "Ada Lovelace", "email": "ada@example.com", "theme": "dark"},
                )
                assert result.structuredContent is not None
                resource_uri = result.structuredContent["resourceUri"]
                resource = await session.read_resource(AnyUrl(resource_uri))
                contents = resource.contents[0]
                assert isinstance(contents, TextResourceContents)
                return tools, result, json.loads(contents.text)

        # WHEN
        try:
            tools, result, profile = asyncio.run(exercise_server())
        finally:
            container.shutdown()

        # THEN
        assert [tool.name for tool in tools.tools] == ["onboard_user"]
        assert result.isError is False
        assert result.structuredContent is not None
        assert result.structuredContent["profile"]["settings"]["theme"] == "dark"
        assert profile["email"] == "ada@example.com"
