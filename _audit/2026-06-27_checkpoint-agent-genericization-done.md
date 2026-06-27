# Checkpoint — 2026-06-27 — agent-genericization-done

> Save-point written at user request. Captures what's in flight at this moment so the next session resumes cleanly.

## What's in flight

The Tier-0 agent genericization is **complete** on the canonical repo at `~/agents/observer-test/`. All five Tier-0 worker agents (research-agent/vidura, hanuman, narada, arjuna, nakula) have been scrubbed of Rootlabs/MagAshwa/Mayank/Kalodata/Cruva-specific references and reframed for general-purpose use. The constitution (bhishma.md) has also been updated to remove the "at Rootlabs" tagline.

This session also identified and corrected a context-drift issue: earlier work in this conversation was accidentally applied to `~/projects/observer-test/` (the LEGACY copy) instead of the canonical `~/agents/observer-test/`. After reading `CLAUDE.md` and `STATE.md`, all edits were re-applied to the correct canonical location.

Nothing is pending from this task. The next things on the STATE.md agenda are operational (run weekly digest, get API keys, add voice samples) — see "Suggested first action" below.

## What was just decided (last 24 hours)

- `2026-06-19_checkpoint-m1p1-learning-started.md` — agent-os repurposed from Rootlabs, 6-month learning plan started, Upwork setup
- `2026-06-25_checkpoint-cottageai-deployed.md` — CottageAI editorial redesign complete, deployed to Vercel

## Files currently modified (uncommitted)

```
 M .claude/agents/_meta/conductor/bhishma.md
 M .claude/agents/arjuna/skill.md
 M .claude/agents/arjuna/agent.md
 M .claude/agents/hanuman/agent.md
 M .claude/agents/hanuman/README.md
 M .claude/agents/hanuman/skill.md
 M .claude/agents/nakula/README.md
 M .claude/agents/narada/agent.md
 M .claude/agents/narada/README.md
 M .claude/agents/narada/skill.md
 M .claude/agents/research-agent/agent.md
 M .claude/agents/research-agent/skill.md
 M .claude/agents/research-agent/README.md
 M .claude/agents/research-agent/.claude/templates/competitor_profile_template.md
 M .claude/agents/research-agent/.claude/templates/monthly_snapshot_template.md
 M .claude/agents/ashwatthama/skill.md (+ dhaumya, drona, ghatotkacha, karna, krishna, kritavarma, pandu, shakuni, vyasa)
 D .claude/agents/research-agent/.claude/rules/dtc-supplements.md
 D .claude/agents/hanuman/platforms/cruva.md
 D .claude/agents/hanuman/platforms/kalodata.md
 D .claude/agents/arjuna/scripts/video-analyze-batch.sh
```

## What changed per agent (summary)

| Agent | Key change |
|-------|-----------|
| **research-agent** | `skill.md` P8 "Competitive monitoring (Rootlab)" → generic template; templates genericized ("What Rootlab should steal" → "What to steal"); `agent.md` Appendix A cleaned |
| **hanuman** | Inputs section: kalodata/cruva/MagAshwa → generic pluggable sources. Risk flag "embarrass Rootlabs" → generic |
| **narada** | Mode 1 renamed `mayank-update` → `stakeholder-update`. Audience model example genericized. README updated |
| **arjuna** | P10 example JSON `bloom-nutrition` → `<entity-slug>` |
| **nakula** | README downstream kalodata/cruva → per-job scripts |
| **bhishma.md** | "at Rootlabs" removed from constitution tagline |
| **10 new agency-agents** | "Rootlabs Context" placeholder → "Project-Specific Context" in all skill.md templates |

## Open questions or pending decisions

- **Draupadi, Abhimanyu, Bhima** (adopted 2026-06-27) still have explicit Rootlabs context (Kalodata/Cruva data sources, Rootlabs portal). These agents depend on infrastructure Kartavya no longer has access to. Decide: repurpose them to new data sources, or leave them dormant until relevant.
- **`~/projects/observer-test/`** (legacy copy) has partial genericization edits from earlier in the session — it's now stale vs the canonical. Should be deleted or left to decay; do not work there.
- **Narada voice samples** — 25 more needed to hit the ≥50 threshold for voice-pipeline activation. The current corpus of ~14 real Mayank-update samples is good training data — keep them.

## Suggested first action next session

Check STATE.md § "IMMEDIATE" actions: run `python ~/agents/ai-knowledge-feed/digest.py` (weekly digest, Gemini keys may have recovered), then replace the Perplexity placeholder key in `~/.claude/settings.json`.

## Provenance

Checkpoint written 2026-06-27 via `/checkpoint`. User-directed save-point after completing Tier-0 agent genericization on canonical `~/agents/observer-test/`.
