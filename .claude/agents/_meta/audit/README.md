# 🔮 Sahadeva — Tier-Audit External Auditor

> Tier-Audit · Mahabharat: Sahadeva, the wisest Pandava (astrologer, sees past/present/future)

Tier-Audit auditor that runs **once weekly with completely fresh context**. Reads the past week's journals, proposals, and approvals across every agent in Kartavya's ecosystem. Detects anomalies, drift, miscalibration, and Bhishma violations. Writes a single weekly report directly to Kartavya, bypassing all other agents.

Never modifies any agent. Read-only on the entire repo.

## Why a separate tier

Sanjaya watches Tier-0 workers. Vyasa watches Sanjaya. Sahadeva watches **all of them**, stateless and weekly, so calibration drift in either meta-agent can't accumulate unnoticed.

## Files

| File / dir     | Purpose                                                  |
| -------------- | -------------------------------------------------------- |
| `agent.md`     | Identity + system prompt                                 |
| `skill.md`     | Audit procedures                                         |
| `README.md`    | This file                                                |
| `CHANGELOG.md` | Append-only agent-level history                          |
| `inbox.md`     | Standing prompts / signals Kartavya wants checked weekly |
| `reports/`     | Dated weekly audit reports                               |

## Upstream / Downstream

- **Upstream:** scheduled (weekly cron) + kartavya (ad-hoc invocation)
- **Downstream:** none (reads everything, writes only to `reports/`)

## What Sahadeva checks

- Sanjaya journals for hallucinated entries or pattern misreads.
- Sanjaya proposals for off-spec changes (e.g. expanding scope beyond `skill.md`).
- Vyasa proposals against Sanjaya for over-correction.
- Tier-0 agents for Bhishma violations (scope creep, undisclosed tool use, voice impersonation).
- Approval cadence and balance (too many auto-approved? too many rejected?).
- Calibration drift: agents quietly broadening their effective scope over time.

## See also

- `agent.md` — full audit charter
- `skill.md` — audit procedures
- `_meta/conductor/bhishma.md` — root behavioral contract Sahadeva checks against
