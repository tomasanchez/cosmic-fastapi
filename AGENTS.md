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
- Keep FastAPI, Pydantic, SQLAlchemy, and external clients at system boundaries.
- Prefer explicit dependencies, small adapters, repositories, and units of work.
- Add patterns when the use case needs them. Do not add ceremony merely to fill
  a directory.
- Keep changes focused. Do not refactor unrelated code while completing a task.
- Record a new ADR when changing a project-wide architectural default.

## Python Style

- Write modern typed Python supported by the project version.
- Add type annotations to production code and preserve useful types across
  boundaries. Avoid widening values to `Any`.
- Use Google-style docstrings for public modules, classes, methods, and
  functions where documentation adds meaning.
- Use `Args:`, `Returns:`, `Raises:`, and `Resources:` sections when relevant.
- Prefer clear names from the business domain over technical or generic names.
- Keep comments brief and explain why a non-obvious choice exists.
- Use Pydantic models for boundary validation and settings, not as a substitute
  for domain modeling.
- Keep SQLAlchemy models and session usage inside persistence adapters.

## Architecture Workflow

When implementing a feature:

1. Identify the business behavior and invariant.
2. Model the domain with plain Python objects.
3. Define boundary schemas for external input and output.
4. Translate requests into commands or query arguments.
5. Orchestrate the use case in an application handler.
6. Access persistence through repositories and a unit of work.
7. Wire dependencies in the composition root.
8. Add the smallest useful tests at each affected boundary.

Use domain events for facts that already happened. Use commands for requests to
perform work. Do not treat API response models as domain events.

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
