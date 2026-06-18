# Observer Self-Diagnostic Skills (additions)

These skills append to your existing Observer `skill.md`. They catch Observer being wrong from *inside* Observer — confidence scores on every proposal, evidence-quality gates before drafting, cross-heuristic checks on patterns, baseline-drift detection, and a final self-review pass before any file is written.

**Philosophy:** No second LLM grades Observer. Observer grades itself. The output is a confidence score and a structured self-review block embedded in every proposal's frontmatter — so when you read a proposal, you see immediately whether Observer thinks it's solid or shaky.

---

## Where these slot into the existing cycle

```
agent_inventory  →  log_ingest  →  pattern_extraction
                                            │
                                            ▼
                                    heuristic_cross_check     ← NEW
                                            │
                                            ▼
                                    baseline_drift_check       ← NEW
                                            │
                                            ▼
              drift_detection (adaptation) OR bootstrap_skill_drafting
                                            │
                                            ▼
                                    evidence_quality_check     ← NEW (gate)
                                            │
                                            ▼
                                    confidence_scoring         ← NEW
                                            │
                                            ▼
                                    proposal_self_review       ← NEW (gate)
                                            │
                                            ▼
                              proposal_drafting (writes file with new frontmatter fields)
                                            │
                                            ▼
                              approval_polling  →  journal_calibration
```

The two NEW gates (`evidence_quality_check`, `proposal_self_review`) can BLOCK a proposal from being written. When they block, Observer logs a "watch list" entry in the journal instead of dropping a file in `proposals/`. The user sees what Observer *almost* proposed but didn't, and why.

---

## Skill: `heuristic_cross_check`
**Purpose:** Re-run `pattern_extraction` with a second grouping heuristic on the same data. If two heuristics disagree about whether a pattern is real, the pattern is fragile.

**Inputs:** Output of `pattern_extraction` (primary heuristic), the same run set
**Outputs:** Per pattern: `{ pattern, primary_count, secondary_count, agreement: 0.0-1.0, fragile: bool }`

