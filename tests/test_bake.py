"""Bake-and-test suite for the Cosmic FastAPI Copier template.

The template repository cannot import its own package in place once the package
path contains Jinja. Instead we *bake* the template: render it to a temporary
directory with a sample answer set and run the generated project's full offline
quality gate (Ruff, Pyrefly, pytest at 100% coverage from the unit + e2e tiers).

The bake runs across the ``database x include_user_example`` matrix so both
database choices and both feature-flag states are validated. The PostgreSQL
integration tier is never run during the bake; it requires Docker and is
covered by a dedicated CI stage (see ADR 0019).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import copier
import pytest
import yaml

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

BASE_ANSWERS: dict[str, object] = {
    "project_name": "Demo Service",
    "project_slug": "demo-service",
    "package_name": "demo_service",
    "project_description": "A demo service generated from the template.",
    "author_name": "Ada Lovelace",
    "author_email": "ada@example.com",
    "author_url": "https://example.com",
    "github_owner": "demo-org",
    "license": "MIT",
    "python_version": "3.13",
}

# The bake matrix: every (database, include_user_example) combination. Each
# entry is a single fixture-param value (a tuple) with a readable id.
BAKE_MATRIX = [
    pytest.param(("postgres", True), id="postgres-user-on"),
    pytest.param(("postgres", False), id="postgres-user-off"),
    pytest.param(("sqlite", True), id="sqlite-user-on"),
    pytest.param(("sqlite", False), id="sqlite-user-off"),
]

FEATURE_FLAG_MATRIX = [
    pytest.param(True, id="user-example-on"),
    pytest.param(False, id="user-example-off"),
]


def _database_url(database: str) -> str:
    """Return the default async database URL for a database choice."""
    if database == "postgres":
        return "postgresql+asyncpg://demo-service:demo-service@localhost:5432/demo-service"
    return "sqlite+aiosqlite:///./demo-service.db"


def _answers(database: str, include_user_example: bool) -> dict[str, object]:
    """Build the full Copier answer set for one matrix cell."""
    return {
        **BASE_ANSWERS,
        "database": database,
        "database_url": _database_url(database),
        "include_user_example": include_user_example,
    }


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a command inside the baked project and capture its output."""
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _snapshot_working_tree(dst: Path) -> Path:
    """Copy the git-tracked working tree into a git-free source directory.

    Copier renders a committed ref when the source is a git repository, which
    would ignore uncommitted template changes. Baking from a snapshot of the
    tracked working tree validates the *current* template instead.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=TEMPLATE_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\0")
    for rel in filter(None, tracked):
        source = TEMPLATE_ROOT / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return dst


@pytest.fixture(scope="module")
def template_source(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Snapshot the tracked working tree once for the whole module."""
    return _snapshot_working_tree(tmp_path_factory.mktemp("template-src"))


def _bake(template_source: Path, dst: Path, database: str, include_user_example: bool) -> Path:
    """Render the template into ``dst`` for one matrix cell.

    ``unsafe=True`` is required so Copier executes the ``_tasks`` entry
    (``uv lock``).
    """
    copier.run_copy(
        str(template_source),
        str(dst),
        data=_answers(database, include_user_example),
        defaults=True,
        unsafe=True,
        quiet=True,
    )
    return dst


