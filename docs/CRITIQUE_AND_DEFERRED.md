# External critique + my response

External review of this ecosystem (by Hyperagent, 2026-05-10): **7.5/10**.

> _"A genuinely interesting system. Better than most multi-agent designs because it takes governance seriously. But it has real risks, and a fair amount of untested complexity. Worth building, but expect the first 60 days to surface things this design didn't anticipate."_

This file captures **what was flagged**, **what I addressed**, and **what I deferred — with reasons**. It exists so a future Claude session (or future-Kartavya) knows why certain known weaknesses haven't been fixed yet.

---

## Addressed in commits

### Bhishma R21 — Proposal expiration

- **Hyperagent flag:** "Single approver. If you're sick for two weeks, the system stalls. No delegation path."
- **Fix applied:** R21 added — low-confidence proposals expire 14 days un-approved, medium-confidence at 30 days, high-confidence never expires. Expired proposals move to `proposals/_expired/`, freeing the cooldown slot.
- **Commit:** see git log for `bhishma: add R21 proposal expiration`
- **Status:** ✓ Done

### Bhishma R22 — Bootstrap mode for R10

- **Hyperagent flag:** "R10's `≥3 example_run_ids` is too strict for early bootstrap. Lots of one-off observations that legitimately can't accumulate three examples yet."
- **Fix applied:** R22 added — during the first 30 days of a target's observation, proposals can set `bootstrap_mode: true` to lower the floor to 1 run_id. Auto-cleared after 30 days. Bootstrap proposals also receive the existing 0.7× confidence multiplier so they cannot reach high band.
- **Commit:** see git log for `bhishma: add R22 bootstrap mode`
- **Status:** ✓ Done

### Audit inbox for escalation

- **Hyperagent flag:** "Sahadeva flags critical violations to a markdown file. If you don't read it on Sunday morning, the violation sits."
- **Fix applied:** Added P9 to Sahadeva's skill.md — critical findings (Bhishma violations, missing heartbeat ≥48h, untracked git commits, agent silence ≥7 days) get appended to `_meta/audit/inbox.md` _in addition to_ the weekly report. The inbox is a daily-glance surface, the report is the weekly read.
- **Status:** ✓ Done (file structure ready; will fill once Sahadeva runs)

### WHO_IS_WHO.md glossary

- **Hyperagent flag:** "Add a one-page glossary so a teammate reading the repo cold isn't lost."
- **Fix applied:** `WHO_IS_WHO.md` at repo root. Each agent: character, role, tier, key constraint, failure mode, counter. Plus data-flow diagram and quick-reference table.
- **Status:** ✓ Done

---

## Deferred — with explicit reasoning

### 1. Cost optimization — Sanjaya on Sonnet by default

- **Hyperagent flag:** "Sanjaya every 30 min on Opus is expensive. Could probably run on Sonnet for routine cycles, Opus only when scoring."
- **Why deferred:** Sanjaya's skill.md v1.1.0 ships with 5 self-diagnostic skills (heuristic_cross_check, baseline_drift_check, evidence_quality_check, confidence_scoring, proposal_self_review). These haven't been validated against real data on Opus, let alone Sonnet. Switching the model could subtly degrade these gates without us noticing.
- **Trigger to revisit:** After 30 days of Opus-Sanjaya operation with stable proposal quality, swap to Sonnet for one week, A/B compare proposal calibration. If Sonnet matches, switch.
- **Cost of waiting:** ~$X/week extra in Anthropic API spend (depends on cycle frequency)
- **Cost of switching wrong:** silent miscalibration of self-diagnostic skills. Higher-stakes than the savings.

### 2. File-level enforcement of "honor system" rules

- **Hyperagent flag:** "Several rules are honor-system: single-writer on heartbeat.json (Nakula promises but nothing prevents another agent from writing); append-only journals (R5 says it; nothing stops Edit). Future Sahadeva should detect these by file-level diffs, not by trust."
- **Why deferred:** These checks belong in Sahadeva, but Sahadeva hasn't run yet. Adding the check before the parent has executed once is premature. Also, building a file-level diff system that can detect "Edit was used on a journal" requires git-level inspection (blame + commit message scanning).
- **Trigger to revisit:** After Sahadeva's third weekly run, audit which honor-system rules have actually been violated. Implement file-level checks for the violated ones first.
- **Cost of waiting:** Some violations may slip through silently for up to 3-4 weeks.
- **Mitigation in the meantime:** Bhishma R5 + R6 are visible to every agent on startup; agents should self-enforce.

