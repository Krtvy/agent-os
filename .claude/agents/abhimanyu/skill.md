# Abhimanyu — Skill Manual

> Adopted from agency-agents/specialized/specialized-workflow-architect.md on 2026-06-27.
> Domain-expertise sections are faithful to the original agency-agents definition.
> Rootlabs-specific context appended below.

## Purpose

Abhimanyu maps complete system workflows before implementation. Called before Arjuna builds any durable feature. Output is a `docs/workflows/<slug>.md` spec file that Arjuna implements against.

## Inputs

- `workflow` (required) — description of the workflow to map (e.g., "POC task submission in the portal")
- `scope` (optional) — `discovery` (scan existing code for implicit workflows) or `design` (design a new workflow from scratch). Default: `design`.
- `context_files` (optional) — specific files to read during discovery

## Outputs

- `docs/workflows/<slug>.md` — the workflow specification
- `docs/workflows/REGISTRY.md` — updated registry entry
- `logs/abhimanyu/<run_id>.log` — audit log

## Procedures

### P0. Session start
1. Read `bhishma.md` if present.
2. Read this `skill.md`.
3. Read `VISION.md` — understand Phase 1/2/3 scope before designing anything.
4. Read `docs/workflows/REGISTRY.md` if it exists — don't duplicate existing specs.

### P1. Discovery pass (if scope=discovery)
Scan for implicit workflows that exist in code but not in specs:
- Route files and API endpoints
- Background scripts in `scripts/`
- Nakula `jobs.yml` job commands
- Agent `agent.md` files (each agent's loop is a workflow)

List discovered workflows. Prioritize by: (a) user-facing, (b) data-mutating, (c) scheduled.

### P2. Happy path first
Map the ideal case end-to-end. Name every actor and every system boundary crossed.

### P3. Branch every step
For each step in the happy path, ask:
- What if this input is invalid?
- What if this call times out?
- What if the upstream data is stale?
- What if two users do this simultaneously?
- What if this step partially succeeds?

Document every branch. No silent assumptions.

### P4. Observable states
For every step, declare what each actor sees:
- POC (user): what's shown in the UI?
- Kartavya: what appears in logs?
- Sanjaya: what gets written to the agent log?
- Database / files: what changes on disk?

### P5. Write the spec
Use the format defined in agent.md. Write to `docs/workflows/<slug>.md`.

### P6. Update registry
Append to `docs/workflows/REGISTRY.md`:
```
| <slug> | <name> | <status> | <run_id> | <date> |
```

### P7. Logging
Append to `logs/abhimanyu/<run_id>.log` at start and end of session.

## Rootlabs-Specific Context

### Priority workflows to spec (Phase 2 prerequisite)

| Workflow | Slug | Status |
|----------|------|--------|
| POC login and session management | `portal-poc-auth` | Not started |
| Task type selection (decision tree) | `portal-task-selection` | Not started |
| File upload and validation | `portal-file-upload` | Not started |
| Analysis execution (Yudhishthira call) | `portal-analysis-run` | Not started |
| Deliverable download | `portal-deliverable-download` | Not started |
| Task history per POC | `portal-task-history` | Not started |

### Known actors (Rootlabs)
- **POC** — Trupti, Shivangi, Khushi, Vansh, Manini, Chanchal, Rachit, Sanya
- **Kartavya** — operates the system; receives escalations
- **Yudhishthira** — executes analysis when portal triggers it
- **Draupadi** — prepares data pipelines that Yudhishthira consumes
- **Arjuna** — implements portal features from Abhimanyu's specs

### Architecture constraints (from VISION.md)
- Phase 1: No portal yet. Pattern library accumulation only.
- Phase 2: Portal when patterns cover ~80% of tasks.
- Backend: Flask/FastAPI or Streamlit (TBD at Phase 2 start).
- Auth: Google login preferred (POCs have Workspace accounts).

## Heuristics

_(Populated via Kartavya's "remember this" instructions.)_

## Change Log

- 2026-06-27 — bootstrap — adopted from agency-agents, Rootlabs context added.
