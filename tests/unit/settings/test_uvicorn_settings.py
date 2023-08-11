"""
Uvicorn settings tests.
"""
from template.settings.uvicorn_settings import UvicornSettings


class TestUvicornSettings:
    """
    Test suite for Uvicorn Settings
    """

    def test_uvicorn_default_values(self):
        """
        Test API default values
        """
        settings = UvicornSettings()

        assert not settings.RELOAD
        assert settings.LOG_LEVEL
        assert settings.PORT
        assert settings.HOST
