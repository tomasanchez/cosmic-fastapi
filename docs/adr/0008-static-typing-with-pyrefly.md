# ADR 0008: Static Typing With Pyrefly

- Status: Accepted
- Date: 2026-05-31

## Context

Coding agents benefit from explicit contracts. Type annotations make repository
ports, handler dependencies, domain messages, and boundary translations easier
to discover and safer to modify.

Python type checking has evolved substantially. Pyrefly reached stable 1.0 in
May 2026. It is distributed as a Python package, has first-party CI and
pre-commit guidance, and supports configuration in `pyproject.toml`. Pydantic
also documents its Pyrefly integration.

## Decision

Use Pyrefly as the default static type checker.

- Add type annotations to production code.
- Type-check new and changed code in CI with `pyrefly check`.
- Keep configuration in `pyproject.toml`.
- Use `typing.Protocol` for repository and adapter ports where structural
  typing expresses the contract clearly.
- Avoid `Any`, casts, and ignore comments unless the boundary genuinely cannot
  be typed more precisely.
- Keep suppressions narrow and explain non-obvious ones.

The checker is a tool choice, not part of the architecture. Replace it through
an ADR if another checker becomes a better fit.

## Consequences

Agents and maintainers receive faster feedback about broken contracts before
running tests. Adding and maintaining annotations costs time, especially around
dynamic third-party APIs, but improves navigation and refactoring confidence.

## Agent Guidance

- Run `uv run pyrefly check` after changing production code.
- Preserve useful types across boundaries instead of widening to `Any`.
- Prefer typed protocols and small adapters over mock-heavy dynamic code.
- Do not suppress a diagnostic until the underlying contract is understood.

## References

- [Pyrefly 1.0 announcement](https://pyrefly.org/blog/v1.0/)
- [Pyrefly installation and CI](https://pyrefly.org/en/docs/installation/)
- [Pyrefly configuration](https://pyrefly.org/en/docs/configuration/)
- [Pydantic Pyrefly integration](https://pydantic.dev/docs/validation/latest/integrations/dev-tools/pyrefly/)
