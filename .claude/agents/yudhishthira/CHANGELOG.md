# Yudhishthira — Changelog

Append-only log of **agent-level** changes (identity, file structure, scope, tooling). Skill-level changes track in `skill.md` § "Change log".

## 2026-05-11

- Bootstrap — initial agent definition committed (`agent.md`, `skill.md`, `playbook.md`).
- Platform: Hyperagent. Phase 1: read-only on Google Sheets.
- Playbook document wired: `cmp1f7kpo105407adc5ijk8r9`.
- Added `README.md` and `CHANGELOG.md` per agent-template standard.
- **Self-audit fix C1.** Added `bhishma.md` to `read_scope` and to skill.md § P1 as the first session-bootstrap step. Closes the gap where Yudhishthira was the only Tier-0 agent not bound to the constitution.
- Added `runtime: hyperagent` discriminator field (resolves audit finding I5).

## 2026-05-12

- **Sheets-fluency upgrade (constitutional change).** Yudhishthira pivoted from pandas-first to formula-first for Google Sheets work. Specific changes:
  - `agent.md` body: new `## Your craft — Sheets-fluent senior analyst` section between `## Your character` and `## Your tier`. Names the formula reference playbook as the single source of truth.
  - `agent.md` Constraints section: added R9 (never invent a formula) and R10 (formula-first default).
  - `agent.md` Failure modes section: added three new failure modes — formula hallucination, false speed (formula where pandas was right), locale-induced formula errors.
  - `skill.md` P3 CLASSIFY: added P3a — a formula-first vs pandas-first decision table covering 9 task shapes.
  - `skill.md` P5 COMPUTE: split into P5a (formula path) and P5b (pandas path). P5a includes mental-eval discipline, miss-behavior statement requirement, QUERY plain-English requirement, lookup-default disclosure.
  - `skill.md`: new top-level § Anti-hallucination rules (formula path) with 10 hard rules.
  - `skill.md` Hard rules: added R8 (never invent a formula) and R9 (formula-first default).
  - Reference doc: `_audit/2026-05-12_sheets-formula-playbook.md` (in flight via background Deep Research at commit time; final size and coverage will populate this entry on completion).
