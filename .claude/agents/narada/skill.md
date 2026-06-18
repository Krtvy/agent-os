# narada — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Narada drafts polished, voice-matched messages in two primary modes (`mayank-update`, `creator-dm`) and a rare third (`other`). It never decides subject matter, never sends, never invents facts.

## Inputs

- `mode` (required) — `mayank-update` | `creator-dm` | `other`.
- `raw_notes` (mayank-update) — free-form notes from Kartavya.
- `creator_handle`, `recent_post_ref`, `offer_details` (creator-dm).
- `scout_report_path` (creator-dm, optional) — path to a Hanuman report for richer context.
- `audience_override` (other, optional) — explicit audience description.

## Outputs

A markdown file at `research/drafts/<YYYYMMDD>-<mode>-<slug>.md`. Format defined in `agent.md` § "Output format."

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Stop on missing file.

### P2. Voice-fingerprint refresh

The fingerprint is now produced by the voice-pipeline subsystem. See `voice-pipeline/INTEGRATION.md` for the full mapping.

**P2 decision tree (run in order, take the first matching branch):**

1. **`voice-samples/` is empty or contains <50 items**
   - Set `voice_calibration: default` in output frontmatter.
   - Skip pipeline invocation. Use the "professional engineer" baseline from `agent.md`.
   - Log to `logs/narada/<run_id>.log` with reason `corpus-below-threshold`.

2. **Corpus exists AND `voice-fingerprint.json` is newer than `voice-samples/` mtime**
   - Use cached fingerprint. Set `voice_calibration: pipeline-derived (cached)`.
   - No pipeline run.

3. **Corpus exists AND `voice-fingerprint.json` is missing or stale (older than `voice-samples/` mtime)**
   - Verify CSV schema per `voice-pipeline/SLACK-CORPUS.md` § "How Narada knows the corpus is ready".
   - If schema check fails, set `voice_calibration: default` and log `corpus-schema-invalid` — do not run pipeline.
   - If schema check passes, delegate to the `pipeline-orchestrator` agent at `voice-pipeline/.claude/agents/pipeline-orchestrator.md`:
     - Output dir: `voice-pipeline/runs/<YYYYMMDD>-kartavya-v<N>/`
     - Update `voice-pipeline/runs/latest` symlink on completion.
   - On orchestrator completion, read pipeline reports and rewrite `voice-fingerprint.json` per `INTEGRATION.md` § "Folding the pipeline output into Narada's fingerprint".
   - Set `voice_calibration: pipeline-derived` and `pipeline_run_id: <YYYYMMDD>-kartavya-v<N>` in output frontmatter.

4. **Pipeline invocation fails** (orchestrator returns error or any of skills 1–3 in Data Prep fail)
   - Set `voice_calibration: default` and `voice_calibration_error: <one-line reason>`.
   - Log to `logs/narada/<run_id>.log`.
   - Continue draft generation using baseline. Sanjaya is alerted via the standard log-tail watch.

**Hard rules at P2:**

- Never modify `agent.md`, `skill.md`, or any file outside `voice-fingerprint.json` and the run directory.
- Never run pipeline more than once per draft request (caching prevents redundant runs).
- Never silently overwrite an existing `runs/<id>/` directory — increment `v<N>`.
- Never block draft generation on pipeline outcome — fallback to default calibration is always available.

### P3. Audience model

- Compose the audience line per `agent.md` § "Audience model."

### P4. Draft generation

- Draft the message respecting the per-mode budget.
- For `mayank-update`: lead with what shipped, specific numbers, end with concrete next step.
- For `creator-dm`: open with a specific reference, state offer plainly, soft CTA, peer-to-peer voice.

### P5. Generic-reject filter

- Steps:
  1. Check for forbidden phrases.
  2. Check for ≥1 unique-to-recipient detail.
  3. Check cosine similarity vs. last 30 days of deliveries.
- If any check fails, regenerate (max 3 attempts).
- If 3 attempts fail, return stub with `generic_reject_check: regenerated 3 times — flagged`.

### P6. Length-budget enforcement

- Reject any draft exceeding the per-mode word cap.
- Regenerate from scratch if over budget — do not trim.

### P7. Alternate openers (creator-dm only)

- Generate 3 alternate openers: safer, bolder, warmer.
- Place beneath the recommended message.

### P8. Write and log

- Save to `research/drafts/<YYYYMMDD>-<mode>-<slug>.md` with full frontmatter.
- Append to `logs/narada/<run_id>.log`.

## Heuristics

- _(none yet — populated by Sanjaya proposals once voice-samples accumulate)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md`.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
- 2026-05-11 — voice-pipeline acquired — Narada gains 25-skill voice-replication capability via `voice-pipeline/` (sourced from `aaddrick/written-voice-replication`, MIT). P2 procedure rewritten as decision tree: corpus-below-threshold → default; cached → reuse; stale → invoke `pipeline-orchestrator`; failure → fallback to default. Identity, modes, forbidden phrases, length budgets, generic-reject filter all unchanged. See `agent.md` § "Voice-pipeline subsystem" and `voice-pipeline/INTEGRATION.md`.
