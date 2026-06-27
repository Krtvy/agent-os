# agent-os — Claude Code Entry Point

**FIRST ACTION IN EVERY SESSION: Read `.planning/STATE.md`**

```
cat .planning/STATE.md
```

---

## Quick orientation

- This repo is `agent-os` — Kartavya's personal multi-agent operating system
- **26 agents** (Mahabharata-themed), governed by Bhishma constitution (23 rules)
- Canonical location: `~/KRTVYDEV/agents/observer-test/`
- GSD framework installed — use `/gsd-progress --next` to get the next task
- All agents: `.claude/agents/<name>/agent.md` | Full roster: `ROSTER.md`
- Constitution: `.claude/agents/_meta/conductor/bhishma.md`

## If something seems broken

1. Check `.planning/STATE.md` → "What FAILED" section
2. Run `/gsd-resume-work` to restore full phase context
3. Check `.claude/agents/_meta/audit/reports/` for latest Sahadeva audit

## Key commands

| What | Command |
|---|---|
| Next step? | `/gsd-progress --next` |
| Resume session | `/gsd-resume-work` |
| Run audit now | `/audit-now` |
| Checkpoint state | `/checkpoint` |
| Run full team on a task | `/team-run` |

## Agent Team (how they coordinate)

Agents communicate through `~/.agent-os/sessions/<id>/`:
- Yudhishthira ⚖️ → strategy
- Vidura 📚 → research
- Hanuman 🐒 → recon
- Arjuna 🏹 → execute
- Narada 🪶 → draft output
- Nakula 🐎 → schedule followups
- Sanjaya 👁️ → journal session

Run the full pipeline: `python lib/team_coordinator.py "your task here"`

Run with specialists: `python lib/team_coordinator.py "task" --specialists auto`

## GSD Phase

Current phase: **Phase 1 — Ecosystem Foundation** (90%)
See `.planning/ROADMAP.md` for full phase breakdown.
