# STATE.md — Session Memory

> **THIS FILE IS THE FIRST THING TO READ IN EVERY NEW SESSION.**
> It tells you exactly where we are, what was last done, and what to do next.
> Updated: 2026-06-17

---

## Current Phase
**Phase 1 — Ecosystem Foundation** (90% complete)

## Last Session Summary (2026-06-17)

### What was completed this session:
1. Scanned all 19 GitHub repos (from previous session) — full ecosystem analysis done
2. Renamed repos: job-scout→job-market-intelligence-agent, vidura→resume-tailor-agent, observer-test→agent-os
3. Cloned all 19 repos to C:\Users\Rawdy\agents\
4. Built full AI knowledge pipeline: discover.py, youtube_source.py, papers_source.py, feeds_source.py, digest.py, run_all.py, notion_push.py
5. Ran GitHub discovery pipeline — 102 knowledge cards summarized with Gemini 2.5 Flash
6. 5 Gemini keys active (KEY_1,2,3,5,6 — KEY_4 invalid, skip it)
7. Notion token configured (stored in ~/agents/ai-knowledge-feed/.env — do not commit)
8. Repurposed Hanuman, Narada, Yudhishthira, Arjuna, Nakula from Rootlabs→personal use
9. Approved 5 pending observer proposals
10. Installed agent-browser (v0.28.0), agent-reach (v1.5.0), mcporter, GSD framework
11. MCP servers in global settings: playwright, puppeteer, firecrawl, perplexity(KEY MISSING), glyph
12. Added agent-browser + agent-reach to observer-test/.mcp.json
13. GSD ecosystem rating: 7.2/10

### What FAILED / is still broken:
- **Notion push FAILED** — database doesn't exist yet, notion_push.py tries to push to a DB that needs to be created first
  - Fix: run `python notion_push.py` which will create the DB first then push 102 cards
  - File: C:\Users\Rawdy\agents\ai-knowledge-feed\notion_push.py
- **Perplexity key missing** — settings.json has placeholder `pplx-REPLACE_WITH_YOUR_KEY`
- **agent-reach Twitter/Reddit/LinkedIn** — needs cookie export from Cookie-Editor Chrome extension
- **Exa API key** — needed for full web search via mcporter
- **Weekly digest** — not generated yet (needs Notion cards first)

---

## Ecosystem Cleanup Done (2026-06-18)

REMOVED (Rootlabs-specific, no value):
- research-agent/docs/competitor_profiles/ (15 supplement brand profiles)
- research-agent/docs/ (rootlabs growth playbook, campaign calendar, brand studies)
- research-agent/.claude/rules/dtc-supplements.md
- research-agent/HANDOFF.md
- hanuman/platforms/cruva.md + kalodata.md
- arjuna/scripts/video-analyze-batch.sh
- yudhishthira deliverables (archived to yudhishthira/archive/rootlabs-2026-05/)

REPURPOSED:
- research-agent: DTC brand analysis → AI tool/career research
- research-agent/skills/brand-audit → AI Tool Audit
- research-agent/skills/growth-playbook → Career Playbook
- yudhishthira/memories.md → cleaned, fresh start
- yudhishthira/playbook.md → personal data analyst patterns

ADDED (Phase 1 upgrades):
- .claude/agents/hanuman/sanitizer.py (injection defense)
- .claude/hooks/post_tool_sanitize.py (wired globally)
- lib/event_bus.py (agent-to-agent communication)
- lib/observability.py (Langfuse setup)
- tests/test_agents_regression.py (DeepEval baseline)
- .planning/ (GSD framework, STATE.md, REQUIREMENTS.md, ROADMAP.md)
- CLAUDE.md (session entry point)

NOTION:
- AI Knowledge Feed database: https://notion.so/b066128f71c94059ada935240b88a7f8
- 59 cards pushed successfully

## Next Actions (in order)

### IMMEDIATE:
1. Run weekly digest (Gemini keys exhausted today — run tomorrow):
   `cd C:\Users\Rawdy\agents\ai-knowledge-feed && python digest.py`
2. Replace Perplexity placeholder key in C:\Users\Rawdy\.claude\settings.json

### SHORT TERM (this week):
4. Get Exa API key from exa.ai → run `mcporter config add exa https://mcp.exa.ai/mcp --header "x-api-key: YOUR_KEY"`
5. Export Twitter/Reddit cookies with Cookie-Editor → configure agent-reach
6. Add agent-browser + agent-reach to global ~/.claude/settings.json (R-14)
7. Fix Nakula K8: add Sunday 23:55 UTC job to jobs.yml

