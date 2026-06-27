# agent-os — Claude Code Entry Point

**FIRST ACTION IN EVERY SESSION: Read `.planning/STATE.md`**

This file tells you exactly where we are, what's broken, and what to do next.
Do not ask "where were we?" — STATE.md has the answer in 2 minutes.

```
cat .planning/STATE.md
```

---

## Quick orientation

- This repo is `agent-os` — Kartavya's personal multi-agent operating system
- 10 agents (Mahabharata-themed), governed by Bhishma constitution (23 rules)
- GSD framework installed — use `/gsd-progress --next` to get the next task
- All agents' purposes are in `.claude/agents/<name>/agent.md`
- Constitution: `.claude/agents/_meta/conductor/bhishma.md`

## If something seems broken

1. Check `.planning/STATE.md` → "What FAILED" section
2. Run `/gsd-resume-work` to restore full phase context
3. Check `.claude/agents/_meta/audit/reports/` for latest Sahadeva audit

## Key commands

| What | Command |
|---|---|
| Where am I? | `/status` |
| Next step? | `/gsd-progress --next` |
| Resume session | `/gsd-resume-work` |
| Run audit now | `/audit-now` |
| Checkpoint state | `/checkpoint` |
| **Run full team on a task** | `/team-run` |
| **gstack planning** | `/office-hours` `/plan-ceo-review` `/review` `/ship` |

## Agent Team (how they coordinate)

When running as a team, agents communicate through `~/.agent-os/sessions/<id>/`:
- Yudhishthira ⚖️ → strategy (01-strategy.md)
- Vidura 📚 → research (02-research.md)
- Hanuman 🐒 → recon (03-recon.md)
- Arjuna 🏹 → execute (04-execution.md)
- Narada 🪶 → draft output (05-draft.md)
- Nakula 🐎 → schedule followups (06-schedule.md)
- Sanjaya 👁️ → journal session (07-journal.md)

Run the full pipeline: `python lib/team_coordinator.py "your task here"`

## GSD Phase

Current phase: **Phase 1 — Ecosystem Foundation** (90%)
See `.planning/ROADMAP.md` for full phase breakdown.
