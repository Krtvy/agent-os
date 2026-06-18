---
agent: nakula
created: 2026-05-10
last_updated: 2026-05-30
mode: adaptation
runs_observed: 1
days_observed: 20
threshold_reached: true
open_proposal_id: 20260528-nakula-adaptation-skills
rejection_cooldowns: {}
---

# Journal: nakula

> Running log of observations. Append-only. New entries go at the END of the Daily Entries section.

---

## Daily Entries

### 2026-05-10 — Run 1 (02:00 IST)

- runs_today: 1
- new_patterns:
  - smoke-test-diagnostic-single-line-protocol
  - bhishma-load-gate-before-all-work
  - cron-driven-scheduling-not-interactive
  - stale-lock-cleanup-on-startup
  - log-rotation-gzip-then-delete
  - due-job-determination-with-60s-tolerance
  - per-job-lockfile-execution-with-heartbeat
  - weekly-summary-heartbeat-sunday-2355-utc
  - upstream-freshness-check-before-execution
- new_errors: []
- notes: |
  First observation of nakula. Agent directory created today (May 10 01:08 IST). Has a
  well-formed skill.md → adaptation mode. One session observed: smoke test (4a1f25ee,
  May 10 01:16 IST, 13 events, 0 tool calls).

  No logs/nakula/ directory. No jobs.yml file visible in repo root. locks/ and scripts/
  directories exist but are empty. No git history.

  Smoke test confirmed: `lockfile_present=no` — accurate (locks/ is empty). This is the
  most operationally honest smoke test response of the batch: it checked a real runtime
  state (lockfile existence) rather than only describing static config.

  All patterns are LOW confidence except smoke-test (MEDIUM).

---

#### Observed Patterns (detailed)

**K1 — Smoke-test diagnostic single-line protocol**

- Session 4a1f25ee: "Smoke test only. Reply with one line: 'nakula loaded; tier=0;
  cadence=cron-driven; lockfile_present=<yes|no>'. Do not invoke any tools."
- Response: `nakula loaded; tier=0; cadence=cron-driven; lockfile_present=no`
- Zero tool calls. Single-line, machine-parseable. 4th new-agent smoke test today; now
  5th total across the fleet (research-agent P16 + hanuman A1 + narada N1 + arjuna R1).
- Notable: `lockfile_present=no` is a runtime state check embedded in a zero-tool-call
  response. Either the agent inferred from context (locks/ is empty) or the smoke test
  prompt was designed to elicit a checkable runtime value. Suggests deeper context
  awareness during smoke tests than a purely static response.
- Confidence: MEDIUM (confirmed in smoke test).
- Source: 4a1f25ee JSONL, final assistant message.

**K2 — Bhishma-load gate before all work**

- skill.md P1: "Read `bhishma.md`. Stop on missing file." First procedure in every run.
- Now the 4th new agent with this gate (hanuman A2, narada N2, arjuna R2, nakula K2).
- The bhishma-load gate is now a fleet-wide pattern with 4 independent confirmations
  across distinct agents. Confidence on the pattern as a system norm: HIGH.
- For nakula specifically: LOW (static artifact, not yet observed in live run).
- Source: skill.md P1.

**K3 — Cron-driven scheduling: agent runs on schedule, not interactively**

- Confirmed in smoke test: `cadence=cron-driven`.
- skill.md: "Nakula owns scheduled recurring jobs defined in `jobs.yml`." The agent does
  not respond to ad-hoc user prompts in the same sense as hanuman/narada/arjuna — it is
  invoked by the scheduler when jobs are due.
- jobs.yml is the sole required input; no user-provided task description.
- Confidence: MEDIUM (confirmed in smoke test + documented in skill.md).
- Source: 4a1f25ee smoke test response; skill.md § "Inputs".

**K4 — Stale-lock cleanup on startup**

- skill.md P3: before running any jobs, check all lockfiles in `.claude/agents/nakula/locks/`.
  For each: read PID → if PID not alive (`kill -0 <pid>` fails) → delete lockfile and
  journal the cleanup.
- This prevents leftover locks from crashed sessions blocking future runs.
- Current state: locks/ is empty → P3 will be a no-op on first real run.
- Confidence: LOW (static artifact).
- Source: skill.md P3.

**K5 — Log rotation: gzip after 24h, delete after 90d**

