# Gap Analysis — Ecosystem vs. Best-Practice Playbook

**2026-05-11 · synthesis deliverable**

Sources combined:

- `2026-05-11_multi-agent-playbook.md` (Deep Research, 37 sources, tier-tagged) — external best practices.
- `2026-05-11_self-audit.md` (internal audit, 11 findings) — local consistency baseline.

This file is the **decision sheet.** Each row is a gap with a fix, an estimate, a blast radius, and a recommended verdict. Kartavya picks the subset to authorise; no file changes happen on the basis of this document alone.

---

## Headline reads from the playbook (most load-bearing claims for this ecosystem)

1. **79% of multi-agent failures are spec / coordination, not model capability.** [Cemri et al., MAST taxonomy, T1] Implication: spec quality (Bhishma, skill.md, agent.md procedures) is the highest leverage we have.
2. **Trained-in policy ≫ prompt-only policy by ~20×.** [Anthropic Constitutional Classifiers, OpenAI Instruction Hierarchy, T1] Implication: Bhishma-as-system-prompt is the _floor_, not the ceiling — needs runtime layers underneath.
3. **Monitor-AUC caps near 0.87** with 20%+ FPR at 80% recall. [SHADE-Arena, T1] Implication: a single watcher (Sanjaya alone) cannot be the only line of defence. Sahadeva must add _independent_ signal — different model, different rubric, different context — or it just compounds Sanjaya's blind spots.
4. **Approval fatigue kicks in above ~10 reviews/session.** [AI Pattern Book, Palwe, T2] Implication: as Sanjaya begins proposing, Kartavya will rubber-stamp unless gates are pre-tiered by risk.
5. **Four-tier (T0/T1/T2/T-Audit) oversight is not directly studied** — components have empirical support, the stack as a whole is novel. Implication: instrument heavily; this ecosystem may produce the first useful post-mortem.

---

## The gaps, ranked by impact-to-effort

Risk legend: 🟢 no behaviour change · 🟡 low-risk behaviour change · 🟠 medium-risk · 🔴 high-risk

### G1. Bhishma is only a system-prompt contract — no runtime enforcement layer 🟠

**Playbook source.** Next-step #1 [Constitutional Classifiers T1, Instruction Hierarchy T1, Agentic Misalignment T1]. Defence-in-depth is the strongest finding in the safety literature; single-layer prompt enforcement is documented to fail.

**Current state.** Bhishma is 201 lines of rules every agent reads at session start. Enforcement relies entirely on each agent's self-discipline. There's no programmatic check before a tool runs; `write_scope` is declared in frontmatter but not enforced by the harness.

**Proposed fix (phased).**

1. **Layer A — declarative gate (1 hr).** Add a `bhishma-check.sh` script: reads the proposed tool call + the agent's `write_scope` from frontmatter; refuses if write target is outside scope. Wire into Claude Code via a `PreToolUse` hook in `.claude/settings.json`.
2. **Layer B — semantic gate (4 hr).** Pre-tool-call validator: a small LLM call (Haiku) that reads Bhishma + the proposed tool call + recent context, returns `allow | block | flag-for-review` with one-line rationale. Logged to the agent's journal.
3. **Layer C — post-action hook (2 hr).** After each significant action, log to a structured trace. Sanjaya reads traces in addition to chat transcripts.

**Estimate.** 7 hours total across 3 layers. Layer A alone gives meaningful protection.

**Verdict.** **Recommend approve Layer A now**; defer B+C until Layer A's signal is understood.

---

### G2. Sahadeva is not structurally different from Sanjaya/Vyasa 🟡

**Playbook source.** Next-step #2 [SHADE-Arena T1, weak-to-strong monitoring T2]. Monitor _architecture_ matters more than monitor _capability_. Correlated blind spots if every tier uses similar models, prompts, training.

