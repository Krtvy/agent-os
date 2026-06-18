# 🏹 Arjuna — Precision Executor

> Tier 0 · Mahabharat: Arjuna, the unerring archer

Precise execution agent for API calls and state-changing operations. Receives explicit instructions and executes via TikTok Creator Marketplace, Cruva, Euka, Periskope, Hyperagent. Refuses ambiguous instructions — never strategizes, only executes.

## Capabilities

- Idempotency keys for every state-changing call (no accidental double-sends).
- Per-target circuit breakers (`circuit-breakers/`) to halt on repeated failure.
- Rate-limit awareness with backoff.
- Rollback plans declared before execution.
- Refuses to act on ambiguous instructions — escalates back to Kartavya.

## Files

| File / dir          | Purpose                                     |
| ------------------- | ------------------------------------------- |
| `agent.md`          | Identity + system prompt                    |
| `skill.md`          | Operational procedures                      |
| `README.md`         | This file                                   |
| `CHANGELOG.md`      | Append-only agent-level history             |
| `scripts/`          | Execution scripts (per-target API wrappers) |
| `idempotency-keys/` | Issued keys, prevents replay                |
| `circuit-breakers/` | Per-target failure-count state              |

## Upstream / Downstream

- **Upstream:** kartavya
- **Downstream:** TCM, Cruva, Euka, Periskope, Hyperagent (MCPs)

## Watched by

- Sanjaya at `_meta/observer/journal/arjuna.md`

## See also

- `agent.md` — full system prompt and constraints
- `skill.md` — execution procedures
- `_meta/conductor/bhishma.md` — root behavioral contract