### MEDIUM TERM:
8. Add voice samples (25 more needed for Narada voice pipeline to activate)
9. Update research-agent docs (replace Rootlabs competitor profiles)
10. Wire Twitter + Reddit sources into ai-knowledge-feed pipeline
11. Add weekly ai-knowledge-feed cron job to Nakula jobs.yml

---

## Key File Locations (quick reference)

```
C:\Users\Rawdy\agents\observer-test\          ← agent-os main repo (=agent-os on GitHub)
C:\Users\Rawdy\agents\ai-knowledge-feed\      ← AI knowledge pipeline
  .env                                         ← 5 Gemini keys + Notion token
  discover.py                                  ← GitHub source
  youtube_source.py                            ← YouTube transcripts
  papers_source.py                             ← ArXiv papers
  feeds_source.py                              ← RSS blogs
  notion_push.py                               ← Push to Notion
  digest.py                                    ← Weekly digest generator
  run_all.py                                   ← Master pipeline runner
  pending_cards.json                           ← 102 cards ready to push
  seen_repos.json                              ← Dedup tracker

C:\Users\Rawdy\.claude\settings.json          ← Global Claude Code settings + MCP servers
C:\Users\Rawdy\agents\observer-test\.mcp.json ← Project MCP (agent-browser, agent-reach)
```

## Notion Structure

```
Parent page: "Interview Study Guide — GitHub Project Portfolio"
  ID: 37f7946f-e2ce-81f8-be92-f5df470d4bc3
  URL: https://app.notion.com/p/37f7946fe2ce81f8be92f5df470d4bc3

Projects database (interview study guide):
  DB ID: d4165a4e-490a-485c-877a-994fef416aac
  19 project pages already created (all GitHub repos)

AI Knowledge Feed database:
  STATUS: NOT YET CREATED — will be created on first notion_push.py run
```

## Active API Keys / Credentials

```
Gemini: 5 keys in C:\Users\Rawdy\agents\ai-knowledge-feed\.env (KEY_1,2,3,5,6)
Notion: ntn_325551... (in .env above)
GitHub: gh CLI authenticated as Krtvy
Firecrawl: fc-00e6c3e000544820ab020a6b49b140d2 (in ~/.claude/settings.json)
Perplexity: MISSING — needs real key
Exa: MISSING — get from exa.ai
```

## Phase 1 Quick Wins Implemented (2026-06-17)

| Item | Status | File |
|---|---|---|
| Prompt injection sanitizer (Hanuman) | ✅ Done | .claude/agents/hanuman/sanitizer.py |
| Post-tool-use injection scan hook | ✅ Done | .claude/hooks/post_tool_sanitize.py |
| Agent-to-agent event bus | ✅ Done | lib/event_bus.py |
| Langfuse observability setup | ✅ Done (needs key) | lib/observability.py |
| agent-browser added to global MCPs | ✅ Done | ~/.claude/settings.json |
| agent-reach added to global MCPs | ✅ Done | ~/.claude/settings.json |
| OpenMemory (local Mem0) added to global MCPs | ✅ Done | ~/.claude/settings.json |
| Langfuse + DeepEval installed | ✅ Done | pip |

Still needs API keys to activate:
- Langfuse: get free keys at cloud.langfuse.com → set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY
- Mem0 cloud (optional): mem0.ai → MEM0_API_KEY (or use OpenMemory local — no key needed)

## Phase 1 Quick Wins Implemented (2026-06-17)


```
Installed: 2026-06-17 via npx @opengsd/gsd-core@latest
Location: C:\Users\Rawdy\agents\observer-test\.claude\skills\
Commands available: /gsd-new-project, /gsd-discuss-phase, /gsd-plan-phase,
                    /gsd-execute-phase, /gsd-verify-work, /gsd-ship,
                    /gsd-quick, /gsd-resume-work, /gsd-progress
```

## Ecosystem Health

```
Last Sahadeva audit: W21 (2026-05-24) — GREEN
Next audit due: W22 (2026-05-31) — overdue, run /audit-now
Proposals approved: 5 (2026-06-17)
Proposals pending: 0
Bhishma hash: 0323c47eb7d2c72d9df42fab01e402da045547b1f0d1cdc014795967d3929133
```

---

## How to Resume Any Session

1. Read this file (STATE.md) — 2 minutes
2. Check REQUIREMENTS.md for what's pending
3. Start with "IMMEDIATE" actions above
4. Run `/gsd-progress --next` for GSD-guided next step
