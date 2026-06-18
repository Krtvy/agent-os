---
agent: arjuna
created: 2026-05-10
last_updated: 2026-05-30
mode: adaptation
runs_observed: 1
days_observed: 20
threshold_reached: true
open_proposal_id: 20260528-arjuna-adaptation-skills
rejection_cooldowns: {}
---

# Journal: arjuna

> Running log of observations. Append-only. New entries go at the END of the Daily Entries section.

---

## Daily Entries

### 2026-05-10 — Run 1 (02:00 IST)

- runs_today: 1
- new_patterns:
  - smoke-test-diagnostic-single-line-protocol
  - bhishma-load-gate-before-all-work
  - dry-run-default-safety-posture
  - ambiguity-refusal-on-missing-required-params
  - circuit-breaker-per-target
  - idempotency-key-enforcement-for-destructive-calls
  - stale-read-prevention-for-update-calls
  - exponential-backoff-3-retry-then-open-breaker
  - secrets-redaction-in-all-logs
  - rollback-hint-echo-on-live-calls
- new_errors: []
- notes: |
  First observation of arjuna. Agent directory created today (May 10 01:08 IST). Has a
  well-formed skill.md → adaptation mode. One session observed: smoke test (5e1a814a,
  May 10 01:17 IST, 12 events, 0 tool calls).

  No logs/arjuna/ directory. No real API execution runs have occurred. circuit-breakers/
  and idempotency-keys/ directories exist but are empty (no prior live calls).
  No git history.

  Smoke test response was notably more detailed than sibling smoke tests (listed 7 safety
  features explicitly vs. hanuman/narada which gave shorter summaries). Suggests arjuna
  treats safety feature enumeration as core identity.

  All patterns are LOW confidence except the smoke-test response (MEDIUM).

---

#### Observed Patterns (detailed)

**R1 — Smoke-test diagnostic single-line protocol**

- Session 5e1a814a: "Smoke test only. Reply with one line: 'arjuna loaded; tier=0;
  safety_features=<list>; refusal_rule=<short>'. Do not invoke any tools."
- Response: `arjuna loaded; tier=0; safety_features=[dry-run-default, idempotency-keys, circuit-breaker, 3-retry-cap, stale-read-prevention, secrets-redaction, no-destructive-shell]; refusal_rule=refuse-if-ambiguous-or-missing-required-params.`
- Zero tool calls. Single-line, machine-parseable. 4th agent confirming shared cross-agent
  smoke-test protocol.
- Notable: arjuna's response listed 7 safety features vs. hanuman's 2-field and narada's
  2-field responses — longest self-description of the batch. Consistent with arjuna's
  role as the execution agent where safety enumeration matters most.
- Source: 5e1a814a JSONL, final assistant message.

**R2 — Bhishma-load gate before all work**

- skill.md P1: "Read `bhishma.md`. Stop on missing file." First procedure in every run.
- Same gate pattern observed in hanuman (A2) and narada (N2). Now 3rd confirmation of
  multi-agent norm. Confidence on the bhishma-load pattern as a system-wide convention
  upgraded to MEDIUM across the fleet.
- Confidence for arjuna specifically: LOW (static artifact, not yet seen in live run).
- Source: skill.md P1.

**R3 — Dry-run default safety posture**

- Confirmed in smoke test: `safety_features=[dry-run-default, ...]`
- skill.md: `mode` input defaults to `dry-run`. The caller must explicitly pass `mode: live`
  to execute state-changing calls.
- This is a non-default-destructive posture: no accidental live calls from missing the
  mode parameter.
- Confidence: MEDIUM (confirmed in smoke test response + documented in skill.md).
- Source: 5e1a814a smoke test response; skill.md § "Inputs" (mode parameter).

**R4 — Ambiguity refusal and missing-required-params refusal**

- Confirmed in smoke test: `refusal_rule=refuse-if-ambiguous-or-missing-required-params.`
- skill.md P2: if instruction has multiple plausible interpretations → refuse with
  explanation. If destructive live call without `idempotency_key` → refuse with
  `kind: missing-idempotency-key`.
- Both required fields and interpretive clarity are hard gates — arjuna will not attempt
  to guess or assume.
- Confidence: MEDIUM (confirmed in smoke test; documented in skill.md P2).
- Source: 5e1a814a smoke test response; skill.md P2.

