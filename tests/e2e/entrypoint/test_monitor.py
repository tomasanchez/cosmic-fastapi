"""
Test Cases for Monitor Entrypoint.
"""

import pytest
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from starlette.testclient import TestClient

from template.asgi import get_application
from template.bootstrap import bootstrap
from template.entrypoint.schemas import LivenessProbed, ReadinessProbed, ResponseModel
from template.settings.database_settings import DatabaseSettings


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

    def test_readiness_probe_when_database_is_reachable(self, test_client):
        """
        GIVEN a FastAPI application whose database is reachable
        WHEN the readiness probe is requested "GET /readiness"
        THEN it should return 200, and a ReadinessProbed JSON with status "Ready"
        """

        # when
        response = test_client.get("/readiness")

        # then
        assert response.status_code == status.HTTP_200_OK
        try:
            probe = ResponseModel[ReadinessProbed].model_validate_json(response.content)
        except ValueError:
            pytest.fail("Response body is not a valid ReadinessProbed JSON")
        assert isinstance(probe.data, ReadinessProbed)
        assert probe.data.status == "Ready"

    def test_readiness_probe_when_database_is_unreachable(self):
        """
        GIVEN a FastAPI application whose database engine has been disposed
        WHEN the readiness probe is requested "GET /readiness"
        THEN it should return 503, and a ReadinessProbed JSON with status "Error"
        """

        # given
        container = bootstrap(DatabaseSettings(URL="sqlite+pysqlite://", AUTO_CREATE_SCHEMA=True))
        app = get_application(container)
        with TestClient(app) as client:
            # Force every subsequent connection attempt to fail so the probe
            # exercises its error branch even with an in-memory StaticPool.
            def _raise_on_connect() -> None:
                raise SQLAlchemyError

            container.engine.connect = _raise_on_connect  # type: ignore[method-assign]

            # when
            response = client.get("/readiness")

        # then
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        try:
            probe = ResponseModel[ReadinessProbed].model_validate_json(response.content)
        except ValueError:
            pytest.fail("Response body is not a valid ReadinessProbed JSON")
        assert isinstance(probe.data, ReadinessProbed)
        assert probe.data.status == "Error"
