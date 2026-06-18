# Claude Code Agent Ecosystem — FREE Optimization Playbook (May 2026)

Audience: Kartavya / observer-test repo (8 Mahabharata-named agents, Bhishma hooks, MCP-heavy)
Cutoff verified: web-searched May 2026 ; Anthropic docs as T1
Hard cap: 3000 words.

---

## TL;DR

Three changes dominate the savings curve, and they are free:

1. **Stop breaking the prompt cache.** Cache reads are 0.1x base input; a single mutated byte in the prefix turns a $1 turn into a $10 turn [1, T1].
2. **Demote per-agent models.** Haiku 4.5 ($1/$5) handles routing/classification/journal-writing; reserve Opus 4.7 ($5/$25) for Vyasa-tier reasoning. 5x cost delta for ~1.2pt SWE-bench gap [11, T1] [4, T3].
3. **Trim deferred-loaded MCP servers, not just allowlisted tools.** Tool Search already trims context 85% but every non-deferred MCP still pays setup cost on every turn [3, T1] [13, T1].

Everything else compounds on top: hooks under 200ms, /clear discipline, worktree isolation for parallel agents, Message Batches for nightly Sahadeva audits.

---

## Top 10 Highest-Impact Free Wins (rank-ordered)

1. **Freeze the system prompt prefix.** Move timestamps, session IDs, dynamic file lists, and any per-turn variables to the END of the prompt. Static-first / dynamic-last is the difference between 90%+ cache hit rate and 0% [1, T1] [18, T3]. Audit `lib/session-start-greeting.sh` output — any clock string in the greeting kills the cache for that turn.
2. **Default the eight agents to Haiku 4.5 or Sonnet 4.6 in their `agent.md` frontmatter.** Only Vyasa (reasoning), Sahadeva (audit synthesis), and Yudhishthira (data) need Sonnet+. Hanuman/Narada/Nakula/Sanjaya/Arjuna can all run Haiku 4.5 with no quality loss for their narrow jobs. Per-subagent `model:` override exists in v2.1+ [15, T2].
3. **Cap hook latency under 200ms.** Current `bhishma-pretool-hook.sh` and `post-tool-hook.sh` fire on every tool use — they MUST stay sub-200ms or every turn drags. The published threshold is "noticeable sluggishness at 500ms+ PostToolUse" [5, T3]. Profile with `time` and short-circuit on `BHISHMA_AGENT=""`.
4. **Adopt Message Batches API for non-interactive work.** Sahadeva's weekly audit, Sanjaya's nightly trace summaries, any backfill — all eligible. 50% off, stacks with prompt caching for up to 95% total reduction [6, T1].
5. **Use `/fewer-permission-prompts` skill** (already in CC-OS). One run rewrites `.claude/settings.json` with the most-frequent read-only commands. Anthropic ships it with sudo/interpreter blocklists built in [7, T3].
6. **Apply `isolation: worktree` to write-heavy subagents.** Lets two agents touch the same file path in parallel without collision. Free; setup is one frontmatter line [10, T1]. Sweet spot is 2-4 parallel sessions; beyond that review queue chokes.
7. **Defer all but one MCP server.** Tool Search auto-defers when server tool descriptions exceed 10K tokens, but verify each MCP in `settings.json` actually benefits — Higgsfield, blueprint, Vibe Prospecting are huge and rarely needed in the same turn. Anthropic measured Opus 4.5 jumping 79.5% → 88.1% accuracy with Tool Search enabled [3, T1].
8. **Adopt adaptive thinking (`thinking: {type: "adaptive"}`) over fixed budgets.** Reported 40–60% pipeline cost reduction at no quality loss because Claude skips reasoning for 40–60% of subtasks [8, T1]. `budget_tokens` is deprecated.
9. **Install ccusage locally**, wire `claude-statusline` to surface "$ spent / tokens left" in the status line. Free, reads from `~/.claude/projects/*.jsonl`, no upload. Until you can see the bill per session you cannot trim it [9, T3] [15, T3].
10. **Use `/clear` after plan acceptance.** v2.1+ already prompts for it; accepting the prompt drops accumulated context and significantly improves plan adherence [12, T2]. Cheaper AND smarter.

---

## 1. Prompt + Context Economy

### Prompt caching mechanics (T1, May 2026 state)