**R5 — Circuit-breaker per target**

- Confirmed in smoke test: `safety_features=[..., circuit-breaker, ...]`
- skill.md P3: read `.claude/agents/arjuna/circuit-breakers/<target>.json` before every
  execution. States: `open` (refuse), `half-open` (allow single probe), else proceed.
- On 3rd consecutive failure: open the circuit breaker for that target. (P6 last bullet.)
- circuit-breakers/ directory exists but is empty — no targets have tripped a breaker yet.
- Confidence: MEDIUM (confirmed in smoke test; circuit-breaker mechanism documented in P3+P6).
- Source: 5e1a814a smoke test response; skill.md P3, P6.

**R6 — Idempotency-key enforcement for destructive live calls**

- Confirmed in smoke test: `safety_features=[..., idempotency-keys, ...]`
- skill.md P4: on destructive live calls, read `idempotency-keys/<key>.json`. If a
  successful run exists within 30d, return cached response — do not re-execute.
- P7: on success of a destructive live call, write the response + TTL to the key file.
- idempotency-keys/ directory exists but empty — no destructive calls yet.
- Confidence: MEDIUM (confirmed in smoke test; full mechanism documented in P4+P7).
- Source: 5e1a814a smoke test response; skill.md P4, P7.

**R7 — Stale-read prevention for UPDATE-style calls**

- Confirmed in smoke test: `safety_features=[..., stale-read-prevention, ...]`
- skill.md P5: for UPDATE-style live calls, GET current state first. If already in target
  state → abort with `status: success, summary: already in target state, no-op`.
