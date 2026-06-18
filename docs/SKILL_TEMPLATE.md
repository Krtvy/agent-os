# `skill.md` Canonical Template

Every agent has a `skill.md` next to its `agent.md`. This file is the operational manual — what the agent knows about *how* to do its job, distinct from `agent.md` which establishes *who* the agent is.

When Sanjaya proposes Tier-0 improvements, it edits `skill.md` (never `agent.md`). When Vyasa proposes Sanjaya improvements, it edits Sanjaya's `skill.md`.

## Required structure

Every `skill.md` has these sections, in this order. Sections may be empty (with a placeholder `_(none yet)_`) but must be present.

```markdown
# <agent name> — Skill Manual

> Last updated: <YYYY-MM-DD> by <approval id or "bootstrap">

## Purpose

One paragraph: what this agent does for Kartavya, and what it explicitly does not do.

## Inputs

The shape of input the agent expects. Required vs optional fields. Example.

## Outputs

The shape of output the agent produces. File paths, frontmatter format, body sections.

## Procedures

Numbered list of the agent's standard procedures. Each procedure has:
- A name
- Preconditions (what must be true before running)
- Steps (numbered, deterministic)
- Postconditions (what must be true after a successful run)
- Failure modes (what to do if a step fails)

## Heuristics

The agent's learned shortcuts. Things like "if X then prefer Y." Each heuristic has:
- A trigger (when this applies)
- An action (what to prefer/avoid)
- Evidence (run_ids that established the heuristic)

This is the section Sanjaya most often modifies.

## Confidence (read-only reference)

A reference to `bhishma.md`'s confidence-scoring weights. The agent never duplicates them — duplication would mean the agent could "interpret" the weights differently from canonical. Just a one-line pointer:

> Confidence weights are defined in `_meta/conductor/bhishma.md` under "Confidence-scoring weights." This agent reads but never duplicates them.

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`. This agent emits run_ids in the standardized format on every action.

## Change log

Append-only list of changes to this file. Each entry:

- `YYYY-MM-DD — <approval id> — <one-line summary>`

The bootstrap entry is the first line:

- `2026-05-10 — bootstrap — initial skill manual.`
```

## What goes in `skill.md` vs `agent.md`

| skill.md | agent.md |
|---|---|
| Procedures, heuristics, output formats | Identity, character, posture |
| Modified by approved proposals | Modified rarely, by direct human edit (R2 prevents self-modification) |
| Each agent owns its own | Each agent owns its own |
| Read by the agent every run | Read by the agent every run |
| Versioned via `change log` section | Versioned via git only |

If you find yourself writing identity/character content in `skill.md`, it belongs in `agent.md`. If you find yourself writing procedural content in `agent.md`, it belongs in `skill.md`.
