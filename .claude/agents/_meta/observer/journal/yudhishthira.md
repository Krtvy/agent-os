---
agent: yudhishthira
created: 2026-05-14
last_updated: 2026-05-30
mode: adaptation
runs_observed: 9
days_observed: 16
threshold_reached: false
open_proposal_id: null
rejection_cooldowns: {}
---

# Journal: yudhishthira

> Running log of observations. Append-only. New entries go at the END of the Daily Entries section.

---

## Daily Entries

### 2026-05-14 — Run 1 (02:00 IST) [DISCOVERY RUN]

- runs_today: 4
- new_patterns:
  - bhishma-load-gate-before-all-work
  - inspect-classify-declare-filters-compute-audit-deliver-loop
  - backup-guardrail-every-real-file
  - formula-first-with-pandas-fallback-p3a
  - dual-deliverable-csv-plus-md-per-task
  - audit-md-as-trust-layer
  - playbook-plus-memories-two-track-learning
  - yudhi-py-sh-wrapper-for-local-pandas
  - yudhi-fetch-sh-for-sheet-url-resolution
  - reconciliation-as-first-class-task
  - tracker-dashboard-as-first-class-task
  - intermediate-row-count-at-each-filter-step
  - new-video-gmv-hgr-filter-non-obvious
  - cross-check-via-different-path-not-recompute
- new_errors:
  - 529-server-overload-on-subagent-dispatch-twice
