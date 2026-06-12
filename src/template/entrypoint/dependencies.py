"""Shared FastAPI dependencies for entrypoints.

Resolves the process-level application container from request state so that
entrypoint handlers depend on the composition root through dependency
injection rather than module-level globals.
"""

from typing import Annotated

from fastapi import Depends, Request

from template.bootstrap import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    """Return application dependencies from FastAPI state."""
    return request.app.state.container


Container = Annotated[ApplicationContainer, Depends(get_container)]
