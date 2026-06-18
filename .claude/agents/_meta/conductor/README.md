# Conductor (Tier-2, DEFERRED)

This directory hosts **Vyasa**, the **Tier-2 Conductor** — a manager-of-managers that watches Sanjaya (the Tier-1 Observer).

**Status:** Defined but intentionally inactive. `agent.md`, `skill.md`, and `bhishma.md` are populated. The agent has never been invoked — no journals, proposals, approvals, or reports exist.

---

## Deferral decision — 2026-05-22

Sahadeva's [2026-W20 audit](../audit/reports/2026-W20.md) flagged Vyasa's dormancy as `severity: critical` (recommendation §2). Resolution chosen: **defer activation; Kartavya is the direct approver of Sanjaya's proposals.**

**Rationale**

- Sanjaya currently produces ~2 proposals/week. Volume does not justify a supervisory layer between Sanjaya and Kartavya.
- Vyasa's primary value (calibrating an over- or under-proposing Observer) requires a baseline of approval/rejection data Sanjaya does not yet have. Sahadeva's §1 confirms calibration is not yet measurable — zero proposals have completed the approval lifecycle.
- The agent definition exists, so activation later is a config-only change (add to crontab, enable journaling). No code is lost by deferring.

**Re-evaluation trigger:** when Sanjaya's approval-rate calibration becomes measurable (Sahadeva §1 begins reporting non-`—` values for ≥4 consecutive weeks), revisit whether Vyasa should activate. Until then, Kartavya remains direct approver.

**Audit-inbox status:** Vyasa-dormant finding marked resolved 2026-05-22.

---

## What a Conductor would do

Where the Observer (Tier 1) watches Workers (Tier 0), the Conductor watches the Observer (and any sibling Tier-1 meta-agents you might add later).

A future Conductor's responsibilities could include:

| Capability                      | Why                                                                                                                                                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Calibrate the Observer**      | If the Observer is over-proposing changes (lots of rejections) or under-proposing (lots of obvious drift it misses), the Conductor adjusts thresholds or adds skills to it.           |
| **Cross-agent reasoning**       | "Researcher and writer keep duplicating effort — propose merging a skill across both." Things the Observer can't see because it watches one agent at a time.                          |
| **Conflict resolution**         | If two Tier-1 meta-agents propose conflicting changes to the same Worker, the Conductor decides.                                                                                      |
| **Policy-based batch approval** | Under explicit human-defined policy, batch-approve low-risk classes of proposals (e.g., "auto-approve any proposal that only adds a documented-but-unused skill back into rotation"). |
| **Tier-1 health monitoring**    | Detect when the Observer itself is broken (no journal updates, repeated errors) and alert.                                                                                            |

---

## Why the slot exists _now_

The Observer's outputs (journals, reports, proposals) all use **structured YAML frontmatter + markdown**. This means a future Conductor can parse them programmatically with zero changes to the Observer.

If we waited until you wanted a Conductor before designing for it, we'd have to refactor the Observer's output format and risk breaking existing journals.

---

## To activate later

When you're ready:

1. Drop a `conductor/agent.md` (with frontmatter + system prompt) and `conductor/skill.md` (its own skills) here.
2. Add a `conductor/config.yml` listing watched Tier-1 agents (e.g., `_meta/observer`).
3. Add a `conductor/run_conductor.sh` script following the same pattern as the Observer's.
4. The Conductor inherits the same approval-gate philosophy: it never modifies a watched meta-agent's files (or a Worker's files via a meta-agent's proposal stream) without your explicit approval.

---

## What this folder contains today

Just this README. The folder exists to:

- Make the multi-tier intent visible in the file structure
- Reserve the canonical name (`_meta/conductor/`) so nothing else collides with it
- Document the design intent so a future maintainer (or future you) understands why we built the Observer the way we did

When you're ready to populate it, see the Observer's files for the pattern to mirror.
