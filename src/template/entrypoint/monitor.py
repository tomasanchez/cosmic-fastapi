"""Monitor entrypoint.

Responsible for probing the system liveness and readiness.
"""
from fastapi import APIRouter, status
from starlette.responses import RedirectResponse

from template.domain.events.monitor import LivenessProbed, ReadinessProbed
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

    When working with Kubernetes, Checks if the application within the pod is running and responsive. If the liveness
    probe fails, Kubernetes might restart the pod to recover from unresponsive states.
    """
    return ResponseModel(data=LivenessProbed())


@router.get(
    "/readiness",
    tags=["Monitor"],
    name="Readiness",
    status_code=status.HTTP_200_OK,
)
async def query_readiness_probe() -> ResponseModel[ReadinessProbed]:
    """
    Probe the system readiness.

    When working with Kubernetes, Checks if the pod is ready to handle incoming traffic and requests. If the
     readiness probe fails, Kubernetes temporarily stops sending traffic to the pod.
    """
    return ResponseModel(data=ReadinessProbed())


@router.get("/", status_code=status.HTTP_301_MOVED_PERMANENTLY, include_in_schema=False)
def root_redirect():
    """
    Redirect to the API documentation.
    """
    return RedirectResponse(url="/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY)
