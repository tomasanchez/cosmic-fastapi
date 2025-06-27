"""
Applicant Main File.
"""

from fastapi import FastAPI

from template.asgi import get_application

app: FastAPI = get_application()


if __name__ == "__main__":
    # pylint: disable=wrong-import-position
    import uvicorn

    # pylint: disable=ungrouped-imports
    from template.settings.uvicorn_settings import UvicornSettings

    settings = UvicornSettings()

    uvicorn.run(
        "template.main:app",
        host=str(settings.HOST),
        port=settings.PORT,
        log_level=settings.LOG_LEVEL,
        reload=settings.RELOAD,
    )
