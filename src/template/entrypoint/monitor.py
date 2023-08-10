"""Monitor entrypoint.

Responsible for probing the system liveness and readiness.
"""
from fastapi import APIRouter, status
from starlette.responses import RedirectResponse

from template.domain.events.monitor import LivenessProbed
from template.domain.schemas import ResponseModel

router = APIRouter()


@router.get(
    "/liveness",
    tags=["Monitor"],
    name="Liveness",
    status_code=status.HTTP_200_OK,
)
async def query_liveness_probe() -> ResponseModel[LivenessProbed]:
    """
    Probe the system liveness.
    """
    return ResponseModel(data=LivenessProbed())


@router.get("/", status_code=status.HTTP_301_MOVED_PERMANENTLY, include_in_schema=False)
def root_redirect():
    """
    Redirect to the API documentation.
    """
    return RedirectResponse(url="/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY)
