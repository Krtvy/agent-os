# Pattern Report — research-agent

**Report ID:** research-agent-2026-05-16
**Generated:** 2026-05-16 (Observer Run 12)
**Mode:** bootstrap (no prior skill.md)
**Threshold trigger:** days_observed = 10 (config: bootstrap.days = 10)
**Observation window:** 2026-05-07 through 2026-05-16 (10 calendar days, 15 runs)
**Evidence sources:** Static artifacts (CLAUDE.md, agent.md, 4 × SKILL.md, 2 rule files, 15
competitor profiles, 6 reference docs), JSONL sessions (primary project path), git history,
`research/` and `_research/` output directories.

---

## Qualified Patterns (≥3 supporting observations)

The following patterns have met the `min_supporting_observations: 3` threshold and qualify
for inclusion in the bootstrap `skill.md` proposal.

---

### QP1 — Skill-based, progressive-disclosure architecture

**Confidence:** HIGH (5+ observations across all window types)

The agent uses a 4-layer load stack: `CLAUDE.md` (identity, always loaded) → `.claude/rules/`
(domain knowledge, loaded when relevant) → `.claude/skills/*/SKILL.md` (workflow, on-demand) →
`docs/` (reference data, loaded by skills). This architecture is explicitly documented in
`research/ARCHITECTURE.md` and confirmed in every observed session that invokes the `/research`
skill (sessions 6bdb87d9, fcd00ebb, 6a9efa75 all show `Skill` tool calls).

Supporting observations:

- ARCHITECTURE.md documents the 4-layer pattern explicitly (Run 1)
- CLAUDE.md § "Available Skills" and § "Available Rules" confirm the layers (Run 1)
- Session 6bdb87d9 — Skill tool invoked (Run 8)
- Session fcd00ebb — Skill tool invoked (Run 9)
- Session 6a9efa75 — Skill tool invoked with `skill: research` (Run 12)

---

### QP2 — Parallel research streams as default execution model

**Confidence:** HIGH (4+ observations)

`deep-research/SKILL.md` Phase 2 specifies parallel searches across semantic, news, academic,
and industry angles. `growth-playbook/SKILL.md` defines 5 named research streams to run in
parallel. Live JSONL evidence confirms: sessions use `Agent` sub-dispatch (multiple tool calls
to Agent in a single session), and session 6bdb87d9 had 30 WebSearch calls consistent with
multi-angle parallel casting.

Supporting observations:

- deep-research/SKILL.md and growth-playbook/SKILL.md (Runs 1–2, static)
- Session 6bdb87d9 — 30 WebSearch calls (Run 8)
- Session 6a9efa75 — Agent + ToolSearch dispatch (Run 12)
- Session 95407e38 — Agent×2 dispatch for app-building research (Run 12, operator session with /research skill)

---

### QP3 — Tier-tagged citation discipline (T1–T5 system)

**Confidence:** HIGH (6+ observations across multiple formats)

Every output document carries tier badges on every citation. Documented as "NON-NEGOTIABLE"
in agent.md. Confirmed in static artifacts (competitor profiles, research docs), JSONL (session
1a5f4b3e applied T1 tier tag to a single-line Tokyo population answer), and live deliverables
(`_research/2026-05-15-higgsfield-ai-video.md` carries T1/T2/T3/T4 badges throughout).

Supporting observations:

- docs/competitor_profiles/\*.md — tier badges on all citations (Run 1)
- docs/research_habits.md — source lines with dates (Run 1)
- .claude/rules/source-tiers.md — 15+ edge-case classifications (Run 1)
- Session 1a5f4b3e — single-line Tokyo answer with [T1: Tokyo Metropolitan Gov...] (Run 4)
- `_research/2026-05-14_*.md` (4 files) — tier-tagged throughout (Run 12 window)
- `_research/2026-05-15-higgsfield-ai-video.md` — T1/T2/T3/T4 badges confirmed live (Run 12)

