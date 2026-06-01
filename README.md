<p align="center">
<img width="320" height="320" src="docs/cosmic_fastapi.png" alt='cosmic fast api'>
</p>

<p align="center">
<em>Kickoff your app like a kangaroo through the stars: clean, fast, and unapologetically structured.</em>
</p>

---

# Cosmic FastAPI

**Cosmic FastAPI** is a template for creating a [FastAPI](https://fastapi.tiangolo.com/) project following
the [Cosmic Python](https://www.cosmicpython.com/) guidelines.

## Content

<!-- TOC -->

* [Cosmic FastAPI](#cosmic-fastapi)
    * [Content](#content)
    * [About](#about)
        * [Features](#features)
        * [Architecture Decision Records](#architecture-decision-records)
        * [Optional MCP Addon](#optional-mcp-addon)
        * [Optional Kafka Addon](#optional-kafka-addon)
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
        * [Installing UV](#installing-uv)
        * [Building the Development Environment](#building-the-development-environment)
    * [Running Local](#running-local)
    * [Running Tests](#running-tests)
    * [Recommended Readings](#recommended-readings)
    * [Licence](#licence)
    * [Acknowledgements](#acknowledgements)

<!-- TOC -->

## About

### Features

This template includes `FastAPI` using the fastest `Pydantic V2` model validation. Designed for Event-Driven
Architecture (EDA) and Domain-Driven Design (DDD). Providing a clean and simple structure to start a new project. With
the addition of `pre-commit` hooks to ensure code quality. And ready to be used in a `CI/CD` GitHub Workflows pipeline.

### Architecture Decision Records

The [Architecture Decision Records](docs/adr/README.md) define the modern Cosmic Python standard used by this template.
They are the first reference for people and coding agents extending the project. The records preserve the book's
domain-first philosophy while adopting FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, uv, Ruff, Pyrefly, and pytest.
Repository-level [agent instructions](AGENTS.md) turn those decisions into an implementation workflow.
The [Cosmic Python coverage matrix](docs/cosmic-python-coverage.md) distinguishes included patterns from conditional
extensions such as optimistic locking, broker adapters, and the transactional outbox.

### Optional MCP Addon

Projects with agent clients can install an opt-in [Model Context Protocol](https://modelcontextprotocol.io/) adapter:

```bash
uv sync --extra mcp
make mcp
```

The standalone Streamable HTTP server is available at `http://127.0.0.1:8000/mcp`.
It demonstrates an intentional primary adapter rather than automatic route exposure:

- `onboard_user` is an MCP tool that dispatches the existing registration command.
- `users://{user_id}` is an MCP resource backed by the existing CQRS reader.
- The tool returns the resource URI so an agent can read persisted preferences before later user-specific actions.

The addon is local-only scaffolding until a project defines authentication, authorization, audit logging, and a threat
review. See [ADR 0015](docs/adr/0015-mcp-is-an-opt-in-primary-adapter.md).

### Optional Kafka Addon

Projects that publish public integration events can install the Kafka addon:

```bash
uv sync --extra kafka
make migrate
make kafka-up
make kafka-relay
```

In another terminal, inspect the published events:

```bash
make kafka-consume
```

For a local browser-based view of topics, messages, partitions, keys, and
consumer groups, start the optional [Kafbat UI](https://github.com/kafbat/kafka-ui):

```bash
make kafka-ui-up
```

Open `http://localhost:8080` and select the `local` cluster. Stop the UI with:

```bash
make kafka-ui-down
```

User registration demonstrates the transactional outbox pattern:

1. The aggregate raises the internal `UserRegistered` domain event.
2. The SQLAlchemy unit of work stores the user and a versioned `UserRegisteredV1` outbox row in one transaction.
3. The broker-neutral relay publishes pending rows through the service-layer `IntegrationMessageBus` port.
4. The opt-in Kafka adapter sends them to the local `users.events` topic.
5. Kafka messages use `userId` as the key and a camel-case JSON envelope containing `eventId`, `occurredAt`,
   `eventType`, `schemaVersion`, and `payload`.

Delivery is at least once. Consumers must deduplicate with `eventId`. Docker Compose runs a single-node KRaft broker for
local development only. Production projects must define security, retention, observability, retry, and dead-letter
policies. See [ADR 0016](docs/adr/0016-external-message-buses-use-a-transactional-outbox.md).

Kafbat UI is also a local-development convenience. It is pinned to a release
image, kept outside the Python application, and excluded from the default
Compose profile.

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

Variables prefixed with `DATABASE_` configure relational persistence.

| Name                        | Description                              | Default Value                          |
|-----------------------------|------------------------------------------|----------------------------------------|
| DATABASE_URL                | SQLAlchemy database URL                  | sqlite+pysqlite:///./cosmic-fastapi.db |
| DATABASE_AUTO_CREATE_SCHEMA | Create tables at startup for local demos | False                                  |

Use Alembic migrations for normal schema management. `DATABASE_AUTO_CREATE_SCHEMA`
exists for isolated tests and local demonstrations only.

Variables prefixed with `KAFKA_` configure the optional outbox relay.

| Name                    | Description                         | Default Value   |
|-------------------------|-------------------------------------|-----------------|
| KAFKA_BOOTSTRAP_SERVERS | Comma-separated Kafka broker list   | localhost:9092  |
| KAFKA_USER_EVENTS_TOPIC | Topic for public user events        | users.events    |
| KAFKA_PUBLISH_TIMEOUT   | Publisher acknowledgement timeout   | 10.0            |
| KAFKA_RELAY_INTERVAL    | Delay between relay polling passes  | 1.0             |
| KAFKA_BATCH_SIZE        | Maximum events per relay pass       | 100             |

### Recommended Directory Structure

As the application grows, keep the dependency direction visible in the directory structure. The domain remains plain
Python. Framework validation belongs at the entrypoint boundary, and persistence belongs in adapters.

```text
.
|-- migrations
|-- src/template
|   |-- adapters                 # (3)
|   |   |-- models
|   |   |   `-- outbox.py
|   |   |-- outbox.py
|   |   |-- queries.py
|   |   |-- repository.py
|   |   `-- unit_of_work.py
|   |-- domain                   # (1)
|   |   |-- commands
|   |   |-- events
|   |   `-- models
|   |-- entrypoint               # (4)
|   |   |-- monitor.py
|   |   |-- schemas.py
|   |   `-- users.py
|   |-- integration_events
|   |   `-- user.py
|   |-- addons                    # (5)
|   |   |-- kafka
|   |   `-- mcp
|   |-- service_layer            # (2)
|   |   |-- handlers.py
|   |   |-- messagebus.py
|   |   |-- queries.py
|   |   |-- read_models.py
|   |   |-- repository.py
|   |   `-- unit_of_work.py
|   |-- settings
|   `-- bootstrap.py
`-- tests
    |-- unit
    |-- integration
    `-- e2e
```

- **(1)**. Domain, from Domain Driven Architecture.
    - **Commands**, from Command Query Responsibility Segregation (CQRS). Commands are the messages that change
      the state of the system.
    - **Events** describe facts that happened in the domain. Domain events do not imply Event Sourcing.
    - **Models**, represent the domain entities, business objects of interest.
- **(2)**. The service layer coordinates use cases with handlers, a message bus, repository ports, and a unit of work.
  What is the difference between a domain service and a service layer?
    - Application service (our service layer) its job is to handle requests from the outside world and to orchestrate an
      operation.
    - Domain Service. This is the name for a piece of logic that belongs in the domain model but doesn't sit naturally
      inside a stateful
      entity or value object. For example, if you were building a shopping cart application, you might choose to build
      taxation rules as a domain service.
- **(3)**. Adapters, it comes from "ports and adapters" terminology. This will fill up with any other abstractions
  around
  external I/O. Strictly speaking, you would call these secondary adapters or driven adapters, or sometimes
  inward-facing adapters.
- **(4)**. Entrypoints are the places we drive our application from. FastAPI routes and Pydantic request or response
  schemas live here. In ports and adapters terminology, these are primary or driving adapters.
- **(5)**. Addons are optional primary adapters for selected projects. The MCP addon exposes agent-oriented tools and
  resources through the same application ports without becoming a default runtime dependency. The Kafka addon is an
  optional secondary adapter implementing the broker-neutral `IntegrationMessageBus` port. The service layer relays
  public events from the transactional outbox without depending on Kafka.

The root `bootstrap.py` module is the composition root. It wires concrete adapters to application ports without leaking
framework concerns into the domain.

### Domain Driven Design

`Commands`, `Events`, and `Models` are the building blocks of our **Domain**. Aggregates and behavior-rich domain objects
remain plain Python. Commands and events may use frozen Pydantic models as immutable schema contracts. See
[ADR 0011](docs/adr/0011-pydantic-message-schemas-with-plain-domain-aggregates.md). Python fields use `snake_case`;
JSON message payloads use `camelCase` as documented in
[ADR 0012](docs/adr/0012-camel-case-json-message-contracts.md).

#### Models

First, we define our domain models. These are the objects that represent the business concepts we’re working with.
They should be as simple as possible and contain only the attributes that are essential to the business, using the
business jargon. The idea is that, if you were to show these models to a non-technical person, but someone who
understands the business process, they would be able to understand what the application does. Models encapsulate the
behaviour, state, and business rules that govern the application. Models can encompass entities, aggregates, and
sometimes even Value Objects.

##### Entities

Entities are objects that have distinct identities that run throughout their lifecycle. In other words, an entity is
defined not just by its attributes but also by a unique identifier that differentiates it from other entities of the
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
Value Objects help to define attributes with semantic meaning and encapsulate their validation and behaviour. In some
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

Schemas define validated data contracts. Boundary schemas describe the input and output data of an API or external
adapter. Immutable command and event schemas describe application messages.

In this project we use `Pydantic` for entrypoint schemas and immutable message schemas. Boundary objects are translated
when their external contract differs from the application message. See the
[Pydantic documentation](https://docs.pydantic.dev/) for runtime validation.

#### Event Driven Architecture

`Commands` and `Events` are the building blocks of our **Event Driven Architecture**. They are immutable Pydantic
models because they carry data contracts and have no behaviour.

Both commands and events are often used in software architectures to promote separation of concerns, modularity, and
extensibility. By encapsulating actions or occurrences into discrete objects, it becomes easier to reason about the
system and make changes without impacting other parts of the codebase.

In an API, boundary schemas validate client requests and are translated into commands. A handler executes the command
inside a unit of work. Events raised by aggregates are dispatched to interested handlers after the command completes.
HTTP responses remain boundary schemas rather than domain events.

Commands may enter through HTTP or message-queue adapters. Domain events may remain in-process or be translated into
versioned integration events for Kafka, RabbitMQ, SQS, or another broker. Integration events and HTTP responses can
describe the same business fact without sharing one lifecycle or envelope.

Write-side commands load aggregate roots through repositories and a unit of work. Read-only queries use purpose-built
read models and reader adapters, as described in [ADR 0014](docs/adr/0014-cqrs-read-models-are-purpose-built.md).

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

### Installing UV

This package uses `uv` for dependency management.

Install `uv` in the system `site_packages`. DO NOT INSTALL IT in a virtual environment itself.

To install `uv`, run:

```bash
pip install uv
```

### Building the Development Environment

1. Clone the repository

    ```bash
    git clone "git@github.com/tomasanchez/cosmic-fastapi.git"
    ```
2. Install dependencies

    ```bash
    cd cosmic-fastapi && uv sync --dev
    ```

3. Activate pre-commit hooks (Optional)

   Using [pre-commit](https://pre-commit.com/) to run some checks before committing is highly recommended.

   To activate the pre-commit hooks, run:

    ```bash
    pre-commit install
    ```

   To run the checks manually, run:

    ```bash
    uv run pre-commit run --all-files
    ```

## Running Local

1. Apply database migrations:

    ```bash
    make migrate
    ```

2. Run:

    ```bash
    uv run python -m template.main
    ```
3. Go to http://localhost:8000/docs to see the API documentation.

## Running Tests

You can run the tests with:

```bash
uv run pytest
```

or with the `make` command:

```bash
make test
```

To generate a coverage report add `--cov src`.

```bash
uv run pytest --cov src
```

Or with the `make` command:

```bash
make cover
```

## Recommended Readings

- [FastAPI official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic official Documentation](https://pydantic-docs.helpmanual.io/)
- [UV official Documentation](https://docs.astral.sh/uv/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Cosmic Python](https://cosmicpython.com/)

## Licence

This project is licensed under the terms of the MIT licence unless otherwise specified. See [`LICENSE`](LICENSE) for
more details or visit https://mit-license.org/.

## Acknowledgements

This project was designed and developed
by [Tomás Sánchez](https://tomsanchez.com.ar/about/) <[info@tomsanchez.com.ar](mailto:info@tomsanchez.com.ar)>.

Deeply inspired by [FastAPI-MVC](https://github.com/fastapi-mvc/fastapi-mvc)
following  [Cosmic Python](https://www.cosmicpython.com/) guidelines for project structure.

If you find this project useful, please consider supporting its development by sponsoring it.
