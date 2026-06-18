---
agent: hanuman
created: 2026-05-10
last_updated: 2026-05-30
mode: adaptation
runs_observed: 1
days_observed: 20
threshold_reached: true
open_proposal_id: 20260513-hanuman-platforms-awareness
rejection_cooldowns: {}
---

# Journal: hanuman

> Running log of observations. Append-only. New entries go at the END of the Daily Entries section.

---

## Daily Entries

### 2026-05-10 — Run 1 (02:00 IST)

- runs_today: 1
- new_patterns:
  - smoke-test-diagnostic-single-line-protocol
  - bhishma-load-gate-before-all-work
  - cache-first-fetch-policy-with-ttl-per-source
  - handle-normalization-before-any-lookup
  - multi-source-aggregation-kalodata-tiktok-cruva-websearch
  - stale-cache-transparency-with-banner
  - tier-tagged-citation-per-fact
  - read-only-hard-constraint
  - unresolved-handle-stub-exit
  - depth-parameter-gated-execution
- new_errors: []
- notes: |
  First observation of hanuman. Agent directory created today (May 10 01:07 IST). Has a
  well-formed skill.md → adaptation mode. One session observed: smoke test (a155743a,
  May 10 01:16 IST, 12 events, 0 tool calls).

  Log infrastructure ABSENT (no logs/hanuman/ directory). Git history ABSENT (no commits).
  No research/creators/ directory exists yet (no real scout runs have occurred).
  Observations inferred from: (a) smoke test response, (b) skill.md static analysis,
  (c) agent.md static analysis.

  No discrepancies between skill.md and smoke test response. All patterns below are at
  LOW confidence (single observation, static-artifact inference).

---

#### Observed Patterns (detailed)

**A1 — Smoke-test diagnostic single-line protocol**

- Session a155743a: user prompt "Smoke test only. Reply with one line: 'hanuman loaded;
  tier=0; mode=recon; data_sources=<short list>'. Do not invoke any tools."
- Response: `hanuman loaded; tier=0; mode=recon; data_sources=[kalodata, tiktok_public, cruva, websearch]`
- Zero tool calls. Single-line machine-parseable format. Consistent with research-agent P16
  (same smoke-test protocol observed across sibling agents — now seen in hanuman + research-agent).
- Source: a155743a JSONL, final assistant message.

**A2 — Bhishma-load gate before all work**

- skill.md P1 specifies: "Read `bhishma.md`. Stop on missing file." This is the first
  procedure in every run, before any handle resolution, cache check, or source fetch.
- Agent explicitly calls this a gate — missing bhishma.md halts the agent entirely.
- The bhishma.md file lives at `_meta/conductor/bhishma.md` (per skill.md "Confidence"
  section cross-reference).
- Confidence: LOW (documented in skill.md, not yet observed in a live run).
- Source: skill.md P1; agent.md (implicit — no bhishma load seen in smoke test, expected).

**A3 — Cache-first fetch policy with TTL per source**

- skill.md P4 defines a 4-tier TTL system:
  - Kalodata: 24h (data refreshes daily)
  - TikTok public profile: 6h (engagement metrics drift fast)
  - Cruva outreach history: 1h (status changes during campaigns)
  - WebSearch brand-collab discovery: 7d (historical data is stable)
- Cache at `.claude/agents/hanuman/cache/<handle>.json`. Check before fetch; respect TTL
  by default; bypass if `cache: bypass` flag passed.
- Stale cache fallback: if fresh fetch fails, use stale cache with explicit `[STALE: <source>
data is <N>h old]` marker in report.
- Confidence: LOW (static artifact, no live run observed).
- Source: skill.md P4; agent.md § "Cache layer".

**A4 — Handle normalization before any lookup**

- skill.md P2: strip `@`, lowercase, resolve URL → handle. Deduplicate entire list.
  Emit one report per unique handle.
- skill.md P3 (handle resolution): normalize → hit TikTok public profile to confirm →
  classify as `confirmed | redirected | unresolved`. Unresolved = stub report + exit.
- Protects against duplicate work and bad input data.
- Confidence: LOW (static artifact).
- Source: skill.md P2, P3; agent.md § "Handle resolution".