- Cache reads cost **0.1x** base input ; 5-min cache writes cost **1.25x** ; 1-hour writes cost **2x** [1, T1].
- TTL dropped from 60 min to **5 min** in early 2026. Each cache hit resets the timer — so a continuously active session stays warm indefinitely [2, T3].
- A 100-turn Opus session costs $50–100 without caching, $10–19 with it [2, T3].
- **What invalidates the cache for an entire turn:** adding a new MCP tool, switching models mid-session, injecting a timestamp into the system prompt, byte-different JSON key order [2, T3] [18, T3].

### Where this project is leaking cache hits

- `lib/session-start-greeting.sh` likely prints `date` or session-specific data. Move that output AFTER any persistent system context, or emit it only on first turn.
- Each new agent invocation adds MCP tool descriptors. The 13+ MCP servers (Higgsfield, blueprint, Notion, Supabase, Slack, Klaviyo, Apollo, Clay, Gmail, Calendar, Drive, Vibe Prospecting, Chrome) collectively bloat the prefix. **Disable any MCP server not used in 80%+ of sessions in `settings.json`** — re-enable per-session as needed. Tool Search handles defer-loading at the tool level but the server connection itself still costs context [3, T1].
- The Token Saviour pre-prompt hook is a net win for user-prompt size BUT make sure the compressed-prompt block is itself stable — if it varies on whitespace/version it breaks cache.

### Skill loading economy

- Pre-loaded metadata is ~100 tokens per skill ; full skill body loads only on match (under 5K) [17, T1] [16, T1].
- Anthropic guidance: **keep SKILL.md body terse, push references/ subfiles for rarely-used detail** [16, T1]. The observer-test skills (audit-now, checkpoint, status) look right-sized. Audit any skill > 5K body.

### Read tool discipline

- Read defaults to 2000 lines / 25K tokens ; line-number prefix adds ~70% overhead [21, T3].
- Use `limit` + `offset` for >500-line files. Use `Grep` to locate, then `Read` with `offset`.
- For git history: `git log --oneline -N` instead of full log (already in CLAUDE.md).

---

## 2. Agent Design

### When to spawn a sub-agent (T1/T3 consensus)

- Subagent overhead: **~20K tokens** of context-loading per spawn [2, T3]. For trivial work this is wasteful — "10x cheaper to stay in main thread for small tasks" [2, T3].
- **Use subagents for**: parallel exploration, heavy verbose output (web research, full-file scans), tasks needing tool restriction, isolated worktree edits.
- **Don't use subagents for**: single-file edits, one-shot bash, follow-ups to a brief already in-thread.

### Briefing pattern (canonical)

> "Even a frontier coding model running on the Claude Agent SDK in a loop across multiple context windows will fall short of building a production-quality web app if it's only given a high-level prompt" [25, T1].

Right altitude: clear, direct, specific deliverables ; not hardcoded brittle logic, not abstract one-liners. The observer-test agents' `agent.md` + `skill.md` split is the correct pattern — frontmatter for routing, body for procedure.

### Worktree isolation

- Frontmatter `isolation: worktree` puts each subagent in `.claude/worktrees/<n>/` ; auto-cleaned if no changes [10, T1].
- "Two to four parallel sessions is where most people land" — past that, human review queue chokes [10, T3].

### Tier-tagging sources

The project already uses T1–T5. This is straight from Anthropic's research-agent style guide pattern — keep it. Add date stamps on every cited URL because doc URLs change.

---

## 3. Hooks

### Latency budget

- ~200ms total per hook event is the published safe zone [5, T3] [22, T1].
- v2.1.116 baseline overhead is ~200ms even with empty hooks — every additional ms compounds across every tool call.
- 95 hooks can coexist if each runs under 200ms [5, T3].

### Patterns useful for this repo

