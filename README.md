# Cosmic FastAPI

**Cosmic FastAPI** is a template for creating a [FastAPI](https://fastapi.tiangolo.com/) project following
the [Cosmic Python](https://www.cosmicpython.com/) guidelines.

## Content

<!-- TOC -->

* [Cosmic FastAPI](#cosmic-fastapi)
    * [Content](#content)
    * [About](#about)
        * [Features](#features)
        * [Project Structure](#project-structure)
            * [Environment Variables](#environment-variables)
        * [Recommended Directory Structure](#recommended-directory-structure)
        * [Domain Driven Design](#domain-driven-design)
            * [Models](#models)
                * [Entities](#entities)
                * [Value Objects](#value-objects)
                * [Aggregates:](#aggregates)
            * [Schemas](#schemas)
            * [Event Driven Architecture](#event-driven-architecture)
                * [Commands](#commands)
                * [Events](#events)
            * [Clean Architecture](#clean-architecture)
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

### Domain Driven Design

`Commands`, `Events`, `Schemas` and `Models` are the building blocks of our **Domain**.

#### Models

First, we define our domain models. These are the objects that represent the business concepts we’re working with.
They should be as simple as possible, and contain only the attributes that are essential to the business, utilizing the
business jargon. The idea is that, if you were to show these models to a non-technical person, but someone who
understand the business process, they would be able to understand what the application does. Models encapsulate the
behavior, state, and business rules that govern the application. Models can encompass entities, aggregates, and
sometimes even Value Objects.

##### Entities

Entities are objects that have distinct identities that run throughout their lifecycle. In other words, an entity is
defined not just by its attributes, but also by a unique identifier that differentiates it from other entities of the
same type. Entities are mutable and can have their attributes modified while maintaining the same identity. They are
often used to represent real-world objects or concepts that have an ongoing existence.

For example, in an e-commerce system, a "Product" can be an entity. Each product has a unique identifier, and its
attributes (such as name, description, price) can change without changing its identity.

##### Value Objects

A Value Object is a concept from Domain-Driven Design (DDD). It's an object that represents a descriptive aspect of the
domain with no conceptual identity. In other words, a `Value Object` is defined solely by its attributes, and two Value
Objects with the same attributes are considered equal. They are immutable and can be thought of as "flyweight" objects
that are shared whenever their values are the same.

Value Objects can be part of a `Model`. In fact, they often enhance the expressiveness and maintainability of Models.
Value Objects help to define attributes with semantic meaning and encapsulate their validation and behavior. In some
cases, a Model might consist of one or more entities and Value Objects that work together to represent and manage the
business logic and data.

##### Aggregates:

Aggregates are clusters of related `entities` and `value objects` that are treated as a single unit. The aggregate is
the boundary within which changes are managed and consistency is maintained. One entity within the aggregate is
designated as the "aggregate root."
All interactions with the aggregate are done through this root entity. This helps ensure that the integrity and
consistency of the data is maintained within the aggregate.

For example, in the case of an e-commerce system, a "Shopping Cart" could be an aggregate. The shopping cart would be
composed of multiple line items (entities representing products in the cart) and possibly other related information. All
changes to the items in the cart would be managed through the shopping cart aggregate root.

Entities can be part of an aggregate, and an aggregate often includes one or more entities and possibly value objects.
Aggregates define the transactional boundaries and consistency rules within the domain. They encapsulate business rules
and enforce invariants to ensure that the data remains in a valid and consistent state.

#### Schemas

Schemas are used to define the structure and validation rules for the input and output data of your API. Schemas help
ensure that data is correctly formatted and adheres to specific criteria before being processed. They are often used to
validate request payloads and to define the shape of the data returned from API endpoints.

In this project we use `Pydantic` to define our schemas. [Pydantic](https://pydantic-docs.helpmanual.io/) is a library
that provides runtime checking and validation.

#### Event Driven Architecture

`Commands` and `Events` are the building blocks of our **Event Driven Architecture**. You can consider both as simple
dataclasses, as they have no behaviour.

Both commands and events are often used in software architectures to promote separation of concerns, modularity, and
extensibility. By encapsulating actions or occurrences into discrete objects, it becomes easier to reason about the
system and make changes without impacting other parts of the codebase.

In an API, we can use `commands` to represent requests from clients to perform certain actions. These commands may need
to be validated before they can be processed. Once validated, they can be executed by an appropriate handler or service.
Following this idea, we can use `events` to represent our API responses. For this, we can associate both as kind
of `schemas`.

##### Commands

Commands represent actions or requests to be performed by a system. They typically encapsulate a specific intent or
operation that needs to be executed. In software development, commands are often used in conjunction with a command
pattern or a similar architectural pattern to decouple the sender of the command from its execution.

For example, in a web application, a command might be used to represent a user's request to update their profile
information. The command object would contain the necessary data to carry out the update operation, and it would be
executed by an appropriate handler or service.

##### Events

Events represent notifications or signals that something has happened within a system. They convey information about a
specific occurrence and are often used for communication between different components or modules of an application.
Events are typically used in event-driven architectures or publish-subscribe patterns.

When an event occurs, it can be published to an event bus or a similar mechanism. Other components that have subscribed
to that event can receive and react to it accordingly. This allows for loose coupling and enables different parts of the
system to respond to events without direct dependencies on each other.

For example, in an e-commerce application, an event might be triggered when a new order is placed. Subscribed
components, such as inventory management or shipping modules, can then react to this event by updating their respective
states or initiating further actions.

### Clean Architecture

The main idea behind Clean Architecture is to create a separation of concerns in software systems, allowing for easier
maintenance, testing, and scalability. The core principle of Clean Architecture is the dependency rule, which states
that dependencies should always point inward towards the core of the application and not outward towards external
frameworks or tools. This helps keep the core of the application independent and flexible.

Clean Architecture typically consists of several layers, each with a specific responsibility:

* Entities: These are the core business objects and rules.
* Use Cases (Interacts): These encapsulate the business logic and orchestrate interactions between entities.
* Interfaces (Gateways): These define the interfaces that allow the use cases to interact with external data sources or
  systems.
* Frameworks and Drivers: These are the outermost layers that deal with the infrastructure, such as databases, web
  frameworks, UI, etc.

In our project, we can easily observe the different layers according to our directory structure. It's an architecture
that "screams": by its naming conventions, we can easily understand what is the responsibility of each module.

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