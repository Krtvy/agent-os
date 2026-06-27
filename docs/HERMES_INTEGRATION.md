# Hermes Agent Integration

> Added 2026-06-27. Hermes Agent (NousResearch) runs as a parallel system alongside the Claude Code observer-ecosystem.

## Architecture

```
┌─────────────────────────────────────┐   ┌──────────────────────────────────────┐
│       Claude Code (interactive)     │   │      Hermes Agent (background)       │
│                                     │   │                                      │
│  Yudhishthira  — data analyst       │   │  /observer-status  — health query    │
│  Sanjaya       — Tier-1 observer    │   │  /nakula-trigger   — manual job fire │
│  Vyasa         — Tier-2 conductor   │   │  ecosystem-health  — cron watchdog   │
│  Sahadeva      — weekly auditor     │   │                                      │
│  Arjuna        — executor           │   │  Cron: every 6h health check         │
│  Hanuman       — scout              │   │  Writes: logs/hermes-bridge/         │
│  Narada        — drafter            │   │                                      │
│  Vidura        — researcher         │   │  LLM: claude-sonnet-4-6 (Anthropic)  │
└──────────────┬──────────────────────┘   └──────────────┬───────────────────────┘
               │                                         │
               └──────────────┬──────────────────────────┘
                              │
               ~/projects/observer-test/logs/
               (shared read; hermes-bridge/ is Hermes-owned)
```

## Division of Labor

| Responsibility | System | Reason |
|---------------|--------|--------|
| Data analysis (Yudhishthira) | Claude Code | Complex reasoning, context-heavy |
| Research (Vidura, Hanuman) | Claude Code | Web search, multi-step analysis |
| Content drafting (Narada) | Claude Code | Voice calibration, creative |
| Execution (Arjuna) | Claude Code | Careful tool use with circuit breakers |
| Observer reporting (Sanjaya, Vyasa) | Claude Code | Complex log analysis |
| Audit (Sahadeva) | Claude Code | Multi-week comparison, trust chain |
| **Background health monitoring** | **Hermes Agent** | Always-on daemon, cron-native |
| **Status queries on demand** | **Hermes Agent** | Instant answers without starting Claude Code |
| **Manual job triggers** | **Hermes Agent** | Fire Nakula jobs from anywhere |

## Coordination Protocol

The two systems coordinate through the shared `logs/` directory:

- **Claude Code agents** write to `logs/<agent-name>/` (read-only for Hermes)
- **Hermes Agent** writes to `logs/hermes-bridge/` (read-only for Claude Code agents)
- **`logs/hermes-bridge/health.json`** — updated every 6h by the ecosystem-health cron skill

Bhishma rules that apply to both systems:
- R5: Append-only journals (Hermes must not delete logs/*)
- R19: UTC timestamps in all log entries
- R20: run_id format in health.json entries

## Skills Installed

Three custom skills live in `~/.hermes/skills/` after setup:

| Skill | Slash command | Use |
|-------|--------------|-----|
| observer-status | `/observer-status` | Instant ecosystem health report |
| nakula-trigger | `/nakula-trigger` | Manually fire a Nakula job |
| ecosystem-health | `/ecosystem-health` | Run the health watchdog (also runs on cron) |

Skills were staged from `hermes-skills/` in this repo. Re-copy from there if Hermes is reinstalled.

## Cron Jobs (Hermes)

One Hermes cron job is configured after setup:

| Job | Schedule | Skill | What it does |
|-----|----------|-------|-------------|
| ecosystem-health-check | `0 */6 * * *` (every 6h) | ecosystem-health | Checks log freshness, writes health.json |

## Setup

See [`hermes-skills/install.ps1`](../hermes-skills/install.ps1) — run it once after installing Hermes Agent.

## Installation Reference

Hermes Agent Windows install (one-liner, no admin required):
```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Data lives at `%LOCALAPPDATA%\hermes\` (persists across Hermes reinstalls).
Skills live at `%LOCALAPPDATA%\hermes\skills\` (= `~/.hermes/skills/` in bash).

## Gateway Auto-Start

To have the Hermes cron scheduler start at login (required for unattended health checks):
```powershell
hermes gateway install
hermes gateway status
```

This uses Windows Scheduled Tasks — no admin required.
