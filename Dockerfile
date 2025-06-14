FROM python:3.11.4-slim AS builder

ARG APP_DIR=/app

ARG ENV

ENV ENV=${ENV} \
    PYTHOPNUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    UV_PYTHON=python3.11 \
    UV_COMPILE_BYTE=1 \
    UV_LINK_MODE=copy \
    UVICORN_PORT=8000 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_RELOAD=0

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR ${APP_DIR}

# Copy dependency definition files
COPY pyproject.toml uv.lock .python-version README.md ${APP_DIR}/

# Build the virtual environment from the lock file, excluding dev dependencies
# This creates a self-contained .venv directory
# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


# Copy the project into the image
COPY src ${APP_DIR}/src

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Set the command to run the application using the Python from the venv
CMD ["uv" , "run", "python", "-m", "template.main"]