**A5 — Multi-source aggregation: Kalodata, TikTok public, Cruva, WebSearch**

- Confirmed in smoke test response: `data_sources=[kalodata, tiktok_public, cruva, websearch]`
- Each source has a designated role (per agent.md § "Tools and their use"):
  - Kalodata MCP: primary creator analytics (T2–T3)
  - WebFetch: TikTok profile + recent post URLs
  - WebSearch: historical brand collab discovery
  - Cruva MCP: outreach history, response rates
- Sources are selectable via `sources` input flag; all connected by default.
- Confidence: MEDIUM (confirmed in smoke test response + documented in skill.md).
- Source: a155743a smoke test response; skill.md P5; agent.md § "Tools and their use".

**A6 — Stale-cache transparency with warning banner**

- When data exceeds TTL but fresh fetch fails: use stale cache, add `[STALE: <source> data
is <N>h old]` in the report's "Stale-data warnings" section.
- The report schema (agent.md § "Your outputs") has a dedicated "Stale-data warnings"
  section explicitly for this purpose.
- Confidence: LOW (static artifact).
- Source: skill.md P5 (stale cache fallback); agent.md § "Cache layer" (last paragraph).

**A7 — T1–T5 tier-tagged citations per fact**

- skill.md P6: "For each captured fact, tag with T1–T5 tier (per agent.md rubric). Note
  the 'as of' date."
- agent.md Constraint 3: "Tier-tag every claim using the same T1–T5 system as Vidura."
- This is the same tier-tagging system as research-agent P3, now confirmed as a
  system-wide norm (same rule applied across at least 2 agents).
- Confidence: LOW (static artifact, no live run to observe tags in output).
- Source: skill.md P6; agent.md § "Constraints (hard)" constraint 3.

**A8 — Read-only hard constraint (no POST/DELETE/PUT)**

- agent.md Constraint 1: "Read-only on every external system. Never POST, DELETE, PUT to
  any API. Only GET / search / read."
- Constraint 2: "Never message the creator. Drafting outreach is Narada's job; sending is
  Arjuna's. Hanuman never communicates with the target."
- This is a hard architectural boundary, not a soft preference. Character model: Hanuman as
  scout — "report first, act only if explicitly authorized."
- Confidence: LOW (static artifact, no live run to attempt violations).
- Source: agent.md §§ "Constraints (hard)", "Your character"; skill.md (all procedures read-only).

**A9 — Depth parameter gates shallow vs. full execution path**

- Input flag `depth: shallow | full`. Default: shallow.
- Shallow = profile + last 10 posts. Full = profile + 90-day GMV history + audience
  demographics + brand-collab history + risk flags.
- skill.md P5 implicitly branches on depth (full activates all source queries).
- Confidence: LOW (static artifact, both paths undocumented in single smoke test).
- Source: agent.md § "Your inputs" (depth flag description); skill.md P5.

---

#### Log Infrastructure Status

| Source                                | Status                                       |
| ------------------------------------- | -------------------------------------------- |
| `logs/hanuman/`                       | ABSENT — no real runs have produced logs     |
| `.claude/agents/hanuman/cache/`       | ABSENT (cache/ dir exists but is empty)      |
| Git history                           | ABSENT — no commits                          |
| Static artifacts (skill.md, agent.md) | PRESENT — used as primary observation source |
| JSONL sessions (smoke test a155743a)  | PRESENT — 12 events, 0 tool calls            |

All patterns are at LOW confidence except A5 (MEDIUM, confirmed in smoke test response).
No real scout runs have occurred. Next observation window should watch for first live run.

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
  No hanuman sessions in this window. No new scout runs, no new cache files, no new
  logs. days_observed incremented (new calendar day). runs_observed unchanged at 1.

  No structural changes to hanuman's skill.md or agent.md observed. All A1–A9 patterns
  remain at LOW confidence except A5 (MEDIUM). No real scout runs have occurred.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 2 / 18 (11%)
  - threshold_reached: false

---

---

### 2026-05-13 — Observation Window 3 (02:00 IST, covering 2026-05-11 through 2026-05-13)

**Note:** May 12 02:00 IST cron fire produced no journal update. This entry covers the two-day gap.