**How:**
- Primary heuristic = whatever your `pattern_extraction` does today (let's say n-grams of tool names)
- Secondary heuristic = a complementary view, e.g. cluster by intent string + first user message keywords, OR by error class + tool sequence
- For each pattern in the primary report, search the secondary report for the same example run IDs
- `agreement` = (run IDs both heuristics flag) / (run IDs primary flags). 1.0 = perfect agreement.
- `fragile = true` if `agreement < 0.6` AND `primary_count <= 4`. A frequent pattern surviving disagreement is still real; an infrequent one isn't.
- Fragile patterns get downweighted in `confidence_scoring`. They are NOT dropped outright — sometimes the fragile one is the right one.

**Output written to:** Cycle's working memory, used by `confidence_scoring`. Summarized in journal under `## Cross-check <date>`.

---

## Skill: `baseline_drift_check`
**Purpose:** Compare this cycle's pattern report to the last 3 cycles for the same target. Wild swings indicate something's broken upstream (log ingest missed files, target agent's behavior actually changed, time window misaligned).

**Inputs:** This cycle's `pattern_extraction` output, last 3 cycles' pattern reports from `journal/<agent>.md`
**Outputs:** `{ status: stable | shifting | volatile | first_observation, signals: [...] }`

**How:**
- For each pattern in this cycle's report, find it in each prior cycle's report
- Compute frequency-over-time series per pattern
- **stable** = all-pattern frequencies within ±30% of trailing average. Normal.
- **shifting** = ≥1 pattern moved 30-100%. Likely real behavior change in the target — proceed with caution.
- **volatile** = ≥1 pattern moved >100%, OR new patterns appeared that match prior-cycle patterns by name (suggests `pattern_extraction` is unstable). DO NOT propose anything new this cycle. Add a journal note and re-observe next cycle.
- **first_observation** = no prior cycles exist for this target. Skip the check, mark as such.
- Volatility blocks `proposal_drafting` for that target this cycle. The block is recorded in the journal so the human sees Observer chose to wait.

**Output written to:** `journal/<agent>.md` under `## Baseline check <date>`

---

## Skill: `evidence_quality_check`
**Purpose:** Before drafting any proposal, validate the evidence backing it is real and sufficient. This is a hard gate — failed evidence checks block the proposal.

**Inputs:** A pattern selected for proposal (from `drift_detection` or `bootstrap_skill_drafting` output)
**Outputs:** `{ verdict: pass | warn | block, signals: [...], evidence_summary: {...} }`

**How:**
Run these checks in order. Any **block** signal blocks the proposal entirely; **warn** signals are recorded in the proposal's frontmatter for the human.

- **Run IDs exist:** Every cited `example_run_id` must resolve to an actual log file or transcript. Missing → `block`.
- **Run count threshold:** ≥3 run IDs cited. Fewer → `block` for adaptation, `block` always for bootstrap (which already requires ≥3).
- **Distinct days:** Cited runs span ≥2 distinct days. All in one day → `warn` (might be a single-batch artifact, not recurrence).
- **Distinct sessions:** Cited runs come from ≥2 distinct sessions/conversations (if your log structure has a session ID). One session → `warn`.
- **Recency:** At least one cited run within the last 7 days. All older → `warn` (pattern might be stale).
- **Heuristic agreement:** If `heuristic_cross_check` flagged this pattern as `fragile`, → `warn`.
- **Volatility check:** If `baseline_drift_check` returned `volatile` for this target, → `block`.
- **Cooldown check:** A proposal targeting this same skill name was rejected in the last 5 cycles → `block` (respect calibration).

**Block paths:** When blocked, write a journal entry under `## Watch List <date>`:
```yaml
- pattern: <name>
  blocked_by: [evidence_quality_check]
  reasons: [run_count_too_low, runs_all_same_day]
  example_run_ids: [...]
  reconsider_after: <date or condition>
```

The human can scan the watch list to see what Observer is keeping an eye on but not yet proposing.

---

## Skill: `confidence_scoring`
**Purpose:** Compute a numeric confidence score for every proposal. Embedded in proposal frontmatter so the human can sort/filter by confidence.

**Inputs:** Pattern, evidence summary from `evidence_quality_check`, cross-check result, baseline drift result, mode (bootstrap | adaptation)
**Outputs:** `{ score: 0-100, band: high | medium | low, contributors: [{factor, delta}] }`

**How:**
Start at 50. Apply each modifier with the listed delta. Clamp final score to 0-100.

| Factor | Condition | Delta |
|---|---|---|
| Pattern repetition | count ≥ 5 | +15 |
| Pattern repetition | count 3-4 | +5 |
| Time spread | ≥3 distinct days | +10 |
| Time spread | ≥7 distinct days | +15 (replaces above) |
| Heuristic agreement | cross-check `agreement >= 0.8` | +10 |
| Heuristic agreement | cross-check `fragile = true` | -15 |
| Mode | adaptation (vs. bootstrap) | +10 |
| Baseline | `baseline_drift_check` returned `stable` | +5 |
| Baseline | `baseline_drift_check` returned `shifting` | -10 |
| Cooldown | similar proposal rejected in last 5 cycles | -20 |
| Recency | most recent cited run within 24h | +5 |
| Recency | all cited runs older than 14 days | -10 |
| Sparse evidence | run count < 5 | -10 |
| Self-review | warnings raised in `proposal_self_review` | -10 per warning (capped at -25) |

**Bands:**
- `high` ≥ 70 — propose normally, frontmatter `confidence: <n>`
- `medium` 40-69 — propose but flag, frontmatter `confidence: <n>, low_confidence: true`
- `low` < 40 — DO NOT propose. Add to watch list. Reconsider next cycle.

The `contributors` array shows which factors pushed the score up or down — embed it in the proposal so the human sees *why* Observer assigned a given confidence.

**Output written to:** Proposal frontmatter (see new format below)

---

## Skill: `proposal_self_review`
**Purpose:** Before writing the proposal file, Observer reviews its own draft. Final gate — catches incoherence between rationale and diff.

**Inputs:** Drafted proposal content (rationale + diff + frontmatter), the cited pattern
**Outputs:** `{ verdict: passed | warnings | flags, notes: [...] }`

**How:**
- **Diff-rationale alignment:** Tokenize the rationale and the diff. At least one significant noun/verb from the cited pattern must appear in both. Missing → `flags` (rationale doesn't match diff).
- **Diff-target alignment:** The diff modifies a path that includes the proposal's `target` field. Mismatch → `flags`.
- **Rationale length:** Rationale is between 3 and 25 lines. Outside → `warnings`.
- **Run ID citations:** Every claim in the rationale that mentions evidence cites at least one run ID. Missing citations → `warnings`.
- **No self-meta references:** Rationale and diff do not reference `_meta/*` paths. If they do → `flags` (caught by self-modification rules in your existing setup; this is a redundant safety net).
- **Skill-name uniqueness (bootstrap only):** Drafted skill names don't collide with existing skills in the target's `skill.md`. Collision → `flags`.

**Verdict handling:**
- `passed` → write proposal, `self_review: passed` in frontmatter
- `warnings` → write proposal, `self_review: warnings` + notes in frontmatter, confidence score takes the hit
- `flags` → DO NOT write proposal. Add to watch list with `blocked_by: [proposal_self_review]` and the specific flag reasons. Next cycle, re-derive the proposal cleanly; do not auto-retry the flagged version.

---

## Updates to existing skills

Two existing skills need small tweaks to consume the new outputs:

### `proposal_drafting` (existing)

**Updated frontmatter format** — add the new fields:

```yaml
id: 20260509-research-add-search-flow
target: research
mode: adaptation
status: pending

# NEW fields from self-diagnostic skills:
confidence: 78
band: high
low_confidence: false
self_review: passed
review_notes: []
heuristic_agreement: 0.85
evidence_count: 7
days_spanned: 4
sessions_spanned: 5
contributors:
  - { factor: pattern_repetition, delta: +15 }
  - { factor: time_spread_3d, delta: +10 }
  - { factor: heuristic_agreement, delta: +10 }
  - { factor: mode_adaptation, delta: +10 }
  - { factor: baseline_stable, delta: +5 }
  - { factor: recency_recent, delta: +5 }
  - { factor: sparse_evidence, delta: -10 }
  # base: 50, total: +28, clamped: 78
```

The body of the proposal is unchanged. Just frontmatter additions.

### `threshold_check` (existing)

**Add a hard floor:** never trigger a proposal if `confidence_scoring` would output `band: low`. Threshold passing alone is not enough — confidence has to clear the floor too.

This means: even when `days_observed >= 10` and `runs_observed >= 20`, if the resulting proposal's confidence is below 40, Observer falls back to the watch list instead.

---

## What you'll see when you read a proposal now

Compared to today, every proposal in `proposals/` will tell you up front:

- **How confident Observer is** (numeric score + band)
- **Why** (the contributors array)
- **What it self-reviewed** (passed / warnings / flags + notes)
- **How well-evidenced** (run count, days spanned, sessions spanned)
- **Whether the pattern is fragile** (heuristic agreement number)

Skim the frontmatter, decide whether to approve based on the score + notes, and only dig into the diff when something looks borderline. That's the value: from "I have to read every proposal carefully" to "high-confidence ones I approve quickly, low-confidence ones I read carefully or reject."

## What you'll see in the journal

Two new sections show up in `journal/<agent>.md`:

- `## Cross-check <date>` — patterns and their heuristic-agreement scores
- `## Baseline check <date>` — stability status for this cycle  
- `## Watch List <date>` — patterns Observer noticed but chose NOT to propose, with reasons

The Watch List is the hidden value. It's where Observer admits "I see something here but the evidence is too thin." Over time, you can scan it and decide if any items are actually worth promoting to a proposal manually.

---

## Implementation notes

- All five skills can be implemented with the tools Observer already has (Glob, Read, Bash, Grep) — no new tooling
- The two gate skills (`evidence_quality_check`, `proposal_self_review`) MUST be able to block proposal_drafting from writing. In your runtime, that probably means proposal_drafting reads their outputs first and exits early on `block`/`flags`.
- Cross-check's "second heuristic" should be intentionally different from your primary one. If both heuristics are the same shape, you're not actually checking anything.
- Confidence weights are starting points. After 2-4 weeks of real proposals, look at which low-confidence proposals you approved anyway and which high-confidence ones you rejected — recalibrate the weights from that data.
- The watch list is append-only per cycle. Do not delete entries; let it grow. It's the diagnostic record of what Observer saw and didn't act on.

## What to add to Observer's frontmatter

```yaml
---
name: observer-skills
version: 1.1.0   # bump from 1.0.0
owner: observer
last_reviewed: 2026-05-09
self_diagnostics: enabled
confidence_floor: 40   # band below which proposals are not written
volatility_block: enabled
---
```
