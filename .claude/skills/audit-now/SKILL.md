---
name: audit-now
description: Trigger Sahadeva's weekly audit immediately, without waiting for the Sunday cron firing. Useful for debugging the first cron run, for re-running after fixing a configuration gap, and for ad-hoc audits when something feels off. Invoke when the user types `/audit-now`.
---

# /audit-now — Manual Sahadeva trigger

## What this skill does

Fires the same Sahadeva audit cycle that the Sunday cron entry runs, but on demand. The audit produces a markdown report at `_meta/audit/reports/<YYYY-WW>.md` and (if criticals exist) appends to `_meta/audit/inbox.md`.

## Procedure

1. **Confirm intent.** Briefly tell the user: "Triggering Sahadeva — this runs the full P1-P11 audit cycle, takes a few minutes, and writes to `_meta/audit/reports/<YYYY-WW>.md`. Continuing."

2. **Pre-flight check.** Verify the runner exists and is executable:

   ```bash
   ls -l .claude/agents/_meta/audit/run_sahadeva.sh
   ```

   If missing or not executable, stop and tell the user. Don't try to create it from scratch — the runner is part of the Mahabharat ecosystem and is committed to git.

3. **Run the audit.** Invoke the runner from the project root:

   ```bash
   .claude/agents/_meta/audit/run_sahadeva.sh
   ```

   The runner manages its own lockfile (`_meta/audit/.run.lock`); if another Sahadeva is already running, the script exits 0 with a message and this skill should report that without retrying.

4. **Show what landed.** After the runner completes:
   - Compute the current ISO week: `date -u +%G-W%V` (e.g., `2026-W19`).
   - Read the report at `_meta/audit/reports/<YYYY-WW>.md` and surface the **summary verdict** (green / amber / red) plus the count of findings by severity.
   - If `_meta/audit/inbox.md` was appended to (mtime newer than the runner start time), tail the new lines.
   - If the run errored, tail the last 30 lines of `_meta/audit/run.log` so the user can see what happened.

5. **Report to the user.** Format:

   ```
   Sahadeva run: <completed | errored>
   ISO week:    <YYYY-WW>
   Verdict:     <green | amber | red>
   Critical:    <count>
   High:        <count>
   Medium:      <count>
   Report:      _meta/audit/reports/<YYYY-WW>.md
   Trace:       _meta/observer/traces/sahadeva/<run_id>.json
   ```

   Plus a one-paragraph "what to look at first" summary if any criticals or highs were found.

## When NOT to invoke this skill

- **During the Sunday cron window** (09:55-10:30 IST). The cron runner holds the lockfile; manual invocation will exit immediately. Wait for the scheduled run to complete and read its report instead.
- **If `lib/trace-writer.sh` is broken.** The runner will still complete but without a trace, which defeats half the audit's signal. Better to fix the trace pipeline first.
- **In rapid succession.** Sahadeva is designed for weekly cadence. Running it five times in an hour doesn't give five times the signal — it just creates noise in the report archive. Use only when there's a real reason (debugging, new constitutional change, configuration gap fix).

## Hard rules

- **This skill never modifies Sahadeva's spec, skill, or test set.** It only invokes the existing runner. If the runner needs changes, those changes go through the proper R23 proposal flow.
- **This skill does not bypass the lockfile.** If Sahadeva is already running, this skill reports that and exits.
- **This skill does not delete reports.** Old reports stay. The append-only discipline mirrors Bhishma R5 for the audit archive.

## Notes for the assistant invoking this

- The runner takes minutes (Claude session inside), not seconds. Be patient with the Bash call.
- The runner exits 0 even if some findings are critical — exit 0 means "Sahadeva ran"; the report contents tell you what it found. Distinguish "runner error" (non-zero exit) from "audit found problems" (exit 0, report says red).
- If this is being invoked because the user wants to test the first cron firing early, mention that the next scheduled cron firing is Sunday 10:00 IST and the manual run is in addition to, not replacement for, the cron.

## Provenance

Skill added 2026-05-12 00:13 IST during the plugins-evaluation phase. Source: `_audit/2026-05-12_hooks-wired.md` watch-list (no specific item, but Kartavya picked "audit-now" via AskUserQuestion as the one defensible plugin add-now). This skill is **not** part of the proposal/approval chain — it's tooling, not constitution. Removal: `rm -r .claude/skills/audit-now/`.
