"""Application implementation - ASGI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from template.router import api_router_v1, root_router
from template.settings.api_settings import ApplicationSettings

log = logging.getLogger(__name__)


async def on_startup():
    """
    Define FastAPI startup event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#startup-event
    """
    log.debug("Execute FastAPI startup event handler.")


async def on_shutdown():
    """
    Define FastAPI shutdown event handler.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#shutdown-event
    """
    log.debug("Execute FastAPI shutdown event handler.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Define FastAPI lifespan event handler.

    Args:
        app (FastAPI): Application object instance.

    Resources:
        1. https://fastapi.tiangolo.com/advanced/events/#lifespan-event
    """
    log.debug("Execute FastAPI lifespan event handler.")

    await on_startup()
    yield
    await on_shutdown()


def get_application() -> FastAPI:
    """
    Initialize FastAPI application.

    Returns:
       FastAPI: Application object instance.
    """
    log.debug("Initialize FastAPI application node.")

    settings = ApplicationSettings()

    license_info: dict[str, str] = settings.PROJECT_LICENSE.model_dump(mode="json")
    contact_info: dict[str, str] = settings.PROJECT_CONTACT.model_dump(mode="json")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        debug=settings.DEBUG,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        lifespan=lifespan,
        license_info=license_info,
        contact=contact_info,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    log.debug("Add application routes.")
    app.include_router(root_router)
    app.include_router(api_router_v1)

    return app
