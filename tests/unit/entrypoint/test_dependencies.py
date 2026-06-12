"""Unit tests for shared entrypoint dependencies."""

from types import SimpleNamespace

from template.entrypoint.dependencies import get_container


class TestGetContainer:
    """Test cases for the container dependency resolver."""

    def test_returns_container_from_request_state(self):
        """
        GIVEN a request whose app holds a container in state
        WHEN get_container is called with that request
        THEN it returns the container stored on the app state
        """

        # GIVEN
        container = object()
        request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(container=container)))

        # WHEN
        resolved = get_container(request)  # type: ignore[arg-type]

        # THEN
        assert resolved is container
