# Checkpoint — 2026-06-20 — 0620-snapshot

> Save-point written at user request. Captures what's in flight at this moment so the next session resumes cleanly.

## What's in flight

This was a research + memory-building session, not a code session. Three things were done:

1. **ruflo research** — User asked about `ruvnet/ruflo` (GitHub, 60.4k stars). Confirmed it supports website scanning via `ruflo-browser` plugin (Playwright-based). User is interested in building an agent that visits any URL and scans/analyzes it. No code written yet — still at research stage.

2. **public-apis reference saved** — `https://github.com/public-apis/public-apis` added to memory (`reference_public_apis.md`) and local file (`C:\Users\Rawdy\api-resources.md`). Future sessions will know to go here for any free API.

3. **App pre-build workflow saved** — Standard PRD → TRD → ERD → API Spec → Wireframes order saved to memory (`reference_app_prebuild_workflow.md`) and local file (`C:\Users\Rawdy\app-prebuild-workflow.md`). Future sessions will follow this before coding any app.

## What was just decided (last 24 hours)

- `2026-06-27_checkpoint-1556-session-end.md`: End-of-session save — Hermes Agent, agency-agents (Draupadi/Abhimanyu/Bhima), master CLAUDE.md at ~/
- `2026-06-25_checkpoint-cottageai-deployed.md`: CottageAI editorial redesign complete, deployed to Vercel
- `2026-06-19_checkpoint-m1p1-learning-started.md`: agent-os repurposed, Upwork setup, 6-month learning plan started

## Files currently modified (uncommitted)

Large number of staged/untracked changes from prior sessions — agent repurposing cleanup (research-agent, arjuna, hanuman, nakula, narada, yudhishthira), new agents added (abhimanyu, bhima, draupadi, karna, krishna, etc.), new lib files (event_bus.py, team_coordinator.py, budget.py), new dirs (.planning/, hermes-skills/, tests/, docs/).

None of these were touched in this session — they are carry-over from 2026-06-17/27 sessions.

## Files modified in the last commit

```
feat: portal v2 full build + observer ecosystem + hackathon kit (9e384f6)
```

## Open questions or pending decisions

- ruflo website scanner: should it use ruflo or a simpler Playwright + Claude setup? Not decided yet.
- `move-todays-work.ps1` — still needs to be run to move Hermes + agency-agents from `~/projects/` → `~/agents/`
- Missing API keys still pending: Perplexity, Exa, Langfuse, agent-reach cookies
- Notion AI Knowledge Feed DB not created yet

## Suggested first action next session

Run `~/move-todays-work.ps1` to fix misplaced files from 2026-06-27 session, then read `.planning/STATE.md` for remaining Phase 1 tasks.

## Provenance

Checkpoint written 2026-06-20 via `/checkpoint`. User-directed save-point.