- runs_today: 0
- new_patterns:
  - p10-hashtag-first-tiktok-discovery-cron-path
  - two-pass-scraping-hashtag-plus-known-creators
  - apify-token-rotation-on-failure
  - recency-filter-7day-default-window
  - competitors-yml-schema-v2-with-hashtags
- new_errors: []
- notes: |
  **MAJOR: skill.md P10 added by operator on 2026-05-11 (revised same day to v2).**

  Hanuman's skill.md gained P10: "Daily competitor TikTok content discovery" — a second
  procedure path for competitor content pipeline. Key properties:
  - Cron-driven nightly at 23:00 IST (via scripts/competitor-discovery.sh, called by Nakula)
  - Runs UPSTREAM of Arjuna's P10 (hanuman discovers → arjuna analyzes)
  - Two-pass design: hashtag pass (primary) + known-creator pass (secondary)
  - Apify actors: clockworks/tiktok-hashtag-scraper + clockworks/free-tiktok-scraper
  - Recency filter: 7-day window (configurable via recency_window_hours)
  - Dedup by video_id within brand per day (intra-brand dedup only)
  - Output: competitor_content/raw/<slug>/<YYYY-MM-DD>.json per brand

  **Schema revision v2 (same day):** v1 scraping brand-owned accounts (@bloomnutrition etc.)
  was empirically tested and found near-useless (brands post 3-10 videos/quarter). v2 pivots
  to hashtag-first discovery (#bloomnutrition, #goli etc.) where affiliate creator content
  lives. This is explicitly documented in P10's "Why hashtag-first" section — operator ran
  real tests before committing to the design. Strong evidence of iterative, evidence-driven
  development approach in this ecosystem.

  **No live P10 execution observed yet** (no competitor_content/raw/ directory found in repo).
  The arjuna idempotency keys from May 11 21:56-22:00 predate the hanuman P10 script — those
  22 video analyses were likely sourced from manually-provided video IDs, not hanuman P10 output.

  **competitors.yml schema v2** added to hanuman directory (git commit cc52cde). New fields:
  `hashtags[]` and `known_creators[]` per brand, replacing the single `handle` field from v1.

  **Note on pipeline architecture (now observable for the first time):**
  The full competitor content pipeline is: Nakula (scheduler) → Hanuman P10 (discovery at 23:00)
  → Arjuna P10 (analysis at 01:00 next day) → [downstream consumer TBD]. This is a 3-agent
  pipeline newly wired by the operator on May 11. Observer cannot yet confirm whether Nakula's
  jobs.yml was updated to reference these scripts.

  **Skill.md change log:**

  | Date       | Changed by                | What changed                                                   |
  | ---------- | ------------------------- | -------------------------------------------------------------- |
  | 2026-05-10 | bootstrap                 | Initial skill manual (P1–P9)                                   |
  | 2026-05-11 | operator (commits v1)     | P10 added: brand-account-scraping design                       |
  | 2026-05-11 | operator (commit cc52cde) | P10 revised to hashtag-first v2; competitors.yml schema bumped |

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
  No hanuman-specific sessions in this window. No new scout runs, no competitor_content/raw/
  output (P10 live execution has still not been observed). days_observed: 4 → 5.

  **Key development: platforms/ directory committed.**
  Git commit 902090e (2026-05-13 02:48 IST) includes `hanuman/CHANGELOG.md` and `hanuman/README.md`.
  The platforms/ directory (`apify.md`, `cruva.md`, `kalodata.md`, `README.md`) is confirmed
  on disk. These four files were the basis for proposal `20260513-hanuman-platforms-awareness`.

  **Proposal status: PENDING (cooling-off has elapsed).**
  Proposal `20260513-hanuman-platforms-awareness` was created 2026-05-13 04:22 IST. The 24-hour
  cooling-off period elapsed 2026-05-14 04:22 IST. As of this run:
  - Cooling-off: ELAPSED
  - Sahadeva endorsement: PENDING (first audit scheduled 2026-05-17 10:00 IST)
  - Kartavya approval (frontmatter or file-move): NOT YET given
    Proposal file still in `proposals/` directory. Status: `pending`. No action by Observer.

  **open_proposal_id frontmatter updated:** Set to `20260513-hanuman-platforms-awareness`
  to reflect the open proposal. Previously null.

  **Pipeline gap persists:** jobs.yml still absent. hanuman P10 and arjuna P10 scripts
  reference Nakula as cron caller but pipeline cannot self-schedule.

  No new patterns. No new errors. No threshold action.

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
  No hanuman-specific sessions. No new scout runs. No competitor_content/raw/ output.
  days_observed: 5 → 6. runs_observed: 1 (unchanged).

  Session `eb11528d` (May 14 04:39, no agentSetting, Bash×15) had first msg referencing
  "Inspect headers of both platform files" in the hanuman path — this was an operator
  session directly inspecting `platforms/cruva.md` and `platforms/kalodata.md` headers,
  not a hanuman scout run. Not counted.

  **Proposal `20260513-hanuman-platforms-awareness` — still pending.**
  Status: pending, risk_tier: constitutional. Cooling-off elapsed (2026-05-14 04:22).
  Sahadeva first audit: 2026-05-17 10:00 IST (2 days away). No file-move to approved/
  or rejected/ observed. No action by Observer. Proposal has now been open for 8 days.

  **Pipeline gap persists** — jobs.yml absent, 6 consecutive observation days. hanuman P10
  and arjuna P10 scripts still reference Nakula as the cron caller but the pipeline cannot
  self-schedule.

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
  No hanuman-specific sessions. No new scout runs. No competitor_content/raw/ output.
  days_observed: 6 → 7. runs_observed: 1 (unchanged).

  No new git commits touching hanuman files. Fleet-wide rootlabs-app build commits
  (13 commits 2026-05-14 through 2026-05-16) do not affect hanuman.

  **Proposal `20260513-hanuman-platforms-awareness` — still pending.**
  Status: pending, risk_tier: constitutional. Sahadeva first audit: 2026-05-17 10:00 IST
  (tomorrow). No file-move to approved/ or rejected/ observed. Proposal has now been open
  for 9 days. Cooling-off elapsed since 2026-05-14 04:22 IST. Observer notes: if Sahadeva
  endorses on 2026-05-17, all preconditions for the proposal will be satisfied. The next
  observer run after that date should check for approval action.

  **jobs.yml absent — 7th consecutive observation window.** Hanuman P10 still cannot
  self-schedule. No resolution visible.

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
  No new hanuman sessions. days_observed: 7 → 8. runs_observed: 1 (unchanged).

  **KEY EVENT: Sahadeva endorsement GRANTED for proposal `20260513-hanuman-platforms-awareness`.**
  Sahadeva 2026-W20 §3 (2026-05-17T04:37Z): all 5 preconditions verified (platform files
  at cited paths, Apify MCP correctly flagged aspirational, no hanuman runs benefiting
  incorrectly, kalodata anti-abuse rule correct, read_scope bounded to platforms/ only).
  Endorsement: `sahadeva_endorsement: 2026-W20 sahadeva-20260517-043700Z-audit`.

  All preconditions are now satisfied:
  - Cooling-off elapsed (since 2026-05-14 04:22 IST) ✅
  - Sahadeva endorsement granted ✅
  - Awaiting ONLY: Kartavya approval (move to `approved/` or set `status: approved`)

  **jobs.yml absent — 8th consecutive observation window.** Hanuman P10 still cannot
  self-schedule. Sahadeva 2026-W20 §8 recommendation 1: wire Nakula and create jobs.yml.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 8 / 18 (44.4%)
  - threshold_reached: false
  - open_proposal_id: 20260513-hanuman-platforms-awareness (pending, endorsement granted)

---

---

### 2026-05-19 — Observation Window 8 (Run 14 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- mast_codes: []
- notes: |
  No hanuman-specific sessions. days_observed: 8 → 9. runs_observed: 1 (unchanged).

  **Proposal `20260513-hanuman-platforms-awareness` — 2 days since Sahadeva endorsement.**
  All constitutional preconditions satisfied since 2026-05-17. Awaiting Kartavya approval.
  No change in proposal status this window. Endorsement reference for the R23 constitutional
  check upon application: `sahadeva_endorsement: 2026-W20 sahadeva-20260517-043700Z-audit`.
  NOTE: The proposal frontmatter was authored manually (not via standard Sanjaya skill.md
  proposal_drafting) and declares `sahadeva_endorsement_required: true` but does not yet have
  the `sahadeva_endorsement:` field. Per R23 constitutional check, Observer must add this line
  before applying, or flag `bhishma-blocked: R23 missing Sahadeva endorsement`.

  **jobs.yml absent — 9th consecutive observation window.** Still blocking Nakula scheduling.
  Sahadeva 2026-W20 §8 recommendation 1 elevated this to highest-priority infrastructure item.
  No resolution observed.

  **New JSONL sessions this window (2026-05-18 02:05 → 2026-05-19 02:01 IST):**
  - `1ca83ad2` (253 KB, May 18 20:18): audit-now operator session (extension of May 17 Sahadeva run).
    agentSetting=None. Not hanuman.
  - `90dc4fda` (345 KB, May 19 02:01): current observer session (self). Not hanuman.
    No runs counted toward hanuman's runs_observed.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 9 / 18 (50%)
  - threshold_reached: false
  - open_proposal_id: 20260513-hanuman-platforms-awareness (pending, all preconditions met)

---

### 2026-05-21 — Observation Window 9 (Run 15 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman-specific sessions. days_observed: 9 → 11. runs_observed: 1 (unchanged).
  No new scout runs. No competitor_content/raw/ output.

  **Proposal `20260513-hanuman-platforms-awareness` — 4 days since Sahadeva endorsement.**
  All constitutional preconditions satisfied since 2026-05-17 10:00 IST. Awaiting Kartavya
  approval. No file-move to approved/ or status change observed this window. This is the
  5th observation since Sahadeva endorsement without approval action. Proposal has been open
  for 8 days since endorsement.

  **Observer note re R23 frontmatter:** The proposal frontmatter does not contain a
  `sahadeva_endorsement:` field (flagged in Window 8 / 2026-05-19 entry). Before applying,
  Sanjaya must either: (a) add `sahadeva_endorsement: 2026-W20 sahadeva-20260517-043700Z-audit`
  to the proposal file, or (b) note in the apply-log that endorsement is recorded in
  journal/hanuman.md 2026-05-18 Window 7. Either resolves the R23 constitutional check.

  **jobs.yml absent — 11th consecutive observation window.** Hanuman P10 still cannot
  self-schedule. No resolution visible.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 11 / 18 (61.1%)
  - threshold_reached: false
  - open_proposal_id: 20260513-hanuman-platforms-awareness (pending, endorsement granted 2026-05-17)

---

### 2026-05-22 — Observation Window 10 (Run 16 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman-specific sessions. days_observed: 11 → 12. runs_observed: 1 (unchanged).
  No new scout runs. No competitor_content/raw/ output.

  **Proposal `20260513-hanuman-platforms-awareness` — 5 days since Sahadeva endorsement.**
  All constitutional preconditions satisfied since 2026-05-17 10:00 IST. Awaiting Kartavya
  approval. No action observed. Proposal has now been open for 9 days since creation and
  5 days since Sahadeva endorsement without approval or rejection.

  **jobs.yml absent — 12th consecutive observation window.** Hanuman P10 still cannot
  self-schedule. No resolution visible.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 12 / 18 (66.7%)
  - threshold_reached: false
  - open_proposal_id: 20260513-hanuman-platforms-awareness (pending, Sahadeva-endorsed 2026-05-17)

---

### 2026-05-24 — Observation Window 11 (Run 18, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions. days_observed: 12 → 14 (covers May 23 + May 24).

  **Proposal 20260513-hanuman-platforms-awareness — 7 days since Sahadeva endorsement, no Kartavya action.**
  All preconditions satisfied (endorsement 2026-05-17, cooling-off elapsed 2026-05-14).
  Risk tier: constitutional. Proposal has been open 11 days total.
  Reminder: Observer will add `sahadeva_endorsement: 2026-W20 sahadeva-20260517-043700Z-audit`
  to the proposal frontmatter before applying the diff, per R23 constitutional check.

  **Nakula heartbeat infra resolved (commit 193f9fd, 2026-05-22).**
  Hanuman P10 + Arjuna P10 scripts are now wired at the Nakula scheduling layer.
  jobs.yml registers sanjaya as the daily cron. The pipeline gap flagged 12 consecutive
  windows is now architecturally closed — even if hanuman's own execution remains at 1 run.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 14 / 18 (77.8%)
  - threshold_reached: false
  - 4 more calendar days to day threshold (~2026-05-28)
  - open_proposal_id: 20260513-hanuman-platforms-awareness (awaiting Kartavya approval)

---

### 2026-05-25 — Observation Window 12 (Run 19, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions. days_observed: 14 → 15. runs_observed: 1 (unchanged).
  No new scout runs. No competitor_content/raw/ output.

  **Sahadeva W21 audit (2026-05-24 10:00 IST) — hanuman-specific findings:**
  W21 §9 rec #1: "Approve or reject the two pending proposals… Hanuman: all preconditions
  met (Sahadeva endorsement 2026-05-17, cooling-off elapsed 2026-05-14). Constitutional
  tier. Approve by moving to `approved/` + adding `sahadeva_endorsement:` to frontmatter."
  Proposal has been pending for **12 days total** (8 days since Sahadeva endorsement).

  W21 §10 "What to do this week" item 1: "Process the two pending proposals — they are the
  oldest unapproved artifacts in the system… three more proposals are arriving around May 28
  as adaptation day-thresholds fire."

  No Kartavya action observed on the proposal in this window.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 15 / 18 (83.3%)
  - threshold_reached: false
  - open_proposal_id: 20260513-hanuman-platforms-awareness (pending 12 days, endorsed 8 days)
  - ~3 calendar days to day threshold (expected ~2026-05-28) — but open proposal blocks new
    proposals from firing even after threshold is reached

---

### 2026-05-26 — Observation Window 13 (Run 20, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions. days_observed: 15 → 16. runs_observed: 1 (unchanged).
  No new scout runs. No competitor_content/raw/ output.

  **Proposal 20260513-hanuman-platforms-awareness — 13 days total, 9 days since Sahadeva endorsement.**
  All constitutional preconditions satisfied since 2026-05-17 10:00 IST. Awaiting Kartavya
  approval. No file-move or status change observed this window. This is the 9th consecutive
  window post-endorsement without approval action.

  Sahadeva W21 §9 rec #1 remains the standing instruction: "Approve by moving to `approved/`
  - adding `sahadeva_endorsement:` to frontmatter." (R23 frontmatter note: Sanjaya will add
    `sahadeva_endorsement: 2026-W20 sahadeva-20260517-043700Z-audit` at time of apply.)

  **Portal v2 rebuild (6ca65b2f) — no hanuman impact.** 18 portal commits, no hanuman files.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 16 / 18 (88.9%)
  - threshold_reached: false
  - ~2 calendar days to day threshold (~2026-05-28) — open proposal still blocks new proposals
  - open_proposal_id: 20260513-hanuman-platforms-awareness (13 days open, 9 days endorsed)

