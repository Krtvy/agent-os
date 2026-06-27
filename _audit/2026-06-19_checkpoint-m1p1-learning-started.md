# Checkpoint — 2026-06-19 19:30 IST — m1p1-learning-started

> Save-point written at user request. Captures what's in flight at this moment so the next session resumes cleanly.

## What's in flight

**Learning plan started — Month 1, Phase 1: Chunking & Embeddings.**
Kartavya has been given 3 resources to read before the build session begins:
1. https://www.pinecone.io/learn/chunking-strategies/ (chunking strategies)
2. https://simonwillison.net/2023/Oct/23/embeddings/ (embeddings intuition)
3. https://www.youtube.com/watch?v=ySus5ZS0b94 (Greg Kamradt chunking comparison, first 20 min)

He has NOT yet read them. The learning flow is: read → come back → I explain → we build → 5 questions → generate_doc.py → HTML doc saved to learning/docs/.

The full 6-month plan lives at: `learning/ROADMAP.md`
The doc generator tool lives at: `learning/generate_doc.py`
Phase docs will save to: `learning/docs/`

## What was just decided (last 24 hours)

- All Rootlabs-specific content removed from agent-os (competitor profiles, TikTok scripts, Kalodata/Cruva platform files, Yudhishthira GMV deliverables)
- 5 pending observer proposals approved and moved to `_meta/observer/approved/`
- Agents repurposed: Hanuman (web research), Narada (communication drafter), Yudhishthira (personal data analyst), Arjuna (general API executor), Nakula (general cron scheduler)
- GitHub repos renamed: job-scout→job-market-intelligence-agent, vidura→resume-tailor-agent, observer-test→agent-os
- GSD framework installed globally via npx @opengsd/gsd-core@latest
- Phase 1 upgrades built: sanitizer.py (injection defense), event_bus.py (agent comms), tracer.py (free local observability), budget.py (hard limits)
- Nakula traced runner fixed for Windows Git Bash (_lib.sh Python path fix)
- Upwork profile set up: bio, skills (13), title, rate ($25/hr)
- LaTeX resume generated: C:\Users\Rawdy\kartavya_joshi_resume.tex
- Mindrift applied to: Machine Learning Engineer ($90/hr), Senior Software Engineer - Agent Evaluation ($60/hr), Senior Data Scraping Engineer ($45/hr)
- AI Knowledge Feed: 59 cards in Notion database (https://notion.so/b066128f71c94059ada935240b88a7f8)
- Weekly digest: Gemini keys exhausted — run `python digest.py` tomorrow morning

## Files currently modified (uncommitted)

All agent .md files (agent.md, skill.md, CHANGELOG.md) for: hanuman, arjuna, nakula, narada, yudhishthira, research-agent.
All Rootlabs docs deleted. All new files untracked.

New untracked files of note:
- `.planning/` — GSD planning dir (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md)
- `CLAUDE.md` — session entry point (reads STATE.md first)
- `learning/` — 6-month AI engineer learning plan + doc generator
- `lib/` — tracer.py, budget.py, event_bus.py, observability.py
- `tests/` — test_agents_regression.py (DeepEval baseline, 10 golden cases)
- `.claude/hooks/` — post_tool_sanitize.py
- `.mcp.json` — agent-browser + agent-reach wired at project level

## Open questions or pending decisions

- Weekly digest not yet generated (Gemini rate limit hit — run tomorrow)
- Perplexity API key still placeholder in ~/.claude/settings.json
- agent-reach Twitter/Reddit channels need cookie export (Cookie-Editor extension)
- Exa API key needed for full web search via mcporter
- Nakula K8 weekly summary cron job not wired (needs separate Sunday 23:55 UTC entry in jobs.yml)
- Voice pipeline at 25/50 samples — needs 25 more to activate Narada pipeline
- Langfuse keys added to .env — not yet tested end-to-end
- All these uncommitted changes should be committed once confirmed stable

## Suggested first action next session

Read `learning/ROADMAP.md` § Month 1 Phase 1, then message: "I finished reading the 3 resources — here's what confused me and what clicked." That triggers the explanation + build session.

## Provenance

Checkpoint written 2026-06-19 19:30 IST via `/checkpoint`. User-directed save-point. Slug: m1p1-learning-started.
