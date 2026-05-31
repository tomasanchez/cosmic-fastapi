# ADR 0010: ADR Lifecycle and Decision Pruning

- Status: Accepted
- Date: 2026-05-31

## Context

As the standard evolves, agents need a compact and reliable view of the
currently active architecture. Reading every historical decision encourages
stale guidance to survive after a decision has been replaced.

Automated tooling can validate ADR metadata and remove inactive records from
agent context. It cannot decide whether an architecture remains appropriate;
that still requires engineering judgment and a new ADR.

## Decision

Maintain an indexed ADR registry and use `scripts/prune_decisions.py` to
validate and prune it.

Supported ADR statuses are:

- `Proposed`: under discussion and not binding.
- `Accepted`: active architectural guidance.
- `Deprecated`: still present but discouraged for new work.
- `Superseded`: replaced by another ADR and excluded from active context.
- `Rejected`: considered but not adopted.

A superseded ADR must include a replacement link:

```text
- Superseded by: [NNNN](NNNN-replacement-title.md)
```

Run:

```bash
make adr-check
make adr-context
```

`adr-check` validates registry consistency. `adr-context` prints a compact
briefing containing only accepted ADR guidance.

## Consequences

Agents can load a smaller architectural context without losing history. The
index, statuses, and supersession links require maintenance when decisions
change.

## Agent Guidance

- Run `make adr-context` before architectural work.
- Run `make adr-check` after adding or changing ADRs.
- Do not edit an accepted ADR to reverse its decision. Add a new ADR and mark
  the old record as superseded.
- Treat generated context as a briefing, not a replacement for engineering
  judgment.

## References

- [Architecture Decision Records](https://adr.github.io/)
