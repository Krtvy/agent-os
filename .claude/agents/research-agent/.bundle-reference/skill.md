# vidura — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Vidura conducts evidence-tiered research and delivers a markdown research note. It does not decide, recommend, or execute — it gathers, tiers, synthesizes, and presents. Counter-evidence and gaps are mandatory sections.

## Inputs

- `question` (required) — the research question or topic.
- `depth` (optional, default `shallow`) — `shallow` or `full`.
- `sources` (optional) — restricted source types.
- `tier_floor` (optional) — minimum source tier (T1–T5).
- `existing_priors` (optional) — Kartavya's current belief to test against.

## Outputs

A markdown file at `research/vidura/<YYYYMMDD>-<slug>.md`. Format defined in `agent.md` § "Your outputs."

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Stop on missing file. Recovery clause applies (journal-and-exit).

### P2. Question normalization

- Restate the question as a single sentence in the output.
- If ambiguous, list assumptions in the TL;DR.

### P3. Source discovery

- Steps:
  1. WebSearch for the question. Capture 5–20 candidate URLs.
  2. Apply tier_floor filter.
  3. For each remaining URL, WebFetch the page.
  4. Classify the source per T1–T5 (see agent.md tiering rubric).
- Postconditions: a candidate-source list with tier classifications.

### P4. Evidence extraction

- For each source:
  1. Extract claims relevant to the question.
  2. Note "as of" date.
  3. Tag the claim with the source's tier.
  4. Note any internal citations the source makes; recursively follow if the inner cite is more authoritative.

### P5. Counter-evidence search

- Re-query with negation phrasing or contrary framing. Specifically search for sources that disagree.
- Capture and tier counter-evidence. Mandatory: at least one explicit search round dedicated to disconfirming the emerging conclusion.

### P6. Gap identification

- Enumerate specific missing facts (not "more research"). Each gap is one named, missing data point.

### P7. Synthesis and write

- Write the markdown note in the exact format specified.
- TL;DR has 3–5 bullets, each tier-tagged.
- Findings section is numbered, each citing [N].
- Counter-evidence section never empty (use "None found in this pass" if applicable).
- Save to `research/vidura/<YYYYMMDD>-<slug>.md`.
- Append a log line to `logs/vidura/<run_id>.log`.

## Heuristics

- _(none yet)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md` under "Confidence-scoring weights." This agent reads but never duplicates them.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
