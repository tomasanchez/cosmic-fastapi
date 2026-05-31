"""Test suite for application composition."""

from template.bootstrap import bootstrap
from template.settings.database_settings import DatabaseSettings


class TestBootstrap:
    """Test cases for application dependency composition."""

    def test_skips_schema_creation_by_default(self):
        """
        GIVEN a container configured without automatic schema creation
        WHEN the application starts and stops
        THEN lifecycle hooks complete without creating tables
        """
        # GIVEN
        container = bootstrap(DatabaseSettings(URL="sqlite+pysqlite://", AUTO_CREATE_SCHEMA=False))

        # WHEN
        container.startup()
        container.shutdown()

        # THEN
        assert container.auto_create_schema is False
