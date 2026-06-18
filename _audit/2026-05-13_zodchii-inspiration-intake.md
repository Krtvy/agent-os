# Inspiration intake — "10 Claude Code agents nobody told you to build"

**Date:** 2026-05-13 03:40 IST
**Source:** X thread by @zodchii — pasted into chat (URL `https://x.com/zodchiii/status/2054137878968439247` was 402-walled to WebFetch).
**Status:** **Noted, no changes applied.** Per Kartavya: "it's up to you." My judgment: hold until Sahadeva's first audit Sunday gives real signal.
**Revisit by:** 2026-05-28 (see `_audit/REMINDERS.md`).

---

## TL;DR

Article is 60% legitimate agent patterns + 40% paid promo for "Teamly" (hosted-agents service). Of the 10 agents proposed, 5 have ideas worth adapting to our Mahabharat ecosystem, 5 don't fit our context. Not applying any tonight because: (a) Sahadeva isn't running yet, so we have no real signal; (b) the override-count discipline says next constitutional change goes through proposals; (c) speculation-driven additions are exactly what Bhishma R23 was designed to prevent.

---

## The 5 ideas worth keeping (in priority order)

### A. Rot detection for Sanjaya

**From the post:** "Refactor Tracker" — greps for TODO, FIXME, oversize files, duplicated logic. Outputs a prioritized rot list weekly.

**Our adaptation.** A new sub-skill in Sanjaya — `spec_rot_detection` — that scans agent `.md` files for:

- TODO / FIXME / `⚠ Pending` markers older than 30 days
- Skill sections that haven't been invoked across observed runs (extends existing `drift_detection`)
- `agent.md` files where the body has diverged from the `CHANGELOG.md`
- Inline `⚠ Pending confirmation` callouts past N days

Weekly output to Sahadeva's inbox. Triage from there.

**Why it fits.** Natural extension of Sanjaya's existing journaling + drift detection. Staleness is a kind of drift. No new tools, no new scope, just additional reading.

**Override tier.** Behavioural — R23 proposal flow.

**Trigger to revisit.** Volume of `⚠ Pending` markers crosses 30 across the repo. (Current: ~24 just in the May report v3.)

---

### B. Pull-based standup mode for Narada

**From the post:** "Daily Standup Agent" — reads GitHub commits + Linear + calendar, writes 4-line summary at 8am.

**Our adaptation.** A new mode for Narada — `mayank-update-auto`. Instead of you typing raw notes, Narada pulls:

- `git log --since="yesterday"`
- New / modified files in `_audit/` in the last 24h
- Sanjaya's daily journal updates
- Most recent Sahadeva findings

Drafts a 4-line update in your voice. You read + edit + send.

**Why it fits.** Narada already has voice-fingerprint + length-budget + generic-reject filter. The post's version has none of those. Ours would be voice-matched and content-grounded.

**Override tier.** Behavioural (new mode within Narada). R23 proposal.

**Trigger to revisit.** Anytime you find yourself manually typing the same standup-shaped notes 3 days in a row.

---

### C. Inbox triage for Sahadeva

**From the post:** "Inbox Triage Agent" — classifies emails into today/this-week/FYI/archive, drafts replies. (High risk for actual email; we narrow the scope.)

**Our adaptation.** When Sahadeva appends a critical finding to `_meta/audit/inbox.md`, also classify:

- **Severity** (already done) — critical / high / medium
- **Recommended action** (new) — investigate-now / queue-for-week / monitor-only / auto-resolve
- **Owner** (new) — which POC or agent should look at this

Without recommended-action + owner, the inbox is a list of problems with no shape. With them, the inbox becomes a triage queue.

**Why it fits.** Sahadeva already has the critical-finding escalation in P9. Triage is the next layer.

**Override tier.** Behavioural — extends existing procedure. R23 proposal.

**Trigger to revisit.** First time `_meta/audit/inbox.md` has 3+ entries.

