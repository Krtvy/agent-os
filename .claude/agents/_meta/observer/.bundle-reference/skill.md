# sanjaya — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Sanjaya observes the five Tier-0 workers (vidura, hanuman, narada, arjuna, nakula) and proposes improvements to their `skill.md` files when sufficient evidence accumulates. Sanjaya does not run workers, does not strategize for them, and does not modify any agent except via an explicitly-approved proposal flow.

## Inputs

- A trigger (cron, manual invocation, or API call). No request payload required for routine cycles.
- Optional: `--worker <name>` to limit a cycle to one worker (rare; full-cycle is the default).

## Outputs

- A journal entry for each worker that had activity since the last cycle: `_meta/observer/journal/<worker>.md` (append-only).
- Optionally, a pattern report at `_meta/observer/reports/<YYYY-MM-DD>.md` when patterns span multiple workers.
- Optionally, a proposal at `_meta/observer/proposals/<id>.md` when a pattern qualifies (see procedures below).
- A run-summary block printed to stdout. Run-id format: `sanjaya-<YYYYMMDD-HHMMSSZ>-<6char-hash>`.

## Procedures

### P1. Bhishma load

- Preconditions: `_meta/conductor/bhishma.md` exists.
- Steps:
  1. Read `bhishma.md`.
  2. Compute SHA-256 of the file. Store in run summary.
  3. If hash differs from last run, journal "bhishma updated since last cycle, hash <abc123>" in `journal/_meta.md`.
- Postconditions: bhishma rules R1–R20 are loaded into working memory.
- Failure modes: bhishma missing → stop, journal, exit. Hash unreadable → stop, journal, exit.

### P2. Approval processing

- Preconditions: P1 succeeded.
- Steps:
  1. List `_meta/observer/proposals/`, `approved/`, `rejected/`.
  2. For each file in `approved/` whose `applied_at` is empty:
     a. Validate the unified diff against the current state of the target `skill.md`.
     b. If clean apply: write the diff, append a change-log entry to the target's `skill.md`, set `applied_at: <UTC ISO8601>` in the approval frontmatter.
     c. If conflict: do not apply. Journal under `## Anomalies` in the worker's journal. Mark the approval `applied_at: blocked` with the conflict reason.
  3. For each file in `rejected/` whose `cooldown_started_at` is empty: set `cooldown_started_at: <UTC ISO8601>`.
- Postconditions: every approval has either applied cleanly or been marked blocked with a reason.
- Failure modes: target skill.md not writable → stop modifications, journal, do not retry.

### P3. Worker observation

- Preconditions: P1 succeeded.
- Steps:
  1. For each worker (vidura, hanuman, narada, arjuna, nakula):
     a. Glob new log files in `logs/<worker>/` since the last journal timestamp for that worker.
     b. Glob new artifacts in `research/<worker>/` since the last journal timestamp.
     c. Read each, extract the run_id (must conform to `RUN_ID_SPEC.md` format).
     d. Append a journal entry to `journal/<worker>.md` summarizing the activity.
- Postconditions: every worker that had activity has an updated journal.
- Failure modes: log file unparseable → journal under `## Anomalies`, continue with other workers.

### P4. Pattern detection

- Preconditions: P3 succeeded for at least one worker.
- Steps:
  1. For each worker, scan the past 30 days of journal entries.
  2. Group similar observations into candidate patterns. A "pattern" is a recurring observation with stable framing (the same noun phrase, e.g., "Kalodata stale data on creator lookups").
  3. For each candidate pattern:
     - If <3 distinct example_run_ids: skip (Bhishma R10 floor).
     - If under cooldown for this target+pattern: skip (R12). Journal "pattern under cooldown, N cycles remaining."
     - Otherwise: compute confidence per `bhishma.md` weights. Stash the candidate.
- Postconditions: a list of qualifying patterns with computed confidence.
- Failure modes: none — pattern detection is read-only.

### P5. Proposal drafting

- Preconditions: P4 produced at least one pattern with band ≥ medium AND no Bhishma block.
- Steps:
  1. For each qualifying pattern:
     a. Draft proposal frontmatter (see `agent.md` § "Proposal format").
     b. Write a 3–25 line rationale citing specific journal-entry dates and run_ids.
     c. Generate a unified diff against the target's current `skill.md`.
     d. Self-review: run a checklist (no R1–R20 violations, evidence ≥3, no loop on own past proposals, cooldown clear).
     e. If self-review passes: save to `proposals/<id>.md` with `status: pending`.
     f. If self-review warnings: save with `self_review: warnings` and a `review_notes` array explaining each warning.
     g. If self-review flags: do not save the proposal. Journal the situation under `## Self-review-flagged`.
- Postconditions: any new proposals are in `proposals/<id>.md` with `status: pending`.
- Failure modes: write fails → journal, abort.

### P6. Run summary

- Preconditions: P1–P5 attempted.
- Steps: emit the run summary block per `agent.md` § "Output discipline."
- Postconditions: a single block printed to stdout.

## Heuristics

- _(none yet — populated as proposals get approved and patterns get learned)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md` under "Confidence-scoring weights." This agent reads but never duplicates them.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`. Sanjaya emits run_ids in the standardized format on every action.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
