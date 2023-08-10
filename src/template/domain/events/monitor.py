"""
Events related to the monitoring of the application.
"""
from typing import Literal

from pydantic import Field

from template.domain.schemas import CamelCaseModel


class LivenessProbed(CamelCaseModel):
    """
    Event that is sent when the application is probed for liveness.
    """

    status: Literal["Ok", "Error"] = Field(
        description="The status of the application.",
        default="Ok",
    )


class ReadinessProbed(CamelCaseModel):
    """
    Event that is sent when the application is probed for readiness.
    """

    status: Literal["Ready", "Error"] = Field(
        description="The readiness probe of the application.",
        default="Ready",
    )
