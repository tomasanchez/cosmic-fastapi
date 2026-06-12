<p align="center">
<img width="320" height="320" src="template/docs/cosmic_fastapi.png" alt='cosmic fast api'>
</p>

<p align="center">
<em>Kickoff your app like a kangaroo through the stars: clean, fast, and unapologetically structured.</em>
</p>

---

# Cosmic FastAPI Template

**Cosmic FastAPI** is a [Copier](https://copier.readthedocs.io/) template that scaffolds a
[FastAPI](https://fastapi.tiangolo.com/) service following the [Cosmic Python](https://www.cosmicpython.com/)
guidelines: a domain-first architecture with Pydantic 2, SQLAlchemy 2, Alembic, uv, Ruff, Pyrefly, and a
pytest suite at 100% coverage.

This repository serves two audiences, kept physically separated (see
[ADR 0015](template/docs/adr/0015-copier-template-engine.md)):

- **Author-facing** (this `README`, `copier.yml`, the bake-and-test suite) lives at the repository root and is
  never rendered into a generated project.
- **Generated-project-facing** lives under [`template/`](template/) and becomes a new project on `copier copy`.

## Usage

Generate a new project with [Copier](https://copier.readthedocs.io/) and `uv`:

```bash
uvx copier copy gh:tomasanchez/cosmic-fastapi my-service
```

Copier asks a few questions and renders the answers into the destination directory. A concrete run:

```text
project_name ........... Demo Service
project_slug ........... demo-service
package_name ........... demo_service
project_description .... A demo service.
author_name ............ Ada Lovelace
author_email ........... ada@example.com
author_url ............. https://example.com
github_owner ........... demo-org
license ................ MIT
python_version ......... 3.13
database_url ........... sqlite+pysqlite:///./demo-service.db
include_user_example ... Yes
```

After copy, a post-copy task runs `uv lock`. Finish setup with:

```bash
cd demo-service
uv sync
make migrate
uv run python -m demo_service.main
```

### Updating a generated project

Because the answers are recorded in `.copier-answers.yml`, a generated project can pull standard improvements
(new ADRs, dependency bumps, CI fixes) over time:

```bash
cd demo-service
copier update
```

## Variables

| Variable               | Description                                                       | Default                                       |
|------------------------|-------------------------------------------------------------------|-----------------------------------------------|
| `project_name`         | Human-readable project name (Swagger title)                       | `My Service`                                  |
| `project_slug`         | Kebab-case slug for repo, container, and database names           | derived from `project_name`                   |
| `package_name`         | Importable Python package name (snake_case)                       | derived from `project_slug`                   |
| `project_description`  | One-line project description                                      | _(empty)_                                     |
| `author_name`          | Author or organization name                                       | `Your Name`                                   |
| `author_email`         | Author contact email                                              | `you@example.com`                             |
| `author_url`           | Author or project URL                                             | `https://example.com`                         |
| `github_owner`         | GitHub owner/org used in clone URLs and image tags                | `your-org`                                    |
| `license`              | License (`MIT`, `Apache-2.0`, `BSD-3-Clause`, `Proprietary`)      | `MIT`                                         |
| `python_version`       | Minimum supported Python version (`3.13` or `3.12`)               | `3.13`                                        |
| `database_url`         | Default SQLAlchemy database URL                                   | `sqlite+pysqlite:///./{project_slug}.db`      |
| `include_user_example` | Include the example User domain slice                             | `true`                                        |

## Developing the template

The template repository cannot import its own package in place once the package path contains Jinja
(`src/{{ package_name }}/`). The template is validated by **baking**: rendering it to a temporary directory
and running the generated project's full suite.

```bash
uv sync
uv run pytest
```

The bake-test ([`tests/test_bake.py`](tests/test_bake.py)) snapshots the tracked working tree, renders it with
a sample answer set, then runs `uv sync`, `ruff check`, `pyrefly check`, and `pytest --cov src` inside the
baked project, asserting 100% coverage. The same bake runs in CI via
[`.github/workflows/template-ci.yml`](.github/workflows/template-ci.yml).

## Acknowledgements

Designed and developed by [Tomás Sánchez](https://tomsanchez.com.ar/about/)
<[info@tomsanchez.com.ar](mailto:info@tomsanchez.com.ar)>, following
[Cosmic Python](https://www.cosmicpython.com/) guidelines for project structure.
