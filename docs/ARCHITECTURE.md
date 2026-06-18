# Architecture — Multi-tier Agent Ecosystem

## Tiers

```
              ┌───────────────────────────────┐
              │  Kartavya (human, principal)  │
              └─────────────┬─────────────────┘
                            │
                            │ approves all proposals,
                            │ edits bhishma.md,
                            │ reads sahadeva reports
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
  ┌─────────┐         ┌──────────┐          ┌─────────┐
  │ Tier 2  │         │ Tier-Audit│          │  Tier 1 │
  │  Vyasa  │         │ Sahadeva │          │ Sanjaya │
  └────┬────┘         └──────────┘          └────┬────┘
       │ proposes changes to                     │ proposes changes to
       │ Sanjaya's skill.md                      │ Tier-0 workers' skill.md
       │ (read-only on Sanjaya artifacts)        │
       ▼                                         ▼
  ┌──────────┐                          ┌─────────────────────┐
  │  Sanjaya │ ◄──── observed by ──────►│      Tier 0         │
  │  (Tier 1)│                          │ ┌─────┐ ┌────────┐  │
  └──────────┘                          │ │vidura│ │hanuman │  │
                                        │ └─────┘ └────────┘  │
                                        │ ┌─────┐ ┌────────┐  │
                                        │ │narada│ │ arjuna │  │
                                        │ └─────┘ └────────┘  │
                                        │       ┌────────┐    │
                                        │       │ nakula │    │
                                        │       └────────┘    │
                                        └─────────────────────┘
```

Sahadeva sits outside the supervisory chain. It reads everyone, modifies no one, reports directly to Kartavya.

## Directory layout

```
~/projects/observer-test/
├── .claude/
│   └── agents/
│       ├── _meta/
│       │   ├── conductor/    (Vyasa + bhishma.md)
│       │   ├── observer/     (Sanjaya)
│       │   └── audit/        (Sahadeva)
│       ├── vidura/
│       ├── hanuman/
│       ├── narada/
│       ├── arjuna/
│       ├── nakula/
│       ├── vyasa.md       → _meta/conductor/agent.md     (symlink)
│       ├── sanjaya.md     → _meta/observer/agent.md      (symlink)
│       ├── sahadeva.md    → _meta/audit/agent.md         (symlink)
│       ├── vidura.md      → vidura/agent.md              (symlink)
│       ├── hanuman.md     → hanuman/agent.md             (symlink)
│       ├── narada.md      → narada/agent.md              (symlink)
│       ├── arjuna.md      → arjuna/agent.md              (symlink)
│       └── nakula.md      → nakula/agent.md              (symlink)
├── docs/                  (this directory)
├── scripts/               (run_*.sh, crontab.example)
├── logs/
│   ├── heartbeat.json     (written by Nakula, read by Sahadeva)
│   ├── nakula/<job>/...   (Nakula per-job logs)
│   └── arjuna/<run>.log   (Arjuna per-call logs)
└── research/
    ├── creators/          (Hanuman scout reports land here)
    └── voice-samples/     (Narada calibration data)
```

## Data flow — supervisory loop

1. **Tier-0 worker runs.** Produces output (research report, draft, executed action, scheduled job result). Emits a run_id. Writes a log line.
2. **Sanjaya reads.** On its next cycle, Sanjaya scans Tier-0 logs, journals what each worker did, computes confidence on any drift it sees.
3. **Sanjaya may propose.** If a pattern accumulates (≥3 distinct run_ids, Bhishma R10), Sanjaya drafts a proposal in `_meta/observer/proposals/<id>.md` targeting one Tier-0 worker's `skill.md`.
4. **Kartavya reviews.** Moves proposal to `approved/<id>.md` (with diff applied) or `rejected/<id>.md` (with reason).
5. **Sanjaya applies.** On its next cycle, Sanjaya processes new approvals and applies the diffs to the targeted `skill.md`. Each apply event references the approved proposal id (Bhishma R4).
6. **Vyasa reads Sanjaya.** Same pattern, one tier up. Vyasa watches Sanjaya's journals, proposals, approvals, rejections. Eventually proposes meta-level changes to Sanjaya's `skill.md`.
7. **Sahadeva reads everyone.** Once a week, stateless, produces an audit report directly to Kartavya.

## Data flow — operational loop (no supervision)

Tier-0 workers do their actual jobs without any awareness of supervision. From their perspective, they read their own `agent.md` + `skill.md` + `bhishma.md`, do their work, log results, and exit. The fact that Sanjaya is reading their logs is invisible to them.

This is intentional. Workers should not perform for an observer. They perform for Kartavya. Sanjaya watches.

## Key invariants

- **Diffs trace to approvals.** Every change to a `skill.md` traces back to an approved proposal id (R4).
- **Tier hierarchy is strict.** No Tier-0 worker reads or writes `_meta/`. No Tier-1 (Sanjaya) reads or writes `_meta/conductor/`. No Tier-2 (Vyasa) reads or writes `_meta/audit/`. Sahadeva reads everyone but writes only to `_meta/audit/`.
- **Heartbeat is single-writer.** Only Nakula writes `logs/heartbeat.json`. Everyone else reads.
- **bhishma.md is single-writer.** Only Kartavya writes (R1).
- **Append-only journals.** No agent rewrites a past journal entry (R5).

## Secondary roles (intentionally not built in this batch)

- **Krishna (strategist).** The role currently played implicitly by Kartavya. If formalized later, Krishna would sit between Kartavya and Arjuna, translating goals into specific execution instructions. For now, Kartavya hands instructions directly to Arjuna.
- **Drona (trainer).** Could load voice-samples and other calibration data; for now Narada handles its own calibration.
- **Drupada (recruiter / new-agent provisioner).** Not needed until the ecosystem grows beyond manual provisioning.

These can be added as Phase-5+ extensions without modifying the existing 8 agents.