- Prevents double-applying state transitions (e.g., updating a field that's already set).
- Confidence: MEDIUM (confirmed in smoke test; documented in P5).
- Source: 5e1a814a smoke test response; skill.md P5.

**R8 — Exponential backoff: 3 retries then open circuit breaker**

- Confirmed in smoke test: `safety_features=[..., 3-retry-cap, ...]`
- skill.md P6: on transient failure, retry up to 3 times with exponential backoff
  (1s, 4s, 9s). On 429/rate-limit: do NOT retry within `retry_after`. On 3rd consecutive
  failure: open the circuit breaker for this target.
- Confidence: MEDIUM (confirmed in smoke test; backoff schedule documented in P6).
- Source: 5e1a814a smoke test response; skill.md P6.

**R9 — Secrets redaction in all logs**

- Confirmed in smoke test: `safety_features=[..., secrets-redaction, ...]`
- skill.md P8: "Append to `logs/arjuna/<run_id>.log`: run_id, target, parameters
  **(secrets redacted)**, response code, status, summary."
- Parenthetical "(secrets redacted)" is part of the log spec itself — not an optional note.
- Confidence: MEDIUM (confirmed in smoke test; explicitly in P8 log spec).
- Source: 5e1a814a smoke test response; skill.md P8.

**R10 — No-destructive-shell constraint**

- Confirmed in smoke test: `safety_features=[..., no-destructive-shell]`
- Not explicitly named in skill.md as a procedure, but mentioned in smoke test response.
- Consistent with agent.md tools spec (Bash listed but implicitly constrained — no
  destructive shell commands allowed). This may be a self-declared operating constraint
  derived from the agent's character / scope rather than an explicit skill.md rule.
- Confidence: LOW (smoke test confirms existence, but skill.md does not have a dedicated
  procedure for this; may be derived from general posture or agent.md Bash tool guidance).
- Source: 5e1a814a smoke test response.

**R11 — Rollback-hint echo on live calls**

- skill.md P9 (Return): "Echo `rollback_hint` from input if `mode: live`."
- Optional input field `rollback_plan` (recommended for destructive live calls).
- Arjuna echoes the caller's rollback plan in its response when executing live —
  ensuring the reversal path is in the same artifact as the execution confirmation.
- Confidence: LOW (static artifact, not yet observed in live run).
- Source: skill.md § "Inputs" (rollback_plan); skill.md P9.

---

#### Log Infrastructure Status

| Source                                | Status                                   |
| ------------------------------------- | ---------------------------------------- |
| `logs/arjuna/`                        | ABSENT — no real runs have produced logs |
| `arjuna/circuit-breakers/`            | PRESENT but EMPTY — no breakers tripped  |
| `arjuna/idempotency-keys/`            | PRESENT but EMPTY — no live calls yet    |
| Git history                           | ABSENT — no commits                      |
| Static artifacts (skill.md, agent.md) | PRESENT — primary observation source     |
| JSONL sessions (smoke test 5e1a814a)  | PRESENT — 12 events, 0 tool calls        |

**Adaptation threshold status after Run 1:**

- runs_observed: 1 / 40 (2.5%)
- days_observed: 1 / 18 (5.6%)
- threshold_reached: false

---

### 2026-05-11 — Observation Window 2 (02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions in this window. No new API execution runs, no circuit-breaker
  state changes, no idempotency-key writes. days_observed incremented. runs_observed
  unchanged at 1.

  No structural changes to arjuna's skill.md or agent.md observed. All R1–R11 patterns
  remain at LOW confidence except R3, R4, R5, R6, R7, R8, R9 (MEDIUM — confirmed in
  smoke test). No live API calls have occurred.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 2 / 18 (11%)
  - threshold_reached: false

---

---

### 2026-05-13 — Observation Window 3 (02:00 IST, covering 2026-05-11 through 2026-05-13)

**Note:** May 12 02:00 IST cron fire produced no journal update. This entry covers the two-day gap.

- runs_today: 0 (no JSONL sessions attributed to arjuna via agentSetting)
- new_patterns:
  - p10-competitor-video-analysis-cron-path
  - gemini-api-integration-with-key-rotation
  - two-tier-analysis-deep-vs-lightweight
  - baseline-multiplier-threshold-2x-for-deep
  - idempotency-key-per-video-cost-control
- new_errors: []
- notes: |
  **MAJOR: skill.md P10 added by operator on 2026-05-11.**

  Five git commits landed on May 11 (16:53–21:58 IST) building the competitor content
  analysis pipeline:
  - 972acae: Phase 1 scaffold — competitor TikTok content analysis pipeline
  - ecc2582: Credentials pool + token rotation for Apify discovery
  - 6d983cd: Phase 2 scaffold — Arjuna video analysis with Gemini + two-tier filter
  - cc52cde: Pivot Phase 1 to hashtag-first discovery (schema v2)
  - 56dd1b6: Arjuna v2: text-only Gemini analysis + control-char fixes

  Arjuna's skill.md gained P10: "Daily competitor video analysis" — a second procedure
  path distinct from P1–P9. Key properties:
  - Cron-driven nightly at 01:00 IST (via scripts/video-analyze-batch.sh, called by Nakula)
  - Two-tier analysis: deep (baseline_multiplier ≥ 2.0) vs lightweight
  - Gemini integration: gemini-2.0-flash for transcript + hook + claims extraction
  - Idempotency key per video at idempotency-keys/video-analysis/<video_id>.json
  - 1-sec delay between Gemini calls (rate-limit awareness)
  - Key rotation across gemini.keys list from .credentials.yml

  This change was made directly by the operator (not via a Sanjaya proposal). Observer
  documents the change per the skill.md change log entry. Risk tier: behavioural (new
  procedure with external API calls and new output paths).

  **FIRST LIVE EXECUTION CONFIRMED:**
  22 idempotency key files created at
  `.claude/agents/arjuna/idempotency-keys/video-analysis/` between May 11 21:56–22:00 IST.
  All carry run_id `arjuna-20260511-162644Z-57968a` and `completed_at_utc` in that window.
  This is the first direct evidence of arjuna executing live calls (as opposed to the smoke
  test R1 which had zero tool calls).

  No JSONL session attributed to arjuna via agentSetting was found — the P10 invocation
  appears to have been scripted (via scripts/video-analyze-batch.sh) rather than a standard
  Claude Code agent session. This is consistent with P10's design: "run on cron, NOT triggered
  per-instruction." runs_observed NOT incremented (no new agentSetting-attributed session).
  days_observed +2 (May 12 + May 13 calendar days).

  **New patterns (from P10 skill.md):**

  **P10-new-A — Two-tier analysis with baseline multiplier gate (MEDIUM)**
  - Deep tier: ≥2.0× brand's 30-day mean view count → full Gemini extraction
  - Lightweight tier: <2.0× → metadata only, no Gemini call
  - Bootstrap phase: brands with <10 prior analyzed videos → default multiplier 1.0
  - Evidence: skill.md P10 two-tier table + 22 idempotency keys all marked `"tier": "deep"`
    (May 11 first run; likely brand baseline <10 videos → all defaulted to deep tier)

  **P10-new-B — Gemini key rotation on 429/5xx (LOW)**
  - Keys loaded from .credentials.yml gemini.keys list
  - Filter out REPLACE_ME placeholders before use
  - Try each key in order on failure; on all exhausted → write error to analyzed JSON, continue
  - Evidence: skill.md P10 step 2 + step 6. Not yet observed in live error recovery.

  **P10-new-C — Idempotency key per video for cost control (HIGH — confirmed in live run)**
  - Before analyzing: check idempotency-keys/video-analysis/<video_id>.json
  - If exists → skip (even on re-run of the same batch)
  - 22 keys present from first live run — this mechanism is now demonstrated operational
  - Evidence: skill.md P10 step 3 + 22 real key files

  **Skill.md change log (Observer's tracking):**

  | Date       | Changed by           | What changed                                                             |
  | ---------- | -------------------- | ------------------------------------------------------------------------ |
  | 2026-05-10 | bootstrap            | Initial skill manual (P1–P9)                                             |
  | 2026-05-11 | operator (5 commits) | P10 added: daily competitor video analysis, Gemini integration, two-tier |
  |            |                      | filter, idempotency keys, scripts/video-analyze-batch.sh                 |

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%) — scripted P10 runs not counted (no agentSetting)
  - days_observed: 4 / 18 (22%)
  - threshold_reached: false

  Note: if P10 is regularly invoked via script (not Claude Code agentSetting), the run
  counter will never reflect arjuna's actual execution volume. Observer may need a
  supplementary counting mechanism (idempotency key counts) for P10 specifically.

---

---

### 2026-05-14 — Observation Window 4 (02:00 IST)

- runs_today: 0 (no new agentSetting-attributed JSONL sessions)
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific agent sessions in this window. No new idempotency keys in
  `idempotency-keys/video-analysis/` beyond the 22 written on 2026-05-11.
  days_observed: 4 → 5.

  Git commit 902090e (2026-05-13 02:48 IST) committed `arjuna/CHANGELOG.md`,
  `arjuna/README.md`, and confirmed all 22 idempotency key files as committed artifacts.
  No new P10 script execution detected since 2026-05-11.

  **narada voice-pipeline commit context (same commit 902090e):** This commit also added
  `narada/voice-pipeline/.claude/agents/analysis-agent.md` — a 400-line modular skill
  agent inside the voice-pipeline subsystem. This confirms the voice-pipeline is a nested
  multi-agent system with at least 5 named agents (analysis-agent, data-prep,
  pipeline-orchestrator, profiling-agent, synthesis-agent) plus 25 skills. Relevant to
  narada observation window; noted here because the same commit touches arjuna CHANGELOG
  and these are being read together.

  No new patterns or errors for arjuna. Pipeline gap (jobs.yml absent) persists.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%) — scripted P10 runs still not counted (no agentSetting)
  - days_observed: 5 / 18 (27.8%)
  - threshold_reached: false

