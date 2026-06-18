---
id: 20260528-arjuna-adaptation-skills
target_agent: arjuna
target_file: .claude/agents/arjuna/skill.md
mode: adaptation
created_at: 2026-05-28T02:00:00+05:30
confidence: medium-low
status: pending
applied_at: null
report_id: arjuna-2026-05-28
---

# Proposal — Arjuna adaptation threshold (day 18): null-change confirmation + credit-pool flag

## Pointer to Pattern Report

`reports/arjuna-2026-05-28.md` — 18 calendar days observed, 1 agentSetting-attributed run (smoke test), 22 live P10 idempotency keys from scripted execution on 2026-05-11. Confidence score: 45 (medium-low, above ≥40 floor).

---

## Finding

No adaptation changes to `skill.md` are warranted at this threshold. The signal analysis produced:

- **Undocumented behavior:** None qualifying at ≥3 observations. P10 (daily competitor video analysis, operator-added 2026-05-11) is fully documented in skill.md P10. Scripted invocation via `scripts/video-analyze-batch.sh` is the intentional execution path per P10 design.
- **Documented-but-unused:** R1–R9 (skill.md P1–P9) have never been invoked in a live interactive arjuna session. This reflects the agent's operational state (P10 is the only active execution path so far) rather than a skill manual gap. skill.md P1–P9 remain accurate for the intended interactive invocation path.
- **Recurring failures:** None. Zero error events attributable to arjuna in 18 days.

**This proposal therefore carries a null diff.** Its purpose is to formally close the adaptation threshold observation cycle, record the finding for Sahadeva's audit, and surface the one actionable operational item below.

---

## Proposed change

```diff
--- a/.claude/agents/arjuna/skill.md
+++ b/.claude/agents/arjuna/skill.md
@@ no change @@
 (No modification to skill.md is proposed at this time.)
```

This is an intentional null diff. Kartavya may approve this proposal to formally acknowledge that the 18-day adaptation cycle has completed cleanly and the skill.md is accurate.

---

## Rationale

- **Observation 1 (smoke test 5e1a814a, 2026-05-10):** Single-line machine-parseable response listing 7 safety features. Confirms P1–P9 self-description is accurate at statement level. No contradictions found between smoke-test output and skill.md documentation.
- **Observation 2 (idempotency keys, 2026-05-11):** 22 files in `idempotency-keys/video-analysis/` confirming P10-new-C (idempotency per video) is operational. All keys carry `run_id: arjuna-20260511-162644Z-57968a` and `completed_at_utc` timestamps — genuine live execution.
- **Observation 3 (skill.md P10, operator-added 2026-05-11):** P10 is fully documented. The two-tier analysis gate (P10-new-A), Gemini key rotation (P10-new-B), and idempotency enforcement (P10-new-C) are all reflected in skill.md. No drift between the spec and the live evidence.

---

## Risk note

Low risk. No skill.md modification is proposed. The only risk of approving this proposal is administrative: it closes the threshold cycle and allows a future adaptation proposal to be drafted at the next threshold (run axis: 40 runs, or calendar reset). If Kartavya disagrees with the null-change finding, the correct action is to reject this proposal and provide a specific change direction.

---

## Open operational item (not in skill.md scope — requires Kartavya action)

**`scripts/video-analyze-batch.sh` auth path verification required before 2026-06-15.**

REMINDERS.md flag `anthropic-agent-sdk-credit-pool` surfaces 2026-06-01. The Anthropic SDK + `claude -p` credit pool separates from the subscription pool on 2026-06-15. If `video-analyze-batch.sh` auths via subscription (Claude Code interactive session) rather than an API key, arjuna's P10 scripted runs will break or draw from the wrong pool after that date.

This is an infrastructure verification item, not a skill.md gap. No diff proposed.
