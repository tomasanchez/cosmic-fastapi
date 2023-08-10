"""
Applicant Main File.
"""
from fastapi import FastAPI

from template.asgi import get_application

app: FastAPI = get_application()


if __name__ == "__main__":
    # pylint: disable=wrong-import-position
    import uvicorn

    uvicorn.run("main:app")
