"""Optional FastMCP server exposing Cosmic Python application ports."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Literal
from uuid import UUID

from mcp.server.fastmcp import FastMCP
from pydantic import EmailStr

from template.addons.mcp.application import McpUserProfile, OnboardUserResult
from template.addons.mcp.application import get_user_profile as query_user_profile
from template.addons.mcp.application import onboard_user as register_user
from template.bootstrap import ApplicationContainer, bootstrap


def create_mcp_server(container: ApplicationContainer | None = None) -> FastMCP:
    """Create an opt-in Streamable HTTP MCP server.

    Args:
        container: Optional application dependency override.

    Returns:
        A configured FastMCP server.
    """
    app_container = container or bootstrap()

    @asynccontextmanager
    async def lifespan(_: FastMCP):
        """Manage resources owned by the standalone MCP process."""
        app_container.startup()
        try:
            yield
        finally:
            app_container.shutdown()

    server = FastMCP(
        "Cosmic FastAPI",
        instructions=(
            "Use tools for explicit write requests. Read resources before making decisions that depend on persisted "
            "user preferences."
        ),
        lifespan=lifespan,
        json_response=True,
        stateless_http=True,
    )

    @server.tool()
    def onboard_user(
        name: str,
        email: EmailStr,
        theme: Literal["light", "dark"] = "light",
        language: str = "en",
        marketing_enabled: bool = False,
        backup_email: EmailStr | None = None,
    ) -> OnboardUserResult:
        """Register a user and return the profile resource an agent should read next."""
        return register_user(
            name=name,
            email=email,
            theme=theme,
            language=language,
            marketing_enabled=marketing_enabled,
            backup_email=backup_email,
            container=app_container,
        )

    @server.resource("users://{user_id}")
    def user_profile(user_id: UUID) -> McpUserProfile:
        """Read persisted user preferences before taking user-specific actions."""
        return query_user_profile(user_id, app_container)

    return server


if __name__ == "__main__":  # pragma: no cover - exercised by running the optional addon
    create_mcp_server().run(transport="streamable-http")
