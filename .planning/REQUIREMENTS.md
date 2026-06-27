# Requirements

> Format: R-XX | Description | Status | Phase

## Phase 1 — Ecosystem Foundation (IN PROGRESS)

| ID | Requirement | Status |
|---|---|---|
| R-01 | All 19 repos cloned to C:\Users\Rawdy\agents\ | ✅ DONE |
| R-02 | Repos renamed: job-scout→job-market-intelligence-agent, vidura→resume-tailor-agent, observer-test→agent-os | ✅ DONE |
| R-03 | All Rootlabs-specific agents repurposed (Hanuman, Narada, Yudhishthira, Arjuna, Nakula) | ✅ DONE |
| R-04 | 5 pending proposals approved (arjuna, nakula, narada, hanuman, research-agent) | ✅ DONE |
| R-05 | MCP servers installed globally (playwright, puppeteer, firecrawl, perplexity) | ✅ DONE |
| R-06 | agent-browser installed (v0.28.0, Chrome 149 downloaded) | ✅ DONE |
| R-07 | agent-reach installed (v1.5.0, 5/13 channels active) | ✅ DONE |
| R-08 | GSD framework installed in agent-os | ✅ DONE |
| R-09 | Perplexity API key — replace placeholder in ~/.claude/settings.json | ❌ PENDING |
| R-10 | agent-reach Twitter cookies configured | ❌ PENDING |
| R-11 | agent-reach Reddit cookies configured | ❌ PENDING |
| R-12 | agent-reach Exa API key for web search | ❌ PENDING |
| R-13 | Nakula K8 weekly summary — add Sunday 23:55 UTC job to jobs.yml | ❌ PENDING |
| R-14 | agent-browser + agent-reach added to global ~/.claude/settings.json (currently only in observer-test/.mcp.json) | ❌ PENDING |
| R-15 | Voice pipeline: 25 more voice samples needed (currently 25/50) to activate Narada pipeline | ❌ PENDING |
| R-16 | Research-agent: replace 15 Rootlabs competitor profiles with personal use docs | ❌ PENDING |

## Phase 2 — AI Knowledge Pipeline

| ID | Requirement | Status |
|---|---|---|
| R-20 | Notion "AI Knowledge Feed" database created (currently missing — push failed) | ❌ PENDING |
| R-21 | 102 GitHub knowledge cards pushed to Notion | ❌ PENDING |
| R-22 | First weekly digest generated and pushed to Notion | ❌ PENDING |
| R-23 | YouTube source (youtube_source.py) tested and working | ❌ PENDING |
| R-24 | ArXiv papers source (papers_source.py) tested | ❌ PENDING |
| R-25 | RSS feeds source (feeds_source.py) tested | ❌ PENDING |
| R-26 | Twitter source via agent-reach wired into run_all.py | ❌ PENDING |
| R-27 | Reddit source via agent-reach wired into run_all.py | ❌ PENDING |
| R-28 | Nakula jobs.yml: add weekly ai-knowledge-feed cron job | ❌ PENDING |

## Phase 3 — Agent Integrations

| ID | Requirement | Status |
|---|---|---|
| R-30 | A2A agent communication pattern wired (agents trigger each other on events) | ❌ FUTURE |
| R-31 | LangGraph supervisor layer for orchestrating agents | ❌ FUTURE |
| R-32 | Langfuse observability (self-hosted, Docker) | ❌ FUTURE |
| R-33 | Redis shared state blackboard across agents | ❌ FUTURE |
| R-34 | Prefect scheduled runs for pipeline jobs | ❌ FUTURE |
