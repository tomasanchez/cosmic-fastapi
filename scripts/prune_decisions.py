"""Validate ADR metadata and print the active architectural context for agents."""

# Context-rich CLI validation errors are more useful than reusable static messages.
# ruff: noqa: TRY003

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

ACTIVE_STATUS = "Accepted"
ALLOWED_STATUSES = {"Accepted", "Deprecated", "Proposed", "Rejected", "Superseded"}
ADR_FILENAME = re.compile(r"(?P<number>\d{4})-[a-z0-9-]+\.md")
ADR_TITLE = re.compile(r"# ADR (?P<number>\d{4}): (?P<title>.+)")
INDEX_ROW = re.compile(r"\| \[(?P<number>\d{4})\]\((?P<path>[^)]+)\) \| (?P<title>[^|]+?) \| (?P<status>[^|]+?) \|")
METADATA = re.compile(r"- (?P<key>Status|Date|Superseded by): (?P<value>.+)")
LINKED_ADR = re.compile(r"\[(?P<number>\d{4})\]\((?P<path>[^)]+)\)")


class DecisionRegistryError(ValueError):
    """Raised when the ADR registry cannot produce reliable agent context."""


def _error(message: str) -> DecisionRegistryError:
    """Create a registry error with a contextual message."""
    return DecisionRegistryError(message)


@dataclass(frozen=True)
class Decision:
    """Represent one architecture decision record."""

    number: str
    title: str
    status: str
    path: Path
    guidance: tuple[str, ...]
    superseded_by: str | None = None
    superseded_path: str | None = None


def _extract_section(content: str, heading: str) -> tuple[str, ...]:
    """Extract non-empty lines from a Markdown section.

    Args:
        content: Markdown document content.
        heading: Second-level Markdown heading to extract.

    Returns:
        The non-empty lines under the requested heading.
    """
    match = re.search(rf"^## {re.escape(heading)}\s*$", content, re.MULTILINE)
    if match is None:
        return ()

    remainder = content[match.end() :]
    next_heading = re.search(r"^## ", remainder, re.MULTILINE)
    section = remainder[: next_heading.start()] if next_heading else remainder
    lines: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- ") or not lines or not lines[-1].startswith("- "):
            lines.append(line)
        else:
            lines[-1] = f"{lines[-1]} {line}"
    return tuple(lines)


def _parse_decision(path: Path) -> Decision:
    """Parse one ADR file.

    Args:
        path: Path to an ADR Markdown file.

    Returns:
        The parsed decision.

    Raises:
        DecisionRegistryError: If required ADR metadata is invalid or missing.
    """
    content = path.read_text(encoding="utf-8")
    title_match = ADR_TITLE.search(content)
    if title_match is None:
        raise _error(f"{path.name}: missing '# ADR NNNN: Title' heading")

    filename_match = ADR_FILENAME.fullmatch(path.name)
    if filename_match is None:
        raise _error(f"{path.name}: ADR filename must use 'NNNN-kebab-case.md'")

    title_number = title_match.group("number")
    filename_number = filename_match.group("number")
    if title_number != filename_number:
        raise _error(f"{path.name}: heading number {title_number} does not match filename")

    metadata = {match.group("key"): match.group("value").strip() for match in METADATA.finditer(content)}
    status = metadata.get("Status")
    if status not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        raise _error(f"{path.name}: status must be one of: {allowed}")
    status = cast(str, status)
    if "Date" not in metadata:
        raise _error(f"{path.name}: missing Date metadata")

    superseded_by = None
    superseded_path = None
    if status == "Superseded":
        superseded_match = LINKED_ADR.fullmatch(metadata.get("Superseded by", ""))
        if superseded_match is None:
            raise _error(f"{path.name}: superseded ADR must link to its replacement")
        superseded_by = superseded_match.group("number")
        superseded_path = superseded_match.group("path")

    guidance = _extract_section(content, "Agent Guidance")
    if status == ACTIVE_STATUS and not guidance:
        raise _error(f"{path.name}: accepted ADR must include Agent Guidance")

    return Decision(
        number=filename_number,
        title=title_match.group("title").strip(),
        status=status,
        path=path,
        guidance=guidance,
        superseded_by=superseded_by,
        superseded_path=superseded_path,
    )


