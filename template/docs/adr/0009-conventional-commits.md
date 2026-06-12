# ADR 0009: Conventional Commits

- Status: Accepted
- Date: 2026-05-31

## Context

Projects created from this template should support automated changelogs,
semantic versioning, and release pipelines. Coding agents also need an explicit
rule for producing a useful Git history.

## Decision

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
for every commit.

Format commit subjects as:

```text
<type>[optional scope]: <description>
```

Use:

- `feat` for new behavior.
- `fix` for bug fixes.
- `docs` for documentation-only changes.
- `test` for test-only changes.
- `refactor` for behavior-preserving code changes.
- `perf` for performance improvements.
- `build` for build system or dependency changes.
- `ci` for continuous integration changes.
- `chore` for maintenance that does not fit another type.
- `style` for formatting-only changes.

Use a `!` before the colon or a `BREAKING CHANGE:` footer when a commit changes
a public contract incompatibly.

Scopes are encouraged when they make the affected area clearer, for example
`feat(api):`, `fix(repository):`, or `docs(adr):`.

## Consequences

Commit history remains readable by people and machines. Changelog generation,
release notes, and semantic version calculation can be automated reliably when
commits are focused and correctly classified.

## Agent Guidance

- Create focused commits with one clear intent.
- Choose the type based on the user-visible meaning of the change.
- Do not hide a breaking change inside a normal commit.
- Do not include unrelated working-tree changes in a commit.
- Use a body or footer when the subject alone cannot explain important context.

## References

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning 2.0.0](https://semver.org/)
