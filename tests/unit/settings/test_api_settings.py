"""
Test suite for API Settings
"""
import pytest

from template.settings.api_settings import ApplicationSettings, ContactInfo, LicenseInfo
from template.version import __version__


class TestAPISettings:
    """
    Test suite for API Settings
    """

    def test_license_info_needs_valid_url(self):
        """
        GIVEN a LicenseInfo model
        WHEN the url is invalid
        THEN a ValueError is raised
        """
        with pytest.raises(ValueError):
            LicenseInfo(name="MIT", url="invalidURL")

    def test_contact_info_needs_valid_url_and_email(self):
        """
        GIVEN a ContactInfo model
        WHEN the url or email is invalid
        THEN a ValueError is raised
        """

        with pytest.raises(ValueError):
            ContactInfo(name="John Doe", url="https://example.com", email="invalidEmail")

        with pytest.raises(ValueError):
            ContactInfo(name="John Doe", url="invalidURL", email="john@doe.mail")

    def test_api_default_values(self):
        """
        Test API default values
        """
        settings = ApplicationSettings()

        assert settings.DEBUG is True
        assert settings.PROJECT_NAME
        assert settings.PROJECT_DESCRIPTION
        assert isinstance(settings.PROJECT_LICENSE, LicenseInfo)
        assert isinstance(settings.PROJECT_CONTACT, ContactInfo)
        assert settings.VERSION == __version__
