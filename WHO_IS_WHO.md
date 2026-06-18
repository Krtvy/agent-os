# Who is who

A one-page glossary of every agent in this ecosystem. Pick this up cold and you should be able to navigate the repo in 5 minutes.

---

## The cast

### Bhishma — the constitution ⚔️ (file, not agent)

|                     |                                                                                                                   |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/_meta/conductor/bhishma.md`                                                                       |
| **Tier**            | none — read by every agent on startup                                                                             |
| **Mahabharata fit** | The grandsire who took the inviolable vow. His vow constrained him from inside, even when his judgment disagreed. |
| **Job**             | 22 hard rules (R1–R22) that no agent may override. Constitutional governance.                                     |
| **Editable by**     | Kartavya only                                                                                                     |
| **Read by**         | Every agent, on every run                                                                                         |

---

### Vyasa — the conductor 📜 (Tier 2)

|                          |                                                                                                                                                                  |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**                 | `.claude/agents/_meta/conductor/`                                                                                                                                |
| **Mahabharata fit**      | The author of the epic. He composed the framework characters operate in. He granted Sanjaya divine sight personally. He intervenes rarely; mostly observes.      |
| **Job**                  | Watches Sanjaya for drift. Proposes meta-changes to Sanjaya's `skill.md` when Sanjaya itself appears to be miscalibrated or repeating the same kind of proposal. |
| **Watches**              | Sanjaya only                                                                                                                                                     |
| **Cadence**              | Every 6 hours (slow on purpose)                                                                                                                                  |
| **Threshold to propose** | 30 days OR 60 proposals processed                                                                                                                                |
| **Key constraint**       | Cannot touch Tier-0 workers (R3). Cannot loosen R1–R13 (R14).                                                                                                    |
| **Failure mode**         | Passivity — does nothing for too long                                                                                                                            |
| **Counter**              | Explicit thresholds force activity                                                                                                                               |

---

### Sanjaya — the observer 👁 (Tier 1)

|                          |                                                                                                                                                                                               |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**                 | `.claude/agents/_meta/observer/` (also aliased as `observer.md`)                                                                                                                              |
| **Mahabharata fit**      | The charioteer-minister granted divya drishti by Vyasa. Watches the entire battlefield. Narrates faithfully — even his own side's defeats. Cannot intervene.                                  |
| **Job**                  | Watches every Tier-0 worker (Vidura, Hanuman, Narada, Arjuna, Nakula). Journals their behavior. After enough evidence, proposes improvements to their `skill.md` files via the approval gate. |
| **Watches**              | All Tier-0 workers                                                                                                                                                                            |
| **Cadence**              | Every 30 minutes                                                                                                                                                                              |
| **Threshold to propose** | 20 runs OR 10 days of observation                                                                                                                                                             |
| **Key constraint**       | Cannot modify any worker without an approved proposal (R4)                                                                                                                                    |
| **Failure mode**         | Misclassification — sees what happens, not always what it means                                                                                                                               |
| **Counter**              | `heuristic_cross_check` skill runs second-heuristic re-grouping                                                                                                                               |

---

### Sahadeva — the auditor 🔮 (Tier-Audit, outside the chain)

|                     |                                                                                                                                                                                                                      |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/_meta/audit/`                                                                                                                                                                                        |
| **Mahabharata fit** | The astrologer Pandava. Cursed: if he reveals knowledge unprompted, his head bursts. So he speaks only when asked.                                                                                                   |
| **Job**             | Once weekly, with stateless context, reads everything (Sanjaya's journals, Vyasa's journals, proposals across both chains, Bhishma hash, heartbeats). Reports anomalies, drift, miscalibration directly to Kartavya. |
| **Watches**         | The whole chain — but reports sideways to Kartavya, not upward                                                                                                                                                       |
| **Cadence**         | Sundays 10:00 IST (= 04:30 UTC)                                                                                                                                                                                      |
| **Key constraint**  | Read-only. Cannot apply anything (R15). Not audited by anyone (R17 — no recursive audit).                                                                                                                            |
| **Failure mode**    | Sees disaster coming but can only inform                                                                                                                                                                             |
| **Counter**         | Critical findings go to `_meta/audit/inbox.md` (not just weekly report) so they don't sit dormant                                                                                                                    |

---

### Vidura — the researcher 🔬 (Tier 0)

