---
id: 20260528-narada-word-count-conflict
target_agent: narada
target_file: .claude/agents/narada/agent.md (primary); .claude/agents/narada/RATING-NOTES.md (secondary)
mode: adaptation
created_at: 2026-05-28T02:00:00+05:30
confidence: medium-low
status: pending
applied_at: null
report_id: narada-2026-05-28
sahadeva_endorsement_required: true
---

# Proposal — Narada adaptation threshold (day 18): resolve mayank-update word-count conflict

## Pointer to Pattern Report

`reports/narada-2026-05-28.md` — 18 calendar days observed, 1 agentSetting-attributed run (smoke test 8d0d2935), 0 live drafts, word-count conflict documented across 16 consecutive observation windows. Confidence score: 45 (medium-low, above ≥40 floor). Sahadeva endorsement required (behavioural tier: modifies agent constraint fields).

---

## Finding

One qualifying signal at the 18-day adaptation threshold with HIGH confidence:

**Word-count conflict — `agent.md` hard cap (200 words) vs `RATING-NOTES.md` launch-day ceiling (350 words) for `mayank-update` mode.**

This conflict has been documented in every observation window since Window 2 (2026-05-11) — 16 consecutive windows. It was escalated to Kartavya by Sahadeva in both W20 §8 rec 4 (2026-05-17, "pick one number") and W21 §9 rec 2 (2026-05-24, "one edit, one number"). Neither file has been updated to resolve the contradiction.

**Consequence:** The first live `mayank-update` draft will produce a non-deterministic word budget — narada will apply whichever file it reads first, yielding either a 200-word or 350-word output. This is a real operational risk, not a theoretical one.

---

## Proposed change (two variants — Kartavya must pick one)

### Variant A — Keep 200 words (recommended: agent.md is the authoritative skill file)

```diff
--- a/.claude/agents/narada/RATING-NOTES.md
+++ b/.claude/agents/narada/RATING-NOTES.md
@@ mayank-update ceiling block @@
-mayank-update: launch-day ceiling: 350 words
+mayank-update: launch-day ceiling: 200 words
+# Unified with agent.md hard cap (2026-05-28). agent.md is authoritative.
```

No change to `agent.md`. The 200-word hard cap in `agent.md` remains as-is.

### Variant B — Keep 350 words (choose if richer launch-day narrative is desired)

```diff
--- a/.claude/agents/narada/agent.md
+++ b/.claude/agents/narada/agent.md
@@ mayank-update constraint block @@
-mayank-update: ≤ 200 words (hard cap)
+mayank-update: ≤ 350 words (hard cap)
+# Aligned with RATING-NOTES.md launch-day ceiling (2026-05-28). RATING-NOTES.md is authoritative.
```

No change to `RATING-NOTES.md`. The 350-word ceiling in `RATING-NOTES.md` remains as-is.

---

## Rationale

- **Observation 1 (Window 2, 2026-05-11):** Operator session `f5e77e7f` produced a live narada draft at ~245 words. Narada itself flagged the word-count contradiction in its draft response. First observation.
- **Observations 2–16 (2026-05-13 → 2026-05-28):** Both files read each window. Both constraints present and contradictory each window. No resolution observed.
- **Sahadeva W20 §8 rec 4 (2026-05-17):** Explicit escalation to Kartavya — "Resolve the Narada word-count conflict. First live mayank-update draft will produce incorrect behavior. Quick decision: pick one number." No action taken.
- **Sahadeva W21 §9 rec 2 (2026-05-24):** Second escalation — "Resolve the Narada word-count conflict. One edit, one number." No action taken.
- **Recommendation:** Variant A (200 words) is recommended. `agent.md` is the primary skill specification; `RATING-NOTES.md` is a reference note. When they conflict, `agent.md` should be authoritative. The 200-word constraint is also more consistent with `mayank-update`'s purpose (concise, message-format content for a messaging app).

---

## Risk note

**Tier: behavioural.** This proposal modifies a word-count constraint in an agent skill file, which changes narada's output behavior on `mayank-update` drafts. Sahadeva endorsement is required before Kartavya approves.

**Risk of approving Variant A:** Any existing drafts or user expectations calibrated to 350 words may need adjustment. Risk is low since 0 live `mayank-update` drafts have been produced in 18 days — no established expectation to break.

**Risk of approving Variant B:** The `agent.md` hard cap would increase from 200 to 350 words. If the downstream consumer of `mayank-update` content (Mayank's messaging) expects concise messages, longer output may reduce quality.

**Risk of rejecting this proposal:** The word-count conflict remains unresolved indefinitely. The first live `mayank-update` session will produce non-deterministic word budget. Observer will re-flag at the next observation window and re-submit at the next adaptation threshold.

---

## Secondary signal (not proposing changes — monitoring only)

**Voice corpus at 25/50 items (16 windows unchanged):** `voice-samples/` has 25 items. `skill.md P2 branch 3` (voice-pipeline delegation to pipeline-orchestrator) requires ≥50 items. The corpus has not grown since Window 2. Narada will continue using `voice_calibration: default` until the corpus reaches 50 items. No skill.md change needed — the branch logic correctly handles this case. Flagging for awareness: if voice-pipeline delegation is a desired capability, 25 more voice samples are needed.
