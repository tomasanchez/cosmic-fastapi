"""
Uvicorn settings
"""

from pydantic import IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class UvicornSettings(BaseSettings):
    """Define UVICORN configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        * UVICORN_HOST
        * UVICORN_PORT
        * UVICORN_LOG_LEVEL
        * UVICORN_RELOAD

    Attributes:
        HOST (IPvAnyAddress): Host to run application on.
        PORT (int): Port to run application on.
        LOG_LEVEL (str): Logging level.
        RELOAD (bool): Enable/disable auto-reload.

    Resources:
        1. https://docs.pydantic.dev/latest/usage/pydantic_settings/
    """

    HOST: IPvAnyAddress = IPvAnyAddress("127.0.0.1")
    PORT: int = 8000
    LOG_LEVEL: str = "info"
    RELOAD: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_prefix="UVICORN_",
    )
