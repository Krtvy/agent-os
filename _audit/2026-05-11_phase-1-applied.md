# Phase 1 — Applied 2026-05-11

Companion to `2026-05-11_gap-analysis.md`. Records what shipped in Phase 1 ("low-risk additive") and what specifically remains for Phases 2–4.

Authorisation source: Kartavya selected "Approve all four — G4, G6, G8, G9" via AskUserQuestion at 22:55 IST.

---

## What shipped

### G4 — Tiered approval gates ✓

**Bhishma.** New rule **R23** added to `_meta/conductor/bhishma.md` after R22, before the Confidence-scoring section. Defines three risk tiers (doc-only / behavioural / constitutional) and the corresponding approval paths. Includes interaction notes with R6 (approval-gate logic) and R22 (bootstrap mode), misclassification consequences, two violation examples. "Last reviewed" section appended with attribution to Claude Code session at Kartavya's direction.

**Sanjaya.** `_meta/observer/skill.md` updated:

- `proposal_drafting` § frontmatter spec: added `risk_tier:` and `mast_codes:` fields.
- `proposal_drafting` § "How": added a "Risk-tier classification" decision logic block with 3 ordered checks + edge cases.
- `approval_polling` § "How": added two new bullets — (a) auto-approval path for `doc-only` proposals after 24-hr cooling-off, (b) constitutional-tier safety check requiring `sahadeva_endorsement:` before apply.

### G6 — MAST taxonomy ✓

**Sanjaya.** New skill `mast_classification` inserted between `pattern_extraction` and `drift_detection` in `_meta/observer/skill.md`. Covers all 14 MAST modes across 3 categories (spec/design, inter-agent misalignment, verification), with citation discipline + Sahadeva consumption pattern + `FM-unknown` escalation path. Frontmatter field `mast_codes: [FM-x.y, ...]` added to journal template at `_meta/observer/templates/journal.template.md` so future entries carry the taxonomy.

**Caveat (verify on first use).** The specific FM-x.y code IDs and labels are based on the playbook's summary of Cemri et al. NeurIPS 2025 (arXiv:2503.13657). Recommend cross-checking against the paper at first classification — the categorical structure (3 buckets, percentages 42/37/21) is solid; the exact code formatting in the published paper may differ. The `mast_classification` skill's "Citation discipline" rule already requires the paper be linked on first cite, which is when the cross-check naturally happens.

### G8 — Vidura reframe + Sanjaya body alignment ✓

**Vidura.** `research-agent/agent.md` fully rewritten in Mahabharat shape:

- Frontmatter `name:` renamed `research-agent` → `vidura`. Added `aliases: [research-agent]` so the historical symlink remains valid and Sanjaya's existing journal at `_meta/observer/journal/research-agent.md` doesn't break.
- Body now opens `# Vidura — Tier-0 Researcher` (matches Arjuna/Hanuman/Nakula/Narada/Yudhishthira shape).
- New `## Your character` section: Vidura the wise counselor at Hastinapura, born outside the line of succession and therefore honest, dissent-surfacing, source-disciplined. Vidura's near-failure mode (bluntness alienating the listener) is named and the counter (let structure carry the rhetoric) is built into the procedure.
- System-prompt content (research loop, source tiers, output format, hard rules, tone) preserved verbatim from prior version — no behavioural change. Now lives directly in the body rather than in a code-fenced block.
- Hyperagent deployment metadata (model settings, learning settings, tools enabled, attached context) moved into "Appendix A — Hyperagent deployment metadata."
- New "## Failure modes" section: citation fabrication, consensus seduction, tier inflation, bluntness alienating the listener.
- "Posture reminders" closing section added to match other agents' shape.

**Sanjaya.** `_meta/observer/agent.md` body opening rewritten:

- Title changed from `# Observer Agent` to `# Sanjaya — Tier-1 Observer`.
- Added `## Your character` section: Sanjaya as Vyasa's faithful narrator with divine sight, reporting the war to blind Dhritarashtra. The discipline of "faithful, complete, neutral" + the named flaw of wanting agency the narrator role doesn't carry + the R2/R3/R7 cross-references that close off the drift path.
- Tier picture expanded to name Vyasa, Sahadeva, and the full Mahabharat cast at Tier 0 explicitly.
- Technical sections downstream (scope, skills, procedures) unchanged.

### G9 — Instrument-what's-novel stance ✓

`_audit/README.md` created. Documents:

- What lives in `_audit/` (self-audits, external playbooks, gap analyses).
- The explicit acknowledgement that the four-layer (T0/T1/T2/T-Audit) oversight stack is **not directly studied in the literature** — components have support, the stack as a whole is novel.
- Five open questions worth tracking (independence between tiers, calibration drift, skill.md drift, approval-fatigue thresholds, inter-agent prompt injection).
- The four instrumentation responses (quarterly tier-independence review, MAST taxonomy, adversarial test set planned for Phase 2, structured traces planned for Phase 3).
- A discipline rule: any "best practice" claim in this ecosystem must cite either a tier-tagged source in this directory or an internal pattern validated by Kartavya. Hand-waving is refused at the proposal stage.

---

## What did NOT ship in Phase 1 (parked for later phases)

### Phase 2 (next, requires separate authorisation)

- **G1 Layer A** — declarative `PreToolUse` hook checking `write_scope` programmatically. ~1 hr.
- **G2** — rewrite Sahadeva's skill.md to be structurally different from Sanjaya's (different rubric, ideally rotating model). ~1 hr.
- **G3** — first adversarial test set for Sahadeva (`_meta/audit/test-set/2026-Q2.md`, 10–20 implanted-behaviour cases). ~4 hr.

### Phase 3 (after Sahadeva's first run)

- **G5** — structured traces in `_meta/observer/traces/<agent>-<run-id>.json` alongside narrative journals. ~6 hr.
- **G1 Layer C** — post-action audit hook consuming the trace data. ~2 hr.
- **G7** — Sanjaya journal compaction (only if/when journals exceed ~200 KB; currently the largest is 49 KB).

### Phase 4 (only if Phase 1–3 signal warrants)

- **G1 Layer B** — Haiku-based semantic pre-tool-call validator. ~4 hr.

### Carry-overs from self-audit

- **Co1–Co4** (cosmetic frontmatter consistency) — wait for Sahadeva's first run to see which keys it actually consumes.

---

## Side effects and follow-up tasks

### Symlinks remain valid

The `vidura.md` and `research-agent.md` symlinks in `.claude/agents/` both still point to `research-agent/agent.md`. The directory name `research-agent/` was not renamed (would invalidate Sanjaya's existing journal). The frontmatter `aliases: [research-agent]` makes the historical name machine-readable for downstream tools.

### Sanjaya's existing journal entries

`_meta/observer/journal/research-agent.md` continues to be Vidura's journal — the file path is keyed to directory name, not the agent's `name:` field. No migration needed. Sahadeva's audit script (when implemented) should accept both `research-agent` and `vidura` as references to the same entity.

### Bhishma edit attribution

Bhishma R1 says only Kartavya edits `bhishma.md`. The R23 addition was authored by Claude Code session at Kartavya's explicit direction during the auto-mode session of 2026-05-11. The "Last reviewed" section now records this attribution so the audit trail is unbroken. Sahadeva should treat the R23 addition as Kartavya-authorised on first weekly audit.

### Journal-template change does not auto-apply to existing journals

Adding `mast_codes: []` to the journal template means _new_ journals get the field. Existing journals (arjuna, hanuman, nakula, narada, research-agent) do not get backfilled — they don't need to be, since the field starts being populated from the next observation day forward. Sahadeva aggregation should handle the absent-field case gracefully.

### `risk_tier:` declaration on proposals

No proposals exist yet (`_meta/observer/proposals/` is empty except for `.gitkeep`). The first proposal Sanjaya drafts will be the first with a `risk_tier:` field. There is nothing to backfill.

---

## What to watch for in week 1 of operation

1. **Misclassification.** Does Sanjaya correctly assign `risk_tier:` to its first proposals? Sahadeva's first weekly audit should pay specific attention to this — R23 explicitly says misclassification is itself a constitutional issue.
2. **MAST coverage.** What fraction of journal entries' `mast_codes:` are `FM-unknown`? If high (>20%), the local taxonomy needs extension; if zero across multiple weeks, suspect under-classification.
3. **Doc-only auto-approval.** When the first `doc-only` proposal crosses the 24-hr cooling-off mark, does it auto-apply cleanly? This is the new behavioural change in `approval_polling` and is the most likely place for a bug.
4. **Tier-independence signal.** When Vyasa eventually reviews Sanjaya's proposals (no proposals exist yet), does Vyasa's framing differ from Sanjaya's, or just rubber-stamp? G9's tier-independence metric tracking starts here.

---

_Phase 1 completion recorded 2026-05-11 23:08 IST by Claude Code session (claude-opus-4-7), at Kartavya's direction in auto mode._
