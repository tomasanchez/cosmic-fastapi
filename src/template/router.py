"""Application configuration - root APIRouter.

Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications
"""
from fastapi import APIRouter

from template.entrypoint import monitor

api_v1_prefix: str = "/api/v1"

root_router: APIRouter = APIRouter()
api_router_v1: APIRouter = APIRouter(prefix=api_v1_prefix)

# Base routers
root_router.include_router(monitor.router)

# API routers