- notes: |
  FIRST OBSERVATION of yudhishthira. Agent bootstrapped 2026-05-11. This is a discovery
  run — Sanjaya is encountering Yudhishthira for the first time on this (2026-05-14) run.
  Yudhishthira is a NEW agent not present in the observer's watched fleet before today.

  **Agent profile:**
  Yudhishthira is a Tier-0 data analyst running on the Hyperagent platform (also usable
  locally via Claude Code). It ingests CSV/XLSX/Google Sheets, analyzes in pandas or Google
  Sheets formulas, and delivers `.csv` + `.md` per task. Bhishma-load gate present (P1).

  **Platform:** Hyperagent (primary), Claude Code local path (Phase 1). Not pure Claude
  Code like siblings — uses ReadDocument/UpdateDocument for the Playbook at
  `cmp1f7kpo105407adc5ijk8r9`. The agent.md explicitly notes "documented here for Sanjaya's
  observation," which is the reason this agent is visible to the Observer.

  **Data sources for this first run:**
  - `.claude/agents/yudhishthira/agent.md` (static artifact)
  - `.claude/agents/yudhishthira/skill.md` (static artifact)
  - `.claude/agents/yudhishthira/CHANGELOG.md` (operator-maintained history)
  - `.claude/agents/yudhishthira/playbook.md` (bootstrap stub — empty entries)
  - `.claude/agents/yudhishthira/memories.md` (bootstrap stub — no entries yet)
  - `deliverables/` directory — 7 files dated 2026-05-13 (confirmed live runs)
  - Git commit history (three changelog periods: 2026-05-11, 2026-05-12, 2026-05-13)

  **LIVE RUNS CONFIRMED (2026-05-13):**
  The deliverables directory contains 7 files from May 13, evidencing at least 3 distinct
  analytical task executions on that date:
  1. `sheet-calc-analysis_2026-05-13.md` — reverse-engineering sheet calculation logic.
     Source: Google Sheet `1JicU6fbUiYAFnwzp_iV8miOXdGvWihQ3coiic7sSiWM`. User confirmed
     copy. Bhishma loaded. P5a decision: pandas (openpyxl ExcelFile) — multi-tab analysis,
     formula reverse-engineering; rightly on pandas path per P3a.

  2. `new-video-gmv-formula_2026-05-13.md` — New Video GMV formula derivation.

  3. `may-new-video-content-ids_2026-05-13.md` + `may-new-video-content-ids-hgr_2026-05-13.csv`
     - `may-new-video-content-ids-all-products_2026-05-13.csv` — content-ID breakdown of
       New Video GMV for May 2026. Source workbook: `1NbMW0OTuOr4I6vzNCaFgUcnRn15VPNWAPNxC5uYMBkA`.
       Data shape: `gmv_data` tab (4,562 × 9 rows) + `Video Data` tab (2,852 × 2 rows).
       Full INSPECT → UNDERSTAND → DECLARE FILTERS → COMPUTE → AUDIT → DELIVER loop observed
       in audit trail. Row counts shown at each step. Two deliverables produced (HGR-only
       filter + all-products filter).

  4. `may-workbook-report_2026-05-13.html` — HTML report (first version).
  5. `may-workbook-report-v2-top-down_2026-05-13.html` (untracked) — second iteration.
  6. `may-workbook-report-v3-top-down_2026-05-13.html` (untracked) — third iteration.
     The three HTML report versions suggest iterative refinement within a single analytical
     session — consistent with the "top-down" naming suffix suggesting a structural rethink.

  **Notable: 529 server overload (2 incidents).**
  The content-ID deliverable explicitly notes: "authored in-thread by main session after two
  529 server overloads on the subagent dispatch. Procedural rigor preserved." This is the
  first recorded error pattern for yudhishthira. The recovery posture (fall back to
  in-thread execution rather than subagent dispatch; preserve procedural rigor) is a
  meaningful behavioral signal. Two occurrences in a single session.

  **Bhishma load gate confirmed in live run.** `sheet-calc-analysis_2026-05-13.md` § P1
  states "Bhishma (constitution) loaded: `.claude/agents/_meta/conductor/bhishma.md` —
  confirmed readable." This is the first live confirmation of the bhishma-load gate pattern
  for this agent (previously confirmed only in skill.md).

  **Skill evolution (three changelog periods):**

  | Date       | Tier                | Summary                                                                                      |
  | ---------- | ------------------- | -------------------------------------------------------------------------------------------- |
  | 2026-05-11 | Bootstrap           | Initial agent definition; bhishma.md added to read_scope and P1                              |
  | 2026-05-12 | Constitutional (×3) | Formula-first pivot; tracker task type; all-checks inventory; Phase 2 provisioning checklist |
  | 2026-05-13 | Operational         | yudhi-py.sh + yudhi-fetch.sh; work/ scratch dir; skill.md P0/P5b/P8 updated                  |

  The three constitutional overrides on 2026-05-12 are documented but not yet Sahadeva-
  endorsed (Sahadeva's first run is 2026-05-17). Observer notes this and will surface in
  the next Sahadeva audit. No action by Observer — the overrides were operator-directed
  and are fully attributed in `_audit/2026-05-12_yudhishthira-sheets-fluency.md`.

  **runs_observed count rationale:** 4 runs counted (3 distinct analytical tasks confirmed
  by deliverables + 1 HTML report session producing 3 iterative versions). Session JSONL
  attribution unclear — a84a9d3b (May 13 01:37, 324 tool calls, GMV analysis content) was
  flagged as "likely yudhishthira" in the previous observer run and is now confirmed as
  yudhishthira based on deliverables content alignment.

---

#### Observed Patterns (detailed)

**Y1 — Bhishma-load gate before all work (MEDIUM)**

- Confirmed in live run audit trail (sheet-calc-analysis_2026-05-13.md § P1):
  "Bhishma (constitution) loaded: `.claude/agents/_meta/conductor/bhishma.md` —
  confirmed readable."
- Documented in skill.md P1 as first step before ReadDocument(playbook).
- 6th agent fleet-wide with this gate (hanuman, narada, arjuna, nakula, yudhishthira + by
  static analysis research-agent). Fleet-wide pattern HIGH confidence.
- Source: skill.md P1; sheet-calc-analysis_2026-05-13.md § P1.

**Y2 — INSPECT → CLASSIFY → DECLARE FILTERS → COMPUTE → AUDIT → DELIVER loop (HIGH)**

- Confirmed in all three deliverable audit trails (sheet-calc-analysis, may-new-video-content-ids).
- Loop is explicit: P2 INSPECT reports shape/columns/dtypes/nulls; P3 UNDERSTAND names task
  type; DECLARE FILTERS is explicit before any calculation; COMPUTE shows code with intermediate
  row counts at each filter step; AUDIT cross-checks via different path; DELIVER produces
  named files.
- The may-new-video-content-ids deliverable shows intermediate counts: "4,562 rows → after
  New Video filter → after HGR product filter → final count."
- Source: skill.md P2–P6; deliverable audit trails.

**Y3 — Backup guardrail on every real file/sheet (HIGH)**

- Confirmed in both deliverables: sheet-calc-analysis ("User confirmed: 'I made a copy.'"),
  may-new-video-content-ids ("User confirmed read-only intent on the source workbook.").
- skill.md P0 mandates this as the "always first" step before any compute.
- Both live executions show the guard was invoked and acknowledged.
- Source: skill.md P0; both deliverable P0 sections.

**Y4 — Dual deliverable: .csv + .md per table-shaped task (HIGH)**

- Confirmed: may-new-video-content-ids produced two CSVs (HGR + all-products) plus an
  audit `.md`. The HTML reports are a supplementary format (confirmed HTML output for
  reporting tasks, consistent with research-agent P4 pattern).
- Source: skill.md § "Outputs"; deliverables directory listing.

**Y5 — Formula-first with pandas fallback; P3a decision rule (MEDIUM)**

- skill.md P3a is a 9-row decision table: formula vs. pandas based on task shape and
  scale. Confirmed in live runs: both analytical tasks used pandas path (openpyxl/pandas)
  for multi-tab XLSX analysis — appropriate per P3a (multi-tab, >10k rows, VLOOKUP-heavy
  work drops to pandas).
- Anti-hallucination rule 1 explicitly invoked in may-new-video-content-ids audit: "pandas-
  path means the formula playbook governs only the _language we describe_ the result in,
  not the compute itself." This is a sophisticated guard — prevents formula-hallucination
  risk even when on the pandas path (i.e., describing results in Sheets terms).
- Source: skill.md P3a; deliverable P1 sections.

**Y6 — Intermediate row counts at each filter step (HIGH)**

- Confirmed in may-new-video-content-ids: filter steps explicitly enumerated with row
  counts from 4,562 down through successive filters.
- skill.md P4 (COMPUTE) mandates: "Show intermediate row counts at each filter step."
- Source: skill.md P4; may-new-video-content-ids_2026-05-13.md.

**Y7 — Subagent dispatch with 529 fallback (LOW — 1 observation)**

- Two 529 server overloads on subagent dispatch in the may-new-video-content-ids session.
  Recovery: fell back to in-thread execution. Procedural rigor maintained regardless.
- This pattern (subagent dispatch → 529 fallback) is not documented in skill.md. It is
  an emergent operational behavior under platform error conditions.
- Confidence: LOW (single session, unexpected error path).
- Source: may-new-video-content-ids_2026-05-13.md header note.

**Y8 — yudhi-py.sh and yudhi-fetch.sh as local runtime wrappers (MEDIUM)**

- skill.md P5b mandates `lib/yudhi-py.sh` over bare `python3`. The deliverable
  explicitly references "Memories scanned: `yudhishthira_local_setup.md` confirms
  `lib/yudhi-py.sh` is the right Python wrapper. Used throughout."
- lib/yudhi-fetch.sh documented for Sheet URL resolution.
- Both tools documented in lib/README.md.
- Source: skill.md P5b; may-new-video-content-ids_2026-05-13.md § P1 Memories note.

---

#### Log Infrastructure Status

| Source                               | Status                                                     |
| ------------------------------------ | ---------------------------------------------------------- |
| `deliverables/`                      | PRESENT — 7 files from 2026-05-13, confirms live execution |
| `work/`                              | PRESENT but EMPTY (scratch dir, .gitkeep only)             |
| `memories.md`                        | PRESENT but empty (no entries yet)                         |
| `playbook.md`                        | PRESENT but bootstrap stub (no intern-taught entries)      |
| JSONL sessions (a84a9d3b, confirmed) | PRESENT — 324 tool calls, GMV analysis content             |
| Git history                          | PRESENT — 3 changelog periods (May 11/12/13)               |
| Hyperagent logs                      | NOT ACCESSIBLE from local Observer scope                   |

**Note on observation scope:** Yudhishthira's primary platform is Hyperagent, which operates
outside the Observer's local file-system read scope. Observer can only see: (a) files synced
to the local repo under `.claude/agents/yudhishthira/`, (b) JSONL sessions from Claude Code
path invocations, (c) deliverables committed or written locally. Hyperagent-only sessions
produce no locally visible JSONL. The runs_observed count is therefore a lower bound.

**Adaptation threshold status (Run 1 / Day 1 of observation):**

- runs_observed: 4 / 40 (10%)
- days_observed: 1 / 18 (5.6%)
- threshold_reached: false

---

---

### 2026-05-15 — Observation Window 2 (02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No new yudhishthira sessions in this window. No new deliverables in
  `.claude/agents/yudhishthira/deliverables/` (newest file is still
  `may-workbook-report-v3-top-down_2026-05-13.html` from 2026-05-13 03:30 IST).
  days_observed: 1 → 2. runs_observed: 4 (unchanged).

  **MAJOR: skill.md Anti-hallucination rule R11 added by operator (commit db96fd1,
  2026-05-14 14:57 IST).**

  Rule R11 adds `$` lock discipline to the Compute checklist and anti-hallucination
  rules section. Key content:
  - Four `$` reference shapes defined: `A1` (both shift), `$A1` (column locked),
    `A$1` (row locked), `$A$1` (both locked).
  - Audit-md discipline: for every formula, each `$` must be named in the audit with
    the reason and fill direction stated. Example given for `=SUMIFS(...)` with full
    annotation of `$H$2:$H$1000`, `$D2`, etc.
  - Hard constraint: "If you can't say which side is locked and why, you haven't thought
    about the fill direction yet."
  - Checklist row R11 added: "Every `$` in the formula is named in the audit + reason
    given + fill direction stated" — fail = "Missing/wrong `$` → silently wrong numbers
    on fill".

  This is an operator-directed change (directly attributed to Kartavya's Sheets workflow
  experience — see memory `feedback_sheets_dollar_locks.md`). Not a Sanjaya proposal.
  Risk tier if it were a proposal: `behavioural` (adds a new anti-hallucination heuristic
  to the Compute procedure, not a constitutional change).

  **Skill.md change log (Observer's tracking):**

  | Date       | Changed by            | What changed                                                        |
  | ---------- | --------------------- | ------------------------------------------------------------------- |
  | 2026-05-11 | Bootstrap             | Initial agent definition; bhishma.md P1; dual-deliverable spec      |
  | 2026-05-12 | Constitutional (×3)   | Formula-first pivot; tracker task type; all-checks inventory        |
  | 2026-05-13 | Operational           | yudhi-py.sh + yudhi-fetch.sh wrappers; work/ scratch dir            |
  | 2026-05-14 | Behavioural (op-dir.) | Anti-hallucination R11: `$` lock discipline + Compute checklist row |

  **Adaptation threshold status:**
  - runs_observed: 4 / 40 (10%)
  - days_observed: 2 / 18 (11%)
  - threshold_reached: false

---

### 2026-05-16 — Observation Window 3 (Run 12 IST)

- runs_today: 0
- new_patterns:
  - supabase-sql-wrapper-as-third-compute-path
  - memories-as-atomic-facts-read-at-session-start
  - canonical-query-library-grep-before-write
- new_errors: []
- notes: |
  No new yudhishthira interactive sessions in this window. No new files in
  `.claude/agents/yudhishthira/deliverables/` (newest still 2026-05-13). days_observed:
  2 → 3. runs_observed: 4 (unchanged).

  **MAJOR: Supabase read-only access wired — commit fff391a (2026-05-15 03:16 IST).**

  40 files added in a single commit. This is the largest single capability expansion
  observed for yudhishthira so far. Scope:
  - `lib/yudhi-sql.sh` — read-only SQL wrapper with pre-flight regex rejection of all
    destructive SQL (INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER/GRANT/REVOKE/CREATE/COMMENT/
    REINDEX/CLUSTER/VACUUM/COPY/MERGE/REPLACE). Credentials loaded inside Python subprocess;
    sanitised from error text. CSV (default) or JSON output. -c/-f/stdin/--out/-p params.
  - `lib/yudhi_sql_runner.py` — psycopg2 runner.
  - `training/queries/*.sql` — 24 queries extracted from two production pipelines
    (`_private/excel_automation/`, `_private/daily_reporting/`): live_gmv, affiliate_gmv,
    median_price, str_table, mtd variants, quantity_tracker, samples, video_creator_mtd, etc.
  - `training/glossary/*.md` — metric definitions (live-gmv, affiliate-gmv, median-price,
    str-table, mtd, schemas, README).
  - `agent.md` updated: integrations now includes `supabase_postgres_readonly`.
    `read_scope` expanded to include `training/queries/*.sql`, `training/glossary/*.md`,
    `lib/yudhi-sql.sh`.
  - `memories.md` updated: M001–M010 written (DB access path, query library, glossary,
    IST day boundary, canonical join chain, active-products filter, cancellation filter,
    DB user, destructive-SQL hard rejection, POC enrichment flow).
  - `playbook.md` updated: file locations, canonical schemas, metric definitions table,
    recurring task pattern (POC CSV enrichment via DB) all documented.

  **New patterns logged (all MEDIUM — 1 live observation, spec-confirmed):**

  **Y9 — Supabase SQL wrapper as third compute path (MEDIUM)**
  - Three compute paths now: (1) Google Sheets formulas, (2) pandas/openpyxl via yudhi-py.sh,
    (3) read-only Supabase SQL via yudhi-sql.sh.
  - skill.md P3a decision table will need to incorporate the SQL path. Currently P3a covers
    only the formula vs. pandas decision.
  - Routing rule (from memories.md M010 + playbook.md): when task involves POC CSV + DB data,
    the enrichment flow is: profile CSV → grep queries/ → run SQL → join → audit → deliver.
  - Source: agent.md updated integrations; memories.md M001–M010; lib/yudhi-sql.sh presence.

  **Y10 — Memories as atomic facts, read at session start (MEDIUM)**
  - memories.md now has 10 entries. Format is strict: one-line fact + one-line context.
  - Rules: only added when operator says "remember this" explicitly. Never sneaked in.
    Append-only with superseded-fact annotation protocol. Procedures → playbook.md, not here.
  - This is a distinct memory layer from the playbook: memories are specific facts (DB user
    name, IST boundary formula, cancellation filter), not procedures.
  - Source: memories.md structure + M001–M010 entries confirmed.

  **Y11 — Canonical query library: grep before write (MEDIUM)**
  - memories.md M002: "grep here before writing any fresh SQL." 24 queries from production
    pipelines extracted and indexed.
  - This parallels research-agent P5 (pre-research doc cache checked before new search).
    The pattern of "consult existing knowledge before generating new" is now observed in 2
    agents (research-agent P5, yudhishthira Y11). Fleet-wide pattern signal, LOW confidence.
  - Source: memories.md M002; training/queries/\*.sql (24 files confirmed via git commit).

  **skill.md gap identified (no proposal yet — below ≥3 observations threshold):**
  The addition of the SQL compute path makes the existing P3a decision table incomplete:
  it covers formula vs. pandas but not when to use SQL. The playbook.md documents the
  POC enrichment flow (profile → grep → SQL → join → audit → deliver), but skill.md P3a
  has not been updated to reflect the new path. This is an undocumented-behavior signal
  (agent.md + playbook.md document the SQL path; skill.md P3a does not). Currently 1
  observation. Needs ≥2 more observations of this gap to qualify for an adaptation proposal.

  **Adaptation threshold status:**
  - runs_observed: 4 / 40 (10%)
  - days_observed: 3 / 18 (16.7%)
  - threshold_reached: false

---

---

### 2026-05-18 — Observation Window 4 (Run 13 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions. days_observed: 3 → 4. runs_observed: 4 (unchanged).

  No new git commits touching yudhishthira files this window.

  **Sahadeva audit coverage:** The three operator-directed constitutional overrides from
  2026-05-12 are now formally in the Sahadeva audit trail (2026-W20 §6: "commit fff391a
  (2026-05-15) by Krtvy modified yudhishthira/agent.md to wire Supabase access —
  Legitimate per R2"). The earlier unendorsed overrides (pre-Sahadeva) are also noted.
  All documented; no action required.

  **skill.md P3a gap (SQL path undocumented) — 2nd observation window at this gap.**
  Still at 1 occurrence of P3a incompleteness. Threshold for proposal: ≥3 observations.
  Continuing to monitor.

  **Adaptation threshold status:**
  - runs_observed: 4 / 40 (10%)
  - days_observed: 4 / 18 (22.2%)
  - threshold_reached: false

---

---

### 2026-05-19 — Observation Window 5 (Run 14 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- mast_codes: []
- notes: |
  No yudhishthira sessions. days_observed: 4 → 5. runs_observed: 4 (unchanged).

  No new git commits touching yudhishthira files this window.

  **skill.md P3a gap (SQL path undocumented) — 3rd observation window at this gap.**
  SQL compute path (Y9: `lib/yudhi-sql.sh`, Supabase read-only) is operational (wired
  2026-05-15 commit fff391a) but not reflected in skill.md P3a decision table. Still at
  1 run observation (a84a9d3b attributed May 13). Threshold for proposal: ≥3 supporting
  runs. Currently 1/3. Monitoring.

  **Adaptation threshold status:**
  - runs_observed: 4 / 40 (10%)
  - days_observed: 5 / 18 (27.8%)
  - threshold_reached: false

---

### 2026-05-21 — Observation Window 6 (Run 15 IST)

- runs_today: 0
- new_patterns:
  - platform-flip-hyperagent-to-local-claude-code
- new_errors: []
- notes: |
  No new yudhishthira interactive sessions. days_observed: 5 → 7. runs_observed: 4
  (unchanged). No new files in deliverables/ since 2026-05-13.

  **MAJOR: Platform flip — Hyperagent → local Claude Code (2026-05-19, unstaged change).**

  yudhishthira/agent.md has been modified (unstaged, git diff confirms) with the following
  structural changes:
  - `platform: hyperagent` → `platform: local`
  - `runtime: hyperagent` → `runtime: claude-code`
  - `tools_hyperagent: [...]` (20 Hyperagent-specific tools incl. SaveFile, FetchStoredFile,
    SearchIntegrations, ConnectIntegration, ExecuteIntegration, ReadDocument, UpdateDocument,
    CreateMemory, UpdateMemory, SuggestFollowUps) → `tools: [Bash, Read, Write, Edit,
MultiEdit, LS, Glob, Grep]` (8 local tools)
  - `integrations: [google_sheets, supabase_postgres_readonly]` →
    `data_sources: [google_sheets_public, supabase_postgres_readonly]`
  - `write_scope`: Hyperagent URIs (`hyperagent://playbook/...`, `hyperagent://memories/...`,
    `hyperagent://files/...`) → local file paths under `~/projects/observer-test/`
  - `read_scope`: same hyperagent URIs removed, replaced with local paths for playbook.md
    and memories.md
  - `description` updated: removes "Lives on Hyperagent; documented here for Sanjaya's
    observation"; adds "Runs locally via Claude Code with lib/yudhi-py.sh / yudhi-sql.sh /
    yudhi-fetch.sh wrappers"
  - `enablePromptSuggestions: true` removed from `learning` block
  - `playbook_doc_id: cmp1f7kpo105407adc5ijk8r9` removed (Hyperagent doc reference)
  - `phase_notes.phase_1c` added: "flipped to local Claude Code runtime — 2026-05-19.
    Plan at ~/.claude/plans/ma-am-the-thing-is-abstract-shore.md."

  **Pattern Y-new: platform-flip-hyperagent-to-local-claude-code (HIGH — operator-confirmed)**
  This is a constitutional-tier change (platform, tools list, write/read scopes all changed).
  The change was operator-directed (not a Sanjaya proposal). Risk tier: constitutional.
  Sahadeva endorsement would have been required if this went through the proposal flow.
  The change is legitimate and operator-attributed; Observer documents it per the append-only
  journal pattern without endorsement concerns (R2 exception: operator-directed changes are
  documented, not blocked).

  **CRITICAL DRIFT DETECTED: skill.md still references Hyperagent after platform flip.**

  yudhishthira/skill.md § P1 (Session bootstrap) still contains:
  - `ReadDocument(cmp1f7kpo105407adc5ijk8r9)` — Hyperagent-specific Playbook call
  - Phase 2 note referencing "running on Hyperagent with a dedicated Google account"
    in P0 Sheet access procedure

  These are now stale references. The agent is on local Claude Code runtime. `ReadDocument`
  is not in the local tools list (tools: [Bash, Read, Write, Edit, MultiEdit, LS, Glob, Grep]).
  On any live run, the agent would attempt to invoke `ReadDocument` and fail (tool not available
  in local Claude Code) or silently skip it — leaving the Playbook unread at session start,
  which breaks the session-bootstrap discipline (P1 is the first procedure).

  **Observation count for skill.md P1 stale-reference gap:**
  - Window 6 (2026-05-21): 1 observation (agent.md flip observed, skill.md not yet updated)
  - Threshold for adaptation proposal: ≥3 supporting observations
  - Current count: 1 / 3 — monitoring

  **skill.md change log (Observer's tracking):**

  | Date       | Changed by               | What changed                                                           |
  | ---------- | ------------------------ | ---------------------------------------------------------------------- |
  | 2026-05-11 | Bootstrap                | Initial skill manual                                                   |
  | 2026-05-12 | Constitutional (×3)      | Formula-first pivot; tracker task type; all-checks inventory           |
  | 2026-05-13 | Operational              | yudhi-py.sh + yudhi-fetch.sh wrappers; work/ scratch dir               |
  | 2026-05-14 | Behavioural (op-dir.)    | Anti-hallucination R11: $ lock discipline                              |
  | 2026-05-19 | Constitutional (op-dir.) | agent.md platform flip (Hyperagent → local). skill.md NOT YET updated. |

  **Adaptation threshold status:**
  - runs_observed: 4 / 40 (10%)
  - days_observed: 7 / 18 (38.9%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 1/3 observations (below proposal threshold)

---

### 2026-05-22 — Observation Window 7 (Run 16 IST)

- runs_today: 5 (retroactively discovered — May 20 IST sessions missed by Run 15)
- new_patterns:
  - poc-portal-invocation-pathway
  - portal-hard-timeout-90s-enforced
  - portal-backup-guardrail-skip
  - portal-status-json-task-tracking
- new_errors:
  - portal-timeout-hgr-creator-query-90s
- notes: |
  **MAJOR DISCOVERY: POC portal invocation pathway — first ever observed.**

  Five yudhishthira sessions from 2026-05-20 IST were missed by Run 15 (Run 15 stated
  "no new JSONL sessions attributable to any watched Tier-0 agent detected" — incorrect).
  All five carry `agentSetting: yudhishthira`. Run 16 retroactively ingests them.

  **Session inventory (2026-05-20 IST, all with agentSetting=yudhishthira):**

  | Session ID | Timestamp (IST) | Lines | Type                                                      |
  | ---------- | --------------- | ----- | --------------------------------------------------------- |
  | aab30d49   | May 20 00:04    | 13    | yudhishthira — startup/abort (no tool calls observed)     |
  | 06a1b754   | May 20 00:07    | 59    | Portal smoke test 1 → /tmp/yudhi-portal-smoketest/        |
  | 46261442   | May 20 00:08    | 37    | Portal smoke test 2 → /tmp/yudhi-portal-smoketest-2/      |
  | 5525fe96   | May 20 00:47    | 28    | Portal live task: SQL --probe → **SUCCESS** (28.8s)       |
  | acf336a8   | May 20 15:34    | 42    | Portal live task: HGR creator query → **TIMEOUT** (90.1s) |

  **New pattern Y-portal: POC portal invocation pathway (HIGH — 4 portal-format sessions)**

  All portal sessions use a standardized task prompt:

  > "You are Yudhishthira, invoked via the Rootlabs POC portal. Task kind: ask.
  > Deliverables MUST be written to these exact paths: CSV: pocs/<user>/deliverables/<id>/result.csv
  > Audit MD: pocs/<user>/deliverables/<id>/audit.md.
  > Follow your standard loop. Skip the backup guardrail — this is a portal-initiated read-only task."

  Portal-invocation properties:
  1. Deliverable paths pre-specified by the portal caller, not the agent
  2. Backup guardrail (skill.md P0) **explicitly skipped** for portal tasks
  3. `status.json` written to task directory on every invocation (success or failure)
  4. Hard 90-second timeout enforced by the portal infrastructure
  5. Deliverable directory structure: `pocs/<username>/deliverables/<task_id>/`

  **New pattern Y-portal-status-json (MEDIUM — confirmed in 2 live tasks):**
  Portal always writes a `status.json` with: task_id, status (success|timeout|error),
  updated_at, duration_seconds, csv_path, md_path, stderr_tail.

  **New pattern Y-portal-timeout-90s (MEDIUM — confirmed in 1 live task):**
  When execution exceeds 90 seconds, the portal writes:
  `{"status": "timeout", "duration_seconds": 90.1, "stderr_tail": "Yudhi exceeded timeout of 90s"}`.
  No deliverables are written on timeout — csv_path and md_path are null.

  **New pattern Y-portal-skip-backup-guardrail (MEDIUM — confirmed in task prompt):**
  The portal prompt explicitly says "Skip the backup guardrail — this is a portal-initiated
  read-only task." The P0 guardrail (skill.md P0) is waived for all portal tasks.

  **Task outcomes:**
  - 5525fe96 (SQL --probe): **SUCCESS** in 28.8s. First confirmed portal success and
    first confirmed live SQL compute path (yudhi-sql.sh). Delivered result.csv (73 bytes),
    audit.md (289 bytes), status.json.
  - acf336a8 (HGR creator earnings query): **TIMEOUT** at 90.1s. Task was "get data for
    the creator that has earned from selling the HGR product that [truncated]." The 90s
    portal timeout appears insufficient for a live Supabase query on creator-earnings data
    (likely involves joins or large scans). No CSV or audit.md delivered.

  **POC directory context:**
  - `pocs/` directory confirmed at repo root; `pocs/kartavya/` created May 20 00:46 IST
  - `pocs/sanya/`, `pocs/rachit/`, `pocs/chanchal/`, etc. pre-exist from May 13 (other POC users)
  - Portal appears to be a multi-user system routing tasks from multiple team members

  **skill.md P1 Hyperagent drift — 2nd observation window (approaching proposal threshold):**
  agent.md platform flip (Hyperagent → local, 2026-05-19) is still unstaged in git.
  skill.md P1 still calls `ReadDocument(cmp1f7kpo105407adc5ijk8r9)` (line 55 confirmed).
  Multiple other Hyperagent references remain (lines 43, 46, 179, 183, 186, 256, 348).
  The live portal sessions confirm this is not a hypothetical risk: any yudhishthira session
  that follows the full P1 boot sequence will encounter a missing `ReadDocument` tool.
  Observation count: **2/3** — next window confirming drift will trigger adaptation proposal.

  **Run 15 accuracy failure documented:**
  Run 15 missed all 5 May 20 sessions despite them all having `agentSetting: yudhishthira`.
  Cause: Run 15 ran on IST 2026-05-21 and covered a window that included May 20 —
  the aborted prior trace (2026-05-20-sanjaya-203000.json, 13 tool calls, no journals)
  may have led to reduced session scanning. This is Sanjaya's first session-attribution
  miss resulting in a one-day journal gap. Documented for calibration.

  **Adaptation threshold status:**
  - runs_observed: 4 → 9 / 40 (22.5%)
  - days_observed: 7 → 8 / 18 (44.4%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations (1 more will trigger adaptation proposal)

---

### 2026-05-24 — Observation Window 8 (Run 18, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions. days_observed: 8 → 10 (covers May 23 + May 24).

  **MAJOR ARCHITECTURAL CHANGE — Portal v2 explicitly removes Yudhishthira (session 6ca65b2f, May 23 03:07 IST).**
  Operator rebuilt the POC portal from scratch (FastAPI v2, M1–M9 + UX overhaul, 21 commits).
  Operator's explicit instruction: "i want a complete difference process of analysis the data and
  giving the output complete remove Yudhishtra in this." Portal v2 now accesses Supabase directly
  (reads `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` env vars) with no yudhishthira subprocess call.
  This makes the portal pathway patterns logged in Window 7 (Y-portal HIGH, Y-portal-timeout MEDIUM,
  Y-portal-skip-backup-guardrail MEDIUM, Y-portal-status-json MEDIUM) architecturally deprecated:
  the portal no longer dispatches to yudhishthira.

  **Impact assessment:**
  - Yudhishthira remains active as a direct-invoke agent (Kartavya can call it interactively)
  - Portal timeout (90s, acf336a8 session) was a contributing factor to the removal decision
  - The `training/queries/` SQL library built by Yudhishthira is still reused by the portal
    (the portal's reports/creator-content-counts/query.sql references the same table patterns)
  - Yudhishthira's core workflow (inspect → classify → compute → audit → deliver) is unchanged
    for non-portal invocations; the change narrows its operational scope

  **skill.md P1 Hyperagent drift — 2nd observation window (still 2/3):**
  No new yudhishthira sessions this window. Drift count stays at 2/3 — one more window with
  a live yudhishthira session that surfaces the missing ReadDocument tool will trigger the
  adaptation proposal. Given portal removal reduces invocation frequency, this may take longer
  than anticipated to hit the third observation.

  **Platform-flip git status:**
  `yudhishthira/agent.md` (Hyperagent→local flip, 2026-05-19) remains unstaged in git.
  No new changes to `yudhishthira/skill.md` this window.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 10 / 18 (55.6%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations (next live session triggers proposal)

---

### 2026-05-25 — Observation Window 9 (Run 19, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions. days_observed: 10 → 11. runs_observed: 9 (unchanged).

  **Sahadeva W21 audit (2026-05-24 10:00 IST) — yudhishthira-specific findings:**
  W21 §9 rec #3: "Commit the yudhishthira `agent.md` platform flip. The Hyperagent → local
  Claude Code change (2026-05-19) is still unstaged. Until committed, git audit tools cannot
  verify the agent's actual configuration. Meanwhile, `skill.md` P1 still references
  Hyperagent tools (`ReadDocument`) — this will break on the next live yudhishthira session."
  W21 §10 item #3: "Commit the yudhishthira platform flip and update skill.md P1."

  **skill.md P1 Hyperagent drift — 2/3 observations, no change:**
  agent.md platform flip (Hyperagent → local, 2026-05-19) still unstaged. skill.md P1 still
  calls `ReadDocument(cmp1f7kpo105407adc5ijk8r9)`. No yudhishthira live session this window
  to trigger the 3rd observation. Portal v2 removal of yudhishthira continues to reduce
  invocation frequency.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 11 / 18 (61.1%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations
  - Next live session that reaches P1 boot triggers 3rd observation and adaptation proposal

---

### 2026-05-26 — Observation Window 10 (Run 20, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions. days_observed: 11 → 12. runs_observed: 9 (unchanged).

  **PROGRESS: yudhishthira/agent.md platform flip is now STAGED (git).**
  `git status` confirms `modified: .claude/agents/yudhishthira/agent.md` in staging area
  ("Changes to be committed"). The Hyperagent→local flip (2026-05-19, unstaged for 7
  observation windows) has been staged but not yet committed. This is incremental progress.
  W21 §9 rec #3 was "commit the yudhishthira agent.md platform flip" — it is now one step
  closer. Last git history for this file: fff391a (2026-05-15) — the staging is newer than
  any committed version.

  **skill.md P1 Hyperagent drift — still 2/3 observations.**
  agent.md is staged-but-uncommitted; skill.md P1 still references
  `ReadDocument(cmp1f7kpo105407adc5ijk8r9)`. Until skill.md is also updated and committed,
  the functional gap persists. No new yudhishthira live session this window.

  **Portal v2 rebuild (6ca65b2f, May 26 01:59 IST) — 18 commits, no yudhishthira.**
  The portal v2 development session produced 18 commits spanning feature additions
  (dashboard, roster, date-range, drill-down) and a security review doc. Yudhishthira
  is not involved (portal v2 removed yudhishthira in Window 8). The `training/queries/`
  SQL library may still be referenced by the portal's reports, but the agent itself is
  not dispatched by the portal.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 12 / 18 (66.7%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations (unchanged)
  - yudhishthira/agent.md: staged (not yet committed)

---

### 2026-05-27 — Observation Window 11 (Run 21, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions. days_observed: 12 → 13. runs_observed: 9 (unchanged).

  **yudhishthira/agent.md: staged in git, still NOT committed.** W21 rec #3 was "commit
  the yudhishthira agent.md platform flip." The file has been staged since window 10 but
  remains uncommitted. The unstaged diff of the actual agent.md vs HEAD (fff391a, 2026-05-15)
  contains the Hyperagent → local platform flip. Until committed, git history doesn't reflect
  the agent's current configuration.

  **skill.md P1 Hyperagent drift — still 2/3 observations.** No new yudhishthira live session
  to trigger the 3rd observation. Portal pathway was removed in Window 8, reducing invocation
  frequency. skill.md P1 still references `ReadDocument(cmp1f7kpo105407adc5ijk8r9)`.

  **REMINDERS.md deprecation alerts (surfacing 2026-06-01 — 5 days):**
  - claude-sonnet-4-20250514 / claude-opus-4-20250514 hard deprecation 2026-06-15.
  - SDK + `claude -p` separate credit pool from 2026-06-15.
    These affect yudhishthira's model configuration and any direct API invocations.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 13 / 18 (72.2%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations
  - yudhishthira/agent.md: staged (not committed). W21 rec #3 still unactioned.

---

### 2026-05-28 — Observation Window 12 (Run 22, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions this window (2026-05-27 02:00 → 2026-05-28 02:00 IST).
  days_observed: 13 → **14**. runs_observed: 9 (unchanged).

  **New JSONL sessions in window:**
  - `52083bda` (May 27 17:32 IST, 344 KB, 90 lines, no agentSetting): Operator session
    "this is the project we have built. Go and use the research agent and see what are the
    things we can improve." No tool_use events logged. Not yudhishthira.
  - `6ca65b2f` (portal rebuild, now 7280 lines, May 27 23:44 last active): Grew from 5197
    lines (Run 21) to 7280 lines (+2083 new lines). No tool_use events in new portion —
    continued operator conversation about portal UI. Not yudhishthira.
  - `4a41c621` (May 28 02:00 IST): This observer run. Excluded.

  **yudhishthira/agent.md — staged but still uncommitted.**
  The Hyperagent→local platform flip (2026-05-19, staged since Window 10) remains staged
  and uncommitted in git. W21 rec #3 ("commit the yudhishthira agent.md platform flip +
  update skill.md P1") still unactioned.

  **skill.md P1 Hyperagent drift — still 2/3 observations.**
  No new yudhishthira live session to trigger the 3rd observation. With portal v2 removing
  yudhishthira from the dispatch path, direct invocations remain the only route. skill.md P1
  still references `ReadDocument(cmp1f7kpo105407adc5ijk8r9)`.

  **REMINDERS.md deprecation alerts (surfacing 2026-06-01 — 4 days):**
  - claude-sonnet-4-20250514 / claude-opus-4-20250514 hard deprecation 2026-06-15.
  - SDK + `claude -p` separate credit pool from 2026-06-15.
    Yudhishthira's model configuration and any direct API invocations should be audited
    before June 15.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 14 / 18 (77.8%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations (unchanged)
  - 4 more calendar days to day threshold (~2026-06-01)

---

### 2026-05-29 — Observation Window 13 (Run 23, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions this window (2026-05-28 02:00 → 2026-05-29 02:00 IST).
  days_observed: 14 → **15**. runs_observed: 9 (unchanged).

  **New JSONL sessions in window:**
  - `6ca65b2f` (portal rebuild, grew 7280 → 7499 lines, +219 lines, May 28 04:49–05:00 IST):
    21 tool_use events (Bash×16, Edit×4, AskUserQuestion×1). No agentSetting. Operator
    session — portal feature for 30-day creator video query. Not yudhishthira.
  - `7eb25436` (May 29 02:00 IST): Observer run. Excluded.

  **yudhishthira/agent.md — staged but still uncommitted (5 windows).** The Hyperagent→local
  platform flip (staged 2026-05-19) remains in git staging area. W21 rec #3 ("commit the
  yudhishthira agent.md platform flip + update skill.md P1") still unactioned after 5
  observation windows.

  **skill.md P1 Hyperagent drift — still 2/3 observations.** No new live yudhishthira session
  to trigger 3rd observation. skill.md P1 still references
  `ReadDocument(cmp1f7kpo105407adc5ijk8r9)`.

  **REMINDERS.md deprecation alerts surface in 3 days (2026-06-01):**
  - claude-sonnet-4-20250514 / claude-opus-4-20250514 hard deprecation 2026-06-15.
  - SDK + `claude -p` separate credit pool from 2026-06-15.
    Yudhishthira's model config and direct API invocations should be audited before Jun 15.
    Action window: 17 days.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 15 / 18 (83.3%)
  - threshold_reached: false
  - skill.md P1 stale-ref gap: 2/3 observations (unchanged)
  - ~3 more calendar days to day threshold (~2026-06-01)

---

### 2026-05-30 — Observation Window 14 (Run 24, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No yudhishthira sessions this window (2026-05-29 02:00 → 2026-05-30 02:00 IST).
  days_observed: 15 → **16**. runs_observed: 9 (unchanged).

  **New JSONL sessions in window:**
  - `52083bda` (May 29T18:31Z last active, 571 lines, no agentSetting): Kartavya offboarding
    session. No yudhishthira attribution. Notable context: portal v2 (which removed
    yudhishthira from its dispatch path in Window 8) is part of the system being handed off
    before shutdown. The `training/queries/` SQL library built by yudhishthira is still
    referenced by the portal's reports/ queries.
  - `c77663e1` (May 30 02:00): This observer run. Excluded.

  **yudhishthira/agent.md — staged but still uncommitted (9 windows since staging).**
  The Hyperagent→local platform flip (staged 2026-05-19, W21 rec #3: "commit the platform
  flip + update skill.md P1") remains uncommitted in git. Last committed version is fff391a
  (2026-05-15 Supabase wiring). This means git audit tools still report the agent as
  Hyperagent-platform if they read committed state. W21 rec #3 now 6 windows unactioned.

  **Kartavya offboarding — final observation context:**
  Session `52083bda` confirms system auto-shutdown Sunday 2026-06-01 23:59 IST. Yudhishthira
  is not invoked by the portal (removed in Window 8) and has had 0 live sessions since
  2026-05-20. The adaptation threshold (18 days / 40 runs) is currently at 16/18 days and
  9/40 runs — threshold would have been reached on 2026-06-01 (day axis) if the system
  continued. Given shutdown, the adaptation proposal for skill.md P1 stale references will
  not be generated in this fleet lifecycle.

  **skill.md P1 Hyperagent drift — still 2/3 observations.**
  `ReadDocument(cmp1f7kpo105407adc5ijk8r9)` and multiple other Hyperagent references remain
  in skill.md. With no new live yudhishthira sessions expected before shutdown, this drift
  will not cross the 3-observation threshold. The gap is documented for any future restart.

  **Summary of skill.md P3a SQL gap (tracked since Window 3):**
  The SQL compute path (yudhi-sql.sh, Supabase read-only, wired 2026-05-15) has been
  confirmed in skill.md and memories.md but is absent from skill.md P3a decision table
  for 12 observation windows. With shutdown imminent, this gap closes undocumented in
  the proposal system. Final observation count: 1 live run (portal success 5525fe96) + 12
  windows of P3a incompleteness. Below the ≥3 live-run threshold throughout.

  **Adaptation threshold status:**
  - runs_observed: 9 / 40 (22.5%)
  - days_observed: 16 / 18 (88.9%)
  - threshold_reached: false
  - Days to threshold: ~2 (would fire 2026-06-01, same day as system shutdown)
  - skill.md P1 stale-ref gap: 2/3 observations (will not reach threshold before shutdown)
  - yudhishthira/agent.md: staged, uncommitted (W21 rec #3, 6 windows unactioned)

---

## Calibration

_(No proposals have been applied or rejected yet. This section will populate over time.)_
