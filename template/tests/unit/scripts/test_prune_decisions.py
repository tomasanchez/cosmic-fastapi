"""Test suite for the architectural decision pruner."""

from pathlib import Path

import pytest

from scripts.prune_decisions import DecisionRegistryError, render_context, validate_registry


def _write_adr(adr_dir: Path, number: str, slug: str, title: str, status: str, extra_metadata: str = "") -> None:
    """Write an ADR fixture.

    Args:
        adr_dir: ADR fixture directory.
        number: Four-digit ADR identifier.
        slug: ADR filename slug.
        title: ADR title.
        status: ADR lifecycle status.
        extra_metadata: Optional additional metadata lines.
    """
    (adr_dir / f"{number}-{slug}.md").write_text(
        f"""# ADR {number}: {title}

- Status: {status}
- Date: 2026-05-31
{extra_metadata}
## Context

Fixture.

## Decision

Fixture.

## Agent Guidance

- Follow ADR {number}.
""",
        encoding="utf-8",
    )


def _write_index(adr_dir: Path, rows: list[tuple[str, str, str, str]]) -> None:
    """Write an ADR index fixture.

    Args:
        adr_dir: ADR fixture directory.
        rows: ADR number, path, title, and status tuples.
    """
    table_rows = "\n".join(f"| [{number}]({path}) | {title} | {status} |" for number, path, title, status in rows)
    (adr_dir / "README.md").write_text(
        f"""# Architecture Decision Records

| ADR | Decision | Status |
| --- | --- | --- |
{table_rows}
""",
        encoding="utf-8",
    )


class TestDecisionPruner:
    """Test cases for active ADR context pruning."""

    def test_context_contains_only_accepted_decisions(self, tmp_path: Path):
        """
        GIVEN accepted and superseded ADRs in a valid registry
        WHEN active decision context is rendered
        THEN only accepted ADR guidance is included
        """
        # GIVEN
        _write_adr(
            tmp_path,
            "0001",
            "old-decision",
            "Old Decision",
            "Superseded",
            "- Superseded by: [0002](0002-new-decision.md)\n",
        )
        _write_adr(tmp_path, "0002", "new-decision", "New Decision", "Accepted")
        _write_index(
            tmp_path,
            [
                ("0001", "0001-old-decision.md", "Old Decision", "Superseded"),
                ("0002", "0002-new-decision.md", "New Decision", "Accepted"),
            ],
        )

        # WHEN
        context = render_context(validate_registry(tmp_path))

        # THEN
        assert "ADR 0001" not in context
        assert "ADR 0002: New Decision" in context
        assert "Follow ADR 0002." in context

    def test_registry_rejects_an_unindexed_decision(self, tmp_path: Path):
        """
        GIVEN an ADR that is missing from the index
        WHEN the ADR registry is validated
        THEN a DecisionRegistryError is raised
        """
        # GIVEN
        _write_adr(tmp_path, "0001", "missing-index-row", "Missing Index Row", "Accepted")
        _write_index(tmp_path, [])

        # WHEN / THEN
        with pytest.raises(DecisionRegistryError, match="missing from ADR index"):
            validate_registry(tmp_path)
