# Cosmic Python Engineer Instructions

This repository is a reusable Python standard for people and coding agents.
Work as a Cosmic Python engineer: preserve the domain-first philosophy from
*Architecture Patterns with Python* while using the modern decisions recorded
in [docs/adr/README.md](docs/adr/README.md).

Read the ADR index before making architectural changes. Accepted ADRs describe
the target standard. Existing scaffold code that conflicts with an ADR is
migration work, not a precedent to repeat.

Before architectural work, run `make adr-context`. It validates the ADR
registry and prints the pruned set of active decisions. After adding or changing
an ADR, run `make adr-check`.

## Engineering Principles

- Put business behavior, language, and invariants at the center of the design.
- Keep dependencies pointing inward toward plain Python domain objects.
- Keep FastAPI, SQLAlchemy, and external clients at system boundaries.
- Use Pydantic deliberately for immutable command and event schemas.
- Use `snake_case` inside Python and `camelCase` when schemas cross JSON
  boundaries.
- Prefer explicit dependencies, small adapters, repositories, and units of work.
- Treat aggregate roots as consistency boundaries and use purpose-built read
  models for query paths.
- Add patterns when the use case needs them. Do not add ceremony merely to fill
  a directory.
- Keep changes focused. Do not refactor unrelated code while completing a task.
- Record a new ADR when changing a project-wide architectural default.
- Treat MCP as an opt-in primary adapter. Expose selected use cases, not every HTTP route.
- Publish external events through a transactional outbox. Assume at-least-once delivery and require idempotent consumers.

## Python Style

- Write modern typed Python supported by the project version.
- Add type annotations to production code and preserve useful types across
  boundaries. Avoid widening values to `Any`.
- Use Google-style docstrings for public modules, classes, methods, and
  functions where documentation adds meaning.
- Use `Args:`, `Returns:`, `Raises:`, and `Resources:` sections when relevant.
- Prefer clear names from the business domain over technical or generic names.
- Keep comments brief and explain why a non-obvious choice exists.
- Use Pydantic models for boundary validation, settings, and immutable command
  or event schemas, not as a substitute for behavior-rich domain modeling.
- Keep SQLAlchemy models and session usage inside persistence adapters.

## Architecture Workflow

When implementing a feature:

1. Identify the business behavior and invariant.
2. Model the domain with plain Python objects.
3. Define frozen Pydantic commands and events when a schema contract helps.
4. Reuse a command as a boundary schema when contracts match; translate when
   they differ.
5. Orchestrate the use case in an application handler.
6. Access persistence through repositories and a unit of work.
7. Keep write commands focused on one aggregate root by default.
8. Use reader ports and read models for query-only paths.
9. Wire dependencies in the composition root.
10. Add the smallest useful tests at each affected boundary.

When adding MCP tools or resources, call application handlers and query
services through the composition root. Do not call HTTP routes or SQLAlchemy
sessions from an MCP adapter. Define authentication, authorization, audit
logging, and a threat review before enabling remote MCP access.

When publishing to Kafka or another broker, depend on the service-layer
`IntegrationMessageBus` port. Translate domain events into
versioned integration events and persist them to the transactional outbox with
the aggregate change. Relay them outside the write transaction. Document
consumer idempotency, retries, dead-letter handling, retention, and
observability before production deployment.

Use domain events for facts that already happened. Use commands for requests to
perform work. Do not treat API response models as domain events. Introduce
versioned integration events before publishing public broker contracts.

## Testing Style

- Use pytest.
- Write test scenarios using GIVEN / WHEN / THEN structure.
- Use uppercase `GIVEN`, `WHEN`, and `THEN` in test docstrings.
- Use `# GIVEN`, `# WHEN`, and `# THEN` comments when they improve the body of a
  non-trivial test.
- Prefer fast unit tests for domain behavior and handlers.
- Use fakes for owned ports such as repositories and units of work.
- Add integration tests for SQLAlchemy mappings, repositories, migrations,
  transaction semantics, and external adapters.
- Keep end-to-end tests focused on critical wiring and user-visible behavior.

## Verification

Use the project commands exposed by the `Makefile` and uv. For a code change,
run the relevant focused tests first, then the available project checks:

```bash
make lint
make test
uv run pyrefly check
```

If a documented check is not yet wired into the evolving scaffold, say so
clearly and add the missing wiring when the task calls for it.

## Git

- Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
- Format commit subjects as `<type>[optional scope]: <description>`.
- Use `feat` for new behavior and `fix` for bug fixes.
- Use `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, and `style`
  when they accurately describe the change.
- Mark breaking changes with `!` or a `BREAKING CHANGE:` footer.
- Keep commits focused so automated changelog and release tooling can infer
  intent reliably.
- Do not include unrelated user changes in a commit.

Examples:

```text
feat(api): add user registration endpoint
fix(repository): rollback failed user creation
docs(adr): define persistence adapter standard
feat(domain)!: replace account identity format
```
