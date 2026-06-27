---
name: nakula-trigger
description: Manually trigger a Nakula automation job from Hermes outside the normal cron schedule
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [observer-ecosystem, rootlabs, automation, nakula]
    category: rootlabs
---

# Nakula Job Trigger

## When to Use

When you need to fire one of Nakula's scheduled jobs immediately without waiting for the cron. Examples:
- "Run the sanjaya observer now"
- "Trigger sahadeva audit"
- "Fire the sanjaya job manually"

Only use for jobs listed in Nakula's `jobs.yml`. Do not invent job names.

## Known Jobs (from jobs.yml)

| Job name | Schedule | What it does |
|----------|----------|-------------|
| `sanjaya` | Daily 02:00 IST | Runs the Tier-1 observer over all Tier-0 agents |
| `sahadeva` | Sundays 10:00 IST | Weekly external audit of the whole ecosystem |

## Procedure

1. **Confirm the job name** with the user if ambiguous. Valid names are `sanjaya` and `sahadeva` (and any others in jobs.yml).

2. **Check for a stale lock** — a lock file means the job is already running or crashed:
   ```bash
   ls ~/projects/observer-test/.claude/agents/nakula/locks/nakula-*.lock 2>/dev/null \
     && echo "LOCK EXISTS — check if job is running before proceeding" \
     || echo "No lock — safe to trigger"
   ```

3. **Read the jobs.yml** to get the exact command for the job:
   ```bash
   cat ~/projects/observer-test/.claude/agents/nakula/jobs.yml
   ```

4. **Trigger the job** via the Nakula dispatcher:
   ```bash
   cd ~/projects/observer-test && bash scripts/nakula-run.sh <job-name>
   ```
   Replace `<job-name>` with the actual job (e.g., `sanjaya` or `sahadeva`).

5. **Tail the log** to confirm it started:
   ```bash
   # For sanjaya:
   ls -lt ~/projects/observer-test/logs/sanjaya/ 2>/dev/null | head -5

   # For sahadeva:
   ls -lt ~/projects/observer-test/logs/sahadeva/ 2>/dev/null | head -5
   ```

6. **Report outcome** — note the run_id from the log filename and whether the job completed or is still running.

## Pitfalls

- The Nakula dispatcher script is at `scripts/nakula-run.sh` inside the observer-test directory, not in the agent-os source repo.
- If `scripts/nakula-run.sh` doesn't exist yet, it hasn't been deployed. Fall back to running the command from jobs.yml directly.
- Do not run `sanjaya` and `sahadeva` in parallel — both can write to overlapping log files.
- Bhishma R19: timestamps in logs are UTC. The schedule in jobs.yml is in host local time (IST).

## Verification

After triggering, a new log file should appear in `~/projects/observer-test/logs/<agent>/` within 30 seconds. If no file appears, the script likely failed silently — check `~/projects/observer-test/logs/nakula/` for a Nakula error log.