- **Constitutional override pattern, third instance.** R23 classifies changes to procedures, scope, and tooling as `constitutional` — requiring Kartavya approval + rationale + Sahadeva endorsement + 24-hour cooling-off. Sahadeva endorsement is structurally unavailable (Sahadeva's first run is Sunday 2026-05-17 10:00 IST). Kartavya directed this change in auto-mode 2026-05-12 18:23 IST under the same override pattern as R23 itself + hook wiring. Sahadeva's first audit is explicitly tasked with retroactively reviewing all three overrides; full attribution trail in `_audit/2026-05-12_yudhishthira-sheets-fluency.md`.
- **Amendment (18:30–18:50 IST, same session as Sheets-fluency upgrade) — task understanding + tracker + comprehensive checks.** Reframed as amendment to override #3, not a separate override #4, because (a) same conversation hour, (b) same agent, (c) iterative authoring of one constitutional act. Changes:
  - `skill.md` P3 expanded from one-line CLASSIFY into a five-substep UNDERSTAND procedure (P3.1 question · P3.2 data we have · P3.3 data we need · P3.4 gaps · P3.5 task type + deliverable shape). Two-source handling explicit within P3.2-3.4 with join-key declaration + non-overlap flagging.
  - `skill.md` P3.5 task taxonomy added new type: `tracker` (live Sheets dashboard).
  - `skill.md` P7 gained a `P7-tracker` deliverable spec: formulas + named ranges + installation order + weekly health-check section, no `.csv` by default.
  - `skill.md` new top-level § "All checks — complete inventory" tabulates every check across pre-flight, P2/P3, P4, P5a/P5b, P6, P7, P7-tracker, P8/P9, hard-rule violation paths. Single-page reference for the discipline.
  - `agent.md` new section `## Tracker (live Sheets dashboard) — first-class task type` alongside the existing reconciliation section.
  - Reference playbook at `_audit/2026-05-12_sheets-formula-playbook.md` landed during this amendment (background Deep Research dispatched 18:25 IST, returned 18:30 IST): 66 formulas across 9 sections, 7 workflows, anti-hallucination protocol with 10 LLM failure modes + verification protocol, 42 tier-tagged sources. Yudhishthira's formula path is now unblocked.
  - Override accounting: still **three** total constitutional overrides (R23, hook wiring, Sheets-fluency-with-amendment). Next constitutional change goes through strict R23 path per `_audit/2026-05-12_hooks-wired.md` threshold.
- 2026-05-12 (preparation, same session, 19:55 IST) — **Google Sheets URL access + Phase 2 provisioning checklist.** P0 expanded with Sheet-URL-specific subsection: "always copy first" formalised as a hard step that makes a copy `<original_name>_yudhishthira_<YYYY-MM-DD>` before any formula touches a real sheet, both sheet IDs recorded in audit, original treated as read-only forever within the task. Phase 2 readiness placeholder expanded from 4 lines into 5-step provisioning checklist (provision dedicated `yudhishthira-*@…` Google account with 2FA · wire into runtime · update spec for new capability with P10 write-back · hard always-copy enforcement · Phase 2 failure modes). `agent.md` § Google Sheets rewritten to reflect copy-first access and to reference the new checklist. **Classified as preparation, not constitutional change** — the Google account doesn't exist yet, so today-behavior is unchanged; this is operational documentation for when provisioning happens. Phase 2 _activation_ itself remains a constitutional change that should go through the strict R23 proposal flow once Sahadeva is running. Override count still 3.

## 2026-05-13

- **Local runtime gap-fill (operational, not constitutional).** User set up the local Claude Code path with `memories.md` stub, `deliverables/` dir, and pandas 3.0.3 in `.venv`. Two infrastructure gaps closed, three procedural references threaded through:
  - **`lib/yudhi-py.sh`** (new) — wrapper that invokes `.venv/bin/python3` for Yudhishthira's pandas path. System `python3` does not have pandas; the venv does. Without the wrapper Yudhishthira's first P5b call would fail with `ModuleNotFoundError`. Tested: imports pandas cleanly, surfaces rebuild instructions if `.venv` is missing.
  - **`lib/yudhi-fetch.sh`** (new) — resolves a Google Sheets URL or local CSV path to a local CSV. For public sheets uses the CSV export endpoint; for private sheets emits an auth-wall error with three actionable options (make public, download manually, provision Phase 2). Local paths pass through unchanged. Tested: bogus input → 64, local file → 0, fake sheet URL → HTTP 404 caught. Bash 3.2 regex-parsing bug caught and worked around (pattern-in-variable indirection).
  - **`work/` scratch dir** (new) at `.claude/agents/yudhishthira/work/` with `.gitkeep`. For intermediate pandas outputs that aren't final deliverables. Keeps `deliverables/` clean.
  - **`skill.md` P0 update** — adds a Phase 1 local path subsection: use `lib/yudhi-fetch.sh <url>` for Sheet URLs, operate on its output. Phase 2 Hyperagent path preserved. The two paths (local vs Hyperagent) are now both explicit.
  - **`skill.md` P5b update** — mandates `lib/yudhi-py.sh` over bare `python3`. Bare `python3` will fail; the wrapper is non-negotiable.
  - **`skill.md` P8 update** — split learning capture into Phase 1 (local `playbook.md` + `memories.md` append-only) vs Phase 2 (Hyperagent `UpdateDocument` + `CreateMemory`). The two storage shapes should stay consistent cross-platform.
  - **`lib/README.md` update** — full documentation of `yudhi-py.sh` and `yudhi-fetch.sh` with usage, exit codes, the Bash 3.2 note.
  - **Classification: operational, not constitutional.** Adds runtime helpers + procedural specificity; does not change Yudhishthira's identity, tool surface, write_scope, or approval-gate logic. R23 behavioural-tier at most. User gave explicit authority. Override count still 3.