- skill.md P4: for each file in `logs/nakula/<job>/`:
  - If older than 24h and not gzipped → gzip it.
  - If `.gz` and older than 90d → delete.
- Rotation runs before due-job determination — housekeeping first.
- Confidence: LOW (static artifact, no logs yet to rotate).
- Source: skill.md P4.

**K6 — Due-job determination with 60-second tolerance**

- skill.md P5: compute next-due time from schedule + last-run timestamp. Mark for
  execution if due within 60-second tolerance window.
- The 60s tolerance prevents clock-skew misses on frequently scheduled jobs.
- No jobs.yml present in repo → P5 will short-circuit on first real run (schema validation
  at P2 will catch the missing file).
- Confidence: LOW (static artifact; jobs.yml absent makes this unobservable currently).
- Source: skill.md P5; directory listing (no jobs.yml found).

**K7 — Per-job lockfile execution loop with heartbeat**

- skill.md P6 (per job):
  1. Acquire lock at `locks/<job>.lock` (write PID)
  2. Run upstream freshness check if configured; skip on stale with heartbeat
  3. Execute command with `timeout_minutes` cap; capture stdout+stderr to log
  4. Compute output_size_bytes
  5. Write heartbeat to `logs/heartbeat.json`
  6. On non-zero exit + `retry: false` → emit alert per `on_failure`
  7. Release lock
- Single-writer heartbeat (`logs/heartbeat.json`) updated after every job execution.
- Confidence: LOW (static artifact).
- Source: skill.md P6.

**K8 — Weekly summary heartbeat (Sunday 23:55 UTC)**

- skill.md P7: if current time is Sunday 23:55 UTC ± 5min → compute weekly summary
  (jobs_total, jobs_success, jobs_failure, jobs_skipped, uptime_pct) and append to
  `logs/heartbeat.json`.
- This is a distinct event type layered on top of per-job heartbeats.
- Confidence: LOW (static artifact; today is Sunday May 10 but ≠ 23:55 UTC; not observable
  this window).
- Source: skill.md P7.

**K9 — Upstream freshness check before job execution**

- skill.md P6.2: if `upstream_freshness_check` configured for a job → run it first.
  If upstream is stale → emit heartbeat `skipped: upstream-stale`, release lock, continue.
- This is an optional per-job guard preventing nakula from running jobs that depend on
  stale upstream data (e.g., running an email send job before the data pipeline has
  refreshed for the day).
- Confidence: LOW (static artifact; no jobs configured yet).
- Source: skill.md P6 step 2.

---

#### Operational Gap (observation)

`jobs.yml` is absent from the repository. skill.md P2 specifies that a schema error
(including presumably a missing file) will trigger a heartbeat with
`status: failure, skip_reason: jobs-yml-schema-error` and halt execution.

This means nakula cannot execute any real jobs until `jobs.yml` is created. The agent
is fully operational in terms of code/skill definition but has no work to do. Not an
error in skill.md — the skill correctly handles the missing-file case.

---

#### Log Infrastructure Status

| Source                                | Status                                           |
| ------------------------------------- | ------------------------------------------------ |
| `logs/nakula/`                        | ABSENT — no real runs have produced logs         |
| `logs/heartbeat.json`                 | ABSENT — no jobs have executed yet               |
| `nakula/locks/`                       | PRESENT but EMPTY — confirmed by smoke test      |
| `nakula/scripts/`                     | PRESENT but EMPTY                                |
| `jobs.yml`                            | ABSENT — nakula cannot run until this is created |
| Git history                           | ABSENT — no commits                              |
| Static artifacts (skill.md, agent.md) | PRESENT — primary observation source             |
| JSONL sessions (smoke test 4a1f25ee)  | PRESENT — 13 events, 0 tool calls                |

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
  No nakula sessions in this window. No job executions (jobs.yml still absent), no
  lockfile activity, no heartbeat updates, no log rotation events. days_observed
  incremented. runs_observed unchanged at 1.

  No structural changes to nakula's skill.md or agent.md observed. All K1–K9 patterns
  remain at LOW confidence except K1, K3 (MEDIUM — confirmed in smoke test).
  jobs.yml still absent — nakula remains unable to execute any real jobs.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 2 / 18 (11%)
  - threshold_reached: false

---

---

### 2026-05-13 — Observation Window 3 (02:00 IST, covering 2026-05-11 through 2026-05-13)