def load_decisions(adr_dir: Path) -> tuple[Decision, ...]:
    """Load numbered ADR documents from a directory.

    Args:
        adr_dir: Directory containing ADR Markdown files.

    Returns:
        Parsed decisions sorted by ADR number.

    Raises:
        DecisionRegistryError: If a duplicate ADR number exists.
    """
    decisions = tuple(
        sorted(
            (_parse_decision(path) for path in adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")), key=lambda adr: adr.number
        )
    )
    numbers = [decision.number for decision in decisions]
    duplicates = sorted({number for number in numbers if numbers.count(number) > 1})
    if duplicates:
        raise _error(f"duplicate ADR numbers: {', '.join(duplicates)}")
    return decisions


def _find_index_errors(decisions: tuple[Decision, ...], index_rows: dict[str, dict[str, str]]) -> list[str]:
    """Find inconsistencies between ADR documents and index rows."""
    errors: list[str] = []
    decision_numbers = {decision.number for decision in decisions}
    for decision in decisions:
        row = index_rows.get(decision.number)
        if row is None:
            errors.append(f"{decision.path.name}: missing from ADR index")
            continue
        if row["path"] != decision.path.name:
            errors.append(f"{decision.path.name}: index path is {row['path']!r}")
        if row["title"] != decision.title:
            errors.append(f"{decision.path.name}: index title is {row['title']!r}")
        if row["status"] != decision.status:
            errors.append(f"{decision.path.name}: index status is {row['status']!r}")

    unknown_rows = sorted(set(index_rows) - decision_numbers)
    if unknown_rows:
        errors.append(f"ADR index references missing records: {', '.join(unknown_rows)}")
    return errors


def _find_lifecycle_errors(decisions: tuple[Decision, ...]) -> list[str]:
    """Find invalid ADR lifecycle references."""
    decision_by_number = {decision.number: decision for decision in decisions}
    errors: list[str] = []
    for decision in decisions:
        if not decision.superseded_by:
            continue
        replacement = decision_by_number.get(decision.superseded_by)
        if replacement is None:
            errors.append(f"{decision.path.name}: replacement ADR {decision.superseded_by} does not exist")
            continue
        if decision.superseded_path != replacement.path.name:
            errors.append(f"{decision.path.name}: replacement path must be {replacement.path.name!r}")
        if replacement.status != ACTIVE_STATUS:
            errors.append(f"{decision.path.name}: replacement ADR {replacement.number} must be accepted")
    return errors


def validate_registry(adr_dir: Path) -> tuple[Decision, ...]:
    """Validate the ADR index and lifecycle metadata.

    Args:
        adr_dir: Directory containing the ADR registry.

    Returns:
        Parsed decisions sorted by ADR number.

    Raises:
        DecisionRegistryError: If the ADR registry is inconsistent.
    """
    decisions = load_decisions(adr_dir)
    index_path = adr_dir / "README.md"
    if not index_path.exists():
        raise _error(f"{index_path}: missing ADR index")

    index_content = index_path.read_text(encoding="utf-8")
    index_rows = {match.group("number"): match.groupdict() for match in INDEX_ROW.finditer(index_content)}
    errors = _find_index_errors(decisions, index_rows) + _find_lifecycle_errors(decisions)
    if errors:
        raise _error("\n".join(errors))
    return decisions


def render_context(decisions: tuple[Decision, ...]) -> str:
    """Render accepted ADR guidance as a compact agent briefing.

    Args:
        decisions: Parsed architecture decisions.

    Returns:
        Markdown containing only active architectural guidance.
    """
    lines = [
        "# Active Architecture Decisions",
        "",
        "Use this pruned context with AGENTS.md before implementing changes.",
        "",
    ]
    for decision in decisions:
        if decision.status != ACTIVE_STATUS:
            continue
        lines.extend(
            [
                f"## ADR {decision.number}: {decision.title}",
                "",
                f"Source: {decision.path.as_posix()}",
                "",
                *decision.guidance,
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "context"), help="Validate the registry or print active guidance")
    parser.add_argument(
        "--adr-dir",
        type=Path,
        default=Path("docs/adr"),
        help="ADR directory relative to the current working directory",
    )
    return parser.parse_args()


def main() -> int:
    """Run the requested ADR pruning command."""
    args = _parse_args()
    try:
        decisions = validate_registry(args.adr_dir)
    except DecisionRegistryError as error:
        print(f"ADR registry error:\n{error}", file=sys.stderr)
        return 1

    if args.command == "context":
        print(render_context(decisions), end="")
    else:
        print(
            f"ADR registry is valid: {len(decisions)} records, {sum(adr.status == ACTIVE_STATUS for adr in decisions)} active."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