|                     |                                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/research-agent/` (also aliased as `vidura.md`)                                                                                                            |
| **Mahabharata fit** | The truth-teller. Considered the wisest character in the epic. Refused to lie even when it would have served the king he advised. The Vidura Niti is studied to this day. |
| **Job**             | Web research with tier-tagged sources (T1–T5). Mandatory counter-evidence and gaps sections. Refuses to fabricate citations.                                              |
| **Tools**           | WebSearch, WebFetch, Read, Write, Bash                                                                                                                                    |
| **Output**          | Markdown research note at `research/vidura/<YYYYMMDD>-<slug>.md`                                                                                                          |
| **Failure mode**    | Too austere to be heard — always right but ignored                                                                                                                        |
| **Counter**         | Don't water down the discipline                                                                                                                                           |

---

### Hanuman — the scout 🐒 (Tier 0)

|                              |                                                                                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**                     | `.claude/agents/hanuman/`                                                                                                                                 |
| **Mahabharata/Ramayana fit** | The supreme reconnaissance specialist. Leaped to Lanka, surveyed enemy defenses, found Sita, returned with a complete report.                             |
| **Job**                      | Given a TikTok creator handle, gathers structured profile data from Kalodata, TikTok, Cruva. Returns tier-tagged report with fit assessment for MagAshwa. |
| **Tools**                    | Read, Write, WebSearch, WebFetch, Bash + MCP servers                                                                                                      |
| **Output**                   | `research/creators/<handle>-<YYYYMMDD>.md`                                                                                                                |
| **Key constraint**           | Read-only on every external system. Never POST/DELETE/UPDATE.                                                                                             |
| **Failure mode**             | Excess scope — Hanuman burned Lanka after his recon was done                                                                                              |
| **Counter**                  | Explicit boundary: report-only                                                                                                                            |

---

### Narada — the drafter 🪶 (Tier 0)

|                     |                                                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/narada/`                                                                                                                                   |
| **Mahabharata fit** | The celestial messenger. Travels with a veena, carrying news between worlds. Every word intentional, weighted for the listener.                            |
| **Job**             | Polishes raw notes into voice-matched messages. Two modes: `mayank-update` (≤200 words, daily AI update to CEO) and `creator-dm` (≤80 words, outreach DM). |
| **Tools**           | Read, Write, Bash                                                                                                                                          |
| **Output**          | `research/drafts/<YYYYMMDD>-<mode>-<slug>.md`                                                                                                              |
| **Key constraint**  | Never decides what to communicate — only how. Bhishma R18 forbids voice impersonation of any other agent.                                                  |
| **Failure mode**    | Mischief — Narada plants suggestions to provoke outcomes                                                                                                   |
| **Counter**         | Polish-only rule, never propose subjects                                                                                                                   |

---

### Arjuna — the executor 🏹 (Tier 0)

|                     |                                                                                                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/arjuna/`                                                                                                                                                                                |
| **Mahabharata fit** | The supreme archer. Drona's test: "What do you see?" — Arjuna: "the eye of the bird, nothing else." Single-minded execution under direction. The Bhagavad Gita is Krishna teaching Arjuna _how to act_. |
| **Job**             | Receives precise instructions, executes via API/MCP. Idempotency keys, circuit breakers, rate-limit awareness, rollback plans.                                                                          |
| **Tools**           | Read, Write, Bash, WebFetch + MCP servers                                                                                                                                                               |
| **Key constraint**  | Refuses ambiguous instructions. Dry-run by default for destructive actions. 3-retry cap. Never invokes another agent.                                                                                   |
| **Failure mode**    | Paralysis without direction (the Gita opens with Arjuna refusing to fight)                                                                                                                              |
| **Counter**         | Refuse-and-ask is a valid output                                                                                                                                                                        |

---

### Nakula — the automation owner 🐎 (Tier 0)

|                     |                                                                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Path**            | `.claude/agents/nakula/`                                                                                                            |
| **Mahabharata fit** | Master of horses, keeper of the Pandavas' stables. The boring critical work that keeps the war machine running. Never sought glory. |
| **Job**             | Reads `jobs.yml`, runs scheduled jobs, emits heartbeats, alerts on failures. Cron-driven.                                           |
| **Tools**           | Read, Write, Bash                                                                                                                   |
| **Output**          | `logs/heartbeat.json` (single-writer per Bhishma) + per-job logs                                                                    |
| **Key constraint**  | Lockfiles prevent concurrent runs. Heartbeats mandatory — silence is treated as failure.                                            |
| **Failure mode**    | Silent failure — the boring jobs nobody watches                                                                                     |
| **Counter**         | Mandatory heartbeats, alert on missed schedule                                                                                      |

---

## The data flow

```
Kartavya (you, the human ceiling)
    │
    │ approves all proposals
    │
    ▼
┌─────────────────────────────────────┐
│  Bhishma R1–R22 (constitution)      │  Read by everyone, written by Kartavya only
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Vyasa (T2 conductor, every 6h)     │  Watches Sanjaya
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Sanjaya (T1 observer, every 30m)   │  Watches all workers
└─────────────────────────────────────┘
    │
    ▼
┌────────┬────────┬────────┬────────┬────────┐
│Vidura  │Hanuman │Narada  │Arjuna  │Nakula  │  Tier 0 — they do the work
│research│scout   │drafter │executor│cron    │
└────────┴────────┴────────┴────────┴────────┘

Sahadeva (Tier-Audit, weekly Sunday)
   │
   │ reads everything, reports DIRECTLY to Kartavya, bypasses chain
   ▼
   _meta/audit/inbox.md (critical findings, daily glance)
   _meta/audit/reports/<YYYY-WW>.md (weekly report)
```

## Quick reference — when to use which

| Task you have                        | Agent to call                          |
| ------------------------------------ | -------------------------------------- |
| "Research X" or "Compare Y vs Z"     | Vidura (= research-agent)              |
| "Pull profile for @creator_handle"   | Hanuman                                |
| "Draft my daily Mayank update"       | Narada (mode: mayank-update)           |
| "Draft an outreach DM to @creator"   | Narada (mode: creator-dm)              |
| "Send this message via TCM"          | Arjuna                                 |
| "Run the daily Kalodata sync"        | Nakula (via cron + jobs.yml)           |
| "What did the workers do this week?" | Read Sanjaya's journals                |
| "Is the system drifting?"            | Read Vyasa's journal (after 30 days)   |
| "Anything broken?"                   | Read Sahadeva's audit (Sunday morning) |

## Quick reference — what NOT to do

- Don't rename `observer/` → `sanjaya/` or `research-agent/` → `vidura/`. They're aliased via symlinks. Renaming would break journal history.
- Don't run the bundle's `deploy.sh` blind — it would overwrite live files via rsync.
- Don't edit `bhishma.md` automatically. Only Kartavya. Each edit is a git commit with rationale.
- Don't auto-approve any agent's own proposals. R7.
- Don't fill in `nakula/jobs.yml` with placeholder data — write the real per-job scripts first.
