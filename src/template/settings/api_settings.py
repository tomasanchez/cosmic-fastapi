"""
API Settings
"""
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from template.version import __version__


class LicenseInfo(BaseModel):
    """Define license information model.

    Attributes:
        name (str): License name.
        url (str): License URL.
    """

    name: str
    url: str


class ContactInfo(BaseModel):
    """Define contact information model.

    Attributes:
        name (str): Contact name.
        url (str): Contact URL.
        email (str): Contact email.
    """

    name: str
    url: str
    email: str


class ApplicationSettings(BaseSettings):
    """Define application configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        * FASTAPI_DEBUG
        * FASTAPI_PROJECT_NAME
        * FASTAPI_PROJECT_DESCRIPTION
        * FASTAPI_PROJECT_LICENSE
        * FASTAPI_PROJECT_CONTACT
        * FASTAPI_VERSION
        * FASTAPI_DOCS_URL

    Attributes:
        DEBUG (bool): FastAPI logging level. You should disable this for
            production.
        PROJECT_NAME (str): FastAPI project name.
        PROJECT_DESCRIPTION (str): FastAPI project description.
        PROJECT_LICENSE (LicenseInfo): FastAPI project license information.
        PROJECT_CONTACT (ContactInfo): FastAPI project contact details.
        VERSION (str): Application version.
        DOCS_URL (str): Path where swagger ui will be served at.
    """

    DEBUG: bool = True
    PROJECT_NAME: str = "Cosmic FastAPI Template"
    PROJECT_DESCRIPTION: str = "This is a FastAPI template demo."
    PROJECT_LICENSE: LicenseInfo = LicenseInfo(name="MIT", url="https://mit-license.org/")
    PROJECT_CONTACT: ContactInfo = ContactInfo(
        name="Tom Sanchez", url="https://tomsanchez.com.ar", email="info@tomsanchez.com.ar"
    )
    VERSION: str = __version__
    DOCS_URL: str = "/docs"

    # All your additional application configuration should go either here or in
    # separate file in this submodule.

    class Config:
        """Config subclass needed to customize BaseSettings settings.
        Attributes:
            case_sensitive (bool): When case_sensitive is True, the environment
                variable names must match field names (optionally with a prefix)
            env_prefix (str): The prefix for environment variable.
        Resources:
            https://pydantic-docs.helpmanual.io/usage/settings/
        """

        case_sensitive = True
        env_prefix = "FASTAPI_"