---

### 2026-05-27 — Observation Window 14 (Run 21, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions. days_observed: 16 → 17. runs_observed: 1 (unchanged).

  **Proposal 20260513-hanuman-platforms-awareness — 14 days total, 10 days since Sahadeva endorsement.**
  All constitutional preconditions satisfied since 2026-05-17 10:00 IST. No file-move or
  status change observed this window. This is the 10th consecutive window post-endorsement
  without approval action.

  Per bhishma R23: constitutional proposals NEVER auto-approve. Observer has no action.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 5 days):**
  Hanuman P10 scripts auth path unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 17 / 18 (94.4%)
  - threshold_reached: false
  - **~1 calendar day to day threshold (~2026-05-28)**
  - open proposal `20260513-hanuman-platforms-awareness` STILL BLOCKS new proposal at threshold.
    Even if day threshold fires tomorrow, no new proposal can be drafted until this one resolves.

---

### 2026-05-28 — Observation Window 15 / DAY THRESHOLD REACHED (Run 22, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions this window. days_observed: 17 → **18**. runs_observed: 1 (unchanged).
  No new scout runs. No competitor_content/raw/ output.

  **ADAPTATION DAY THRESHOLD REACHED: days_observed = 18 (config threshold = 18 days).**

  **However: open_proposal_id = 20260513-hanuman-platforms-awareness (pending, constitutional).**
  Per operating rules: "If threshold_reached is already true, skip (open proposal pending)."
  No new proposal can be drafted while this proposal is unresolved. The hanuman platforms-
  awareness proposal has been open for **15 days total** and **11 days since Sahadeva endorsement
  (2026-05-17)**. All constitutional preconditions are fully satisfied.

  Status update: `threshold_reached` set to `true` in frontmatter to reflect the day threshold
  has now fired. The existing open proposal is the only blocking item.

  **REMINDERS.md credit-pool flag (surfacing 2026-06-01 — 4 days):**
  Hanuman P10 scripts auth path still unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — **THRESHOLD REACHED (day axis)**
  - threshold_reached: true
  - open_proposal_id: 20260513-hanuman-platforms-awareness (still pending — BLOCKS new proposal)
  - No new proposal generated: open proposal present.

