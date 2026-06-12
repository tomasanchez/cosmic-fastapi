# Template Architecture Decision Records

This directory records decisions about the **template itself** — how this
repository is authored, generated, and evolved. These are author-facing records;
they are never rendered into a generated project.

The **generated service's** architectural standard (the Cosmic Python defaults a
new project inherits) lives in [`template/docs/adr/`](../../template/docs/adr/).

ADR numbers continue one shared historical sequence across both sets. The
generated set therefore has a gap at 0015 — that number belongs to the
template-engine decision recorded here.

## Decision Records

| ADR | Decision | Status |
| --- | --- | --- |
| [0015](0015-copier-template-engine.md) | Copier as the Template Engine | Accepted |

## Creating a template-meta ADR

Record a new ADR here when changing how the template is authored or generated
(the engine, the author-vs-generated layout, the bake-and-test workflow). Assign
the next four-digit number in the shared sequence and keep the decision focused.
Decisions about the generated service's runtime architecture belong in
[`template/docs/adr/`](../../template/docs/adr/) instead.
