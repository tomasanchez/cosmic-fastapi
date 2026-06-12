# ADR 0015: Copier as the Template Engine

- Status: Accepted
- Date: 2026-06-12

## Context

Cosmic FastAPI began as a *clone-and-rename* template: the Python package is
literally named `template`, and project identity (name, author, URLs, database
defaults) is hardcoded across `pyproject.toml`, settings, docs, Docker, and CI.
Adopting it means cloning the repository and hand-editing every occurrence,
which is error-prone and leaves the new project with no link back to the
standard it was generated from.

The value of this repository is not a one-time scaffold; it is an **evolving
standard**. The ADR set, [AGENTS.md](../../AGENTS.md), the Cosmic Python
coverage matrix, and the tooling baseline keep changing. A generated project
should be able to pull those improvements over time, not fork them at birth.

Two mature Python scaffolding engines exist: cookiecutter and Copier. We need a
durable decision about which one this template targets, and how the repository
is laid out to serve both template authors and generated projects.

## Decision

Use **Copier**.

- **Updates are first-class.** Copier records answers in a generated
  `.copier-answers.yml` and supports `copier update`, so a project created from
  this template can re-pull standard improvements (new ADRs, dependency bumps,
  CI fixes). This is the deciding factor: it matches the "reusable, evolving
  standard for people and agents" intent. Cookiecutter has no native update
  story (it requires bolting on `cruft`).
- **Conditional content is declarative.** Copier renders Jinja in both file
  contents and paths and excludes files with `_exclude` and templated
  filenames, which fits optional features (for example
  `include_user_example`) better than cookiecutter's post-generation hook
  deletions.
- **Questions are typed and validated.** Copier validates answers (slug regex,
  email, choices) from `copier.yml` without extra hook code.

### Repository layout

The template repository serves two audiences. We keep them physically
separated:

- **Author-facing, at the repository root** (never rendered into a generated
  project): `copier.yml`, the template `README` / `CONTRIBUTING`, this
  `docs/adr/` standard, the coverage matrix, and the template's own
  bake-and-test suite.
- **Generated-project-facing, under a `template/` subdirectory** referenced by
  Copier's `_subdirectory: template`: everything that becomes a new project —
  `pyproject.toml`, `src/{{ package_name }}/`, `migrations/`, `Makefile`,
  `Dockerfile`, `docker-compose.yaml`, CI, and a starter copy of `AGENTS.md`
  and the ADRs.

Generation copies the rendered `template/` tree into the destination directory
the user names (`copier copy gh:tomasanchez/cosmic-fastapi my-service`); we do
not nest the output inside a redundant `{{ project_slug }}/` folder.

### Parameters

The `template` package is renamed to `{{ package_name }}`. Identity is driven by
Copier questions: `project_name`, `project_slug`, `package_name`,
`project_description`, `author_name`, `author_email`, `author_url`,
`github_owner`, `license`, `python_version`, `database_url`, and the
`include_user_example` feature flag. `uv.lock` is never templated; a post-copy
task regenerates it with `uv lock`.

### Testing

The template repository cannot import its own package in place once the package
path contains Jinja. The template is validated by **baking**: render it to a
temporary directory and run the generated project's full suite (Ruff, Pyrefly,
pytest at 100% coverage). This bake-and-test replaces in-place testing for the
template repository and runs across the feature-flag matrix in CI.

## Consequences

Adopting and updating a project becomes a supported workflow rather than a
manual rename. Optional features can be added later as Jinja-guarded flags (the
Kafka, MCP, and integration-event scaffolds removed during hardening can return
this way once they carry real content). The ADRs ship into generated projects
as starter records while this repository remains the authoritative standard.

The costs: contributors must run a bake to test changes (slower than a direct
`pytest`), and template authoring requires care where Jinja delimiters meet
literal `${{ }}` in GitHub Actions or `{}` in f-strings — those regions are
wrapped in `{% raw %}` blocks. Copier becomes a development dependency of the
template repository.

## Agent Guidance

- Edit generated-project files under `template/`. Do not add project identity as
  a hardcoded string; use the Copier variable (`{{ package_name }}`,
  `{{ project_name }}`, etc.).
- Keep author-facing files (this ADR set, the template README/CONTRIBUTING, the
  bake-and-test suite) at the repository root, outside `_subdirectory`.
- When adding an optional feature, add a boolean question to `copier.yml`, guard
  the files with `_exclude` or templated names, and cover both states in the
  bake matrix.
- Never template `uv.lock`; regenerate it in a post-copy task.
- Wrap GitHub Actions `${{ ... }}` and other literal brace blocks in
  `{% raw %}{% endraw %}` inside `.jinja` files.

## References

- [Copier documentation](https://copier.readthedocs.io/)
- [Copier: updating a project](https://copier.readthedocs.io/en/stable/updating/)
- [Epic #24: convert cosmic-fastapi into a Copier template](https://github.com/tomasanchez/cosmic-fastapi/issues/24)
