This repository is a **Copier template**, not a regular application. Read
`CONTRIBUTING.md` before changing anything; its guidance is imported below.

@CONTRIBUTING.md

## Key rules for agents working on the template

- Edit the generated project under `template/`. The repository **root is
  author-facing** (`copier.yml`, this file, `CONTRIBUTING.md`, `tests/`,
  `.github/`, and the template-meta ADRs in `docs/adr/`) and is never rendered
  into a generated project.
- Files ending in `.jinja` are rendered by Copier; use variables like
  `{{ package_name }}` and `{{ project_name }}`. Wrap literal GitHub Actions
  `${{ ... }}` in `{% raw %}{% endraw %}` inside `.jinja` files. Do not template
  `uv.lock` (a post-copy task regenerates it).
- Validate every change by **baking**: `uv sync` then `uv run pytest` runs the
  `database × include_user_example` matrix and the offline quality gate.
- The generated project's own agent guidance is `template/AGENTS.md`
  (auto-loaded in generated projects via `template/CLAUDE.md`).
