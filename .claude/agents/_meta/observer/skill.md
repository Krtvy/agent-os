---
name: observer-skills
version: 1.1.0
owner: observer
last_reviewed: 2026-05-09
self_diagnostics: enabled
confidence_floor: 40
volatility_block: enabled
---

# Observer Skills

Skills the Observer agent uses to do its work. Each skill is named, has a clear purpose, inputs, outputs, and invocation notes.

---

## Skill: `agent_inventory`

**Purpose:** Discover all sibling agents and classify them.

**Inputs:** Path to `.claude/agents/`
**Outputs:** A list of `{ name, tier, has_skill_md, agent_md_path }` per agent.

**How:**

- `Glob(".claude/agents/**/agent.md")`
- Exclude any path containing `/_meta/`
- For each, check sibling `skill.md` existence
- Classify tier from path (worker vs `_meta/*`)

---

## Skill: `log_ingest`

**Purpose:** Read new transcripts, tool-call logs, and error logs for a target agent since the last journal update.

**Inputs:** Agent name, `last_updated` timestamp from journal frontmatter
**Outputs:** Structured list of runs `[{ run_id, started_at, transcript_excerpt, tools_used, errors }]`

**How:**

- Resolve paths from `config.yml.input_sources` (no `{agent}` substitution — sources are session-scoped JSONL globs, not per-agent dirs). Each source is a **list of globs**; iterate every entry.
- For each JSONL file newer than `last_updated`:
  - Each line is a JSON object representing one event in the session
  - Filter to sessions whose **first** `type: agent-setting` event has `agentSetting == <target>` — that's the session-to-agent binding
  - `run_id` = filename stem (the session UUID)
  - `started_at` = file mtime (or first event timestamp if present)
  - `transcript_excerpt` = concatenate `text` blocks from `user` events (the prompt) + final `assistant` event
  - `tools_used` = ordered list of `name` from every event where `message.content[].type == "tool_use"`
  - `errors` = events where `message.content[].type == "tool_result"` AND `is_error == true`, plus any top-level `error` events
- Fall back to `git log --since=<last_updated> -- .claude/agents/<agent>/` if no JSONL matches
- If nothing found, return empty list and note "no_data" in the journal entry

---

## Skill: `git_diff_observer`

**Purpose:** Inspect changes to a target agent's own files over time (catches when a worker self-modifies).

**Inputs:** Agent name, time window
**Outputs:** Summary of file paths changed, diff line counts, commit messages

**How:**

- `Bash: git log --since=<start> --until=<end> --oneline -- .claude/agents/<agent>/`
- `Bash: git diff <since>..HEAD -- .claude/agents/<agent>/skill.md` (when present)

---

## Skill: `pattern_extraction`

**Purpose:** Identify recurring task types, common tool sequences, and failure patterns across observed runs.

**Inputs:** List of runs from `log_ingest`
**Outputs:** Frequency-ranked list of `{ pattern, count, example_run_ids[] }`

**How:**

