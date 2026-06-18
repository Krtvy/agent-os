# 🐒 Hanuman — Reconnaissance Scout

> Tier 0 · Mahabharat: Hanuman, the scout who leapt to Lanka

Reconnaissance/scout agent for creator-ops. Given a TikTok creator handle or URL, gathers structured information from Kalodata, TikTok public profiles, and Cruva. Returns tier-tagged profile reports with fit assessment for MagAshwa. Read-only on all external systems — never sends, never modifies.

## Capabilities

- Profile lookup: shallow (profile + last 10 posts) or full (90-day GMV, audience demos, brand-collab history, risk flags).
- Source-tier tagging on every claim.
- Caches scout results locally (`cache/`) for replay and Sanjaya inspection.
- Competitor tracking driven by `competitors.yml`.

## Files

| File / dir        | Purpose                              |
| ----------------- | ------------------------------------ |
| `agent.md`        | Identity + system prompt             |
| `skill.md`        | Operational procedures               |
| `README.md`       | This file                            |
| `CHANGELOG.md`    | Append-only agent-level history      |
| `scripts/`        | Scrape/query scripts for each source |
| `cache/`          | Cached scout reports                 |
| `competitors.yml` | Tracked competitor handles + cadence |

## Upstream / Downstream

- **Upstream:** kartavya, narada (creator-dm mode pulls scout reports)
- **Downstream:** kalodata, cruva (MCPs, read-only)

## Watched by

- Sanjaya at `_meta/observer/journal/hanuman.md`

## See also

- `agent.md` — full identity and scope
- `skill.md` — scout procedures
- `_meta/conductor/bhishma.md` — root behavioral contract