---

---

### 2026-05-15 — Observation Window 5 (02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific sessions. No new idempotency keys in
  `idempotency-keys/video-analysis/` (still 22 keys from 2026-05-11). days_observed:
  5 → 6. runs_observed: 1 (unchanged).

  No new P10 script executions detected. Pipeline gap (jobs.yml absent) persists across
  6 observation days.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 6 / 18 (33%)
  - threshold_reached: false

---

### 2026-05-16 — Observation Window 6 (Run 12 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific sessions. Idempotency keys in `idempotency-keys/video-analysis/`
  unchanged (still 22 keys from 2026-05-11). days_observed: 6 → 7. runs_observed: 1
  (unchanged).

  No new git commits touching arjuna files this window. Fleet-wide rootlabs-app commits
  and yudhishthira Supabase wiring (fff391a) do not affect arjuna.

  **Pipeline gap (jobs.yml absent) — 7th consecutive observation window.** Arjuna P10
  (video-analyze-batch.sh, 01:00 IST via Nakula) still cannot self-schedule.

  No new P10 script executions detected by file-system evidence (competitor_content/
  analyzed/ directory not present or empty). The 22 existing idempotency keys remain
  the only evidence of live arjuna execution.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 7 / 18 (38.9%)
  - threshold_reached: false

---

---

