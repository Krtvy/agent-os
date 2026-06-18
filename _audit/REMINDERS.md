# Reminders

Append-only list of "remind me about this on/after a date." The SessionStart greeting at `lib/session-start-greeting.sh` reads this file and surfaces any reminder whose `remind_after` date is today or earlier.

## Format

Each reminder is a single block:

```
- id: <slug>
  added: YYYY-MM-DD
  remind_after: YYYY-MM-DD
  topic: <one-line subject>
  why: <why future-you would want this reminder>
  ref: <optional path to a related file>
```

When a reminder fires (surfaced in the greeting), either act on it or move its `remind_after` date forward. Don't delete — the audit trail of "things future-me wanted future-future-me to revisit" is itself useful.

## Active reminders

- id: zodchii-agent-ideas-revisit
  added: 2026-05-13
  remind_after: 2026-05-28
  topic: Revisit the 5 agent-ecosystem ideas from the zodchii Twitter thread
  why: Kartavya shared an X thread on 2026-05-13 about "10 Claude Code agents nobody told you to build." 5 ideas were judged worth-adapting (rot detection · pull-based standup · inbox triage · content repurpose · doc-consistency check) but deferred because Sahadeva hadn't run yet. By 2026-05-28, Sahadeva should have produced ~2 weekly audits, giving real operational signal to evaluate the ideas against. Decide which (if any) to propose for adoption.
  ref: \_audit/2026-05-13_zodchii-inspiration-intake.md

- id: anthropic-sonnet4-opus4-deprecation
  added: 2026-05-14
  remind_after: 2026-06-01
  topic: Sonnet 4 / Opus 4 (`-20250514`) hard-deprecate on 2026-06-15
  why: Any code or agent still pinned to `claude-sonnet-4-20250514` or `claude-opus-4-20250514` will break after 2026-06-15. Repo audit on 2026-05-14 found zero references — current agents all on 4.6 / 4.5. Re-grep before June 15 in case new code lands (cmo-agent, Rootlabs app, automations). Migration target: Opus 4.7 or Sonnet 4.6 depending on workload. NOTE Opus 4.7 has a new tokenizer that eats 15–35% more text tokens — re-baseline cost before mass-switching text-heavy agents (Vidura, Sahadeva).
  ref: \_research/2026-05-14_anthropic-agent-ecosystem.md

- id: anthropic-agent-sdk-credit-pool
  added: 2026-05-14
  remind_after: 2026-06-01
  topic: Agent SDK + `claude -p` start drawing from separate Pro/Max credit pool on 2026-06-15
  why: Starting 2026-06-15, Agent SDK usage and `claude -p` (headless / scripted invocations) on Pro/Max subscriptions draw from a separate monthly credit pool — not the regular subscription allowance. Affects Nakula's cron pattern if it auths via subscription rather than API key. Audit before June 15. Switch crons to API-key auth if the new pool is too small for the workload.
  ref: \_research/2026-05-14_anthropic-agent-ecosystem.md