@pytest.fixture(params=BAKE_MATRIX)
def baked_project(
    request: pytest.FixtureRequest,
    template_source: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """GIVEN the template, render it for each matrix cell."""
    database, include_user_example = request.param
    dst = tmp_path_factory.mktemp("baked")
    return _bake(template_source, dst, database, include_user_example)


def test_package_directory_is_rendered(baked_project: Path) -> None:
    """WHEN the template is baked THEN the package dir uses the answer, not Jinja."""
    assert (baked_project / "src" / "demo_service").is_dir()
    assert not (baked_project / "src" / "{{ package_name }}").exists()
    # No Jinja markers should survive in rendered files.
    assert "{{" not in (baked_project / "pyproject.toml").read_text(encoding="utf-8")


def test_no_template_package_references(baked_project: Path) -> None:
    """WHEN baked THEN no stale `template.` package imports remain in src/tests."""
    offenders: list[str] = []
    for path in baked_project.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from template" in text or "import template" in text:
            offenders.append(str(path))
    assert not offenders, f"stale template imports: {offenders}"


@pytest.mark.parametrize("include_user_example", FEATURE_FLAG_MATRIX)
def test_user_slice_presence_matches_flag(
    template_source: Path,
    tmp_path_factory: pytest.TempPathFactory,
    include_user_example: bool,
) -> None:
    """WHEN baked THEN the user example slice is present only when the flag is on."""
    dst = tmp_path_factory.mktemp("baked-flag")
    _bake(template_source, dst, "postgres", include_user_example)
    user_model = dst / "src" / "demo_service" / "domain" / "models" / "user.py"
    user_router = dst / "src" / "demo_service" / "entrypoint" / "users.py"
    user_migration = dst / "migrations" / "versions" / "20260531_0001_create_users.py"
    assert user_model.exists() is include_user_example
    assert user_router.exists() is include_user_example
    assert user_migration.exists() is include_user_example


@pytest.mark.parametrize(
    "database",
    [pytest.param("postgres", id="postgres"), pytest.param("sqlite", id="sqlite")],
)
def test_postgres_service_present_iff_postgres(
    template_source: Path,
    tmp_path_factory: pytest.TempPathFactory,
    database: str,
) -> None:
    """WHEN baked THEN docker-compose has a `db` service only for PostgreSQL."""
    dst = tmp_path_factory.mktemp("baked-compose")
    _bake(template_source, dst, database, True)
    compose = yaml.safe_load((dst / "docker-compose.yaml").read_text(encoding="utf-8"))
    has_db_service = "db" in compose["services"]
    assert has_db_service is (database == "postgres")
    if database == "postgres":
        assert compose["services"]["db"]["image"] == "pgvector/pgvector:pg17"


@pytest.mark.parametrize(
    "database",
    [pytest.param("postgres", id="postgres"), pytest.param("sqlite", id="sqlite")],
)
def test_integration_ci_job_present_iff_postgres(
    template_source: Path,
    tmp_path_factory: pytest.TempPathFactory,
    database: str,
) -> None:
    """WHEN baked THEN the CI integration job exists only for PostgreSQL."""
    dst = tmp_path_factory.mktemp("baked-ci")
    _bake(template_source, dst, database, True)
    workflow = yaml.safe_load((dst / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8"))
    has_integration_job = "integration" in workflow["jobs"]
    assert has_integration_job is (database == "postgres")


def test_baked_project_passes_offline_quality_gate(baked_project: Path) -> None:
    """WHEN the baked project is synced THEN ruff, pyrefly and the offline gate pass at 100%."""
    sync = _run(["uv", "sync"], baked_project)
    assert sync.returncode == 0, f"uv sync failed:\n{sync.stdout}\n{sync.stderr}"

    ruff = _run(["uv", "run", "ruff", "check", "."], baked_project)
    assert ruff.returncode == 0, f"ruff failed:\n{ruff.stdout}\n{ruff.stderr}"

    # Mirror the generated project's `make lint`, which also enforces formatting.
    ruff_format = _run(["uv", "run", "ruff", "format", "--check", "."], baked_project)
    assert ruff_format.returncode == 0, f"ruff format failed:\n{ruff_format.stdout}\n{ruff_format.stderr}"

    pyrefly = _run(["uv", "run", "pyrefly", "check"], baked_project)
    assert pyrefly.returncode == 0, f"pyrefly failed:\n{pyrefly.stdout}\n{pyrefly.stderr}"

    # The offline gate excludes the PostgreSQL integration tier (ADR 0019).
    tests = _run(
        [
            "uv",
            "run",
            "pytest",
            "-m",
            "not integration",
            "--cov",
            "src",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        ],
        baked_project,
    )
    assert tests.returncode == 0, f"pytest/coverage failed:\n{tests.stdout}\n{tests.stderr}"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-v"]))