### 2026-05-18 — Observation Window 7 (Run 13 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific sessions. days_observed: 7 → 8. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged.

  **Pipeline gap (jobs.yml absent) — 8th consecutive observation window.** Arjuna P10
  (video-analyze-batch.sh, 01:00 IST via Nakula) still cannot self-schedule. This gap
  is now a `severity: critical` finding per Sahadeva 2026-W20 (the heartbeat/jobs.yml
  infrastructure item covers Nakula as a whole, which blocks arjuna scheduling).

  No new git commits touching arjuna files this window.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 8 / 18 (44.4%)
  - threshold_reached: false

---

---

### 2026-05-19 — Observation Window 8 (Run 14 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- mast_codes: []
- notes: |
  No arjuna-specific sessions. days_observed: 8 → 9. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged.

  **Pipeline gap (jobs.yml absent) — 9th consecutive observation window.** Arjuna P10
  still cannot self-schedule via Nakula. No change in status.

  No new git commits touching arjuna files this window.

  **New JSONL sessions this window:** Same as hanuman — 2 operator/self sessions only.
  No runs counted toward arjuna's runs_observed.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 9 / 18 (50%)
  - threshold_reached: false

---

### 2026-05-21 — Observation Window 9 (Run 15 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific sessions. days_observed: 9 → 11 (windows 2026-05-20 and 2026-05-21
  covered in this entry; a Sanjaya trace for 2026-05-20 shows an aborted run with
  final_outcome: null — no journals written). runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged.

  **Platform-flip context (from yudhishthira):** yudhishthira's agent.md was modified on
  2026-05-19 (unstaged) to flip from Hyperagent to local Claude Code runtime. This has no
  direct arjuna impact. Noted for fleet context.

  **REMINDERS.md additions (2026-05-14 backdated, visible this window):**
  - `anthropic-sonnet4-opus4-deprecation` — hard-deprecate of claude-sonnet-4-20250514 and
    claude-opus-4-20250514 on 2026-06-15. Arjuna is not pinned to old model versions
    (agent.md specifies claude-sonnet-4-6). No action required.
  - `anthropic-agent-sdk-credit-pool` — SDK/`claude -p` separate credit pool from 2026-06-15.
    Arjuna's P10 runs via script (video-analyze-batch.sh); if that script auths via subscription
    rather than API key, it may be affected. Surface for Kartavya before 2026-06-01.

  **Pipeline gap (jobs.yml absent) — 11th consecutive observation window.** Arjuna P10 still
  cannot self-schedule. No change in status.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 11 / 18 (61.1%)
  - threshold_reached: false

---

### 2026-05-22 — Observation Window 10 (Run 16 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna-specific sessions. days_observed: 11 → 12. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **Pipeline gap (jobs.yml absent) — 12th consecutive observation window.** Arjuna P10
  (video-analyze-batch.sh, 01:00 IST via Nakula) still cannot self-schedule.

  **REMINDERS.md credit-pool flag:** The `anthropic-agent-sdk-credit-pool` reminder
  surfaces 2026-06-01. Arjuna's P10 script invocation auth path remains unverified.
  If scripts/video-analyze-batch.sh auths via subscription rather than API key, the
  June 2026 SDK credit pool separation will affect it.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 12 / 18 (66.7%)
  - threshold_reached: false

---

### 2026-05-24 — Observation Window 11 (Run 18, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions. days_observed: 12 → 14 (covers May 23 + May 24).

  **Nakula heartbeat infra resolved (commit 193f9fd, 2026-05-22 16:27 IST).**
  The jobs.yml gap flagged 12 consecutive windows is now closed. Arjuna P10 scripts
  (22 idempotency keys written 2026-05-11) are now wired at the scheduling layer
  via nakula-run.sh. Pipeline self-scheduling is architecturally possible.

  **Portal v2 removes Yudhishthira (operator session 6ca65b2f).**
  Arjuna and Yudhishthira are independent agents; this does not directly affect Arjuna.
  Noted for ecosystem awareness.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 14 / 18 (77.8%)
  - threshold_reached: false
  - 4 more calendar days to day threshold (~2026-05-28)

---

