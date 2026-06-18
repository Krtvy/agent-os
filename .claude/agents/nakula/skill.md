# nakula — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Nakula owns scheduled recurring jobs defined in `jobs.yml`. It runs each due job, captures stdout/stderr to per-job logs, emits a heartbeat regardless of outcome, alerts on failure, and rotates logs.

## Inputs

- `jobs.yml` (required) — the schedule definition file.

## Outputs

- Per-job logs at `logs/nakula/<job>/<run_id>.log`.
- A single `logs/heartbeat.json` (single-writer; updated after every run).
- A weekly summary heartbeat (Sunday 23:55 UTC).
- Optional alert messages per `on_failure` config.

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Stop on missing file.

### P2. Schema validation

- Read `jobs.yml`. Validate per `agent.md` § "jobs.yml schema validator."
- On schema error: heartbeat with `status: failure, skip_reason: jobs-yml-schema-error`, alert, exit.

### P3. Stale-lock cleanup

- For each lockfile in `.claude/agents/nakula/locks/`:
  - Read PID. If the PID is not alive (`kill -0 <pid>` fails), delete the lockfile and journal the cleanup.

### P4. Log rotation

- For each file in `logs/nakula/<job>/`:
  - If older than 24h and not gzipped: `gzip` it.
  - If `.gz` and older than 90d: delete.

### P5. Due-job determination

- For each job in `jobs.yml`:
  - Compute next-due time from schedule + last-run timestamp.
  - If due now (within 60s tolerance): mark for execution.

### P6. Per-job execution loop

- For each due job:
  1. Acquire lock at `locks/<job>.lock` (write PID).
  2. Run `upstream_freshness_check` if configured.
     - If upstream stale: heartbeat `skipped: upstream-stale`, release lock, continue.
  3. Execute command in subprocess with `timeout_minutes` cap.
  4. Capture stdout+stderr to `logs/nakula/<job>/<run_id>.log`.
  5. Compute `output_size_bytes`.
  6. Heartbeat: write to `logs/heartbeat.json`. Format defined in `agent.md`.
  7. If exit non-zero and `retry: false`: emit alert per `on_failure`.
  8. Release lock.

### P7. Weekly summary

- If current time is Sunday 23:55 UTC ± 5min:
  - Read this week's heartbeat history.
  - Compute `jobs_total`, `jobs_success`, `jobs_failure`, `jobs_skipped`, `uptime_pct`.
  - Append a weekly-summary heartbeat to `logs/heartbeat.json`.

### P8. Output

- Stdout: one line per job (running... / exit 0 / FAILED). Per `agent.md` output discipline.

## Heuristics

- _(none yet)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md`.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