- Group transcripts by intent (use the user message + agent's first plan step as a signal)
- Cluster tool-call sequences (n-grams of tool names) — `tools_used` from `log_ingest` is already an ordered list extracted from `tool_use` blocks in the JSONL
- Tally error categories by exception class or first-line of stderr (errors are surfaced as `is_error: true` tool results, plus any top-level `error` events)
- Output-format patterns are also visible: scan the final `assistant` text for recurring tokens like `[T1]`/`[T2]` (citation tier tags), `*Synthesis:*`, `**Sources:**`, code-fence languages, table headers

---

## Skill: `mast_classification`

**Purpose:** Classify observed failure patterns against the MAST taxonomy from Cemri et al. NeurIPS 2025 (arXiv:2503.13657) — the largest published empirical taxonomy of multi-agent LLM failure modes (1,600+ traces, 7 frameworks, Cohen κ = 0.88). Provides a stable diagnostic vocabulary so trends can be aggregated across agents and weeks rather than re-described in fresh prose each time.

**Inputs:** Output of `pattern_extraction` (failure-shaped patterns), plus the agent's `agent.md` description and `skill.md` procedures (for spec-violation classification).

**Outputs:** A list of `{ mast_code, category, observed_count, example_run_ids[] }` rows. Also writes `mast_codes: [FM-x.y, ...]` into the journal entry frontmatter for the day. Empty list `mast_codes: []` is the correct value on days with no observed failure mode.

**The taxonomy (3 categories, 14 modes — names per Cemri et al. summary; verify exact code spelling against the paper on first use):**

### Category 1 — Specification and system design (≈42% of multi-agent failures)

| Code   | Mode                              | Trigger pattern in journals                             |
| ------ | --------------------------------- | ------------------------------------------------------- |
| FM-1.1 | Disobey task specification        | Agent did the task its way despite explicit instruction |
| FM-1.2 | Disobey role specification        | Agent stepped outside its declared role/scope           |
| FM-1.3 | Step repetition                   | Same step run multiple times without progress           |
| FM-1.4 | Loss of conversation history      | Agent forgot earlier turns mid-task                     |
| FM-1.5 | Unaware of termination conditions | Agent didn't know when to stop                          |

### Category 2 — Inter-agent misalignment (≈37%)

| Code   | Mode                          | Trigger pattern in journals                    |
| ------ | ----------------------------- | ---------------------------------------------- |
| FM-2.1 | Conversation reset            | Context dropped between agents                 |
| FM-2.2 | Fail to ask for clarification | Agent guessed at ambiguous input               |
| FM-2.3 | Task derailment               | Agent slid into a different task               |
| FM-2.4 | Information withholding       | Agent had data, didn't pass it on              |
| FM-2.5 | Ignored other agent's input   | Upstream output silently dropped               |
| FM-2.6 | Reasoning-action mismatch     | Agent's stated plan and actual action diverged |

### Category 3 — Task verification and termination (≈21%)

| Code   | Mode                          | Trigger pattern in journals      |
| ------ | ----------------------------- | -------------------------------- |
| FM-3.1 | Premature termination         | Agent ended before task complete |
| FM-3.2 | No or incomplete verification | No check on the produced output  |
| FM-3.3 | Incorrect verification        | Check ran but verdict was wrong  |

**How to classify:**

1. From `pattern_extraction`, isolate the patterns that look like failures (errors, repeated retries, dropped instructions, abandoned sub-tasks).
2. For each, walk down the table: which mode most closely matches the observed behaviour? Prefer the most specific code. A single observation can carry ≥1 code.
3. If the pattern fits none of the 14 — log `mast_codes: [FM-unknown]` plus a free-text `unknown_pattern_description` line. After 3 unknowns of the same shape, escalate to Kartavya as a candidate addition to the local extension table.
4. Write the result into both:
   - The daily journal entry's `mast_codes:` field, AND
   - Any proposal that cites the pattern as evidence (in proposal frontmatter as `mast_codes: [...]`).

**How Sahadeva consumes this:**

- Weekly aggregation: per-agent MAST-code frequency, week-over-week trend.
- Alerts on rising categories — e.g., if FM-2.5 (ignored other agent's input) climbs across multiple workers, that's a coordination-layer bug, not a per-agent bug.
- Alerts on `FM-unknown` accumulation — that's evidence the taxonomy needs local extension or that the agent is doing something genuinely novel.

**Hard rule.** Do not invent new codes. Use only the 14 published modes or `FM-unknown`. The taxonomy's value is its stability — local invention defeats cross-week aggregation.

**Citation discipline.** First time a code appears in a proposal, link the source: `MAST taxonomy [Cemri et al. 2025, T1] — arXiv:2503.13657`. Subsequent uses can omit. (Matches Bhishma's evidence-trail expectation.)

---

## Skill: `drift_detection`

**Purpose:** (Adaptation mode only) Compare a target's `skill.md` against observed behavior. Surface three drift types.

**Inputs:** Target's current `skill.md`, output of `pattern_extraction`
**Outputs:**

- `undocumented`: behaviors observed ≥3 times but absent from `skill.md`
- `unused`: skills described in `skill.md` but never invoked in the observation window
- `failures_missing_skill`: error patterns repeating ≥3 times that look like a missing skill

**How:**

- Parse `skill.md` to a list of named skills
- Cross-reference against observed patterns
- Flag mismatches with supporting evidence (run IDs)

---

## Skill: `bootstrap_skill_drafting`

**Purpose:** (Bootstrap mode only) From accumulated observations, draft a first `skill.md` for an agent that has none.

**Inputs:** Output of `pattern_extraction`
**Outputs:** A `skill.md` draft string ready to embed in a proposal diff

**How:**

- Take patterns with count ≥3
- Convert each to a skill definition: `name`, `purpose`, `inputs`, `outputs`, `how`
- Order by frequency (most-used first)
- Emit YAML frontmatter + skill sections in the project's standard format

---

## Skill: `proposal_drafting`

**Purpose:** Build a structured proposal file ready for human review.

**Inputs:** Mode, target agent, pattern report ID, drafted change (skill.md content or diff segments)
**Outputs:** Proposal markdown file content, ready to write to `proposals/<id>.md`

**How:**

- Generate a unified diff against the current `skill.md` (or against `/dev/null` for bootstrap)
- Compose YAML frontmatter in the following format:

```yaml
id: <YYYYMMDD>-<agent>-<short-slug>
target: <agent name>
mode: bootstrap | adaptation
status: pending
risk_tier: doc-only | behavioural | constitutional # see Bhishma R23; declared at draft time, audited by Sahadeva
mast_codes: [FM-1.1, ...] # see skill.md § mast_classification; the failure mode(s) this proposal addresses

# NEW fields from self-diagnostic skills:
confidence: <0-100>
band: high | medium | low
low_confidence: <true if band == medium, false otherwise>
self_review: passed | warnings | flags
review_notes: [...]
heuristic_agreement: <0.0-1.0>
evidence_count: <int>
days_spanned: <int>
sessions_spanned: <int>
contributors:
  - { factor: <name>, delta: <signed int> }
```

- Render rationale bullets, each citing a specific observation
- Render risk note (what could go wrong)
- ID format: `<YYYYMMDD>-<agent>-<short-slug>`

Confidence score, band, and contributors are computed by `confidence_scoring`. Self-review status and notes are computed by `proposal_self_review`. Both must run before this skill writes the file.

**Risk-tier classification (Bhishma R23).** Before writing the proposal file, classify the change against R23's three tiers and set `risk_tier:` in the frontmatter. Decision logic:

1. **Does the diff touch any of:** `tools:`, `write_scope`, `read_scope`, `upstream`, `downstream`, `model:`, the approval-gate logic, Bhishma rule references, or `bhishma.md` itself? → **`constitutional`**. Approval requires Kartavya + one-line rationale + Sahadeva endorsement + 24-hour cooling-off.
2. **Else, does the diff add, remove, or change a procedure / heuristic / threshold / safeguard?** → **`behavioural`**. Approval requires Kartavya + one-line rationale.
3. **Else, is the diff prose-only — explanatory text, typo fixes, heading reorganisation, link clarifications, no behavioural effect?** → **`doc-only`**. Auto-approves after 24-hour cooling-off if no human objection.

Edge cases:

- Adding a new `## Heuristics` paragraph that describes a NEW heuristic is `behavioural` (the heuristic itself is the change). Reorganising existing heuristic prose without changing the rules is `doc-only`.
- A proposal that changes one column of an existing table (e.g. tightens a threshold from 10→8) is `behavioural`, not `doc-only`.
- Renaming an internal section heading without changing content is `doc-only`. Renaming an agent's identity (`name:` field) is `constitutional`.
- When in doubt, classify upward (the stricter tier). Misclassification downward is a Bhishma violation per R23.

The classification reasoning is recorded in the proposal body under `## Risk-tier rationale` (one to three sentences).

---

## Skill: `approval_polling`

**Purpose:** On each run, find approved/rejected proposals and act.

**Inputs:** None (scans `proposals/`, `approved/`, `rejected/`)
**Outputs:** Per proposal: action taken (`applied`, `rejected_logged`, `noop`)

**How:**

- For each file in `approved/`: re-read it, validate diff still applies, apply via `Edit` or patch, update `status: applied` and `applied_at`, append calibration note
- For each file in `rejected/`: read the reason (if any in frontmatter), append calibration note, mark agent's "do not re-propose this" timer for 5 runs
- For each file still in `proposals/` with `status: approved` (alternative path): treat the same as `approved/`
- **R23 doc-only auto-approval path.** For each file in `proposals/` where `status: pending` AND `risk_tier: doc-only` AND `drafted_at` is ≥ 24 hours before now AND no `human_objection:` field has been set: move the file to `approved/` with `approved_by: auto + cooling-off elapsed` and `approved_at: <now>` in frontmatter, then apply as for any approved file. Behavioural and constitutional tiers never auto-approve regardless of age.
- **R23 constitutional check.** Before applying any file in `approved/` with `risk_tier: constitutional`: verify that frontmatter contains a `sahadeva_endorsement:` line referencing a real Sahadeva report. If absent, do NOT apply — append a journal entry noting `bhishma-blocked: R23 missing Sahadeva endorsement` and move the file back to `proposals/` with `status: pending`.

---

## Skill: `journal_calibration`

**Purpose:** After accept/reject outcomes, write a calibration note so future proposals improve.

**Inputs:** Proposal id, outcome, target agent, optional human note
**Outputs:** Appended `## Calibration` entry in `journal/<agent>.md`

**How:**

- Open the journal, find the `## Calibration` section (create if missing)
- Append a dated entry with: trigger (what we saw), outcome, lesson
- Keep entries concise — each ≤5 lines

---

## Skill: `threshold_check`

**Purpose:** Decide whether a target has accumulated enough observation to trigger a proposal.

**Inputs:** Mode, journal counters (`days_observed`, `runs_observed`), thresholds from `config.yml`
**Outputs:** `true` (proposal due) or `false` (keep observing)

**How:**

- Bootstrap: trigger if `days_observed >= 10` OR `runs_observed >= 20`
- Adaptation: trigger if `days_observed >= 18` OR `runs_observed >= 40`
- Honor per-agent overrides from `config.yml.overrides`
- **Confidence floor:** Even when day/run thresholds pass, never trigger a proposal if `confidence_scoring` would output `band: low` (score < 40). Fall back to the watch list instead.

---

## Skill: `heuristic_cross_check`

**Purpose:** Re-run `pattern_extraction` with a second grouping heuristic on the same data. If two heuristics disagree about whether a pattern is real, the pattern is fragile.

**Inputs:** Output of `pattern_extraction` (primary heuristic), the same run set
**Outputs:** Per pattern: `{ pattern, primary_count, secondary_count, agreement: 0.0-1.0, fragile: bool }`

**How:**

- Primary heuristic = whatever `pattern_extraction` does today (likely n-grams of tool names)
- Secondary heuristic = an intentionally different view (cluster by intent string + first user message keywords, OR by error class + tool sequence)
- For each pattern in the primary report, search the secondary report for the same example run IDs
- `agreement` = (run IDs both heuristics flag) / (run IDs primary flags). 1.0 = perfect agreement.
- `fragile = true` if `agreement < 0.6` AND `primary_count <= 4`
- Fragile patterns are downweighted by `confidence_scoring`, NOT dropped outright

**Output written to:** Cycle's working memory; summarized in journal under `## Cross-check <date>`

---

## Skill: `baseline_drift_check`

**Purpose:** Compare this cycle's pattern report to the last 3 cycles for the same target. Wild swings indicate something's broken upstream.

**Inputs:** This cycle's `pattern_extraction` output, last 3 cycles' pattern reports from `journal/<agent>.md`
**Outputs:** `{ status: stable | shifting | volatile | first_observation, signals: [...] }`

**How:**

- For each pattern in this cycle's report, find it in each prior cycle's report
- Compute frequency-over-time series per pattern
- **stable** = all-pattern frequencies within ±30% of trailing average
- **shifting** = ≥1 pattern moved 30-100% (likely real behavior change, proceed with caution)
- **volatile** = ≥1 pattern moved >100%, OR new patterns appeared that match prior-cycle pattern names. DO NOT propose anything new this cycle.
- **first_observation** = no prior cycles exist for this target. Skip the check, mark as such.
- Volatility blocks `proposal_drafting` for that target this cycle. Block is recorded in journal.

**Output written to:** `journal/<agent>.md` under `## Baseline check <date>`

---

## Skill: `evidence_quality_check`

**Purpose:** Hard gate before drafting any proposal. Validate evidence is real and sufficient.

**Inputs:** A pattern selected for proposal (from `drift_detection` or `bootstrap_skill_drafting`)
**Outputs:** `{ verdict: pass | warn | block, signals: [...], evidence_summary: {...} }`

**How:** Run these checks in order. Any **block** signal blocks the proposal entirely; **warn** signals are recorded in the proposal frontmatter for the human.

- **Run IDs exist:** Every cited `example_run_id` resolves to an actual log file. Missing → `block`
- **Run count threshold:** ≥3 run IDs cited. Fewer → `block`
- **Distinct days:** Cited runs span ≥2 distinct days. All in one day → `warn`
- **Distinct sessions:** Cited runs come from ≥2 distinct sessions. One session → `warn`
- **Recency:** ≥1 cited run within the last 7 days. All older → `warn`
- **Heuristic agreement:** If `heuristic_cross_check` flagged this pattern as `fragile` → `warn`
- **Volatility check:** If `baseline_drift_check` returned `volatile` for this target → `block`
- **Cooldown check:** A proposal targeting this same skill name was rejected in the last 5 cycles → `block`

**Block paths:** When blocked, write a journal entry under `## Watch List <date>`:

```yaml
- pattern: <name>
  blocked_by: [evidence_quality_check]
  reasons: [run_count_too_low, runs_all_same_day]
  example_run_ids: [...]
  reconsider_after: <date or condition>
```

---

## Skill: `confidence_scoring`

**Purpose:** Compute a numeric confidence score for every proposal. Embedded in proposal frontmatter so the human can sort/filter.

**Inputs:** Pattern, evidence summary, cross-check result, baseline drift result, mode (bootstrap | adaptation)
**Outputs:** `{ score: 0-100, band: high | medium | low, contributors: [{factor, delta}] }`

**How:** Start at 50. Apply each modifier with the listed delta. Clamp final score to 0-100.

| Factor              | Condition                                  | Delta                          |
| ------------------- | ------------------------------------------ | ------------------------------ |
| Pattern repetition  | count ≥ 5                                  | +15                            |
| Pattern repetition  | count 3-4                                  | +5                             |
| Time spread         | ≥3 distinct days                           | +10                            |
| Time spread         | ≥7 distinct days                           | +15 (replaces above)           |
| Heuristic agreement | cross-check `agreement >= 0.8`             | +10                            |
| Heuristic agreement | cross-check `fragile = true`               | -15                            |
| Mode                | adaptation (vs bootstrap)                  | +10                            |
| Baseline            | `baseline_drift_check` returned `stable`   | +5                             |
| Baseline            | `baseline_drift_check` returned `shifting` | -10                            |
| Cooldown            | similar proposal rejected in last 5 cycles | -20                            |
| Recency             | most recent cited run within 24h           | +5                             |
| Recency             | all cited runs older than 14 days          | -10                            |
| Sparse evidence     | run count < 5                              | -10                            |
| Self-review         | warnings raised in `proposal_self_review`  | -10 per warning, capped at -25 |

**Bands:**

- `high` ≥ 70 — propose normally
- `medium` 40-69 — propose, frontmatter `low_confidence: true`
- `low` < 40 — DO NOT propose, add to watch list, reconsider next cycle

The `contributors` array shows which factors moved the score; embed it in the proposal so the human sees _why_ the score is what it is.

**Output written to:** Proposal frontmatter (see Edit 3)

---

## Skill: `proposal_self_review`

**Purpose:** Final gate before writing the proposal file. Catches incoherence between rationale and diff.

**Inputs:** Drafted proposal content (rationale + diff + frontmatter), the cited pattern
**Outputs:** `{ verdict: passed | warnings | flags, notes: [...] }`

**How:**

- **Diff-rationale alignment:** Tokenize rationale and diff. ≥1 significant noun/verb from the cited pattern must appear in both. Missing → `flags`
- **Diff-target alignment:** Diff modifies a path that includes the proposal's `target` field. Mismatch → `flags`
- **Rationale length:** Between 3 and 25 lines. Outside → `warnings`
- **Run ID citations:** Every evidence claim cites ≥1 run ID. Missing → `warnings`
- **No self-meta references:** Rationale and diff do not reference `_meta/*` paths. If they do → `flags`
- **Skill-name uniqueness (bootstrap only):** Drafted skill names don't collide with existing skills in the target's `skill.md`. Collision → `flags`

**Verdict handling:**

- `passed` → write proposal, `self_review: passed` in frontmatter
- `warnings` → write proposal, `self_review: warnings` + notes in frontmatter, confidence score takes the hit
- `flags` → DO NOT write proposal, add to watch list with `blocked_by: [proposal_self_review]`. Do not auto-retry the flagged version.