### 3. Sanjaya bootstrap on Sonnet escalating to Opus

- **Hyperagent flag:** Same as #1 but specifically "escalate to Opus only when a draft proposal is being scored."
- **Why deferred:** This requires intra-cycle model switching, which adds complexity to Sanjaya's run logic. Not worth the effort until the simple "always Opus" baseline is proven.
- **Trigger to revisit:** After we have data showing which sub-skills (pattern_extraction vs proposal_drafting vs confidence_scoring) actually need Opus.

### 4. Daily sanity scan by Nakula

- **Hyperagent flag:** "Sahadeva weekly is a long blast radius. Add a 'daily sanity scan' by Nakula that does only the cheap checks (heartbeat freshness, agent silence, bhishma hash) and only escalates to a full Sahadeva pass mid-week if something fires."
- **Why deferred:** Nakula's `jobs.yml` is currently empty (no scripts written yet). Adding a sanity-scan job before any of the actual data-pipeline jobs exist is jumping ahead. Also, this is a meaningful new responsibility for Nakula — should be its own design pass once Nakula has at least 2-3 real jobs running.
- **Trigger to revisit:** After Nakula's first real job (likely log-rotation) is running stably for 1 week.

### 5. Voice fingerprinting for Narada — full implementation

- **Hyperagent flag:** "Voice fingerprinting in Narada is ambitious. Cosine similarity ≤0.85 vs. last 30 days is a real bar to clear consistently. May produce a lot of regenerations and generic-reject-couldnt-resolve flags in the early weeks."
- **Why deferred:** The skill.md describes the mechanism but the actual fingerprint extraction is supposed to happen at runtime via Bash + Python. The agent will improvise this on each run. Building a stable Python helper at `narada/lib/fingerprint.py` would be more robust but premature — we don't have voice samples yet, so there's nothing to fingerprint.
- **Trigger to revisit:** After Kartavya drops 5+ voice samples into `narada/voice-samples/` and Narada has run 10+ times. Then either bake the helper script or relax the cosine threshold based on observed regeneration rate.

### 6. Slack/email escalation for critical findings

- **Hyperagent flag:** "There should be a Slack/email channel for `critical: yes` findings."
- **Why deferred:** Slack MCP is connected to this Claude account but not authenticated for this specific project's use. Setting up the auth + writing a clean alerting integration requires real attention. The `inbox.md` file (added today) is the lightweight version of this — a single file you check daily that's roughly equivalent to "an inbox."
- **Trigger to revisit:** When inbox.md has accumulated 10+ critical findings AND Kartavya has missed any of them for >24 hours. Then build the Slack push.

### 7. Recovery automation

- **Hyperagent flag:** "Recovery is 'stop and journal.' Failures sit silent until human attention. If Sanjaya's skill.md corrupts, the whole supervisory chain halts and only Sahadeva will surface it — up to a week later."
- **Why deferred:** Auto-recovery has the same hazard as auto-modification: it can mask root causes. Manual stop-and-journal is the safer baseline. After the system proves stable, narrow auto-recovery for specific known failure types (e.g., stale lockfile, JSON parse error in jobs.yml) might be added.
- **Trigger to revisit:** First 3 actual halts that turn out to be benign + recoverable.

### 8. WHO_IS_WHO.md is a stop-gap for plugin manifest

- **Reddit/agent-dev-kit critique:** "L5 Distribution (Plugins) — you don't have this."
- **Why deferred:** Plugin manifest is a migration-day need (Rachit's account → Kartavya's personal account). WHO_IS_WHO.md gives most of the same value (a teammate or future-Kartavya can pick up the system) without the engineering of a real `manifest.json`.
- **Trigger to revisit:** When Kartavya's personal Anthropic account is provisioned and migration is within 2 weeks.

---

## How this file should be used

- **Future Claude sessions:** read this on a fresh session before suggesting any of the deferred items. The reasoning may have changed; check git log for evidence.
- **Future Kartavya:** when you find yourself thinking "we should add X" — check this file first. If X is in the deferred list, the trigger condition tells you whether the time has actually come.
- **External reviewers:** this file is the system's own honest answer to "what's not done and why?" — read it before assuming we missed something.

## Last updated

2026-05-10 — initial response to Hyperagent 7.5/10 review.

When the next external review happens, append a new section to this file rather than overwriting. The history of critiques + responses is itself signal.
