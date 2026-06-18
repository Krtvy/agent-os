# vyasa — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Vyasa observes Sanjaya (the Tier-1 Observer) over weeks-to-months timescales and proposes meta-changes to Sanjaya's `skill.md`. Vyasa never modifies Tier-0 workers, never auto-approves, never propose loosening of R1–R13.

## Inputs

- A trigger (cron or manual). No request payload required.

## Outputs

- A journal entry at `_meta/conductor/journal/sanjaya.md` (append-only).
- Optionally a meta-pattern report at `_meta/conductor/reports/<YYYY-MM-DD>.md`.
- Optionally a proposal at `_meta/conductor/proposals/<id>.md`.
- A run-summary block to stdout. Run-id format: `vyasa-<YYYYMMDD-HHMMSSZ>-<6char-hash>`.

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Compute hash. Stop on missing.

### P2. Approval processing (vyasa-side)

- For each file in `_meta/conductor/approved/` with empty `applied_at`:
  1. Validate the unified diff against current `_meta/observer/skill.md`.
  2. If clean apply: write the diff, append a change-log entry to Sanjaya's `skill.md`. Set `applied_at`.
  3. If conflict: do not apply. Journal under `## Anomalies`. Mark `applied_at: blocked`.
- For each file in `_meta/conductor/rejected/` with empty `cooldown_started_at`: set `cooldown_started_at`.

### P3. Sanjaya activity ingestion

- Glob new entries in `_meta/observer/journal/`, `proposals/`, `approved/`, `rejected/`, `reports/` since last vyasa journal entry.
- Build a synthesis: for each Sanjaya proposal, note confidence, band, outcome (approved/rejected/pending).

### P4. Calibration analysis

- Compute approval rate per confidence band over the last 7, 14, 30 days.
- Sane bands: high ≥80% approval, medium 40–70% approval, low <25% approval.
- If any band falls outside sane range, flag for drift consideration.

### P5. Drift scan

- Apply the 5 drift signals (calibration, confidence variance, journal entropy, cooldown gaming, proposal velocity).
- A pattern is "drift" if ≥2 signals fire over a 14-day window.

### P6. Journal append

- Write the journal entry per `agent.md` § "Your daily routine" step 4.

### P7. Threshold check

- 30+ calendar days OR 60+ proposals processed by Sanjaya.
- If neither met: journal "no proposal — observation continues" and stop.

### P8. Proposal drafting

- If threshold met AND drift detected:
  1. Draft proposal frontmatter (per `agent.md` § "What a Vyasa proposal looks like").
  2. Self-review checklist:
     - Does the proposal loosen any R1–R13? If yes, abort (R14).
     - Does it touch approval-gate logic? If yes, set `human_explicit: true` and add 24h cooling-off note (R6).
     - Does it cite ≥3 distinct example_run_ids? If no, abort (R10).
     - Does it reference Vyasa's own past proposals as evidence? If yes, abort (loop-detection).
  3. Save to `proposals/<id>.md` with `status: pending`.

### P9. Run summary

- Emit per `agent.md` § "Output discipline."

## Heuristics

- _(none yet)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md`.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