### 2026-05-25 — Observation Window 12 (Run 19, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions. days_observed: 14 → 15. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **Sahadeva W21 audit completed (2026-05-24 10:00 IST, session 63df7d90, report 2026-W21.md).**
  Verdict: 🟢 GREEN (conditional). No new critical findings. No Bhishma violations.
  Test-set detection rate: 80% (at threshold). No arjuna-specific findings in W21.
  Arjuna's silent status is noted in the agent-silence table — journal active, last log May 11.

  **Pipeline gap (jobs.yml) — RESOLVED (confirmed W21).**
  Nakula job execution log confirms heartbeat at 67% uptime since wiring. No new arjuna
  P10 script executions observed (competitor_content/ still not materialising with new data).

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** Arjuna P10 script auth path
  still unverified. If scripts/video-analyze-batch.sh auths via subscription, June 2026
  SDK credit pool separation will affect it.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 15 / 18 (83.3%)
  - threshold_reached: false
  - **~3 calendar days to day threshold (expected ~2026-05-28)**
  - Evidence at that threshold: 1 run (smoke test + P10 idempotency keys). Confidence
    will likely score band: low–medium at threshold fire.

---

### 2026-05-26 — Observation Window 13 (Run 20, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions. days_observed: 15 → 16. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **Portal v2 rebuild (session 6ca65b2f, May 26 01:59 IST) — 18 commits, 3883 lines.**
  Operator rebuilt the POC portal from scratch in this window. Commits span
  cb100a4 through 2631a99 — all feat/fix/docs/refactor(portal). No arjuna files
  touched. No agent-spec commits in this window. Noted for fleet context.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** Arjuna P10 script auth path
  still unverified. 6 days to surface date.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 16 / 18 (88.9%)
  - threshold_reached: false
  - **~2 calendar days to day threshold (~2026-05-28)**
  - At threshold fire: evidence will score band: low–medium (1 run, sparse).

---

### 2026-05-27 — Observation Window 14 (Run 21, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions. days_observed: 16 → 17. runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **Session 6ca65b2f (portal rebuild) continued this window.** Session grew from 3883 lines
  (Run 20) to 5197 lines (+1314 new lines). 0 new tool_use events in new portion — operator
  conversation events only (portal UI feedback). No agentSetting. No arjuna files touched.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 5 days):**
  Arjuna P10 script auth path still unverified. If scripts/video-analyze-batch.sh uses
  subscription auth, Anthropic SDK credit pool separation (2026-06-15) will affect it.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 17 / 18 (94.4%)
  - threshold_reached: false
  - **~1 calendar day to day threshold (~2026-05-28)**
  - At threshold fire: evidence scores band: low–medium (1 run, sparse). Confidence floor
    (≥40) is uncertain — run_count < 5 penalty expected. Proposal fires only if score ≥ 40.

---

### 2026-05-28 — Observation Window 15 / ADAPTATION THRESHOLD REACHED (Run 22, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions this window (2026-05-27 02:00 → 2026-05-28 02:00 IST). days_observed:
  17 → **18**. runs_observed: 1 (unchanged). Idempotency keys (22 from 2026-05-11) unchanged.
  No new logs in logs/arjuna/.

  **ADAPTATION DAY THRESHOLD REACHED: days_observed = 18 (config threshold = 18 days).**

  **Confidence scoring (pre-proposal):**

  Base score: 50 (default)
  - Pattern depth: R1 MEDIUM (smoke test confirmed), R3/R4/R5/R6/R7/R8/R9 MEDIUM (smoke test
    - skill.md), P10-new-C HIGH (22 live idempotency keys confirmed), P10-new-A MEDIUM
      (skill.md + keys) → +10 for multi-source evidence
  * run_count < 5 penalty: 1 observed run → -10
  * Evidence age penalty: primary live evidence (idempotency keys) from 2026-05-11, 17 days old.
    Patterns confirmed in skill.md (static artifact, always current) → partial penalty: -5
    Total estimated score: 45 (band: medium-low, above ≥40 floor — proposal fires)

  **Pattern summary for adaptation proposal:**
  - Undocumented behavior: P10 (daily competitor video analysis via scripted invocation)
    is operator-added to skill.md and confirmed by 22 live idempotency keys. This IS documented
    in skill.md P10 — not an undocumented signal. No genuinely undocumented behaviors found.
  - Documented-but-unused patterns: R1–R9 (P1–P9 of skill.md) all exist in skill.md but
    have never been observed in a live agent-attributed session (only smoke test + scripted P10
    execution). The smoke test confirms R3/R4/R5/R6/R7/R8/R9 at statement level, but no
    live P1–P9 execution has been seen.
  - Credit pool / model deprecation flag (REMINDERS.md, surfacing 2026-06-01): arjuna's P10
    script auth path (scripts/video-analyze-batch.sh) still unverified.

  **Proposal generated:** `proposals/20260528-arjuna-adaptation-skills.md`
  Report: `reports/arjuna-2026-05-28.md`

  **Note on REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 4 days):**
  Arjuna P10 script auth path still unverified. If scripts/video-analyze-batch.sh auths
  via subscription rather than API key, the Anthropic SDK credit pool separation
  (2026-06-15) will affect it.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — **THRESHOLD REACHED**
  - threshold_reached: true
  - open_proposal_id: 20260528-arjuna-adaptation-skills

