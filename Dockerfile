FROM python:3.13-slim AS builder

ARG APP_DIR=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    UV_PYTHON=python3.13 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR ${APP_DIR}

# Copy dependency definition files.
COPY pyproject.toml uv.lock .python-version README.md ${APP_DIR}/

# Build the virtual environment from the lock file, excluding dev dependencies.
# This creates a self-contained .venv directory.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the project into the image and sync it.
COPY src ${APP_DIR}/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.13-slim AS runtime

ARG APP_DIR=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PATH="${APP_DIR}/.venv/bin:$PATH" \
    UVICORN_PORT=8000 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_RELOAD=0

# Create an unprivileged application user.
RUN groupadd --system app && useradd --system --gid app --home-dir ${APP_DIR} app

WORKDIR ${APP_DIR}

# Copy the prebuilt virtual environment and the application source.
COPY --from=builder --chown=app:app ${APP_DIR}/.venv ${APP_DIR}/.venv
COPY --from=builder --chown=app:app ${APP_DIR}/src ${APP_DIR}/src

USER app

EXPOSE 8000

# Run the application using the Python from the prebuilt venv.
CMD ["python", "-m", "template.main"]
