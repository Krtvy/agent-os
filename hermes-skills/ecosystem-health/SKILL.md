---
name: ecosystem-health
description: Scheduled health watchdog — checks observer-ecosystem log freshness and writes health.json
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [observer-ecosystem, rootlabs, monitoring, cron]
    category: rootlabs
---

# Ecosystem Health Watchdog

## When to Use

This skill is designed to run on a **Hermes cron schedule** (every 6 hours) as a lightweight background watchdog. It reads log freshness from the Claude Code observer-ecosystem and writes a structured `health.json` to the bridge directory so other tools can check ecosystem status without parsing raw logs.

You can also invoke it manually: "run ecosystem health check" or "check if the observer is healthy".

## Schedules to Monitor

| Agent | Expected cadence | Max acceptable gap |
|-------|------------------|--------------------|
| Sanjaya | Daily | 26 hours |
| Sahadeva | Weekly (Sundays) | 8 days |

## Procedure

1. **Get current UTC time**:
   ```bash
   NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
   echo "Health check at $NOW"
   ```

2. **Find last Sanjaya log**:
   ```bash
   LAST_SANJAYA=$(ls -t ~/projects/observer-test/logs/sanjaya/*.log 2>/dev/null | head -1)
   if [ -n "$LAST_SANJAYA" ]; then
     SANJAYA_MOD=$(date -u -r "$LAST_SANJAYA" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
       || stat -c "%y" "$LAST_SANJAYA" 2>/dev/null | cut -d' ' -f1,2 | tr ' ' 'T')
   else
     SANJAYA_MOD="never"
   fi
   echo "Sanjaya last log: $SANJAYA_MOD"
   ```

3. **Find last Sahadeva log**:
   ```bash
   LAST_SAHADEVA=$(ls -t ~/projects/observer-test/logs/sahadeva/*.log 2>/dev/null | head -1)
   if [ -n "$LAST_SAHADEVA" ]; then
     SAHADEVA_MOD=$(date -u -r "$LAST_SAHADEVA" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
       || stat -c "%y" "$LAST_SAHADEVA" 2>/dev/null | cut -d' ' -f1,2 | tr ' ' 'T')
   else
     SAHADEVA_MOD="never"
   fi
   echo "Sahadeva last log: $SAHADEVA_MOD"
   ```

4. **Check for recent alert files**:
   ```bash
   ALERTS=$(find ~/projects/observer-test/logs/ -name "alert-*.txt" -mtime -2 2>/dev/null | wc -l)
   echo "Recent alerts (48h): $ALERTS"
   ```

5. **Check Nakula lock state**:
   ```bash
   LOCKS=$(ls ~/projects/observer-test/.claude/agents/nakula/locks/*.lock 2>/dev/null | wc -l)
   echo "Active Nakula locks: $LOCKS"
   ```

6. **Ensure bridge directory exists**:
   ```bash
   mkdir -p ~/projects/observer-test/logs/hermes-bridge/
   ```

7. **Write health.json** — use the gathered values to write a JSON status file:

   Write the following to `~/projects/observer-test/logs/hermes-bridge/health.json`:
   ```json
   {
     "checked_at": "<NOW>",
     "hermes_version": "parallel",
     "agents": {
       "sanjaya": {
         "last_log": "<SANJAYA_MOD>",
         "status": "<ok|overdue|missing>"
       },
       "sahadeva": {
         "last_log": "<SAHADEVA_MOD>",
         "status": "<ok|overdue|missing>"
       }
     },
     "alerts_48h": <ALERTS>,
     "nakula_locks": <LOCKS>
   }
   ```
   
   Set `status` to:
   - `ok` — last log within expected window
   - `overdue` — last log exists but older than max gap
   - `missing` — no logs found at all

8. **Report summary** — one short sentence: "Ecosystem healthy as of [time]" or "Sanjaya overdue — last ran [time], expected within 26h".

## Pitfalls

- The `date -r` flag works on macOS/Linux but may differ on Git Bash on Windows. Use the fallback `stat -c` form if `-r` fails.
- The `sanjaya/` and `sahadeva/` log directories only exist after the observer-ecosystem has been deployed and the agents have run at least once.
- Do not overwrite `health.json` if you cannot determine freshness (e.g., bash errors) — leave the previous file in place and append a `"check_error"` field instead.

## Verification

After running, confirm:
```bash
cat ~/projects/observer-test/logs/hermes-bridge/health.json
```
The file should exist and have a `checked_at` timestamp matching the current run.