---

### D. Content repurposer mode for Vidura

**From the post:** "Content Repurposer" — long-form post → 3 tweets + 1 LinkedIn + 1 newsletter + 5 alt headlines.

**Our adaptation.** When Vidura produces a long research deliverable (5K+ words, e.g. the multi-agent playbook), also output:

- 2-paragraph executive summary for `_audit/README.md`
- 5 key findings in tweet-length form
- A glossary-entry-shaped extraction of any new terminology
- An honest "what I couldn't verify" callout

Makes long research **portable** instead of stuck in one document nobody reads.

**Why it fits.** The teaching loop (VISION Phase 1) needs SHORTER artifacts to feed into glossary and patterns. Repurposing is the bridge.

**Override tier.** Behavioural (new output mode in Vidura).

**Trigger to revisit.** Next time Vidura produces a 3K+ word deliverable.

---

### E. Doc-consistency pre-commit check (not auto-write)

**From the post:** "Doc Writer" — auto-PRs docs on every merge. Risky.

**Our adaptation.** A pre-commit check (NOT auto-write):

- When you edit an agent's `skill.md`, the check looks at the diff and flags: "Did `agent.md` and `CHANGELOG.md` need updating too?"
- Does not auto-write. Blocks the commit until you confirm or annotate.
- Same shape as `lib/bhishma-check.sh` — pre-tool-use guard with clear allow/block.

**Why it fits.** Our discipline is "humans write docs, machines check consistency." The post inverts that.

**Override tier.** Constitutional — touches `.claude/settings.json` hooks. Strict R23 path.

**Trigger to revisit.** Next time you edit `skill.md` and forget the `CHANGELOG.md` entry. (Will happen.)

---

## The 5 ideas not worth keeping (and why)

- **PR Reviewer / Test Generator** — we're not a code-review shop. Revisit when the Phase 2 portal codebase exists.
- **Bug Hunter (auto-fix PRs from Sentry)** — too autonomous, too risky. Auto-drafting fix PRs from stacktraces is how confidently-wrong code gets shipped.
- **Cold Outreach Personalizer** — we already have this (Hanuman + Narada with anti-hallucination discipline). Better than the post's version.
- **Customer Feedback Synthesizer** — possibly relevant for Rootlabs _product_ team, not for the data-analyst-for-POCs work we're building toward.
- **Teamly (the hosted-agents service)** — affiliate pitch in the post. Standard hosting (Fly.io, Railway, Render, $5 VPS) does the same thing without single-vendor dependency.

## Why I'm not applying any tonight

1. **Sahadeva hasn't run yet.** First audit Sunday 2026-05-17. Until then we have zero operational signal — adopting ideas now is pure speculation.
2. **Override count discipline.** R23 line was drawn: next constitutional change goes through proposals + Sahadeva endorsement. Applying ANY of these in-thread would be override #4 (or amendment to override #3 within the same conversation, like before — but this is a different conversation hour, so it'd genuinely be #4).
3. **None of them are urgent.** Triggers for each idea are documented above. When the trigger fires, evaluate against fresh signal, not against today's enthusiasm.
4. **Inspiration-intake itself should be a discipline.** Read article → fit-check → document → defer until trigger. Not "read article → apply 5 things at 4am."

## What I AM doing tonight

- Saving this analysis durably (this file).
- Building a real 15-day reminder mechanism at `_audit/REMINDERS.md` + extending the SessionStart greeting to surface overdue reminders.
- That's it. No spec changes.

## Inspiration-intake as a project discipline

Adding to `VISION.md` Phase 1 practices: **read articles, do per-idea fit-checks, document the analysis, defer to trigger.** This file is the template for that practice. Future inspiration articles get the same treatment.

---

_Inspiration intake recorded 2026-05-13 03:45 IST. Author: Claude Code session at Kartavya's direction. Revisit: 2026-05-28 per `_audit/REMINDERS.md`._