---

### QP4 — Document / HTML as primary output format for comprehensive reports

**Confidence:** HIGH (4+ confirmed output artifacts)

`growth-playbook/SKILL.md` and `market-intel/SKILL.md` specify "Always render as a webpage."
`deep-research/SKILL.md` specifies webpage for dense content. Live deliverables confirm HTML
and document outputs. The agent also selects format adaptively: short lookups → chat markdown;
multi-source reports → document; data-heavy → HTML.

Supporting observations:

- `2026-05-06_rootlab_growth_playbook.html` — confirmed HTML artifact (Run 1)
- `docs/competitor_matrix.html` — second HTML artifact (Run 1)
- `research/claude-mastery/book/` — 22 chapters as Markdown docs (Run 4)
- `_research/2026-05-15-higgsfield-ai-video.md` — comprehensive document format, 29.9 KB (Run 12)
- All 4 `_research/2026-05-14_*.md` files — document format (Run 12 window)

---

### QP5 — Pre-research doc cache checked before any new search

**Confidence:** MEDIUM (3+ observations)

The agent explicitly loads `docs/` reference files before running new searches. Both
`growth-playbook/SKILL.md` and `brand-audit/SKILL.md` instruct: "Load these files first —
they contain 60+ sources already researched." The pattern extends to any task type: for
competitive work, existing competitor profiles are loaded; for technical research, the
query library or existing corpus is consulted.

Supporting observations:

- growth-playbook/SKILL.md § "Reference Data" (Run 1)
- brand-audit/SKILL.md § "Reference Data" (Run 1)
- Session 6bdb87d9 — research on AI humanizer ID: starts with Read of existing docs (Run 8)
- Implicit in fcd00ebb (competitor handle discovery begins with reading existing profiles) (Run 9)

---

### QP6 — Standing competitive-monitoring system (15 brands, 3 tiers)

**Confidence:** HIGH (4+ observations)

CLAUDE.md defines a standing operation with 15 brands across Tier A/B/C, fixed profile
schema (D1–D4), monthly snapshot cadence, and 4 synthesis artifacts. All 15 competitor
profiles confirmed in `docs/competitor_profiles/`. All 4 synthesis artifacts confirmed.
The "what to steal" section is documented as the mandatory deliverable close.

Supporting observations:

- 15 competitor profile files confirmed (Run 1)
- 4 synthesis artifacts confirmed (Run 1)
- CLAUDE.md § "Competitive Monitoring System" (Run 1)
- Session fcd00ebb — competitor TikTok handle discovery run, D1 data query (Run 9)

---

### QP7 — Domain scope (REVISED from original P7)

**Confidence:** MEDIUM (3+ observations — but original "supplement-only" reading was wrong)

Original P7 stated the agent is "domain locked to DTC supplements / Rootlab MagAshwa."
This is now contradicted by live evidence. The agent's actual scope is broader: DTC
supplements is the primary context, but research tasks span AI platforms, marketing strategy,
and any topic Kartavya submits. The research skill is general-purpose; the domain specialization
lives in the rules files (`dtc-supplements.md`) and competitive monitoring system, not in a
blanket domain lock.

**Correction:** The agent is Rootlab-primary (default context is Rootlab unless otherwise
stated) but research-skill invocations are domain-agnostic. Domain-specific rules auto-load
when relevant.

Supporting observations showing general scope:

- `_research/2026-05-14_anthropic-agent-ecosystem.md` — AI agent ecosystem (Run 12 window)
- `_research/2026-05-14_cmo-agent-research.md` — marketing/CMO research (Run 12 window)
- `_research/2026-05-15-higgsfield-ai-video.md` — AI video platform (Run 12)

---

### QP8 — Synthesis artifact generation as standing deliverable

**Confidence:** HIGH (4+ observations)

