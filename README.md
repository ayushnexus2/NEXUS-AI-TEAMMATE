# NEXUS AI TEAMMATE

**Your AI coding teammate inside Discord.** NEXUS receives a `/task` request, creates a traceable job, hands the work to a Switch-connected coding agent (Codex), and reports the result back to the Discord channel.

> Status: starter implementation. The Discord task intake and job tracking are implemented. The Switch/Codex handoff is isolated behind an adapter and must be configured against the Switch server/protocol version you run. Do not describe a live Codex execution as working until you complete the end-to-end test in `docs/DEMO.md`.

## Architecture

```text
Discord /task
    |
    v
NEXUS Discord bot (discord.py)
    |
    v
Task queue + job record
    |
    v
Switch bridge adapter  ---> Switch room ---> Codex agent
    |                                      |
    <------------- agent result -----------<
    |
    v
Discord result message
```

Switch is the collaboration layer: it hosts the shared room and connects the coding agent to the team's chat workflow. NEXUS handles task intake, validation, job status and the Discord-facing result.

## Features

- `/task description:<work>` creates a task and acknowledges it in Discord.
- `/job id:<job-id>` shows the current task status.
- `/health` checks whether the bot process is alive.
- Task IDs and status are logged.
- Configurable task-size limits and allowed-channel restriction.
- No hard-coded secrets; use environment variables.
- The Switch adapter is deliberately separate from Discord code.

## Requirements

- Python 3.11+
- A Discord application/bot with `applications.commands` and `bot` scopes.
- A Switch server and a Codex agent connected to a Switch room.
- Docker/Switch Console and an available Codex plan or API access, as required by your setup.

## Setup

1. Create a Discord application at https://discord.com/developers/applications.
2. Add a bot and invite it with `bot` and `applications.commands` scopes. Grant `Send Messages`, `Use Slash Commands`, and `Read Message History`.
3. Copy `.env.example` to `.env` and fill in values.
4. Install dependencies and start the bot:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

5. In Discord, run `/task description: Fix the login form validation bug`.
6. Check `/job` for the job status.

## Switch and Codex setup

Switch Console is a desktop application and runs the Switch services (including its collaboration bridge). Connect your Discord workspace and configure a Codex provider/agent in Switch Console. Add the NEXUS task agent to the same Switch room or adapt `SwitchAdapter` to the exact agent-protocol endpoint exposed by your installed Switch version.

Official resources:
- Switch hackathon: https://www.wemakedevs.org/hackathons/switch
- Switch docs: https://docs.switchagents.ai/
- Switch repository: https://github.com/sandbox-quantum/switch
- Codex docs MCP command: `codex mcp add switch-docs --url https://docs.switchagents.ai/mcp`

**Important:** Switch does not ship an AI model. You supply Codex and configure it in Switch. This repository does not pretend that posting a Discord message directly to a local Codex CLI is equivalent to using Switch.

## Configuration

See `.env.example`.

- `DISCORD_BOT_TOKEN`: bot token (keep private).
- `DISCORD_GUILD_ID`: optional guild for fast slash-command registration.
- `ALLOWED_CHANNEL_ID`: optional channel restriction.
- `SWITCH_BASE_URL`: Switch server URL, if your selected integration exposes an HTTP endpoint.
- `SWITCH_ROOM_ID`: room identifier configured in Switch.
- `SWITCH_AGENT_NAME`: configured Codex agent name.
- `SWITCH_SHARED_SECRET`: optional shared secret for your own authenticated bridge.
- `TASK_TIMEOUT_SECONDS`: maximum wait for a handoff.
- `MAX_TASK_CHARS`: maximum task length.

## Security

- Never commit `.env`, bot tokens, API keys, or shared secrets.
- Keep the bot limited to a dedicated team channel.
- Treat Discord task text as untrusted input. Codex must ask before destructive actions, secret access, external messages, purchases, deployments, or production changes.
- Review code changes before merging.
- Do not expose the Switch server publicly without authentication and TLS.

## Project structure

```text
bot/
  main.py          Discord commands and startup
  jobs.py          In-memory job state
  switch_adapter.py Switch handoff boundary
docs/
  ARCHITECTURE.md
  DEMO.md
.env.example
requirements.txt
```

## Current limitations

- Job records are in memory and reset when the bot restarts.
- A production deployment should use persistent storage and a durable queue.
- The Switch adapter requires the exact endpoint/authentication contract from your Switch deployment. See `bot/switch_adapter.py`.
- The end-to-end Discord → Switch → Codex → Discord flow is not verified until you record a successful test.