**Note:** May 12 02:00 IST cron fire produced no journal update. This entry covers the two-day gap.

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions in this window. jobs.yml still absent — nakula cannot execute any
  scheduled jobs. No structural changes to nakula's skill.md or agent.md in the last 5
  git commits.

  **New pipeline context (from hanuman/arjuna P10 additions):** Nakula is now referenced
  as the cron caller for both hanuman's competitor-discovery.sh (23:00 IST) and arjuna's
  video-analyze-batch.sh (01:00 IST). These scripts appear to have been placed in the repo
  but jobs.yml still has not been created. Until jobs.yml is created, Nakula cannot schedule
  either script. The pipeline is wired at the script level but not yet at the Nakula job
  scheduling level.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 4 / 18 (22%)
  - threshold_reached: false

---

---

### 2026-05-14 — Observation Window 4 (02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions. jobs.yml still absent. days_observed: 4 → 5.

  Commit 902090e added `nakula/CHANGELOG.md` and `nakula/README.md`. The CHANGELOG
  has been read as part of the general fleet commit. No new nakula-specific operational
  content.

  Pipeline context: hanuman P10 + arjuna P10 scripts still reference Nakula as the cron
  caller, but jobs.yml has now been absent for 5 observation days. The pipeline is wired
  at the script level but cannot self-schedule. No resolution visible.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 5 / 18 (27.8%)
  - threshold_reached: false

---

---

### 2026-05-15 — Observation Window 5 (02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions. jobs.yml still absent — 6 consecutive observation days. Nakula
  cannot schedule or execute any jobs until jobs.yml is created. days_observed: 5 → 6.
  runs_observed: 1 (unchanged).

  Pipeline context unchanged: hanuman P10 (competitor-discovery.sh, 23:00 IST) and arjuna
  P10 (video-analyze-batch.sh, 01:00 IST) both reference Nakula as their cron caller.
  Neither pipeline can self-schedule without jobs.yml. This is the 6th consecutive window
  flagging the jobs.yml gap.

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
  No nakula sessions. jobs.yml still absent — 7th consecutive observation window.
  days_observed: 6 → 7. runs_observed: 1 (unchanged).

  No new git commits touching nakula files. Pipeline gap unchanged: hanuman P10
  and arjuna P10 both depend on Nakula for cron scheduling; neither can self-execute
  until jobs.yml is created.

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
  No nakula sessions. jobs.yml still absent — 8th consecutive observation window.
  days_observed: 7 → 8. runs_observed: 1 (unchanged).

  **CRITICAL gap escalated by Sahadeva.** 2026-W20 §5 classifies the heartbeat infrastructure
  absence as `severity: critical`. Direct recommendation: "Create `logs/heartbeat.json` and wire
  Nakula's `jobs.yml`. This is the single highest-impact infrastructure gap." Nakula's absence
  blocks: Sanjaya scheduled runs, hanuman/arjuna pipeline scheduling, weekly heartbeat, and
  Sahadeva's ability to compute uptime %.

  Sahadeva test-set detection rate (67%) is directly reduced by TC-15 (Nakula heartbeat gap
  not detectable without heartbeat.json). Resolving this one gap would improve the detection rate.

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
  No nakula sessions. jobs.yml still absent — 9th consecutive observation window.
  days_observed: 8 → 9. runs_observed: 1 (unchanged).

  **Critical gap persists (Sahadeva severity: critical).** Heartbeat infrastructure absent.
  `logs/heartbeat.json` does not exist. Nakula has never executed a scheduled job. All
  dependent systems (Sanjaya cron, hanuman/arjuna pipeline scheduling, weekly summary,
  Sahadeva uptime %) remain unmeasurable or non-functional.

  **No new git commits touching nakula files this window.**

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
  No nakula sessions. jobs.yml still absent — 11th consecutive observation window.
  days_observed: 9 → 11. runs_observed: 1 (unchanged).

  **REMINDERS.md addition: `anthropic-agent-sdk-credit-pool` (2026-05-14, surfacing 2026-06-01).**
  Nakula's cron pattern is the primary fleet mechanism for scheduling. If it auths via
  subscription rather than API key, the new SDK credit pool separation (effective 2026-06-15)
  will affect it. Since jobs.yml does not yet exist, Nakula has never executed a scheduled
  job and this risk cannot be assessed yet. Note flagged for Kartavya.

  **Critical gap persists (Sahadeva severity: critical).** Heartbeat infrastructure absent.
  `logs/heartbeat.json` does not exist. No job has ever executed.

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
  No nakula sessions. jobs.yml still absent — 12th consecutive observation window.
  days_observed: 11 → 12. runs_observed: 1 (unchanged).

  **Critical gap persists (Sahadeva severity: critical).** Heartbeat infrastructure absent.
  `logs/heartbeat.json` does not exist. No job has ever executed. The 90-second portal
  timeout observed in yudhishthira (acf336a8 session) is an indirect signal that the
  pipeline infrastructure has timing constraints — if Nakula were wired, it would provide
  a scheduling layer that avoids portal timeout races. Noted for context.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** Nakula's cron auth path
  must be verified before June 2026 if jobs.yml is ever created.

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
  No nakula sessions. days_observed: 12 → 14 (covers May 23 + May 24).

  **W20 CRITICAL FINDING #1 RESOLVED — Heartbeat infrastructure wired (commit 193f9fd, 2026-05-22 16:27 IST).**
  jobs.yml created at `nakula/jobs.yml`. Two jobs defined:
  - sanjaya: "0 2 \* \* \*" (02:00 IST daily) → run_observer.sh via nakula-run.sh wrapper
  - sahadeva: "0 10 \* \* 0" (10:00 IST Sunday) → run_sahadeva.sh via nakula-run.sh wrapper
    nakula-run.sh: shell wrapper with lockfile, bounded timeout (sanjaya: 30m, sahadeva: 45m),
    contract-conformant heartbeat emission on exit. Crontab now invokes the wrapper.
    validate-jobs.sh: schema checker for jobs.yml entries.
    First real-run heartbeat written 2026-05-22T10:33:49Z (sanjaya, exit 0 — Run 17).
    TC-15 will pass on Sahadeva's next audit. Inbox updated 2026-05-22T10:55:00Z: resolved.

  **W20 CRITICAL FINDING #2 — Vyasa dormancy — deferred by decision (commit 193f9fd).**
  Documented in `_meta/conductor/README.md`: "Kartavya is direct approver until Sanjaya
  approval-rate calibration data exists." Agent stays defined; activation is a config-only
  change. This is a documented deferral, not a gap. Inbox updated 2026-05-22T09:48:00Z: resolved.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** nakula-run.sh auth pattern
  should be verified before June 2026. If subscription auth is used, the Anthropic SDK
  credit pool will separate from 2026-06-15. Carried forward.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 14 / 18 (77.8%)
  - threshold_reached: false
  - 4 more calendar days to day threshold (expected ~2026-05-28 if daily observation)