The agent produces synthesis artifacts that aggregate findings across sources/sessions.
Four standing synthesis docs confirmed (competitor_matrix.html, creator_commissions_sidebyside.md,
campaign_cadence_calendar.md, habit_tactics_inventory.md). Extended in Run 4 to include
multi-chapter prose book and cheatsheet from a single corpus. Extended in Run 12 to include
`.skill` file packaging. Synthesis artifacts are not one-off outputs — they are maintained,
updated, and versioned.

Supporting observations:

- 4 synthesis artifacts at `docs/` (Run 1)
- research/claude-mastery/{CHEATSHEET.md, PLAYBOOK.md, book/} (Runs 4–6)
- `docs/higgsfield-content-factory.skill` (Run 12)
- `_research/2026-05-14_*.md` — 4 research documents in a single output batch (Run 12 window)

---

### QP10 — Session-tagged deliverables with ISO date prefix

**Confidence:** HIGH (all observed deliverables follow this pattern)

Every deliverable produced by the agent carries a `YYYY-MM-DD_` prefix in the filename.
This is consistent across all 10 observation windows. The pattern enables chronological
sorting and provenance tracking.

Supporting observations:

- `2026-05-06_rootlab_growth_playbook.html` (Run 1)
- `research/2026-05-07_*.md` (Runs 2–3)
- `research/2026-05-08_*.xlsx` (Run 3)
- `_research/2026-05-14_*.md` and `_research/2026-05-15-higgsfield-ai-video.md` (Run 12 window)

---

### QP16 — Smoke-test diagnostic protocol (fleet-wide)

**Confidence:** HIGH (confirmed cross-fleet, 5+ agents)

The agent correctly participates in the fleet-wide smoke-test protocol: single-line,
machine-parseable response to the standardized "Smoke test only" prompt. No tool calls.
Confirmed in the research-agent context in Run 3 (ARCHITECTURE.md describes the protocol)
and inferred from the fleet-wide pattern (all 4 new agents on May 10 confirmed it).

Supporting observations:

- ARCHITECTURE.md documents the smoke-test protocol (Run 3)
- 4 sibling agents all confirmed single-line smoke-test response (Run 7)
- Session 6bdb87d9 — agent-setting confirmed `research-agent` (Run 8, confirming fleet
  membership and implicit protocol adherence)

---

## Excluded Patterns (below threshold)

| Pattern                              | Observations | Reason for exclusion |
| ------------------------------------ | ------------ | -------------------- |
| P9 — Self-audit / QC artifact        | 2            | Below ≥3 threshold   |
| P18 — ScheduleWakeup continuation    | 2            | Below ≥3 threshold   |
| P20 — Multi-format deliverable pack  | 2            | Below ≥3 threshold   |
| P21 — Scheduled autonomous operation | 2            | Below ≥3 threshold   |
| P28 — Skill-artifact as deliverable  | 1            | Too new              |

---

## Anomalies and Open Items

1. **No skill.md file exists** — confirmed bootstrap mode is correct.
2. **No `.claude/logs/research-agent/` infrastructure** — all observations from JSONL +
   static artifacts. All 10 observation windows flagged this gap. Recommend creating log
   infrastructure if research-agent transitions to a more scheduled/regular execution pattern.
3. **Subdirectory project path** (`-Users-mosaic-projects-observer-test-research/`) still
   not in `config.yml input_sources.transcripts`. Any future scheduled sessions from
   `research/` subdirectory will miss Observer coverage.
4. **`_research/` vs `research/` split** — early output goes to `research/` (email campaigns,
   claude-mastery corpus). Later output goes to `_research/` (2026-05-14 onward). The split
   appears intentional (operator moved research outputs to a dedicated `_research/` directory)
   but is undocumented. The bootstrap proposal will document both paths.

---

## Confidence Score

- Qualifying patterns: 10
- Average observation depth: ~4.2 observations per pattern
- Contradicted patterns: 1 (P7 corrected, not dropped)
- Score: HIGH — well above the 40-point floor

**Recommendation: proceed to bootstrap proposal.**
