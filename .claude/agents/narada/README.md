# 🪶 Narada — Message Drafter

> Tier 0 · Mahabharat: Narada, the celestial messenger

Message-drafting agent for Kartavya's external communications. Any format — emails, project updates, cold outreach, LinkedIn messages, cover letters, interview follow-ups. Voice-matched, no AI tells, hard length budgets. Never sends, never decides what to communicate — only polishes.

## Modes

- **`stakeholder-update`** — ≤200 words, scannable, lead with shipped output, end with concrete next step.
- **`creator-dm`** — ≤80 words, one specific reference to recent content, plain offer, soft CTA.
- **`other`** (rare) — Slack, email, etc. Same principles.

## Voice replication

Narada has a 25-skill voice-replication pipeline at `voice-pipeline/` (sourced from `aaddrick/written-voice-replication`, MIT). When `voice-samples/` corpus crosses ≥50 items, the pipeline derives `voice-fingerprint.json` which feeds into drafting. See `voice-pipeline/INTEGRATION.md`.

## Files

| File / dir               | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `agent.md`               | Identity + system prompt                          |
| `skill.md`               | Operational procedures                            |
| `README.md`              | This file                                         |
| `CHANGELOG.md`           | Append-only agent-level history                   |
| `voice-samples/`         | Kartavya's writing corpus (Slack DMs, AI updates) |
| `voice-pipeline/`        | 25-skill voice-replication pipeline               |
| `voice-fingerprint.json` | Derived style profile (when present)              |

## Upstream / Downstream

- **Upstream:** kartavya
- **Downstream:** none (drafts only; sending is arjuna's job)

## Watched by

- Sanjaya at `_meta/observer/journal/narada.md`

## See also

- `agent.md` — full identity, modes, forbidden phrases, generic-reject filter
- `skill.md` — drafting procedures and voice-pipeline decision tree
- `voice-pipeline/INTEGRATION.md` — how pipeline outputs fold into the fingerprint
