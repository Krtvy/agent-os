# Install — Observer Agent Bundle

This bundle adds a Tier-1 Observer meta-agent (and a reserved Tier-2 Conductor slot) to a Claude Code project.

## Quick install (3 steps)

1. **Copy `_meta/` into your project's `.claude/agents/` directory:**
   ```bash
   cp -r _meta /path/to/your/project/.claude/agents/
   ```

   Final layout in your project:
   ```
   .claude/agents/
   ├── _meta/                    ← from this bundle
   │   ├── observer/
   │   └── conductor/            ← reserved (placeholder README only)
   ├── <your-existing-worker-1>/
   └── <your-existing-worker-2>/
   ```

2. **Edit `.claude/agents/_meta/observer/config.yml`:**
   - Confirm `input_sources:` paths match where your transcripts/tool-logs/errors live.
   - Optionally restrict `watched_agents:` to a specific list (default: watch everything except `_meta/`).

3. **Make the runner executable:**
   ```bash
   chmod +x .claude/agents/_meta/observer/run_observer.sh
   ```

## First run (manual, smoke test)

```bash
.claude/agents/_meta/observer/run_observer.sh
```

You should see:
- A run start/complete timestamp pair
- Journals appearing under `.claude/agents/_meta/observer/journal/<agent>.md` (one per watched agent)
- No errors

## Schedule daily (cron)

```cron
# Observer daily at 02:00 UTC
0 2 * * * cd /path/to/your/project && .claude/agents/_meta/observer/run_observer.sh >> .claude/agents/_meta/observer/run.log 2>&1
```

## What you'll see over time

- **Days 1–9 (bootstrap) or 1–17 (adaptation):** journal entries accumulate, no proposals yet.
- **Threshold day:** a Pattern Report appears in `reports/` and a Proposal appears in `proposals/`.
- **Your move:** review the proposal, then either:
  - `mv proposals/<id>.md approved/<id>.md` to approve
  - `mv proposals/<id>.md rejected/<id>.md` to reject
  - Edit the diff in-place and leave it in `proposals/` to revise

On the next run after approval, the observer applies the diff to the target's `skill.md` and logs a calibration note.

## What's inside this bundle

```
_meta/
├── README.md                   # Overview of meta tier & hierarchy philosophy
├── observer/
│   ├── agent.md                # Observer agent definition (frontmatter + system prompt)
│   ├── skill.md                # Observer's own skills
│   ├── config.yml              # Thresholds, watched agents, paths, approval method
│   ├── run_observer.sh         # Invocation script (manual + cron)
│   ├── README.md               # Full operating guide
│   ├── templates/              # Schemas: journal, pattern-report, proposal
│   ├── journal/                # Per-agent journals (filled at runtime)
│   ├── reports/                # Dated pattern reports (filled at runtime)
│   ├── proposals/              # Awaiting your decision (filled at runtime)
│   ├── approved/               # Archive of accepted (filled at runtime)
│   └── rejected/               # Archive of rejected (filled at runtime)
└── conductor/
    └── README.md               # Tier-2 placeholder (reserved slot)
```

## Tier hierarchy

| Tier | Role | This bundle ships |
|------|------|-------------------|
| 0 | Workers (your existing agents) | — |
| 1 | Meta-observer | ✅ `_meta/observer/` |
| 2 | Conductor (manager-of-managers) | 🔲 reserved slot only |

To activate a Tier-2 Conductor later, see `_meta/conductor/README.md`.

## Default thresholds

| Mode | Calendar days | Distinct runs | Whichever |
|------|---------------|---------------|-----------|
| Bootstrap (no skill.md) | 10 | 20 | first |
| Adaptation (has skill.md) | 18 | 40 | first |

Adjust per-agent in `config.yml` under `overrides:`.

## Safety contract

The observer is **read-only on Tier-0 agents** until you explicitly approve a proposal. There is no auto-apply mode and no way to bypass the approval gate from inside the agent.