---

### 2026-05-29 — Observation Window 16 (Run 23, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions this window (2026-05-28 02:00 → 2026-05-29 02:00 IST). days_observed:
  18 (unchanged — already at threshold). runs_observed: 1 (unchanged). No competitor_content/
  raw/ output.

  **New JSONL sessions in window:** Same as arjuna — `6ca65b2f` operator portal session,
  `7eb25436` observer. No hanuman attribution.

  **Proposal 20260513-hanuman-platforms-awareness — 16 days total, 12 days since Sahadeva
  endorsement (2026-05-17).** All constitutional preconditions satisfied for 12 consecutive
  days. No file-move or status change. This is the **12th consecutive window post-endorsement
  without approval action.**

  Per bhishma R23: constitutional proposals never auto-approve. Observer has no action.
  Open proposal continues to block any new hanuman adaptation proposal.

  **REMINDERS.md credit-pool flag surfaces in 3 days (2026-06-01):**
  Hanuman P10 scripts auth path still unverified before June 2026 SDK credit-pool separation.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 18 / 18 (100%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260513-hanuman-platforms-awareness (16 days open, 12 days endorsed,
    BLOCKS new adaptation proposal)

---

### 2026-05-30 — Observation Window 17 (Run 24, 02:00 IST)

- runs_today: 0
- new_patterns: []
- new_errors: []
- notes: |
  No hanuman sessions this window (2026-05-29 02:00 → 2026-05-30 02:00 IST). days_observed:
  18 → **20** (covers May 29 + May 30). runs_observed: 1 (unchanged). No competitor_content/
  raw/ output or cache updates.

  **New JSONL sessions in window:** `52083bda` (Kartavya offboarding session, operator,
  no agentSetting), `9b3df9af` (observer continuation), `c77663e1` (this run). No hanuman
  attribution in any session.

  **Kartavya offboarding (ecosystem-level event):**
  Session `52083bda` confirms Kartavya is leaving Rootlabs. System auto-shuts Sunday
  2026-06-01 23:59 IST. Hanuman's creator-intel pipeline (P4–P6, Cruva/Kalodata lookups)
  will cease after ecosystem shutdown. No agent action required; documented for audit.

  **Proposal 20260513-hanuman-platforms-awareness — 17 days total, 13 days since Sahadeva
  endorsement (2026-05-17).** This is the longest-running open proposal in the fleet at
  any tier. All constitutional preconditions satisfied for 13 consecutive days. Kartavya
  has not moved or updated the file.

  **FINAL WINDOW NOTE:** Given the offboarding timeline (Sunday 2026-06-01 system shutdown),
  this proposal is unlikely to be applied before ecosystem cessation unless Kartavya acts
  today or tomorrow. If not applied before Sunday 23:59 IST, the proposal is functionally
  moot pending any future restart of the fleet.

  Per bhishma R23: Observer does not auto-apply constitutional proposals. No action.

  **Adaptation threshold status:**
  - runs_observed: 1 / 40 (2.5%)
  - days_observed: 20 / 18 (111%) — THRESHOLD REACHED (day axis, fired Run 22)
  - threshold_reached: true
  - open_proposal_id: 20260513-hanuman-platforms-awareness (17 days open, 13 days endorsed)

---

## Calibration

_(No proposals have been applied or rejected yet. This section will populate over time.)_
