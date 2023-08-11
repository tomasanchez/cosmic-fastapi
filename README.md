# Cosmic FastAPI

**Cosmic FastAPI** is a template for creating a [FastAPI](https://fastapi.tiangolo.com/) project following
the [Cosmic Python](https://www.cosmicpython.com/) guidelines.

## Content

<!-- TOC -->

* [Cosmic FastAPI](#cosmic-fastapi)
    * [Content](#content)
    * [Features](#features)
    * [Continuous Integration](#continuous-integration)
    * [Development Environment](#development-environment)
        * [Installing Poetry](#installing-poetry)
        * [Building the Development Environment](#building-the-development-environment)
    * [Running Local](#running-local)
    * [Running Tests](#running-tests)
    * [Updating Dependencies](#updating-dependencies)
    * [Recommended Readings](#recommended-readings)
    * [License](#license)
    * [Acknowledgements](#acknowledgements)

<!-- TOC -->

## About

### Features

This template includes `FastAPI` using the fastest `Pydantic V2` model validation. Designed for Event-Driven
Architecture (EDA) and Domain-Driven Design (DDD). Providing a clean and simple structure to start a new project. With
the addition of `pre-commit` hooks to ensure code quality. And ready to be used in a `CI/CD` GitHub Workflows pipeline.

### Project Structure

#### Environment Variables

Variables prefixed with `FASTAPI_` are used to configure the API UI.

| Name                        | Description         | Default Value    |
|-----------------------------|---------------------|------------------|
| FASTAPI_DEBUG               | Debug Mode          | False            |
| FASTAPI_PROJECT_NAME        | Swagger Title       | API GATEWAY      |
| FASTAPI_PROJECT_DESCRIPTION | Swagger Description | ...              |
| FASTAPI_PROJECT_LICENSE     | License info        | ...              |
| FASTAPI_PROJECT_CONTACT     | Contact details     | ...              |
| FASTAPI_VERSION             | Application Version | template.version |
| FASTAPI_DOCS_URL            | Swagger Endpoint    | /docs            |

Variables prefixed with `UVICORN_` are used to configure the server.

| Name              | Description           | Default Value |
|-------------------|-----------------------|---------------|
| UVICORN_HOST      | Server Host           | '127.0.0.1'   |
| UVICORN_PORT      | Server Port           | 8000          |
| UVICORN_LOG_LEVEL | Log Level             | 'info'        |
| UVICORN_RELOAD    | Enable/Disable Reload | False         |

### Recommended Directory Structure

As our application gets bigger, we’ll need to keep tidying our directory structure. The layout of our project gives us
useful hints about what kinds of object we’ll find in each file. We can use this to navigate our codebase more easily.

```text
.
├── settings.py
├── domain  #(1)
│   ├── commands.py
│   ├── events.py
│   ├── schemas.py
│   └── models.py
├── service_layer #(2)
│   └── services.py
├── adapters  #(3)
│   ├── orm.py
│   └── repository.py
├── entrypoints  #(4)
│   ├── __init__.py
│   └── monitor.py
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── unit
    ├── integration
    └── e2e
        └── test_monitor.py
```

- **(1)**. Domain, from Domain Driven Architecture.
    - **Commands**, from Command Query Responsibility Segregation (CQRS). Commands are the messages that change
      the state of the system.
    - **Events**, from Event Sourcing. Events are the messages that describe a change in the system.
    - **Schemas**, from FastAPI, data models or data structures that are used to define the shape or structure
      of data that your API receives or returns.
    - **Models**, represent the domain entities, business objects of interest.
- **(2)**. The service layer will be distinguished. What is the difference between a domain service and a service layer?
    - Application service (our service layer) ts job is to handle requests from the outside world and to orchestrate an
      operation.
    - Domain Service. This is the name for a piece of logic that belongs in the domain model but doesn't sit naturally
      inside a stateful
      entity or value object. For example, if you were building a shopping cart application, you might choose to build
      taxation rules as a domain service.
- **(3)**. Adapters, it comes from ports and adapters terminology. This will fill up with any other abstractions around
  external I/O. Strictly speaking, you would call these secondary adapters or driven adapters, or sometimes
  inward-facing adapters.
- **(4)**. Entrypoints are the places we drive our application from. In the official ports and adapters terminology,
  these are adapters too, and are referred to as primary, driving, or outward-facing adapters.

We may even consider splitting our models, schemas, events and commands into separate packages and files if they get too
big.

## Continuous Integration

This project uses `make` as an adaptation layer.

Run `make help` to see all available commands.

## Development Environment

### Installing Poetry

This package uses poetry for dependency management.

Install poetry in the system `site_packages`. DO NOT INSTALL IT in a virtual environment itself.

To install poetry, run:

```bash
pip install poetry
```

### Building the Development Environment

1. Clone the repository

    ```bash
    git clone "git@github.com/tomasanchez/cosmic-fastapi.git"
    ```
2. Install dependencies

    ```bash
    cd cosmic-fastapi && poetry install
    ```

   Note that poetry doesn't activate the virtual environment for you. You have to do it manually.
   Or prefix subsequent the commands with

    ```bash
    poetry run
    ```

   You can view the environment that poetry uses with

    ```bash
    poetry env info
    ```

   To activate run:

    ```bash
    poetry shell
    ```
3. Activate pre-commit hooks (Optional)

   Using [pre-commit](https://pre-commit.com/) to run some checks before committing is highly recommended.

   To activate the pre-commit hooks run:

    ```bash
    pre-commit install
    ```

   To run the checks manually run:

    ```bash
    poetry run pre-commit run --all-files
    ```

   The following checks are run: `black`, `flake8`, `isort`, `mypy`, `pylint`.

## Running Local

1. Run:

    ```bash
    poetry run python -m template.main
    ```
2. Go to http://localhost:8000/docs to see the API documentation.

## Running Tests

You can run the tests with:

```bash
poetry run pytest
```

or with the `make` command:

```bash
make test
```

To generate a coverage report add `--cov src`.

```bash
poetry run pytest --cov src
```

Or with the `make` command:

```bash
make cover
```

## Updating Dependencies

To update the dependencies run:

```bash
poetry update
```

## Recommended Readings

- [FastAPI official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic official Documentation](https://pydantic-docs.helpmanual.io/)
- [Cosmic Python](https://cosmicpython.com/)

## License

This project is licensed under the terms of the MIT license unless otherwise specified. See [`LICENSE`](LICENSE) for
more details or visit https://mit-license.org/.

## Acknowledgements

This project was designed and developed
by [Tomás Sánchez](https://tomsanchez.com.ar/about/) <[info@tomsanchez.com.ar](mailto:info@tomsanchez.com.ar)>.

Deeply inspired by [FastAPI-MVC](https://fastapi-mvc.netlify.app/)
following  [Cosmic Python](https://www.cosmicpython.com/) guidelines for project structure.

If you find this project useful, please consider supporting its development by sponsoring it.