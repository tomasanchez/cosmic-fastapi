"""Bake-and-test suite for the Cosmic FastAPI Copier template.

The template repository cannot import its own package in place once the package
path contains Jinja. Instead we *bake* the template: render it to a temporary
directory with a sample answer set and run the generated project's full quality
gate (Ruff, Pyrefly, pytest at 100% coverage).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import copier
import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_ANSWERS: dict[str, object] = {
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
    "database_url": "sqlite+pysqlite:///./demo-service.db",
    "include_user_example": True,
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
def baked_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """GIVEN the template, render it once with the sample answers.

    `unsafe=True` is required so Copier executes the `_tasks` entry (`uv lock`).
    """
    src = _snapshot_working_tree(tmp_path_factory.mktemp("template-src"))
    dst = tmp_path_factory.mktemp("baked")
    copier.run_copy(
        str(src),
        str(dst),
        data=SAMPLE_ANSWERS,
        defaults=True,
        unsafe=True,
        quiet=True,
    )
    return dst


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


def test_baked_project_passes_quality_gate(baked_project: Path) -> None:
    """WHEN the baked project is synced THEN ruff, pyrefly and pytest all pass at 100%."""
    sync = _run(["uv", "sync"], baked_project)
    assert sync.returncode == 0, f"uv sync failed:\n{sync.stdout}\n{sync.stderr}"

    ruff = _run(["uv", "run", "ruff", "check", "."], baked_project)
    assert ruff.returncode == 0, f"ruff failed:\n{ruff.stdout}\n{ruff.stderr}"

    pyrefly = _run(["uv", "run", "pyrefly", "check"], baked_project)
    assert pyrefly.returncode == 0, f"pyrefly failed:\n{pyrefly.stdout}\n{pyrefly.stderr}"

    tests = _run(
        ["uv", "run", "pytest", "--cov", "src", "--cov-report=term-missing", "--cov-fail-under=100"],
        baked_project,
    )
    assert tests.returncode == 0, f"pytest/coverage failed:\n{tests.stdout}\n{tests.stderr}"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-v"]))
