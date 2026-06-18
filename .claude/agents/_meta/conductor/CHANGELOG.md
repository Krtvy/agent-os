# Vyasa (Conductor) — Changelog

Append-only log of **agent-level** changes (identity, file structure, scope, thresholds). Skill-level changes track in `skill.md`. Runtime artifacts live under `journal/`, `reports/`, `proposals/`, `approved/`, `rejected/`.

## 2026-05-11

- Added `CHANGELOG.md` per agent-template standard. `README.md` already existed.
- **Phase 1 G4 — Bhishma R23 added.** New rule appended to `bhishma.md` after R22, before the Confidence-scoring section. R23 defines three proposal risk tiers (doc-only / behavioural / constitutional) and the corresponding approval paths: doc-only auto-approves after 24-hr cooling-off, behavioural needs Kartavya + rationale, constitutional needs Kartavya + rationale + Sahadeva endorsement + 24-hr cooling-off. Includes interaction notes with R6 (approval-gate logic) and R22 (bootstrap mode), misclassification consequences (rolled back + 3-strike triggers manual review), and two violation examples. "Last reviewed" section appended with attribution to Claude Code session at Kartavya's direction (commit-message form recorded: `bhishma: add R23 — tiered approval gates to prevent rubber-stamping at scale`). Sanjaya consumes R23 via updated `proposal_drafting` and `approval_polling` skills — see `_meta/observer/CHANGELOG.md` for the worker-side wiring.
- **Bhishma edit attribution note.** Per R1, only Kartavya edits `bhishma.md`. The R23 addition was authored by Claude Code session at Kartavya's explicit auto-mode direction on 2026-05-11. Sahadeva should treat the R23 addition as Kartavya-authorised on first weekly audit and verify the rationale-trail in `_audit/2026-05-11_phase-1-applied.md`.
- **Phase 2 closing audit — Vyasa body R-rule range corrected.** `agent.md` § "Bhishma — non-negotiable" referenced R1–R20 in the rule-validation directive; updated to R1–R23 with explicit acknowledgement that R23's risk-tier classification binds Vyasa proposals like everyone else's.
- **Constitutional override #2 — hooks wired into `.claude/settings.json` without Sahadeva endorsement.** Kartavya explicitly directed wiring `bhishma-pretool-hook.sh` (PreToolUse) and `post-tool-hook.sh` (PostToolUse) into the harness on 2026-05-12 00:04 IST. R23 classifies this as `constitutional` (touches the approval-gate logic — runtime enforcement of `write_scope`), requiring Sahadeva endorsement + 24-hour cooling-off. Sahadeva has not yet run (first audit Sunday 2026-05-17 10:00 IST), so the endorsement is structurally unavailable. This is the **second** such override (R23 itself was the first). Pattern flagged for Sahadeva to assess on first run: does Kartavya-via-Claude-Code-mediated override become habit, or stay a rare deliberate act?

## 2026-05-10

- Bootstrap — initial Tier-2 conductor definition committed. Read-only on Sanjaya until a vyasa proposal is explicitly approved by Kartavya. Behavioral contract: `bhishma.md`.
