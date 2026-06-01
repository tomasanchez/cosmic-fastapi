# ADR 0015: MCP Is an Opt-In Primary Adapter

- Status: Accepted
- Date: 2026-05-31

## Context

Coding agents increasingly act as application clients. Model Context Protocol
(MCP) gives them a standard way to discover tools and read context. Exposing
every HTTP endpoint automatically would blur use-case intent, enlarge the
attack surface, and couple an agent contract to transport details.

## Decision

Offer MCP as an optional primary adapter backed by the official Python SDK.

- Install it explicitly with the `mcp` project extra.
- Expose selected mutations as MCP tools and selected read-only context as MCP
  resources.
- Dispatch tools through the same command bus and query services as HTTP
  entrypoints.
- Keep MCP server imports isolated from the default runtime.
- Run the example as a standalone Streamable HTTP server. Mounting it into an
  existing ASGI process remains a project-level deployment choice.
- Require a project to define authentication, authorization, and audit policy
  before exposing an MCP server beyond a trusted local environment.

The sample addon exposes `onboard_user` as a tool and `users://{user_id}` as a
resource. The tool returns the durable resource URI so an agent can read
persisted preferences before taking later user-specific actions.

## Consequences

Agent-oriented projects receive a concrete MCP path without making MCP a
dependency or network surface for every generated service. MCP contracts are
intentional and can evolve independently from HTTP routes. Projects must make
security and deployment decisions before production exposure.

## Agent Guidance

- Do not auto-generate MCP tools from FastAPI routes.
- Keep mutations explicit and narrow. Prefer one aggregate boundary per tool.
- Expose read-only context as resources when it gives an agent durable,
  addressable information.
- Call the application layer, never HTTP routes or SQLAlchemy sessions.
- Do not expose internal domain events as MCP tools.
- Add authentication, authorization, audit logging, and a threat review before
  enabling remote access.

## References

- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK server documentation](https://modelcontextprotocol.github.io/python-sdk/server/)
