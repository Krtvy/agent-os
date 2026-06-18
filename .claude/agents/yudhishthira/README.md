# ⚖️ Yudhishthira — Data Analyst

> Tier 0 · Mahabharat: Yudhishthira, the dharmaraja who answers truthfully

Data analyst for Kartavya. Profiles a file, declares filters, computes in pandas, audits its own numbers, and ships two deliverables per task: a clean `.csv` and an audit-ready `.md`. Reconciliation between two sources is a first-class task type. Learns each recurring task once via a living Playbook.

The deployed agent runs on the **Hyperagent** platform. Local files document identity and procedures so Sanjaya can observe.

## The loop (every task)

1. INSPECT — shape, columns, dtypes, nulls, sample
2. CLASSIFY — single-number / breakdown / time series / reconciliation / segmentation
3. DECLARE FILTERS — every filter named before any calculation
4. COMPUTE — pandas, with row counts at each filter step
5. AUDIT — recompute a summary number a second way; sanity-check against an anchor
6. DELIVER — `.csv` + `.md`

## Learning

- **Playbook** (Hyperagent doc `cmp1f7kpo105407adc5ijk8r9`, mirrored at `playbook.md`) — procedures, schemas, metric definitions, intern conventions. Updated only on explicit "remember this".
- **Memories** — atomic facts (file paths, column names). `autoSaveMemories: false`.

## Files

| File / dir     | Purpose                                 |
| -------------- | --------------------------------------- |
| `agent.md`     | Identity + system prompt                |
| `skill.md`     | Operational procedures (P0–P9)          |
| `playbook.md`  | Local mirror of the Hyperagent Playbook |
| `README.md`    | This file                               |
| `CHANGELOG.md` | Append-only agent-level history         |

## Phase

- **Phase 1 (current):** read-only on Google Sheets; produces `.csv` + `.md` per task.
- **Phase 2 (future):** Sheets write-back via dedicated service account. Not yet provisioned.

## Upstream / Downstream

- **Upstream:** kartavya (the data intern)
- **Downstream:** none (analytical output only; no state-changing calls)

## Watched by

- Sanjaya at `_meta/observer/journal/yudhishthira.md` (auto-created on next observer run)

## See also

- `agent.md` — full identity, the loop, deliverable format, reconciliation spec
- `skill.md` — operational procedures including backup guardrail (P0)
- `playbook.md` — local mirror of the learning artifact
