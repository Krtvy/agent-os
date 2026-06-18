# Bootstrap Order

Bringing the ecosystem online has dependencies. Some agents must exist (and have run at least once) before others can do meaningful work. This document specifies the order.

## Phase 0 — Foundation (Kartavya, manual)

1. Initialize git repository at `~/projects/observer-test/`.
2. Verify `~/projects/observer-test/.claude/agents/_meta/conductor/bhishma.md` exists and is committed. **Nothing runs without Bhishma.**
3. Verify `docs/RUN_ID_SPEC.md`, `docs/SKILL_TEMPLATE.md`, `docs/ARCHITECTURE.md` are in place.
4. Verify the directory tree matches the structure shipped in this bundle (use `tree -d -L 4 .claude/` to spot-check).

## Phase 1 — Tier 0 Workers (in any order)

These have no upstream dependencies. They can each be exercised independently before supervision is wired up.

- `vidura/` — research agent
- `hanuman/` — scout agent
- `narada/` — drafter agent
- `arjuna/` — executor agent
- `nakula/` — automation agent

For each: read `agent.md`, read `skill.md`, run a smoke task, verify `logs/<agent>/` got an entry, verify the entry includes a valid run_id.

**Nakula** specifically: verify `jobs.yml` exists (use `jobs.yml.example` as a starting point), and verify `logs/heartbeat.json` is being written. Several other agents (especially Sahadeva) read this file.

## Phase 2 — Tier 1 Observer

Once at least one Tier-0 agent has produced run logs and journal-readable artifacts:

- Bring up `_meta/observer/` (Sanjaya).
- Run Sanjaya once. It should journal the Tier-0 agents it found and produce no proposals on the first run (it has no observation history yet).
- Verify `_meta/observer/journal/<worker>.md` files are being created.

Sanjaya's first proposals require accumulating evidence — typically 1–2 weeks of Tier-0 activity before the first meaningful proposal lands.

## Phase 3 — Tier 2 Conductor

Once Sanjaya has produced at least 7 days of journals and at least one proposal:

- Bring up `_meta/conductor/` (Vyasa).
- Run Vyasa once. It should journal Sanjaya's recent activity and produce no proposals on the first run (its threshold is 30 days OR 60 proposals — both far in the future at this point).

Vyasa is intentionally slow. Don't expect proposals from Vyasa for a month after Sanjaya is online.

## Phase 4 — Tier-Audit External

Sahadeva can run from day one of any phase, but its reports are most useful once there's at least a week of data to compare. Add to crontab early so the schedule is consistent:

```
0 10 * * 0  bash ~/projects/observer-test/scripts/run_sahadeva.sh
```

The first 1–2 weekly reports will be very short. That is correct.

## Common bootstrap failures

| Symptom | Cause | Fix |
|---|---|---|
| Agent refuses to run, "bhishma.md not found" | Phase 0 incomplete | Verify the file path and commit |
| Sanjaya creates empty journals | Tier-0 agents haven't run | Exercise Tier-0 first |
| Vyasa journals "no sanjaya activity" repeatedly | Sanjaya isn't running | Check Sanjaya cron / manual invocations |
| Sahadeva reports "no heartbeat data" | Nakula `jobs.yml` not configured | Phase 1, Nakula step |
| run_id validation fails on a proposal | run_id not in standardized format | Check `docs/RUN_ID_SPEC.md` and the agent's emit code |

## Promotion gates

Before promoting from one phase to the next:

- **Phase 0 → 1.** Bhishma is committed. Directory tree is clean.
- **Phase 1 → 2.** Each Tier-0 agent has at least one successful run with a valid run_id and a journal-readable artifact.
- **Phase 2 → 3.** Sanjaya has 7+ days of journal entries and at least one proposal that was approved or rejected (so the approval gate has been exercised end-to-end).
- **Phase 3 → 4.** Vyasa has produced at least one journal entry. (Sahadeva can come up earlier; it doesn't depend on Vyasa.)
