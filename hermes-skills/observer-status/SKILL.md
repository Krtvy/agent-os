---
name: observer-status
description: Show health and last-run status of the observer-ecosystem Claude Code agents
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [observer-ecosystem, rootlabs, monitoring]
    category: rootlabs
---

# Observer Ecosystem Status

## When to Use

When you need to know the current health of the Mahabharata-themed Claude Code agent ecosystem at `~/projects/observer-test/`. Use when asked "what's running?", "check the ecosystem", "observer status", or "is everything okay?"

## What This Covers

The observer-ecosystem has two scheduled Claude Code agents:

| Agent | Schedule | Purpose |
|-------|----------|---------|
| Sanjaya (observer) | Daily 02:00 IST | Watches all Tier-0 agents, writes drift reports |
| Sahadeva (auditor) | Sundays 10:00 IST | Weekly external audit of the whole ecosystem |

Tier-0 workers (Yudhishthira, Arjuna, Hanuman, Narada, Nakula, Vidura) run on-demand from Kartavya or when triggered by Sanjaya.

## Procedure

1. **Check log directories exist**
   ```bash
   ls ~/projects/observer-test/logs/
   ```

2. **Find last run for each scheduled agent** — look for the most recent `.log` file:
   ```bash
   # Sanjaya last run
   ls -lt ~/projects/observer-test/logs/sanjaya/ 2>/dev/null | head -3

   # Sahadeva last run
   ls -lt ~/projects/observer-test/logs/sahadeva/ 2>/dev/null | head -3
   ```

3. **Check for alert files** (Nakula writes these on job failure):
   ```bash
   find ~/projects/observer-test/logs/ -name "alert-*.txt" -newer ~/projects/observer-test/logs -mtime -7 2>/dev/null
   ```

4. **Check Hermes bridge health file** (written by the ecosystem-health cron):
   ```bash
   cat ~/projects/observer-test/logs/hermes-bridge/health.json 2>/dev/null || echo "No bridge health file yet"
   ```

5. **Check Nakula locks** (a stale lock means a job is stuck or crashed):
   ```bash
   ls -la ~/projects/observer-test/.claude/agents/nakula/locks/ 2>/dev/null
   ```

## Report Format

Summarize findings as:

```
Observer Ecosystem — [DATE UTC]

Scheduled agents:
  Sanjaya:   last run [TIME] — [OK / OVERDUE / MISSING LOGS]
  Sahadeva:  last run [TIME] — [OK / OVERDUE / MISSING LOGS]

Alerts (last 7 days): [none / list files]
Nakula locks: [clear / STALE LOCK: filename]
Hermes bridge: [last health check time / not yet running]
```

Flag OVERDUE if Sanjaya hasn't run in >26 hours, or Sahadeva hasn't run in >8 days.

## Pitfalls

- Logs are under `~/projects/observer-test/logs/`, not the source repo at `~/projects/rootlabs-scan/agent-os/`.
- Windows paths: use bash-style `~/projects/...` — Hermes resolves these via Git Bash.
- If `sanjaya/` or `sahadeva/` log directories are missing, the observer wasn't deployed yet — check `~/projects/observer-test/.claude/agents/_meta/observer/`.
