# agent-os — Project Definition

> GSD framework installed: 2026-06-17
> Owner: Kartavya Joshi (Krtvy on GitHub)
> Primary working directory: C:\Users\Rawdy\agents\observer-test

## Vision

A personal multi-agent operating system — Mahabharata-themed — that acts as Kartavya's AI-powered second brain. Handles research, communication drafting, data analysis, scheduled automation, and knowledge curation. Governed by Bhishma (constitutional rules), supervised by a tiered observation chain (Sanjaya → Vyasa → Sahadeva).

## Core Constraints

- All agents on claude-sonnet-4-6 (Tier 0 workers) or claude-haiku-4-5 (Nakula)
- Write-scope is strictly bounded per agent (Bhishma R11)
- No agent self-modifies (Bhishma R2)
- All skill changes must go through proposal → approval cycle (Bhishma R4)
- MCP tools: playwright, puppeteer, firecrawl, agent-browser, agent-reach (all installed)
- 5 Gemini keys active (GEMINI_KEY_1,2,3,5,6 — key 4 invalid)
- Notion integration: token active, parent page ID: 37f7946f-e2ce-81f8-be92-f5df470d4bc3

## Agent Roster (10 agents)

| Agent | Tier | Purpose | Status |
|---|---|---|---|
| Hanuman | 0 | General web research + recon | ✅ Active, repurposed 2026-06-17 |
| Narada | 0 | General communication drafter | ✅ Active, repurposed 2026-06-17 |
| Yudhishthira | 0 | Personal data analyst | ✅ Active, repurposed 2026-06-17 |
| Arjuna | 0 | General API executor | ✅ Active, repurposed 2026-06-17 |
| Nakula | 0 | Cron scheduler / pipeline owner | ✅ Active, K8 fix needed |
| Vidura/research-agent | 0 | Source-disciplined researcher | ✅ Active |
| Sanjaya | 1 | Agent observer | ✅ Running under Nakula |
| Vyasa | 2 | Meta-conductor | ⚠️ Deferred (documented) |
| Sahadeva | Audit | Weekly auditor | ✅ W21 GREEN |
| Bhishma | Constitution | 23 hard rules | ✅ Unchanged |

## GitHub Repos (all cloned to C:\Users\Rawdy\agents\)

All 19 repos cloned. Renames done:
- job-scout → job-market-intelligence-agent
- vidura → resume-tailor-agent
- observer-test → agent-os

## Key File Paths

- Constitution: .claude/agents/_meta/conductor/bhishma.md
- Agent files: .claude/agents/<name>/agent.md
- Proposals: .claude/agents/_meta/observer/proposals/
- Approved: .claude/agents/_meta/observer/approved/
- AI knowledge pipeline: C:\Users\Rawdy\agents\ai-knowledge-feed\
- All repo clones: C:\Users\Rawdy\agents\