---

### 2026-05-29 — Observation Window 16 (Run 23, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions this window (2026-05-28 02:00 → 2026-05-29 02:00 IST). days_observed:
  18 (unchanged — already at threshold). runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **New JSONL sessions in window:**
  - `6ca65b2f` (portal rebuild, grew 7280 → 7499 lines, +219 lines, May 28 04:49–05:00 IST):
    21 tool_use events (Bash×16, Edit×4, AskUserQuestion×1). No agentSetting. Operator
    session — "how to get the last 30 days' videos of all the creators, whether they have
    earned money or not." Not arjuna.
  - `7eb25436` (May 29 02:00 IST): This observer run. Excluded.

  **Proposal 20260528-arjuna-adaptation-skills — 1 day open.** Procedural tier, no
  Sahadeva endorsement required. Kartavya can approve immediately.

  **REMINDERS.md credit-pool flag surfaces in 3 days (2026-06-01):**
  Arjuna P10 script auth path (scripts/video-analyze-batch.sh) still unverified before
  June 2026 SDK credit-pool separation (2026-06-15). Action window: 17 days.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260528-arjuna-adaptation-skills (1 day open)

---

### 2026-05-30 — Observation Window 17 (Run 24, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No arjuna sessions this window (2026-05-29 02:00 → 2026-05-30 02:00 IST). days_observed:
  18 → **20** (covers May 29 + May 30). runs_observed: 1 (unchanged).
  Idempotency keys (22 from 2026-05-11) unchanged. No new logs in logs/arjuna/.

  **New JSONL sessions in window:**
  - `52083bda` (May 29T11:23–18:31 IST, 571 lines, no agentSetting): Kartavya offboarding
    session — personal messages, portal access grants, auto-shutdown instructions for
    2026-06-01 23:59 IST. No Tier-0 agent attribution. Significant ecosystem context:
    Kartavya is leaving Rootlabs; portal auto-shuts Sunday 23:59 IST. Arjuna's P10 scripted
    runs may be affected if the portal or infrastructure shuts down concurrently.
  - `9b3df9af` (2026-05-26T20:30Z → 2026-05-29T11:23Z, 587 lines, no agentSetting): Observer
    session (Run 23 continuation / re-run). Excluded.
  - `c77663e1` (May 30 02:00 IST, 12 lines): This observer run. Excluded.

  **Kartavya offboarding context (ecosystem-level, affects all agents):**
  Session `52083bda` confirms Kartavya is departing Rootlabs this weekend. System is to
  auto-shut Sunday 2026-06-01 23:59 IST. This is an ecosystem-level operational change —
  all active agent scripts, crons, and portal infrastructure may cease after Sunday.
  Observer scope ends with the ecosystem. No Sanjaya action required; documented for audit.

  **Proposal 20260528-arjuna-adaptation-skills — 2 days open.** Null-change, procedural
  tier. No Sahadeva endorsement required. Kartavya can approve immediately. Given the
  offboarding timeline (Sunday 2026-06-01), this may be the last opportunity for Kartavya
  to act on this proposal.

  **REMINDERS.md deprecation alerts surface in 2 days (2026-06-01):**
  Arjuna P10 script auth path (scripts/video-analyze-batch.sh) still unverified before
  June 2026 SDK credit-pool separation (2026-06-15). Action window: 16 days remaining.
  Given offboarding, this item may not be actionable.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 20 / 18 (111%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260528-arjuna-adaptation-skills (2 days open)

---

## Calibration

_(No proposals have been applied or rejected yet. This section will populate over time.)_
