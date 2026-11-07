# Architecture

## Roles

- **Discord**: team interface; `/task` is the explicit task intake.
- **NEXUS bot**: validates requests, assigns IDs, records status, and posts results.
- **Switch**: required collaboration and agent-connection layer. The Codex agent joins a Switch room; Switch provides shared room context and routes messages to agents.
- **Codex**: performs code investigation, edits, tests, and reports findings.

## Trust boundaries

Discord messages are untrusted input. The agent must work only in the approved repository/workspace. Require human confirmation for destructive changes, secret access, production deployments, external communications, purchases, or permission changes.

## Current implementation boundary

The Discord bot and job registry are runnable. `SwitchAdapter` expects a small authenticated HTTP bridge with a documented contract. This avoids inventing undocumented Switch endpoints. Implement that bridge using the current Switch agent protocol for the exact server version, then set the environment variables. Until then, `/task` correctly reports `needs_setup` instead of pretending it called Codex.