- **PreToolUse for write_scope check** — already wired via Bhishma. Verify it short-circuits fast on `BHISHMA_AGENT=""`.
- **UserPromptSubmit for prompt augmentation** — current Token Saviour pattern. Known limitation: stdout from UserPromptSubmit _appends_ via `additionalContext` ; it cannot _replace_ the user prompt today (issue #46761 open) [23, T3]. Net cost ↑ unless you keep the appended block tiny and stable.
- **SessionStart** for ambient context — good place for REMINDERS surfacing (already done). Keep output <1KB; this text rides every turn until /clear.
- **PostToolUse for trace writing** — already done. Make sure `lib/trace-writer.sh` runs async (`&` + `disown`) so the next turn doesn't block on disk write.
- **Stop hook** as a final quality gate — not wired ; consider adding for "did Vidura write to the right path?"

### Hook stats pattern

Add a one-liner to each hook:

```
printf '%s\t%s\t%d\n' "$(date -u +%s)" "$HOOK_NAME" "$ELAPSED_MS" >> .claude/_meta/hook-stats.tsv
```

Then `awk` for p95 weekly. Free. Catches a slow hook the day it regresses.

---

## 4. Slash Commands / Skills

- `/loop INTERVAL PROMPT` — recurring task in the active session, up to 72h, 10% jitter [19, T3]. Use for polling deploy status, periodic Sahadeva spot-checks. Dies on session exit.
- `/schedule` — persistent scheduled tasks via desktop app or remote routine. Survives restarts. Use for the Sunday Sahadeva audit instead of local cron — Anthropic infra handles cold-start [19, T3].
- `ScheduleWakeup` tool — dynamic-pacing inside an agent run (model self-schedules its next wake). Available via the schedule skill in the deferred list above.
- **Skill composition**: skills cannot explicitly `import` other skills, but Claude auto-loads multiple matching skills in one turn [24, T3]. So don't try to chain via code — chain via the model: write skills whose descriptions overlap with predictable upstream tasks, and the matcher will compose them.

---

## 5. Settings.json Optimization

### Per-agent model override (the single biggest win after caching)

Per-subagent `model:` frontmatter is supported [15, T2]. Suggested mapping for observer-test:

| Agent        | Today (assumed) | Suggested  | Why                                 |
| ------------ | --------------- | ---------- | ----------------------------------- |
| Vidura       | Opus / default  | Sonnet 4.6 | Routing, not reasoning              |
| Hanuman      | default         | Haiku 4.5  | File fetching / mechanical work     |
| Narada       | default         | Haiku 4.5  | Messaging / notifications           |
| Arjuna       | default         | Sonnet 4.6 | Tactical content work               |
| Nakula       | default         | Haiku 4.5  | Light analysis                      |
| Sanjaya      | default         | Haiku 4.5  | Trace summarisation, narrow         |
| Vyasa        | Opus            | Opus 4.7   | Long-form synthesis — keep          |
| Sahadeva     | default         | Sonnet 4.6 | Weekly audit — Sonnet 4.6 is enough |
| Yudhishthira | default         | Sonnet 4.6 | Data work, pandas reasoning         |

**Important Opus 4.7 footgun**: new tokenizer can produce up to 35% more tokens for the same text [4, T3]. Real bill goes up even though rate card didn't. Reserve Opus 4.7 for tasks where the reasoning gap matters.

### Permission allowlist

Run `/fewer-permission-prompts`. It scans transcripts, ranks by frequency, drops <3-occurrence commands, blocks dangerous wildcards (`Bash(python3:*)`, sudo) [7, T3]. Should reduce friction without security regression.

### env vars worth setting

- `ANTHROPIC_LOG=warn` (drops verbose stdout)
- `CLAUDE_CODE_DISABLE_TELEMETRY=1` if privacy > observability
- `BHISHMA_AGENT=""` in interactive sessions so hooks no-op fast

### statusLine

Wire `claude-statusline` (community, free) — surfaces model, dir, branch, **session $ spent**, **tokens-to-context-limit**. Make sure the status command itself runs in <50ms or it stutters every turn [15, T3].

---

## 6. MCP Servers

### Local vs remote

- Local MCP avoids network latency entirely [27, T3].
- Remote MCP introduces ~50–200ms per call but offers shared state across machines.
- **Caching**: a benchmark showed cold-start MCP tool call at ~2,485ms vs ~0.01ms on cache hit — 41x speedup [27, T3]. If your MCP server doesn't cache responses internally, wrap calls in a local TTL cache.

### When MCP is slower than just running bash

- Single-shot file reads / git ops — bash beats MCP every time.
- Counting rows — `psql -c` beats Supabase MCP roundtrip.
- **Heuristic**: if the MCP tool wraps a CLI you already have, prefer the CLI.

### For this repo specifically

- Higgsfield, blueprint, Vibe Prospecting are project-specific — defer-load them ; do not surface in agents that won't use them.
- Supabase MCP is high-value (typed queries, advisors). Keep on.
- Notion / Gmail / Drive / Calendar — only authenticate if used in this session. Authentication adds tool descriptors.

---

## 7. Multi-Agent Workflows

### Observability (already partially built)

- `_meta/observer/traces/sanjaya/*.json` follows the pattern Anthropic now formalizes as OTLP spans per agent-loop step [29, T3]. Consider exporting to Langfuse/Honeycomb for free trace visualization — both have free tiers.
- The Anthropic-recommended loop detector: **hash the last N tool calls (name + args) ; flag if any hash appears 3+ times** [29, T3]. Bhishma's constitution already mentions loop detection — wire this exact hash-and-count pattern into `bhishma-pretool-hook.sh`.

### Approval gates that scale

- Sanjaya-proposes / Kartavya-approves pattern matches Anthropic's "lead-agent synthesizes, sub-agents explore" canonical structure [25, T1].
- Keep approval payloads small (1–2K token summaries from each sub-agent, per Anthropic's published number) [25, T1].

### Avoiding cascading subagent costs

A 3-agent team can consume **7x** a single-agent session's tokens [26, T3]. **Rule of thumb**: never spawn a subagent for a task you could finish in <5 tool calls inline.

---

## 8. Anthropic API + SDK Efficiency

### Cache breakpoints

- Up to 4 `cache_control` breakpoints per request.
- Mark the LAST stable block (e.g. end of system prompt, end of tool definitions) — Anthropic auto-applies to the last cacheable prefix.

### Extended thinking — use adaptive

- `thinking: {type: "adaptive"}` + `effort` parameter is the new standard; `budget_tokens` is deprecated [8, T1].
- Adaptive lets Claude skip reasoning when not needed — 40–60% reported pipeline cost reduction [8, T1].

### Tool use parallelism

- New streaming-tool-use shipped 2026 reduces parameter buffering delay [22, T1].
- For multi-tool turns, kick off independent tools as soon as their JSON parses — don't wait for the full message.

### Message Batches

- 50% off, 24-hour SLA, stacks with caching [6, T1].
- Sahadeva weekly audits: perfect fit. Nightly trace digests: perfect fit. Anything interactive: bad fit.

### Streaming

- Sets time-to-first-token low ; perceived latency drops dramatically [22, T3]. Already on by default in Claude Code.

---

## 9. Cost & Token Monitoring (Free)

- **ccusage** (`ryoppippi/ccusage`) — local CLI, reads `~/.claude/projects/*.jsonl`, no upload, breakdowns by day/month/session/5h-block [9, T3]. Install once.
- **Claude-Code-Usage-Monitor** (`Maciek-roboblog/...`) — live "fuel gauge" with ML predictions, complements ccusage [9, T3].
- **ccflare** — web dashboard if you want graphs.
- **Token Saviour stats** — `python3 ~/.claude/hooks/token_saviour.py --stats` pattern is referenced in user instructions ; verify it logs to a file and surface in weekly status.

The 2026 v2.1.89 release notoriously chewed through rate limits 3–50x faster than expected [9, T3]. Monitoring is no longer optional.

---

## 10. Productivity Wins (Claude Code CLI)

- **Plan mode**: type `!` (or whatever the project binds). Centre of gravity in 2026 has shifted to plan-first ; teams shipping cleanest PRs treat plans as first-class artifacts [12, T3].
- **/clear discipline**: clear on context switch, accept the auto-clear on plan approval [12, T2].
- **Rewind**: ctrl-Z-equivalent for accepted plans ; cheap insurance.
- **Keybindings**: customize via `~/.claude/keybindings.json` — the `keybindings-help` skill walks through chord bindings. Bind one chord to "compact + clear" for fast context reset.
- **Status line tweaks**: token-remaining counter is the single most behaviour-shaping addition.

---

## Dissent & Counterpoints

### Does prompt caching always help?

**No.** Three failure modes:

1. **Dynamic prefix kills it** — putting any per-turn variable (timestamp, user ID, request ID) at the start of the prompt voids the cache, AND each request pays 1.25x for a useless write. Worse than no caching [18, T3].
2. **Short-lived sessions** — if you spawn fresh agents every few minutes and don't keep them warm, 5-min TTL expires before reuse. The 1-hour cache helps but doubles write cost (2x) — only worth it if you genuinely hit it [1, T1].
3. **Many small distinct prompts** — bulk evaluation, ad-hoc one-off queries. Caching infrastructure is pure overhead.

### Do subagents save tokens?

**Frequently no.** The 20K-token spawn overhead means a single subagent for a one-shot task is a loss [2, T3]. They only save tokens when the verbose intermediate output would have polluted the main context for many subsequent turns.

### Is Opus 4.7 worth the price?

**Often no.** Sonnet 4.6 is 1.2 points behind on SWE-bench Verified and 40% cheaper per input AND output token [4, T3]. The new Opus 4.7 tokenizer can inflate token counts ~35% — real bills can rise on the "unchanged" rate card [4, T3]. Reserve Opus 4.7 for genuine reasoning bottlenecks.

### Are more hooks always better?

**No.** Every hook adds latency to every matched event. The 95-hook champion in the community uses sub-200ms hooks across the board [5, T3] — but most projects regress when they add a 600ms PostToolUse and don't notice for weeks.

---

## Confidence Assessment

- **Strong evidence (T1/T2 + multiple T3 corroboration)**: prompt caching mechanics, Tool Search numbers, model pricing, Message Batches discount, hook latency thresholds, ccusage availability, plan mode behaviour.
- **Convergent reporting (T3 only)**: subagent 20K-overhead figure, 3-agent 7x token multiplier, Opus 4.7 tokenizer inflation, worktree sweet spot of 2–4.
- **Single source / unverified**: caveman-prompts 30–55% compression number [23, T3] — try locally before trusting. The "v2.1.89 3–50x rate-limit consumption" claim [9, T3] is widely reported but Anthropic's own postmortem [link in [5, T1]] should be the authoritative reference.

---

## Gaps & Open Questions

- No T1 source seen for **exact tokenizer delta of Opus 4.7 vs Sonnet 4.6** on real workloads. Test locally with a representative `_meta/` file.
- UserPromptSubmit hook **replacing** (vs appending) the user prompt is still a feature request (issue #46761). If/when shipped, Token Saviour becomes net-negative cost.
- Anthropic has not (publicly) published a recommended **token budget per agent** number ; the "1-2K summary out of tens of thousands of exploration" figure [25, T1] is the closest guidance.
- Whether the Bhishma loop-detector hash-and-count is faster as a hook or as an inline check in `agent.md` — would need benchmarking.

---

## Suggested Next Steps (Concrete)

1. **This week**: profile `lib/bhishma-pretool-hook.sh` and `lib/post-tool-hook.sh` latency with `time` ; install ccusage ; run `/fewer-permission-prompts`.
2. **Next sprint**: add `model:` frontmatter to all 8 agent files per table in §5 ; rerun a representative Sahadeva audit to confirm zero quality regression.
3. **Within a month**: convert Sahadeva weekly audit to Message Batches API ; wire trace export to Langfuse free tier ; add hash-and-count loop detector to bhishma.
4. **Test then adopt**: adaptive thinking on Vyasa and Sahadeva — measure with ccusage before/after.

---

## Source Bibliography

[1] Prompt caching — Claude API Docs — platform.claude.com, 2026 — T1
https://platform.claude.com/docs/en/build-with-claude/prompt-caching
Cache pricing, TTLs, breakpoint mechanics.

[2] Claude prompt caching in 2026: 5-minute TTL — dev.to, Apr 2026 — T3
https://dev.to/whoffagents/claude-prompt-caching-in-2026-the-5-minute-ttl-change-thats-costing-you-money-4363
Concrete cost deltas, what breaks cache.

[3] What is MCP Tool Search — atcyrus.com, Jan 2026 — T3 with T1 Anthropic announcement
https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide
85% token reduction, Opus 4.5 49→74% accuracy gain.

[4] Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 pricing — finout.io, May 2026 — T3
https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag
Per-token pricing, Opus 4.7 tokenizer inflation.

[5] Claude Code Hooks: 95 hooks — blakecrosley.com, 2026 — T3
https://blakecrosley.com/blog/claude-code-hooks
~200ms safe latency, 500ms+ feels sluggish.

[6] Introducing Message Batches API — anthropic.com/news — T1
https://www.anthropic.com/news/message-batches-api
50% discount, 24h SLA, batch + cache stacking.

[7] Automatic allowlist in Claude Code — wmedia.es, 2026 — T3
https://wmedia.es/en/tips/claude-code-fewer-permission-prompts
/fewer-permission-prompts mechanics, security blocklists.

[8] Adaptive thinking — Claude API Docs — T1
https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking
40-60% pipeline cost reduction with adaptive vs fixed.

[9] Best ways to monitor Claude Code token usage — dev.to, 2026 — T3
https://dev.to/kuldeep_paul/best-ways-to-monitor-claude-code-token-usage-and-costs-in-2026-5j3
ccusage, Claude-Code-Usage-Monitor, ccflare.

[10] Run parallel sessions with worktrees — Claude Code Docs — T1
https://code.claude.com/docs/en/worktrees
isolation: worktree, 2-4 parallel sweet spot.

[11] Pricing — Claude API Docs — T1
https://platform.claude.com/docs/en/about-claude/pricing
Authoritative per-token pricing.

[12] Claude Code Plan Mode 2026 — claudedirectory.org — T3
https://www.claudedirectory.org/blog/claude-code-plan-mode-guide
Plan-mode discipline, /clear behaviour.

[13] Advanced tool use — Anthropic Engineering — T2
https://www.anthropic.com/engineering/advanced-tool-use
Tool Search official guidance.

[14] Effective context engineering for AI agents — Anthropic — T1
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
Sub-agent design philosophy, 1-2K summary output target.

[15] Claude Code Statusline Guide 2026 — claudedirectory.org — T3
https://www.claudedirectory.org/blog/claude-code-statusline-guide
Statusline customisation, per-subagent model overrides.

[16] Skill authoring best practices — Claude Docs — T1
https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
Keep SKILL.md terse, reference subfiles.

[17] Extend Claude with skills — Claude Code Docs — T1
https://code.claude.com/docs/en/skills
Progressive disclosure, 100 tokens metadata / <5K body.

[18] Prompt caching saves money until it doesn't — medium.com — T3
https://medium.com/@mdfadil/prompt-caching-saves-money-until-it-doesnt-8519c470918d
Dynamic prefix failure mode.

[19] /loop and /schedule recurring tasks — medium.com Rick Hightower — T3
https://medium.com/@richardhightower/put-claude-on-autopilot-scheduled-tasks-with-loop-and-schedule-built-in-skills-43f3be5ac1ec
Interval syntax, jitter, persistence semantics.

[20] Local vs remote MCP servers — red-gate.com — T3
https://www.red-gate.com/simple-talk/ai/local-vs-remote-mcp-servers-which-should-you-choose/
Latency comparison.

[21] Read tool 25k token limit — github.com/anthropics/claude-code issue #15687 — T3
https://github.com/anthropics/claude-code/issues/15687
Line-number overhead, offset/limit usage.

[22] Streaming tool calls — Alex Albert X post + Anthropic — T2
https://x.com/alexalbert__/status/1932830278789255351
Latency improvements to tool parameter streaming.

[23] Claude Code hooks reference — Claude Code Docs + issue #46761 — T1/T3
https://code.claude.com/docs/en/hooks
UserPromptSubmit append-only limitation.

[24] Claude Skills complete 2026 guide — buildfastwithai.com — T3
https://www.buildfastwithai.com/blogs/claude-skills-complete-guide-2026
Skill composition model.

[25] Effective context engineering for AI agents — Anthropic Engineering — T1
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
Lead-agent / sub-agent canonical pattern, summary token target.

[26] AI agent token budget management — mindstudio.ai — T3
https://www.mindstudio.ai/blog/ai-agent-token-budget-management-claude-code
3-agent 7x multiplier.

[27] MCP server caching — fast.io — T3
https://fast.io/resources/mcp-server-caching/
Cold-start 2485ms vs cached 0.01ms.

[28] Observability with OpenTelemetry — Claude Code Docs — T1
https://code.claude.com/docs/en/agent-sdk/observability
OTLP spans per agent-loop step.

[29] Multi-agent observability hooks — github.com/disler/claude-code-hooks-multi-agent-observability — T3
https://github.com/disler/claude-code-hooks-multi-agent-observability
Loop-detector hash pattern.

---

End. Word count: ~2950.
