---
id: 20260528-nakula-adaptation-skills
target_agent: nakula
target_file: .claude/agents/nakula/skill.md
mode: adaptation
created_at: 2026-05-28T02:00:00+05:30
confidence: low
status: pending
applied_at: null
report_id: nakula-2026-05-28
---

# Proposal — Nakula adaptation threshold (day 18): K8 weekly-summary annotation

## Pointer to Pattern Report

`reports/nakula-2026-05-28.md` — 18 calendar days observed, 1 agentSetting-attributed run (smoke test 4a1f25ee), heartbeat.json confirmed operational (3 exit-0 entries). Confidence score: 40 (low, exactly at ≥40 floor).

---

## Finding

One qualifying signal was found at the 18-day adaptation threshold:

**K8 (weekly summary heartbeat, Sunday 23:55 UTC) — documented but not observed running.**

- skill.md P7 documents: on Sunday at 23:55 UTC ± 5 min, nakula-run.sh should compute a weekly summary (jobs_total, jobs_success, jobs_failure, jobs_skipped, uptime_pct) and append a weekly-summary entry to `logs/heartbeat.json`.
- Nakula was wired 2026-05-22. First eligible Sunday: 2026-05-24 23:55 UTC.
- `logs/heartbeat.json` inspected in Windows 13, 14, and 15 (3 consecutive observation windows post-wiring): contains only per-job sanjaya entries. No weekly-summary entry present.
- 3 windows of confirmed absence after the first eligible Sunday meets the ≥3 observation threshold for a documented-but-unused signal.
- Note: evidence is absence-evidence (weak). The second eligible Sunday (2026-05-31) will definitively confirm or clear this gap. Sahadeva W22 (2026-05-31) is expected to check this.

**All other skill.md procedures (K4, K5, K6, K9) are documented and not contradicted.** They have not been exercised because nakula has had 0 live job runs beyond the sanjaya daily scheduler (heartbeat confirmed). These are structural completions not yet reached due to low invocation frequency — not skill gaps.

This proposal therefore carries a **minimal diff** — annotating P7's K8 sub-procedure as requiring verification rather than modifying operational behavior.

---

## Proposed change

```diff
--- a/.claude/agents/nakula/skill.md
+++ b/.claude/agents/nakula/skill.md
@@ P7 weekly-summary block @@
-If current time is Sunday 23:55 UTC (±5 min):
-  compute weekly_summary = {
-    jobs_total, jobs_success, jobs_failure, jobs_skipped, uptime_pct
-  }
-  append to logs/heartbeat.json as type: weekly-summary
+If current time is Sunday 23:55 UTC (±5 min):
+  compute weekly_summary = {
+    jobs_total, jobs_success, jobs_failure, jobs_skipped, uptime_pct
+  }
+  append to logs/heartbeat.json as type: weekly-summary
+  # NOTE (observer 2026-05-28): K8 has not produced a heartbeat entry after the first
+  # eligible Sunday (2026-05-24). Verify that nakula-run.sh implements this Sunday-time
+  # branch. If not implemented, this block is aspirational — mark TODO until wired.
```

---

## Rationale

- **K8 absence pattern (3 windows):** Windows 13 (Run 20, 2026-05-26), 14 (Run 21, 2026-05-27), and 15 (Run 22, 2026-05-28) all show `logs/heartbeat.json` containing sanjaya per-job entries only. No weekly-summary entry present. First eligible Sunday was 2026-05-24 at 23:55 UTC.
- **Possible causes:** (a) nakula-run.sh does not yet implement the Sunday-time branch of P7 (K8 is aspirational documentation); (b) the implementation exists but a timing bug prevents the branch from firing; (c) the cron job does not run at Sunday 23:55 UTC (current crontab fires at 02:00 IST = 20:30 UTC, not 23:55 UTC).
- **Cause (c) is the most probable:** The `jobs.yml` sanjaya entry runs at `cron: "30 20 * * *"` (daily 02:00 IST = 20:30 UTC). There is no separate Sunday 23:55 UTC job entry in jobs.yml. K8 cannot fire unless nakula-run.sh has an internal time-check, or a separate cron job is added.
- **Resolution paths for Kartavya:**
  1. Add a separate Sunday 23:55 UTC job to `nakula/jobs.yml` pointing to a weekly-summary script.
  2. Implement the time-check inside nakula-run.sh and confirm it fires at 23:55 UTC.
  3. Remove K8 from skill.md P7 if the weekly summary is not planned.

---

## Risk note

Low risk. The annotation proposed is comment-only and does not change operational behavior. The finding is absence-evidence (weak). Kartavya may approve this proposal to formally acknowledge the K8 gap and trigger a jobs.yml update, or reject it if K8 is intentionally deferred. If rejected, the observer will archive this proposal and stop flagging K8 until a new observation is made.

---

## Open operational item (not in skill.md scope — requires Kartavya action)

**`nakula-run.sh` auth path verification required before 2026-06-15.**

REMINDERS.md flag `anthropic-agent-sdk-credit-pool` surfaces 2026-06-01. The Anthropic SDK + `claude -p` credit pool separates from the subscription pool on 2026-06-15. If `nakula-run.sh` (or any script it calls) auths via subscription rather than an API key, jobs that invoke Claude will break or draw from the wrong pool after that date.

This is an infrastructure verification item, not a skill.md gap. No diff proposed.
