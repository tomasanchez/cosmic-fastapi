# Contributing to the Cosmic FastAPI template

This repository is a [Copier](https://copier.readthedocs.io/) template. Thanks for helping evolve it.

## Author-facing vs generated project

The repository serves two audiences, kept physically separated (see
[ADR 0015](docs/adr/0015-copier-template-engine.md)):

- **The repository root is author-facing** — it documents how to use and evolve the template and is never
  rendered into a generated project. This includes `copier.yml`, the root `README.md`, this `CONTRIBUTING.md`,
  the bake-and-test suite in `tests/`, the template CI workflow in `.github/workflows/`, the root
  `pyproject.toml`, `.gitignore`, `.pre-commit-config.yaml`, and the template-meta ADRs in `docs/adr/`.
- **The `template/` directory is the generated project.** Copier renders it via `_subdirectory: template`
  with `_templates_suffix: .jinja`: files ending in `.jinja` are rendered, everything else is copied
  verbatim, and path segments containing `{{ ... }}` always render. Generated docs must read as the new
  project itself — never hardcode the brand "Cosmic FastAPI" or `src/template`; use a Copier variable
  (`{{ project_name }}`, `{{ package_name }}`, ...) or generic prose.

## Copier variables and feature flags

The questions in `copier.yml` drive project identity and optional content:

| Variable               | Description                                                  |
|------------------------|--------------------------------------------------------------|
| `project_name`         | Human-readable project name (Swagger title)                  |
| `project_slug`         | Kebab-case slug for repo, container, and database names      |
| `package_name`         | Importable Python package name (snake_case)                  |
| `project_description`  | One-line project description                                 |
| `author_name`          | Author or organization name                                  |
| `author_email`         | Author contact email                                         |
| `author_url`           | Author or project URL                                        |
| `github_owner`         | GitHub owner/org used in clone URLs and image tags           |
| `license`              | License (`MIT`, `Apache-2.0`, `BSD-3-Clause`, `Proprietary`) |
| `python_version`       | Minimum supported Python version                             |
| `database`             | `postgres` or `sqlite`                                       |
| `database_url`         | Default SQLAlchemy async database URL                        |
| `include_user_example` | Include the example User domain slice                        |

Two feature axes shape generated output: `database` (PostgreSQL by default, SQLite optional — see ADR 0018)
and `include_user_example` (the example User slice). Guard optional files with `_exclude` patterns or
templated names in `copier.yml`, and cover both states in the bake matrix.

Do not rename `copier.yml` variables and do not template `uv.lock` — a post-copy task regenerates it with
`uv lock`. Wrap literal GitHub Actions `${{ ... }}` and other literal brace blocks in `{% raw %}{% endraw %}`
inside `.jinja` files.

## Bake and test

The template cannot import its own package in place once the package path contains Jinja
(`src/{{ package_name }}/`). It is validated by **baking**: rendering it to a temporary directory and running
the generated project's full offline quality gate.

```bash
uv sync
uv run pytest
```

`tests/test_bake.py` snapshots the tracked working tree, renders it for each cell of the
`database × include_user_example` matrix (four combos), then inside each baked project runs `uv sync`,
`ruff check`, `ruff format --check`, `pyrefly check`, `pytest -m "not integration"` at 100% coverage, and
`make adr-check` to validate the generated ADR registry. The PostgreSQL integration tier requires Docker and
runs in a dedicated CI stage (see ADR 0019), not during the bake. The same matrix runs in CI via
`.github/workflows/template-ci.yml`.

## Adding or superseding an ADR

There are two ADR sets, sharing one historical number sequence:

- **Generated-standard ADRs** live in `template/docs/adr/`. They describe the runtime architecture a new
  project inherits and ship into generated projects as starter records. They are validated by
  `make adr-check` inside a generated project (and during the bake). Add the next number, update
  `template/docs/adr/README.md`, and include an `Agent Guidance` section for accepted ADRs. To supersede one,
  set its status to `Superseded` and link `Superseded by` to an accepted replacement.
- **Template-meta ADRs** live in the root `docs/adr/` and record decisions about the template itself (the
  engine, the author-vs-generated layout, the bake workflow). Update the root `docs/adr/README.md` registry.

The number sequence is shared, so the generated set has a gap at 0015 (the Copier-engine decision is
template-meta and lives at the root). The registry validator has no contiguity requirement, so gaps are fine.

## Conventional commits

Use [Conventional Commits](https://www.conventionalcommits.org/) for all Git history (see
[ADR 0009](template/docs/adr/0009-conventional-commits.md)): `feat:`, `fix:`, `docs:`, `refactor:`,
`test:`, `chore:`, and so on.