---

### 2026-05-25 — Observation Window 12 (Run 19, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions. days_observed: 14 → 15. runs_observed: 1 (unchanged).

  **Sahadeva W21 audit (2026-05-24 10:00 IST) — nakula-specific findings:**
  Heartbeat table in W21 §5 shows:
  - nakula-20260523-203000Z-845820: sanjaya job, exit 0 ✅ (IST May 24 02:00 = Run 18)
  - nakula-20260524-043001Z-52c47c: sahadeva job, in-progress (W21 run itself)
  - Missed run: 2026-05-22 20:30 UTC (May 23 02:00 IST) — crontab transition gap, first night after wiring.
  - Uptime since wiring: 67% (2/3 runs completed).

  **Weekly summary heartbeat (P7 — Sunday 23:55 UTC):** W21 notes this has not yet been
  generated. First eligible Sunday after wiring was 2026-05-24; expected output at 23:55 UTC
  tonight (2026-05-24T23:55Z = 2026-05-25 05:25 IST). Observer will check next run.

  W21 §9 rec #4: "Verify crontab stability. Sanjaya missed its May 23 02:00 IST scheduled
  run. Run `crontab -l` and check the Nakula cron entry."

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** nakula-run.sh auth pattern
  still unverified before June 2026.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 15 / 18 (83.3%)
  - threshold_reached: false
  - ~3 calendar days to day threshold (~2026-05-28)
  - Note: adaptation proposal will fire at ~May 28. Evidence is sparse (1 smoke test run).
    Confidence scoring will likely yield band: low at threshold fire.

---