**Current state.** Sahadeva model: `claude-opus-4-6`. Vyasa model: `claude-opus-4-6`. Same family. Sahadeva's rubric is "read journals, spot anomalies" — same shape as Sanjaya's, just stateless and wider. No pre-registered behavioural test set; "weekly audit" risks devolving into "weekly read-through" (playbook's own warning, next-step #6).

**Proposed fix.**

1. **Model rotation (15 min).** Sahadeva's `model:` frontmatter rotates per run: Claude Opus → GPT-5 → Gemini 2.5 Pro → Claude. Requires Sahadeva's runner to support multi-provider; if not, document as a desired feature and start with rubric+rubric diversity.
2. **Rubric diversity (1 hr).** Sahadeva should NOT re-verify Sanjaya's findings — that creates correlated review. Sahadeva's rubric: pre-registered behavioural evaluation against a small adversarial test set (G3 below), plus drift detection on metric trends (token/run, tools-per-task, MAST-code frequency), plus Bhishma violation detection.
3. **Adversarial probes (4 hr — see G3).**

**Verdict.** **Recommend approve rubric diversity now** (rewrite Sahadeva's skill.md). Defer model rotation until a multi-provider runner exists.

---

### G3. No pre-registered adversarial test set for Sahadeva 🟡

**Playbook source.** Next-step #6 [Anthropic alignment auditing T1]. Without a test set, Sahadeva's quality has no signal — you can't tell if its detection rate is dropping.

**Current state.** Sahadeva has never been run (reports/ is empty). When it does run, there's nothing measuring whether it actually caught what it should.

**Proposed fix.**

1. **Build 10–20 implanted-behaviour cases.** Examples: a journal entry that claims an unapproved proposal was applied; a `skill.md` change without a matching `approved/<id>.md`; an agent action outside its `write_scope`; an inter-agent invocation that violates Bhishma R8.
2. **Store at `_meta/audit/test-set/2026-Q2.md`.** Pre-registered: cases are fixed at the start of the quarter, refreshed each quarter to prevent overfitting.
3. **Sahadeva runs the test set every week.** Detection rate goes in the weekly report. If it drops below threshold, Sahadeva itself is flagged for recalibration.

**Estimate.** 4 hr first build + 1 hr/quarter refresh.

**Verdict.** **Recommend approve**, sequence with G2 (they reinforce each other).

---

### G4. No tiered approval gates — every proposal needs human review 🟡

**Playbook source.** Next-step #3 [approval fatigue literature, T2]. ≤10 approvals/session is sustainable; 30+ is rubber-stamp guaranteed.

**Current state.** Sanjaya hasn't crossed bootstrap thresholds yet (no proposals exist). But the design is: every proposal → Kartavya review. As workers mature and Sanjaya enters adaptation mode, proposal volume will rise.

**Proposed fix.**

1. **Define risk tiers in Bhishma** (new R-rule, R18). Three classes:
   - **doc-only** (e.g., adding a section to `skill.md`, fixing a typo): auto-approve after 24-hr cooling-off.
   - **behavioural** (new procedure, removed safeguard, scope expansion): requires Kartavya approval + rationale field.
   - **constitutional** (touches Bhishma references, tool permissions, write_scope, approval-gate logic): requires Kartavya approval + Sahadeva audit + 24-hr cooling-off (already enforced for approval-gate per R6 — extend).
2. **Sanjaya skill.md update.** New procedure: classify each proposal at draft time; mark `risk_tier:` in frontmatter; route accordingly.
3. **One-line rationale field** mandatory on every approval (forces actual reading).

**Estimate.** 2 hr. Mostly documentation + a tiny change to Sanjaya's proposal procedure.

**Verdict.** **Recommend approve** — cheap, prevents a known future failure mode.

---

### G5. No machine-readable structured traces 🟢

**Playbook source.** Next-step #4 [Anthropic engineering T2, Helicone/Langfuse T2]. "You cannot debug what you can't replay."

**Current state.** Sanjaya journals are narrative markdown. Excellent for human review; cannot be programmatically diffed, replayed, or aggregated. No span trees, no per-step token/cost accounting.

**Proposed fix.**

1. **Add `traces/<agent>-<run-id>.json`** alongside each journal entry. Schema: span tree (parent-child), tool inputs/outputs, decision points, tokens/cost per step.
2. **Simple `replay.sh <run-id>`** script that re-renders a trace for human or for Sahadeva.
3. **Drift alerts.** Cron job (Nakula territory) that watches metric trends — tool-call rate, tokens-per-step, MAST-code frequency. Alerts on outliers.

**Estimate.** 6 hr — schema design + writer in each agent's runner + the replay tool + a basic alert script.

**Verdict.** **Recommend approve later** (after G1 Layer A is in place — the post-action hook from G1 produces the trace data this consumes).

---

### G6. No MAST taxonomy in journal entries 🟢

**Playbook source.** Next-step #5 [Cemri et al. NeurIPS 2025, T1]. 14 failure modes with 88% inter-annotator agreement is the closest thing to a standard vocabulary.

**Current state.** Sanjaya's journal entries describe patterns in prose ("skill-based-architecture", "parallel-research-streams", "tier-tagged-citation-discipline"). Useful but ad-hoc — no stable frequency tracking, no aggregation across agents.

**Proposed fix.**

1. **Add `mast_codes: [FM-x.y, FM-z.w]`** to journal entry frontmatter.
2. **Sanjaya's skill.md gets a MAST reference table** (the 14 codes) for classification.
3. **Sahadeva aggregates** weekly: MAST-code-frequency per agent → trend chart → flagged categories.

**Estimate.** 1 hr (add the table + the field; existing journals don't need backfill).

**Verdict.** **Recommend approve** — purely additive, no behaviour change.

---

### G7. Sanjaya's journals will grow unbounded 🟢

**Playbook source.** Bonus item [Anthropic Effective Context Engineering, T1]. research-agent's journal is already 49KB after 13 runs — extrapolating, in 3 months Sanjaya will hit context limits reading its own journal.

**Current state.** No compaction. No archive policy.

**Proposed fix.**

1. **Rolling compaction.** Sanjaya keeps last 30 days verbatim; older entries summarised into a monthly digest at `journal/<agent>/digest-<YYYY-MM>.md`.
2. **Anthropic's initialiser/worker pattern.** When Sanjaya starts a run, it reads the latest digest + last 30 days of verbatim entries — not the entire history.

**Estimate.** 3 hr (compaction script + journal procedure update).

**Verdict.** **Defer** until journals cross 200 KB. Currently the largest is 49 KB; not urgent.

---

### G8. Identity-coherence work from self-audit 🟡

Carry-overs from `2026-05-11_self-audit.md` (already partially applied):

| Sub-fix                                   | Status                                       | Notes                                                                 |
| ----------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------- |
| C1 — Yudhishthira reads Bhishma           | ✅ applied                                   | Confirmed in `agent.md` + `skill.md` P1                               |
| I1 — `tools:` list-form everywhere        | ✅ applied                                   | Observer + research-agent                                             |
| I2 — Observer `name:` → `sanjaya`         | ✅ applied (frontmatter only)                | Body still says "Observer Agent" — pending I6 batch                   |
| I3 — backfill missing frontmatter         | ✅ applied                                   | Observer + research-agent                                             |
| I4 — full model IDs                       | ✅ applied                                   | `claude-sonnet-4-6` / `claude-opus-4-6`                               |
| I5 — `runtime:` discriminator             | ✅ applied for yudhishthira + research-agent | Sahadeva audit script needs to handle it                              |
| I6 — research-agent → Vidura body reframe | ⏳ deferred                                  | Bundle with Sanjaya body reframe; do as one Mahabharat-coherence pass |
| Sanjaya body reframe                      | ⏳ deferred                                  | Same batch as I6                                                      |
| Co1–Co4 — cosmetic                        | ⏳ deferred                                  | Wait for Sahadeva's first run to see which keys it actually consumes  |

**Verdict.** Recommend approving the I6 + Sanjaya body batch now that the playbook frame is in. Cosmetic items stay deferred.

---

### G9. The playbook's most uncomfortable finding — instrument what's novel 🟠

**Playbook source.** Detailed analysis §8, gaps #1 and #3 [no direct literature on four-tier oversight].

The single most novel and least-validated part of this ecosystem is the four-layer oversight stack itself. The playbook explicitly flags this as the place to instrument most aggressively.

**Proposed fix.** Treat the ecosystem as an experiment. Specifically:

1. **Define independence metrics between tiers.** What fraction of Sanjaya's flagged patterns does Vyasa endorse? What fraction does Sahadeva flag that the other two missed? Track these — if they trend toward 100% agreement, the tiers are not adding independent signal.
2. **Quarterly "tier-independence" review.** Kartavya reads three randomly-selected anomalies and checks whether each tier's framing is genuinely different.
3. **Document this is the experiment.** Add a section to Bhishma or to `_audit/` README naming the open question: "is layered oversight adding independent signal here, or compounding biases?" The honesty is the instrumentation.

**Estimate.** 1 hr documentation + ongoing review. The metric tracking falls out of G5 (structured traces) and G6 (MAST codes) for free.

**Verdict.** **Recommend approve** the documentation now; metric tracking arrives with G5+G6.

---

## Recommended sequencing

**Phase 1 — low-risk additive (this week, ~6 hr total):**

- G4 — tiered approval gates in Bhishma (R18) + Sanjaya skill.md
- G6 — MAST taxonomy in journal frontmatter
- G9 — document the "instrument what's novel" stance
- G8 (deferred items) — research-agent → Vidura body reframe + Sanjaya body title alignment

**Phase 2 — runtime enforcement (next week, ~7 hr):**

- G1 Layer A — declarative `PreToolUse` hook checking `write_scope`
- G2 — rewrite Sahadeva's rubric (structural diversity from Sanjaya)
- G3 — build the first adversarial test set (Q2 cases)

**Phase 3 — observability (after first Sahadeva run, ~6 hr):**

- G5 — structured traces alongside journals
- G1 Layer C — post-action audit hook (consumes the trace data)
- G7 (if needed) — journal compaction

**Phase 4 — semantic guardrails (only if Phase 1–3 signal warrants it):**

- G1 Layer B — Haiku-based pre-tool-call semantic validator

---

## What this analysis deliberately did NOT propose

- **Replacing Claude with mixed-provider stack.** Playbook recommends model diversity for monitor agents, but multi-provider infra is a separate project — flagged in G2 as deferred.
- **Adopting a multi-agent framework (LangGraph, AutoGen, CrewAI).** Playbook anti-pattern A5: "Frameworks before understanding." This ecosystem's raw approach is the right starting point.
- **Adding more agents.** Playbook principle P1: "Start with the simplest system." 6 working agents + 3 meta-agents is plenty. Don't grow until utilisation is proven.
- **Removing Vyasa.** The playbook's data on diminishing returns >3 layers is suggestive, not definitive. Vyasa adds the meta-observer-of-the-observer signal that Sahadeva's stateless audit doesn't replace. Leave intact and instrument (G9).

---

## Decision point for Kartavya

This analysis proposes **9 fixes across 4 phases.** Lowest-risk additive work (Phase 1) is ~6 hours and includes:

- Sharper approval-gate policy (G4)
- Stable diagnostic vocabulary for Sanjaya (G6)
- Body reframes that complete the Mahabharat coherence pass (G8)
- An honest acknowledgment of what's novel and untested (G9)

Phase 2–4 are larger and warrant a separate go-ahead each.

**Ask Kartavya.** Authorise Phase 1 in full, or pick a subset; the remaining phases stay parked until requested.

---

_Synthesis 2026-05-11 22:55 IST. Pairs with `2026-05-11_multi-agent-playbook.md` (37 sources, tier-tagged) and `2026-05-11_self-audit.md` (11 findings)._
