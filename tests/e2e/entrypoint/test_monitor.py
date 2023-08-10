"""
Test Cases for Monitor Entrypoint.
"""
import pytest
from fastapi import status

from template.domain.events.monitor import LivenessProbed, ReadinessProbed
from template.domain.schemas import ResponseModel


class TestMonitorEntryPoint:
    def test_api_root_redirects_to_docs(self, test_client):
        """
        GIVEN a FastAPI application configured with the Monitor Entrypoint
        WHEN the root path is requested "GET /"
        THEN it should redirect to the docs "GET /docs"
        """

        # when
        response = test_client.get("/").history[0]

        # then
        assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY
        assert response.headers["location"] == "/docs"

    def test_liveness_probe(self, test_client):
        """
        GIVEN a FastAPI application configured with the Monitor Entrypoint
        WHEN the liveness probe is requested "GET /liveness"
        THEN it should return 200, and a valid LivenessProbed JSON
        """

        # when
        response = test_client.get("/liveness")

        # then
        assert response.status_code == status.HTTP_200_OK
        try:
            ResponseModel[LivenessProbed].model_validate_json(response.content)
        except ValueError:
            pytest.fail("Response body is not a valid LivenessProbed JSON")

    def test_readiness_probe(self, test_client):
        """
        GIVEN a FastAPI application configured with the Monitor Entrypoint
        WHEN the readiness probe is requested "GET /readiness"
        THEN it should return 200, and a valid ReadinessProbed JSON
        """

        # when
        response = test_client.get("/readiness")

        # then
        assert response.status_code == status.HTTP_200_OK
        try:
            ResponseModel[ReadinessProbed].model_validate_json(response.content)
        except ValueError:
            pytest.fail("Response body is not a valid ReadinessProbed JSON")