### 2026-05-26 — Observation Window 13 (Run 20, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions. days_observed: 15 → 16. runs_observed: 1 (unchanged).

  **Heartbeat check:** Last heartbeat entry in logs/heartbeat.json is
  `nakula-20260524-203000Z-7e9bf6` (Run 19, exit=0, May 25 02:00 IST). Run 20's
  heartbeat will be written when nakula-run.sh exits after this session.
  sanjaya.lock present with PID 11518 (this run, acquired by nakula-run.sh).

  **Portal v2 rebuild (6ca65b2f) — no nakula impact.** 18 portal commits in this window.
  No nakula or jobs.yml changes.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01):** nakula-run.sh auth pattern
  still unverified. 6 days to surface date.

  **Weekly summary heartbeat (P7 — Sunday 23:55 UTC):** The first eligible Sunday after
  wiring was 2026-05-24 23:55 UTC. W21 noted this was expected then. Observer will check
  for the weekly summary entry in heartbeat.json next window (if present, confirms K8).

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 16 / 18 (88.9%)
  - threshold_reached: false
  - **~2 calendar days to day threshold (~2026-05-28)**

---

### 2026-05-27 — Observation Window 14 (Run 21, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions. days_observed: 16 → 17. runs_observed: 1 (unchanged).

  **Heartbeat check:** logs/heartbeat.json contains a single entry:
  `nakula-20260525-203001Z-bdd158` (started_at: 2026-05-25T20:30:01Z, ended_at: 2026-05-25T21:00:01Z,
  exit_code: 0, job_name: sanjaya). This is the Run 20 heartbeat — the sanjaya job completed
  successfully. Run 21's heartbeat will be written by nakula-run.sh after this session closes.

  **K8 — Weekly summary heartbeat ABSENT.** The first eligible Sunday after Nakula wiring
  (2026-05-22) was 2026-05-24 23:55 UTC = May 25 05:25 IST. The second eligible Sunday
  would be 2026-05-31. No weekly-summary entry is present in heartbeat.json. This either
  means: (a) jobs.yml only has sanjaya + sahadeva jobs and the weekly-summary heartbeat
  (K8/P7) is not separately wired, or (b) nakula-run.sh doesn't yet implement the K8
  Sunday 23:55 UTC heartbeat. Flagging for Sahadeva's next audit (2026-05-31).

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 5 days):**
  nakula-run.sh auth pattern still unverified before June 2026.

  **Sahadeva inbox check:** Both W20 critical findings (`heartbeat absent`, `Vyasa dormant`)
  now show `resolved` status. Inbox clear of open criticals.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 17 / 18 (94.4%)
  - threshold_reached: false
  - **~1 calendar day to day threshold (~2026-05-28)**
  - At threshold: evidence sparse (1 smoke test run). Confidence band: low expected.

---

### 2026-05-28 — Observation Window 15 / ADAPTATION THRESHOLD REACHED (Run 22, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions this window (2026-05-27 02:00 → 2026-05-28 02:00 IST). days_observed:
  17 → **18**. runs_observed: 1 (unchanged).

  **ADAPTATION DAY THRESHOLD REACHED: days_observed = 18 (config threshold = 18 days).**

  **Confidence scoring (pre-proposal):**

  Base score: 50 (default)
  - K1 MEDIUM (smoke test confirmed cadence=cron-driven, lockfile_present=no — runtime-aware)
  - K3 MEDIUM (cron-driven scheduling confirmed)
  - jobs.yml now present (wired 2026-05-22), heartbeat.json confirmed (exit 0 three times)
    → K7 partially confirmed (job execution loop is real), K4/K5 operational
    +5 for live infrastructure evidence
  * run_count < 5 penalty: 1 observed run → -10
  * K8 weekly summary heartbeat absent (not confirmed, possible unimplemented) → -5
    Total estimated score: 40 (band: low, exactly at ≥40 floor — proposal fires)

  **Pattern summary for adaptation proposal:**
  - Documented-but-not-yet-confirmed: K8 (weekly summary heartbeat Sunday 23:55 UTC) —
    first eligible Sunday was 2026-05-24; no entry in heartbeat.json. Either not implemented
    or not wired in jobs.yml. This is a documented skill that has not been observed running.
    3 windows of absence (Windows 13, 14, 15) qualifies as documented-but-unused signal.
  - K4 (stale-lock cleanup), K5 (log rotation), K6 (due-job determination), K9 (upstream
    freshness check) are all documented procedures never yet observed (no live nakula sessions).
    These are structural completions, not misfirings.
  - No genuinely undocumented behavior detected.
  - No recurring failures detected.

  **Proposal generated:** `proposals/20260528-nakula-adaptation-skills.md`
  Report: `reports/nakula-2026-05-28.md`

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 4 days):**
  nakula-run.sh auth path still unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — **THRESHOLD REACHED**
  - threshold_reached: true
  - open_proposal_id: 20260528-nakula-adaptation-skills

---

### 2026-05-29 — Observation Window 16 (Run 23, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions this window (2026-05-28 02:00 → 2026-05-29 02:00 IST). days_observed:
  18 (unchanged). runs_observed: 1 (unchanged).

  **Heartbeat status:**
  heartbeat.json last entry: `nakula-20260527-203000Z-62d612`, started_at 2026-05-27T20:30Z
  (May 28 02:00 IST = Run 22). No new nakula heartbeat written since Run 22. Today's sanjaya
  run was manually invoked by Kartavya (no parent_run_id in trace, no heartbeat for today yet).
  Nakula cron fires daily at 20:30Z — if it fires today it will attempt to invoke sanjaya while
  this manual run is in progress. Duplicate-run concern noted.

  **K8 weekly summary heartbeat — still absent.** Third eligible Sunday (2026-05-31) is 2 days
  away. Proposal `20260528-nakula-adaptation-skills` surfaces this for action.

  **New JSONL sessions in window:** `6ca65b2f` operator portal, `7eb25436` observer. No nakula
  attribution.

  **Proposal 20260528-nakula-adaptation-skills — 1 day open.** Procedural tier, no
  Sahadeva endorsement required. Kartavya can approve immediately.

  **REMINDERS.md credit-pool flag surfaces in 3 days (2026-06-01):**
  nakula-run.sh auth path still unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260528-nakula-adaptation-skills (1 day open)

---

### 2026-05-30 — Observation Window 17 (Run 24, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No nakula sessions this window (2026-05-29 02:00 → 2026-05-30 02:00 IST). days_observed:
  18 → **20**. runs_observed: 1 (unchanged).

  **Heartbeat status — today's window:**
  Nakula cron fires at 20:30Z (daily). Last heartbeat entry: `nakula-20260527-203000Z-62d612`
  (Run 22, 2026-05-28 02:00 IST). Runs 23 and 24 have been manually invoked by Kartavya —
  no nakula parent_run_id in today's trace (`c77663e1`). This means nakula cron may or may
  not have fired in this window. Heartbeat.json not re-inspected this run (no write access to
  worker files without proposal approval); relying on Run 23's last-known state.

  **K8 weekly summary heartbeat — third eligible Sunday is TOMORROW (2026-05-31).**
  The cron at `"30 20 * * *"` runs daily, not just Sundays — K8 requires an internal
  Sunday-time branch. Proposal `20260528-nakula-adaptation-skills` surfaces this. Sahadeva
  W22 (2026-05-31 10:00 IST) will be the first Sahadeva audit where the K8 gap is directly
  checkable.

  **Kartavya offboarding (ecosystem-level event):**
  Session `52083bda` confirms system auto-shutdown Sunday 2026-06-01 23:59 IST. Nakula is
  the cron runner for the entire observer fleet — shutdown of Nakula ends all scheduled
  observation runs. If shutdown proceeds as planned, this may be Nakula's last observation
  window before ecosystem cessation.

  **New JSONL sessions in window:** `52083bda` (Kartavya offboarding, no agentSetting),
  `9b3df9af` (observer), `c77663e1` (this run). No nakula attribution.

  **Proposal 20260528-nakula-adaptation-skills — 2 days open.** Procedural tier, no
  Sahadeva endorsement required. Kartavya can approve immediately. K8 resolution should
  happen before Sunday shutdown — otherwise the K8 gap persists in any future restart.

  **REMINDERS.md credit-pool flag surfaces tomorrow (2026-06-01):**
  nakula-run.sh auth path still unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 20 / 18 (111%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260528-nakula-adaptation-skills (2 days open)

---

## Calibration

_(No proposals have been applied or rejected yet. This section will populate over time.)_
