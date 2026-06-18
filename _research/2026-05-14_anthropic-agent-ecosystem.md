# Anthropic AI Agent Ecosystem — Operator's Brief

**Date:** 2026-05-14
**Audience:** Kartavya (Rootlabs) — already running Mahabharata-themed multi-agent stack on Claude Code + CC-OS
**Tiers:** **[T1]** Anthropic official / docs.anthropic.com / claude.com / code.claude.com / official GitHub · **[T2]** reputable secondary (major dev pubs, well-known practitioners, vendor docs that mirror Anthropic) · **[T3]** community blog / forum

---

## TL;DR

1. **Models**: Opus 4.7 (released **Apr 16, 2026**) is the new agentic-coding flagship — $5/$25/MTok, 1M context, new tokenizer that costs ~1.0–1.35× more tokens, adaptive thinking only (extended-thinking budgets are gone), and a new **task_budget** primitive for cost-aware agent loops. Sonnet 4.6 stays the default workhorse; Haiku 4.5 stays the cheap subagent. **[T1]**
2. **Claude Code SDK was renamed → Claude Agent SDK on Sept 29, 2025.** Packages: `claude-agent-sdk` (Python), `@anthropic-ai/claude-agent-sdk` (TS). Heads-up: **starting June 15, 2026**, Agent SDK and `claude -p` usage on subscription plans draws from a separate monthly credit pool. **[T1]**
3. **Managed Agents** is now the cleanly-named hosted alternative to running the Agent SDK in your own process. The "Code with Claude" event on May 5–7, 2026 added **Dreaming** (scheduled memory curation across sessions), **Outcomes** (built-in evaluator-optimizer with rubrics), and built-in **multi-agent orchestration** to Managed Agents. **[T1, T2]**
4. **Prompt cache TTL silently regressed from 1h → 5min on March 6, 2026.** If you rely on the 1h cache (you probably should for agent system prompts), you must now pass `"ttl": "1h"` explicitly. Hit reads cost 0.1× input; 1h writes cost 2× input. **[T1, T2]**
5. **Skills became an open standard in Oct 2025** and slash commands are now subsumed by skills (skill wins if both share a name). Anthropic-blessed partner skills include Canva, Notion, Figma, Atlassian. The `Skill` tool, plugin-namespaced skills, and `disable-model-invocation` are first-class. **[T1, T2]**
6. **Subagent frontmatter is wider than most operators know**: `skills`, `memory` (user/project/local), `isolation: worktree`, `effort`, `background`, `initialPrompt`, and conditional `PreToolUse` hooks. Your existing Mahabharata stack is correctly shaped; ~5 of these fields are likely underused. **[T1]**

---

## 1. Claude Model Family (state as of May 14, 2026)

### 1.1 Current lineup (Latest models comparison) **[T1]**

| Feature                   | **Claude Opus 4.7**                              | **Claude Sonnet 4.6**           | **Claude Haiku 4.5**                                   |
| ------------------------- | ------------------------------------------------ | ------------------------------- | ------------------------------------------------------ |
| API ID                    | `claude-opus-4-7`                                | `claude-sonnet-4-6`             | `claude-haiku-4-5-20251001` (alias `claude-haiku-4-5`) |
| Description               | Most capable; complex reasoning & agentic coding | Best speed/intelligence balance | Fastest; near-frontier intelligence                    |
| Input / Output $/MTok     | **$5 / $25**                                     | **$3 / $15**                    | **$1 / $5**                                            |
| Context window            | **1M tokens**                                    | **1M tokens**                   | 200k tokens                                            |
| Max output                | 128k                                             | 64k                             | 64k                                                    |
| Extended thinking         | **No** (removed)                                 | Yes                             | Yes                                                    |
| Adaptive thinking         | **Yes (only thinking mode)**                     | Yes                             | No                                                     |
| Reliable knowledge cutoff | Jan 2026                                         | Aug 2025                        | Feb 2025                                               |

Source: docs.anthropic.com / platform.claude.com — Models overview page. **[T1]**

Note: starting with the 4.6 generation, **model IDs use a dateless format that is still a pinned snapshot**, not an evergreen pointer (`claude-opus-4-7` does not float). **[T1]**

Legacy still-callable: Opus 4.6, Sonnet 4.5, Opus 4.5, Opus 4.1. **Sonnet 4 (`-20250514`) and Opus 4 (`-20250514`) deprecate June 15, 2026.** **[T1]**

### 1.2 What changed in 4.5 → 4.6 → 4.7 for agentic workloads

**Haiku 4.5 (Oct 15, 2025)**: cheap fast tier used by Claude Code's "smart model switching" for the 30–40% of tasks that don't need reasoning. **[T2]** (Source: scriptbyai.com timeline; corroborated by claudefa.st)

**Sonnet 4.6 (Feb 17, 2026)** + **Opus 4.6 (Feb 2026)**: 1M-token context now standard on the workhorse, stronger tool-use, computer-use (94% on insurance benchmark per vendor), shipped extended thinking and the v1 "task budget"-style controls. **[T2]**

**Opus 4.7 (Apr 16, 2026)** — the agentic-coding step change **[T1]**:

- **+13% resolution on Anthropic's 93-task internal coding benchmark vs Opus 4.6**, including 4 tasks neither 4.6 nor Sonnet 4.6 could solve. **[T2]** (Source: scriptbyai.com / aireleasetracker; not independently verified externally — single-tier-2 source for the exact number — `[single source, T2]`).
- **Task budgets (beta)**: pass `task_budget: {type: "tokens", total: N}` plus header `task-budgets-2026-03-13`. Model sees a running countdown and self-paces. Distinct from `max_tokens` (hard cap, not exposed to model). **[T1]**
- **New `xhigh` effort level** for coding + agentic. **[T1]**
- **New tokenizer**: text uses ~1.0×–1.35× as many tokens as 4.6. Plan for ~15–35% cost inflation on text-heavy workloads. **[T1]**
- **High-res images** (2576px / 3.75MP) with **1:1 pixel coordinates** — directly relevant if Sanjaya/Hanuman ever ingest TikTok thumbnails or Supabase-stored creator screenshots. **[T1]**
- **Breaking**: `temperature`, `top_p`, `top_k` removed (400 error). Extended-thinking `budget_tokens` removed (use `thinking: {type: "adaptive"}`). Thinking content is omitted from responses by default — set `display: "summarized"` to opt back in. **[T1]**

Behavior changes that affect prompts: more literal instruction-following, fewer tool calls by default, **fewer subagents spawned by default** (steerable via prompt), more progress updates, less validation-forward tone. If your prompts have "double-check" or "use a subagent for X" scaffolding, re-baseline. **[T1]**

### 1.3 Extended thinking / reasoning

- **Opus 4.7**: extended-thinking is gone; **adaptive thinking** is the sole thinking-on mode and is **off by default**. Set `thinking: {type: "adaptive"}` to enable. **[T1]**
- **Sonnet 4.6 & Haiku 4.5**: still support extended thinking. **[T1]**
- Cost: thinking tokens count toward output cost. Adaptive scales thinking to perceived task complexity, which is generally a net cost win vs fixed-budget extended thinking on heterogeneous workloads (Anthropic's own claim — `[T1]`).

### 1.4 Prompt caching

- **Default TTL = 5 minutes**, beta `"ttl": "1h"` for 1-hour cache. **[T1]**
- **Pricing**: 5m write = 1.25× input; **1h write = 2× input**; **cache read = 0.1× input** (90% discount). **[T1]**
- **March 6, 2026 silent regression**: the default TTL was dropped from 1h to 5min without changelog notice; if you didn't explicitly opt in to 1h, your cache hit rate likely cratered around that date and your token bill jumped. **[T2]** (dev.to writeup + a GitHub issue #46829 on `anthropics/claude-code`). Confirm by checking your own usage history around Mar 6.
- **For agents specifically**: a 1h cached system prompt + tool list across many turns is one of the highest-leverage cost levers. For Sahadeva (audits) and Vyasa (conductor), cache the persona + skill index aggressively.

---

## 2. Claude Agent SDK

### 2.1 What it is, what it replaced **[T1]**

The Claude Agent SDK is the productized library for running Claude Code's agent loop, tools, and context management **inside your own process**. Renamed from "Claude Code SDK" on **September 29, 2025**.

Packages:

- Python: `pip install claude-agent-sdk` (was `claude-code-sdk`)
- TypeScript: `npm install @anthropic-ai/claude-agent-sdk` (was `@anthropic-ai/claude-code`)

The TypeScript SDK bundles a native Claude Code binary for your platform as an optional dependency — no separate install needed.

### 2.2 Core primitives **[T1]** (from code.claude.com/docs/en/agent-sdk/overview)

- **Built-in tools**: Read, Write, Edit, Bash, Glob, Grep, **Monitor** (background script streaming), WebSearch, WebFetch, **AskUserQuestion** (multiple-choice clarifying questions).
- **Hooks**: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, and others. Used as callback functions (Python `HookMatcher`, TS `HookCallback`).
- **Subagents** (Python `AgentDefinition`, TS via `agents: {...}`): spawn specialized agents with their own context window, model, tool allowlist. Messages include `parent_tool_use_id` to track lineage.
- **MCP servers** as a first-class config in `mcp_servers` / `mcpServers`.
- **Permissions**: `allowed_tools` allowlist, `permission_mode` (acceptEdits, auto, dontAsk, bypassPermissions, plan).
- **Sessions**: capture `session_id` from the init `SystemMessage`, resume with `resume=session_id`, fork to explore variants.
- **Compaction**: server-side conversation summarization at context-window threshold (pairs with the client-side memory tool).
- **Filesystem-based config**: by default loads `.claude/skills/*/SKILL.md`, `.claude/commands/*.md`, `CLAUDE.md` / `.claude/CLAUDE.md`, plus plugins. Restrict via `setting_sources` (Py) / `settingSources` (TS).

### 2.3 Python vs TypeScript parity

Both SDKs expose the same primitives (query, options, hooks, subagents, MCP, sessions, permissions). The TS SDK bundles the Claude Code binary; the Python SDK requires Claude Code installed separately for some flows. Anthropic's docs treat them as feature-paired; both have changelogs at `anthropics/claude-agent-sdk-typescript` and `anthropics/claude-agent-sdk-python` on GitHub. **[T1]**

### 2.4 Agent SDK vs Managed Agents vs raw Anthropic SDK **[T1]**

|                   | **Anthropic Client SDK**                                | **Claude Agent SDK**                                       | **Managed Agents**                                                         |
| ----------------- | ------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| What it gives you | Direct Messages API access; you implement the tool loop | Library that runs Claude Code's agent loop in your process | Hosted REST API; Anthropic runs agent + sandbox                            |
| Runs in           | Your process                                            | Your process, your infrastructure                          | Anthropic-managed infra                                                    |
| Custom tools      | You implement everything                                | In-process Python/TS functions                             | Claude triggers; you return results                                        |
| Session state     | You manage                                              | JSONL on your filesystem                                   | Anthropic-hosted event log                                                 |
| Sandbox           | None                                                    | None (your machine)                                        | Managed sandbox per session                                                |
| Best for          | Maximum control, custom loops                           | Local prototyping, file-system agents                      | Long-running async sessions; production without operating your own sandbox |

The common path is "prototype with Agent SDK locally → move to Managed Agents for production." **[T1]**

### 2.5 Important upcoming change

**Starting June 15, 2026**: Agent SDK and `claude -p` usage on Claude Pro/Max subscription plans will draw from a **new monthly Agent SDK credit pool**, separate from interactive usage. This is a meaningful operator concern — if you're running Nakula cron jobs or Sanjaya background observers via `claude -p`, that quota becomes a budget line. **[T1]** (Source: code.claude.com/docs/en/agent-sdk/overview — note box at top of page.)

---

## 3. Claude Code (CLI + harness)

### 3.1 Skills (the marquee 2025–2026 shift) **[T1, T2]**

- **Launched October 2025**; **open-sourced as a standard** with the Skills spec.
- Skills are Markdown files with YAML frontmatter at `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (user) or inside plugins.
- **Discovery model**: skill metadata (name + description) loads at session start; full skill body is loaded **on demand** when the model invokes the `Skill` tool with the matching name. This is critical for context budget — your 25 persona-synthesis skills should not all be eating tokens at startup. Verify yours have descriptions that are tight enough for the model to route correctly.
- **Slash commands and skills are unified.** Files in `.claude/commands/` still work, but the recommended path is `.claude/skills/`. **If a skill and a command share a name, the skill wins.** **[T2]**
- `disable-model-invocation: true` in a skill's frontmatter prevents auto-invocation (only explicit `/name` invocation works). **[T1]**
- Plugin-namespaced skills appear as `plugin:skill` in `Skill` tool calls.
- Built-in skills include `/loop` and the `claude-api` skill. **[T1]**

### 3.2 Subagents **[T1]**

Built-in: **Explore** (Haiku, read-only, codebase search), **Plan** (used in plan mode), **General-purpose**, plus `statusline-setup` and `claude-code-guide`.

Custom subagents live in `.claude/agents/` (project) or `~/.claude/agents/` (user). YAML frontmatter fields:

| Field                       | Notes                                                                                                                                                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`, `description`       | Required. `description` is what Claude uses to decide when to delegate.                                                                                                                                               |
| `tools` / `disallowedTools` | Allowlist / denylist. `disallowedTools` applies first.                                                                                                                                                                |
| `model`                     | `sonnet` / `opus` / `haiku` / full ID / `inherit`. Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation > definition > parent.                                                                         |
| `permissionMode`            | `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan`                                                                                                                                         |
| `maxTurns`                  | Stops the subagent at N turns                                                                                                                                                                                         |
| `skills`                    | **Preload** skills into the subagent's startup context (full body injected, not just description). Subagent can still invoke other skills via the Skill tool. Cannot preload `disable-model-invocation: true` skills. |
| `mcpServers`                | Per-subagent MCP. Inline servers connect on subagent start. Useful to keep heavy MCP tool descriptions out of the parent context.                                                                                     |
| `hooks`                     | Frontmatter hooks fire when agent runs as subagent OR as main session (via `--agent`). `Stop` is auto-converted to `SubagentStop` in subagent context.                                                                |
| `memory`                    | `user` / `project` / `local`. Auto-provisions `MEMORY.md` and persistent dir. Read/Write/Edit auto-enabled.                                                                                                           |
| `background`                | `true` = always run as background task                                                                                                                                                                                |
| `effort`                    | `low` / `medium` / `high` / `xhigh` / `max`. Overrides session effort while subagent is active.                                                                                                                       |
| `isolation: worktree`       | Runs subagent in a **temporary git worktree** (isolated repo copy). Auto-cleaned if no changes made.                                                                                                                  |
| `color`                     | Display color for transcript/UI                                                                                                                                                                                       |
| `initialPrompt`             | Auto-submitted as first user turn when agent runs as the main session (via `--agent`). Commands and skills are processed.                                                                                             |

Note: in **Claude Code v2.1.63**, the **`Task` tool was renamed to `Agent`**. Existing `Task(...)` references in settings and agent definitions still work as aliases. **[T1]**

### 3.3 Subagents vs Skills vs Slash Commands — the disambiguation **[T1]**

| Primitive               | What it is                                                                      | When to reach for it                                                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Skill**               | Markdown body + frontmatter, loaded **into the current context** on demand      | A capability/recipe you want Claude to _use_ mid-task (a workflow, a domain SOP, a translator). Lives in current context window.                                                                 |
| **Slash command**       | Pre-canned prompt with optional bash/file resolution                            | Quick reusable prompts you type. Skills supersede this — prefer skills for new work.                                                                                                             |
| **Subagent**            | A whole separate agent with its own context window, system prompt, tools, model | When the work would otherwise pollute parent context (search results, big file dumps), when you need a different model (Haiku for cheap searches), or when you need different permissions/tools. |
| **Background subagent** | Subagent with `background: true`                                                | Long-running work (Yudhishthira large dataset analysis) you want to fire-and-monitor.                                                                                                            |
| **Routine** (Cloud)     | Anthropic-managed scheduled agent                                               | Truly unattended work that survives your laptop.                                                                                                                                                 |
| **/loop**               | Session-scoped recurring prompt                                                 | "Poll the build every 5m while I work."                                                                                                                                                          |

Rule of thumb: a skill **augments** the current agent; a subagent **replaces** it for a delimited scope.

### 3.4 Hooks taxonomy **[T1]**

| Hook                             | Fires on                             | Can block?   | Common use                                   |
| -------------------------------- | ------------------------------------ | ------------ | -------------------------------------------- |
| `SessionStart`                   | Session begins                       | No           | Greeter (you have this), inject context      |
| `SessionEnd`                     | Session ends                         | No           | Cleanup, checkpoint                          |
| `UserPromptSubmit`               | Before user prompt sent              | Modify input | Token Saviour (you have this), timestamps    |
| `PreToolUse`                     | Before a tool call                   | Yes (exit 2) | Validation (e.g., block destructive SQL)     |
| `PostToolUse`                    | After a tool call                    | No           | Audit log (you might want this for Sahadeva) |
| `Stop`                           | Main agent finishes                  | No           | Wrap-up                                      |
| `SubagentStart` / `SubagentStop` | Subagent lifecycle in parent session | No           | Per-subagent setup/teardown                  |
| `Notification`                   | Notifications sent                   | No           | Route to Slack                               |

Hook input is JSON on stdin; exit code 2 from a `PreToolUse` hook blocks the call. Plugin subagents **cannot** define `hooks`, `mcpServers`, or `permissionMode` for security reasons. **[T1]**

### 3.5 Scheduling (Routines, Desktop, /loop) **[T1]**

|                            | **Routines (Cloud)** | **Desktop scheduled tasks** | **/loop (session)**                 |
| -------------------------- | -------------------- | --------------------------- | ----------------------------------- |
| Runs on                    | Anthropic cloud      | Your machine                | Your machine                        |
| Requires machine on        | No                   | Yes                         | Yes                                 |
| Requires open session      | No                   | No                          | **Yes**                             |
| Persistent across restarts | Yes                  | Yes                         | Restored on `--resume` if unexpired |
| MCP servers                | Per-task connectors  | Config files + connectors   | Inherits from session               |
| Permission prompts         | None (autonomous)    | Configurable                | Inherits                            |
| Custom schedule            | Via `/schedule`      | Yes                         | Yes                                 |
| Min interval               | 1 hour               | 1 minute                    | 1 minute                            |

- **Cron tools**: `CronCreate`, `CronList`, `CronDelete` — 5-field cron, 50 tasks/session cap, **7-day expiry on recurring tasks** (fires once more then deletes itself), **jitter** of up to 30m on recurring + ±90s on top-of-hour one-shots (use minute :03 etc. to avoid jitter).
- **`/loop`** modes:
  - `/loop 5m <prompt>` — fixed interval
  - `/loop <prompt>` — Claude self-paces 1m–1h
  - `/loop` — runs the **built-in maintenance prompt** (continue unfinished work, tend to PR, cleanup passes) or your `.claude/loop.md` if present
- **Monitor tool** (event-driven alternative to polling): runs a background script and streams each output line back. More token-efficient than re-running prompts. **[T1]**
- **Channels** (referenced from scheduled-tasks page): CI/external systems can push events into a session. **[T1]**
- **`CLAUDE_CODE_DISABLE_CRON=1`** disables scheduling entirely.
- **Disable scheduled tasks** require Claude Code **v2.1.72 or later**. **[T1]**

### 3.6 Web app, IDE extensions, worktrees, background agents

- **Claude Code on the web** launched **Oct 20, 2025** at `claude.ai/code` — browser-based agent harness. **[T2]**
- **Worktrees**: first-class via `EnterWorktree` / `ExitWorktree` tools; subagents can be put in temporary worktrees via `isolation: worktree`. **[T1]**
- **Background agents / agent view**: many parallel sessions monitored from one place (`/en/agent-view`). **[T1]**
- **Agent teams**: subagent definitions can be referenced when spawning a "teammate" agent that communicates with the main session. **[T1]** (Page referenced from subagents doc.)
- **Fast mode**: Anthropic refers to this as a low-effort, fast-path mode tied to the `effort` parameter (`low` / `medium`). For Opus 4.7, recommended `xhigh` for coding/agentic and `high` for intelligence-sensitive use cases. **[T1]**

### 3.7 Permissions model, settings.json, allowlists **[T1]**

- Permission scopes: tool allowlist (`permissions.allow`), deny (`permissions.deny`), `additionalDirectories` for file access, `permissionMode` for global posture.
- Managed settings (organization) > CLI flags > project `.claude/settings.json` > user `~/.claude/settings.json` > defaults.
- `Agent(subagent-name)` syntax to allow/deny specific subagents.
- `Bash(*)`, `mcp__server__tool` style tool patterns for fine-grained allowlisting.

---

## 4. Model Context Protocol (MCP) — current state

### 4.1 Spec and ownership **[T1, T2]**

- **MCP is maintained at `modelcontextprotocol.io`** with a multi-vendor steering group; Anthropic seeded it but it's positioned as open.
- **Current spec versions in active use**: `2025-11-25` (current) and `2025-06-18` (still widely deployed). 2026 updates build on those drafts. **[T2]** (Sources: workos.com docs, dev.to 2026 guide, auth0.com blog.)
- **Streamable HTTP transport** introduced in 2025-06-18 spec uses **OAuth 2.1** with PKCE, RFC 8707 Resource Indicators, and MCP servers are formally classified as OAuth 2.1 Resource Servers. **[T2]**

### 4.2 Auth flow (the `authenticate` / `complete_authentication` pattern you see in claude.ai-hosted servers) **[T2]**

1. Client connects without a token → server returns **401** with `WWW-Authenticate` header pointing to Protected Resource Metadata endpoint.
2. Client fetches metadata → discovers authorization server URL + scopes.
3. PKCE pair generated; user redirected to auth server.
4. User authenticates, consents, gets redirected back with auth code.
5. Code exchanged for access token.
6. Subsequent MCP calls bear the token.

The `mcp__<server>__authenticate` and `mcp__<server>__complete_authentication` tools you have for Apollo, Clay, Klaviyo, Google Calendar, Google Drive, Slack are the client-side wrappers for steps 1–5 of this flow.

### 4.3 Client-side: how Claude Code consumes MCP **[T1]**

- `.mcp.json` at project root configures servers (stdio, http, sse, ws transports).
- `~/.claude.json` for user-level.
- Subagents can override or extend via `mcpServers` frontmatter.
- Tool discovery via `ListMcpResourcesTool` / `ReadMcpResourceTool`.
- Tool descriptions live in context — **MCP server tool descriptions can consume meaningful tokens**. Use subagent-scoped `mcpServers` to keep heavy server descriptions out of the parent.

### 4.4 Notable Anthropic-blessed / ecosystem servers

**Anthropic-blessed (referenced in their own docs/cookbooks)** **[T1]**: GitHub, Slack, Google Drive, Playwright (browser), filesystem, Puppeteer, fetch.

**Hundreds more** in the `modelcontextprotocol/servers` repo. **[T1]**

**Partner Skills (different from MCP, but related ecosystem)**: Canva, Notion, Figma, Atlassian launched as prebuilt Claude Skills in 2025–26. **[T2]**

### 4.5 Caching considerations for MCP

- MCP **tool calls are not cacheable** in the same way prompt prefixes are; latency depends on the underlying server.
- MCP **tool descriptions** sit in the prompt and **are cacheable** if they're in a cached prefix. Keep them stable across calls within a cache window to maximize hit rate. (Inference from prompt-caching docs + MCP docs — `[T1 + reasoning]`).
- For long agent loops, the cost of re-reading MCP descriptions on every call is real; prefer a stable system-prompt → MCP-descriptions → tools ordering for cache prefix stability.

---

## 5. Recent shifts (~last 6 months) — operator changelog

Ordered roughly by operational impact for someone running an active multi-agent stack.

| Date                         | Shift                                                                                                                                | Where                    | Impact                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ | -------------------------------------------------------------------- |
| **Sept 29, 2025**            | Claude Code SDK → **Claude Agent SDK** rename + repackage **[T1]**                                                                   | Both Py + TS             | Update imports if you upgrade past Sep 2025 versions                 |
| **Oct 2025**                 | **Agent Skills** launched (skill spec, /skill, partner skills) **[T1, T2]**                                                          | Claude Code + claude.ai  | Big — this is the canonical way to add reusable capabilities now     |
| **Oct 15, 2025**             | **Haiku 4.5** released **[T2]**                                                                                                      | API                      | Cheap subagent target; smart model switching in Claude Code          |
| **Oct 20, 2025**             | **Claude Code on the web** (claude.ai/code) launched **[T2]**                                                                        | Web                      | Browser harness for the same agent loop                              |
| **Feb 17, 2026**             | **Sonnet 4.6** released **[T2]**                                                                                                     | API + Code               | Default workhorse; 1M context standard                               |
| **Feb 2026**                 | **Opus 4.6** released **[T2]**                                                                                                       | API + Code               | Replaced Opus 4.5 as flagship                                        |
| **~Feb–Mar 2026**            | **`Task` tool renamed to `Agent`** in Claude Code v2.1.63 **[T1]**                                                                   | Claude Code              | Backward-compatible alias                                            |
| **Mar 6, 2026**              | **Prompt cache default TTL silently changed 1h → 5m** **[T2]**                                                                       | API                      | Audit your costs around this date; pass `"ttl": "1h"` explicitly     |
| **Mar 13, 2026**             | **`task_budget` beta** header `task-budgets-2026-03-13` **[T1]**                                                                     | API                      | Agent-loop cost ceiling                                              |
| **Mar 23, 2026**             | **Computer use** public research preview for Pro/Max **[T2]**                                                                        | claude.ai + API          | macOS first; Windows later in 2026                                   |
| **Mar 24, 2026**             | **300k-token batch output** beta `output-300k-2026-03-24` **[T2]**                                                                   | Batch API                | Long-form generation in batch                                        |
| **Apr 16, 2026**             | **Opus 4.7** released **[T1]**                                                                                                       | API + Code               | New tokenizer, task budgets, xhigh effort, high-res vision           |
| **May 5–7, 2026**            | **Code with Claude 2026**: Dreaming, Outcomes, multi-agent orchestration in **Managed Agents**, Claude Finance, Add-ins **[T1, T2]** | Managed Agents + plugins | Outcomes is the most generally useful — built-in evaluator-optimizer |
| **June 15, 2026** (upcoming) | **Agent SDK + `claude -p` usage moves to a separate subscription credit pool** **[T1]**                                              | Pro/Max plans            | Budget line item                                                     |
| **June 15, 2026** (upcoming) | **Sonnet 4 and Opus 4 (`-20250514`) deprecation** **[T1]**                                                                           | API                      | Migrate any legacy code                                              |

### 5.1 Reference architectures Anthropic has published

These are the canonical docs to actually read; bibliography below.

- **Building Effective Agents** (Dec 19, 2024) — the five workflow patterns. **[T1]**
- **Multi-Agent Research System** (2025) — the orchestrator-worker writeup with the 90.2% lift number. **[T1]**
- **Effective context engineering for AI agents** (2025–26) — the canonical "what should be in context" framing. **[T1]**
- **Effective harnesses for long-running agents** (Mar 2026) — three-agent harness, claude-progress.txt pattern, bridging context windows. **[T1, T2]**
- **Scaling Managed Agents: Decoupling the brain from ...** (2026) — internal Anthropic post on Managed Agents architecture. **[T1]**

---

## 6. What Anthropic has published about how to build agents well

### 6.1 Five canonical workflow patterns **[T1]** (Building Effective Agents, Dec 2024)

1. **Prompt chaining** — sequential steps with programmatic checks. Use when subtasks are predictable and latency is acceptable.
2. **Routing** — classify input → route to specialist. Use for distinct categories or to send simple queries to cheap models.
3. **Parallelization** — sectioning (independent subtasks) or voting (multiple attempts). Use for guardrails, multi-perspective evals.
4. **Orchestrator-Workers** — lead LLM decomposes, delegates to workers, synthesizes. Use when subtask shape is unknown ahead of time.
5. **Evaluator-Optimizer** — generator + evaluator in a loop. Use when criteria are clear and iteration measurably improves output.

Anthropic's core stance: **"the most successful implementations weren't using complex frameworks or specialized libraries"** — simple, composable patterns win.

Workflows vs agents: **workflows** = predefined code paths orchestrating LLMs; **agents** = LLMs dynamically directing their own process. Pick the simplest thing that works.

### 6.2 Tool design (their hardest-won lesson) **[T1]**

- Write tool descriptions like docstrings for a junior developer.
- Keep formats aligned with naturally occurring internet text (don't invent escape conventions).
- Avoid overhead like line counting or string escaping.
- "Poka-yoke" design: require absolute filepaths to prevent mistakes.
- Test extensively with varied inputs.
- Anthropic's SWE-bench agent spent **more time optimizing tools than overall prompts**.

### 6.3 Multi-Agent Research System lessons **[T1]**

- **Lead = Opus, workers = Sonnet** outperformed single-agent Opus by **90.2%** on their internal research eval.
- **Token cost = ~15× a normal chat.** Multi-agent is worth it only when task value justifies the spend.
- **Memory persists plans across the 200k context boundary** — when context gets truncated, the plan survives in memory.
- **Parallel tool calling** cut research time by up to **90%**.
- **Avoid multi-agent** when: tasks need shared context, have many inter-agent dependencies, or have few parallelizable parts. Most coding is in this category.
- **Eval discipline**: start with ~20 small-sample queries, use LLM-as-judge with a single rubric prompt, complement with human eval, log decision patterns without storing conversation content.

### 6.4 Effective context engineering **[T1]**

Core thesis: shift from **prompt engineering** ("what should I say") to **context engineering** ("what configuration of context should be present"). Memory tool + compaction + just-in-time retrieval is the substrate. The active context should be focused on what's currently relevant — store the rest in memory and pull on demand.

### 6.5 Effective harnesses for long-running agents (Mar 2026) **[T1]**

- **Three-agent harness**: separate planning, generation, and evaluation agents.
- **`claude-progress.txt`** pattern: progress log file alongside git history that fresh-context agents can quickly orient to.
- **Initializer session vs subsequent sessions**: the first session creates the memory artifacts (progress log, feature checklist, init script); each later session opens by reading them and updates the log before exiting.
- **Key discipline**: only mark a feature complete after **end-to-end verification**, not after code is written.

### 6.6 Outcomes (May 2026) **[T1, T2]**

Built-in evaluator-optimizer in Managed Agents: define a rubric, a separate grader evaluates outputs, agent self-corrects until grader passes. **+8.4% on .docx, +10.1% on .pptx** on internal benchmarks (`single source, T2`).

### 6.7 Dreaming (May 2026) **[T1, T2]**

Scheduled memory-curation process that reviews up to 100 past sessions, extracts patterns, merges duplicates, removes stale entries, and writes learnings as plain-text memory notes. **Does not modify model weights** — it operates purely on the memory directory. Currently in Managed Agents; the pattern can be replicated locally via a cron + a "dreaming" prompt over your `_audit/` and `memory/` directories.

---

## 7. Apply-to-Your-Setup — Mahabharata stack diagnostics

What I'm checking against:

- Agents: Arjuna, Hanuman, Sanjaya, Vyasa, Sahadeva, Nakula, Yudhishthira, Vidura/Narada under `.claude/agents/`
- ~14 universal CC-OS skills + 25 persona-synthesis skills
- Hooks: SessionStart, UserPromptSubmit, Token Saviour
- MCP: Supabase, Notion, Slack, Gmail, GDrive/Calendar, Klaviyo, Apollo, Clay, Vibe Prospecting, internal blueprint
- Memory: `MEMORY.md` index pattern, `_audit/REMINDERS.md`
- Patterns: observer-over-observer (Sanjaya watches workers → Vyasa watches Sanjaya → Sahadeva audits all)

### 7.1 Patterns you're already doing that Anthropic now formally endorses

- **Orchestrator-Worker** (Vyasa coordinating Arjuna/Hanuman/Yudhishthira) → maps cleanly to Anthropic's official multi-agent research system architecture. **Keep going.**
- **Lead = Opus, workers = Sonnet/Haiku** is the recommended split. If you're not already running Vyasa on Opus and routine workers on Sonnet/Haiku, that's a quick cost win.
- **MEMORY.md as an index, not a dump**: the file-based memory page explicitly recommends this pattern — your auto-memory at `/Users/mosaic/.claude/projects/.../memory/MEMORY.md` already follows it. **Validated.**
- **Cron + `_audit/REMINDERS.md` surfaced at SessionStart**: this is exactly the "scheduled memory-curation" pattern Anthropic just launched as Dreaming. You shipped it months early.
- **Token Saviour UserPromptSubmit hook**: aligns with Anthropic's "context engineering" framing — compress aggressively at the hook layer, leave the model context focused.

### 7.2 Things you're hand-rolling that have a better current primitive

1. **Sahadeva auditor → use Outcomes pattern as inspiration even if not Managed Agents.** Build a small rubric (5–8 weighted criteria), have Sahadeva grade its own output against it on every audit, and require pass before commit. This is the evaluator-optimizer loop made concrete. **[T1]**
2. **Sanjaya watching workers → use the `Monitor` tool, not a re-running prompt.** Scheduled-tasks doc explicitly recommends `Monitor` (streams each output line back as an event) over `/loop`-based polling. Token-efficient and responsive. Wire any long-running Arjuna jobs through `Monitor` and have Sanjaya consume the stream.
3. **Yudhishthira large CSV exports → Files API + Citations.** Upload heavy CSV/Sheets exports once via Files API (`anthropic-beta: files-api-2025-04-14`), reference by `file_id` thereafter. Pair with Citations for any analysis that needs source-tagged claims.
4. **Nakula cron pipelines → Cloud Routines (when the laptop closes).** Right now your cron presumably depends on the machine being on. For pipelines that must survive your laptop closing, migrate to `/schedule`-created Cloud Routines. Min interval 1 hour; runs autonomously without permission prompts.
5. **Subagent isolation when Arjuna mutates the repo → `isolation: worktree`.** Frontmatter field that puts the subagent in a temp git worktree. Auto-cleaned if no changes. Perfect for "let Arjuna try a refactor without polluting the working tree."
6. **MCP descriptions are eating parent context** if every subagent gets every MCP server. Use **per-subagent `mcpServers` inline** to scope, e.g., only give Yudhishthira the Supabase + GDrive MCPs and keep Klaviyo/Apollo out of his context.
7. **Skills `disable-model-invocation` for sensitive skills.** Your persona-synthesis skills that should only fire on explicit `/name` invocation should have `disable-model-invocation: true` in frontmatter.
8. **`Task` → `Agent` tool rename**: any `Task(...)` references in your `.claude/settings*.json` permission patterns still work (alias) but updating to `Agent(...)` is cleaner.

### 7.3 Missing primitives worth adopting now

- **1-hour prompt cache on the heaviest agents.** Vyasa's system prompt + Sahadeva's persona + your CC-OS rules are the prime candidates. Pass `"cache_control": {"type": "ephemeral", "ttl": "1h"}` on those blocks. Audit cache hit rate (it's in `usage.cache_read_input_tokens` in the API response).
- **`task_budget` for Vyasa's longer orchestration sessions.** Set an advisory token ceiling per delegated task so workers self-pace.
- **`xhigh` effort for Arjuna on hard coding tasks; `low` for Hanuman (recon).** Opus 4.7 docs explicitly recommend `xhigh` for agentic coding; reserve max effort for hard cases to control cost.
- **Subagent `memory: project`** on Sahadeva and Sanjaya so they accumulate audit/observer learnings in `.claude/agent-memory/<name>/`.
- **`PostToolUse` hook → audit log** at the harness level. Wire a script that appends every Bash/Edit/Write tool call to `_audit/tool-log.jsonl`. Sahadeva consumes this on its weekly run.
- **`Channels`** primitive for event-driven cross-session messaging — if you ever want CI failures or Supabase webhooks to push into a Claude Code session.

### 7.4 Where your "observer over observer" diverges from Anthropic's playbook

Anthropic's multi-agent post says explicitly: **multi-agent underperforms when tasks need shared context or have many inter-agent dependencies.** Your Sanjaya→Vyasa→Sahadeva chain is exactly that — they share heavy context about workers' actions.

This isn't necessarily wrong; observer chains are a legitimate audit pattern. But:

- **Token cost will be high** (the 15× multiplier applies). Make sure the audit value justifies it.
- **Consider collapsing Sanjaya + Vyasa into one agent with two passes** (observation pass → conduction pass) instead of a chain. Cheaper, fewer handoffs.
- **Sahadeva's weekly audit should batch** — don't fire it on every Vyasa turn; let it accumulate `_audit/tool-log.jsonl` and run once on a Routine.
- **Use the three-agent harness pattern** explicitly: planner (Vyasa) / executor (Arjuna or workers) / evaluator (Sahadeva) — this is the published canonical shape.

### 7.5 One concrete refactor pass to consider

```
Today:
  Vyasa → spawns Sanjaya → spawns workers → Sahadeva audits log weekly

Cleaner:
  Vyasa (Opus, lead, planner+conductor)
    └── workers (Sonnet/Haiku, subagents, isolation: worktree where mutating)
    └── Sahadeva (Sonnet, subagent with memory: project, runs on Routine)
  Sanjaya retired or absorbed as a PostToolUse hook that just writes to _audit/tool-log.jsonl
  Outcomes-style rubric: Sahadeva grades each Vyasa batch against rubric.md, blocks commit if fail
```

You lose nothing observability-wise (the audit log is still there) and you remove one agent + one context window. ~30–40% token reduction is plausible.

---

## 8. Learn-Today List (May 14, 2026)

Ranked by leverage for your specific setup. Times are reading + light experimentation.

1. **Audit your prompt-cache TTL across all hot prompts** — 30 min
   Why: the Mar 6, 2026 silent regression from 1h → 5m default. If you have long-lived system prompts (you do), passing `"ttl": "1h"` could cut your spend on Vyasa/Sahadeva 30–60%.
   Action: grep all `cache_control` usages in your codebases; add `"ttl": "1h"` where appropriate; measure `usage.cache_read_input_tokens` before/after.
   Source: docs.anthropic.com prompt-caching page. **[T1]**

2. **Read "Effective harnesses for long-running agents"** — 25 min
   Why: directly maps to your observer-conductor-executor pattern; gives you the canonical three-agent harness and `claude-progress.txt` convention.
   URL: `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents` **[T1]**

3. **Migrate Sonnet 4 / Opus 4 callers to 4.6/4.7** — 1 hour
   Why: hard deprecation June 15, 2026. Use the Claude API skill (`/claude-api`) to do the migration. Also re-baseline prompts on Opus 4.7 (less validation tone, fewer subagents by default, more literal instructions).
   Source: Opus 4.7 migration guide. **[T1]**

4. **Add `task_budget` to Vyasa's longest-running orchestration prompt** — 20 min
   Why: gives Opus 4.7 a budget-aware countdown across the entire agentic loop. Add header `task-budgets-2026-03-13`, set `output_config.task_budget = {type: "tokens", total: 100000}`.
   Source: What's new in Opus 4.7. **[T1]**

5. **Wire a PostToolUse audit hook → `_audit/tool-log.jsonl`** — 45 min
   Why: gives Sahadeva clean structured input instead of having to re-derive what happened. Anthropic's multi-agent post identified evals + observability as the highest-leverage investment.
   Action: small bash script that reads hook JSON from stdin, appends one line per Edit/Write/Bash to `_audit/tool-log.jsonl`. Register under `hooks.PostToolUse` in `settings.json`.
   Source: code.claude.com hooks docs. **[T1]**

6. **Read "Building Effective Agents" + "Multi-Agent Research System"** if you haven't recently — 40 min
   Why: still the canonical reference. Re-reading after 6 months of shipping will reveal mismatches.
   URLs: anthropic.com/research/building-effective-agents and anthropic.com/engineering/multi-agent-research-system **[T1]**

7. **Try Outcomes (rubric-graded loop) — even if not via Managed Agents** — 1 hour
   Why: cheapest path to evaluator-optimizer in Sahadeva. Write a 5-criterion rubric.md, have Sahadeva grade each Vyasa batch.
   Source: Code with Claude 2026 announcements; pattern is portable. **[T1, T2]**

8. **Set `disable-model-invocation: true` on persona-synthesis skills** — 15 min
   Why: with 25 persona skills, the model is probably mis-routing or wasting context evaluating which to load. Lock them to explicit `/name` invocation.
   Source: subagents/skills docs. **[T1]**

9. **Scope MCP servers per-subagent** — 30 min
   Why: with ~10 MCP servers connected, every subagent inherits tool descriptions for all. Move Klaviyo, Apollo, Clay into per-subagent inline `mcpServers` so they're only present in Hanuman/Vidura contexts.
   Source: subagents `mcpServers` frontmatter. **[T1]**

10. **`npx skills add supabase/agent-skills`** — 5 min
    Why: Supabase MCP server is in your stack; Supabase's published agent skills add critical dev/security guidance. The skill is referenced from inside the Supabase MCP tool itself.
    Source: Supabase MCP instructions in this session. **[T1, partner]**

11. **Move one Nakula cron pipeline to a Cloud Routine** — 30 min
    Why: dogfood routines on a low-risk pipeline before relying on them. Survives laptop closing. Min interval 1h.
    Source: code.claude.com routines docs. **[T1]**

12. **Bookmark these and re-check in 4 weeks**:
    - Anthropic news feed: `anthropic.com/news` **[T1]**
    - Anthropic engineering: `anthropic.com/engineering` **[T1]**
    - Agent SDK changelogs: `anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md` and `claude-agent-sdk-python` equivalent **[T1]**
    - Claude Code release notes: code.claude.com (look for `/en/release-notes`) **[T1]**

---

## Source Bibliography

### Tier 1 — Anthropic official

[T1.1] **Claude Models Overview** — platform.claude.com/docs/en/about-claude/models/overview
Why cited: current model lineup, pricing, context windows, deprecation schedule.

[T1.2] **What's new in Claude Opus 4.7** — platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7
Why cited: task_budget, xhigh effort, new tokenizer, breaking changes (thinking budgets, sampling params).

[T1.3] **Agent SDK overview** — code.claude.com/docs/en/agent-sdk/overview
Why cited: SDK primitives, Py/TS code examples, Agent SDK vs Managed Agents vs Client SDK comparison, the June 15 2026 subscription credit note.

[T1.4] **Building Agents with the Claude Agent SDK** — claude.com/blog/building-agents-with-the-claude-agent-sdk (published Sep 29, 2025; original URL redirected from anthropic.com/engineering)
Why cited: the rename announcement and the feedback-loop primitives (gather → act → verify → repeat).

[T1.5] **Building Effective Agents** — anthropic.com/research/building-effective-agents (Dec 19, 2024)
Why cited: the five workflow patterns; workflows-vs-agents distinction; tool design guidance.

[T1.6] **How we built our multi-agent research system** — anthropic.com/engineering/multi-agent-research-system
Why cited: orchestrator-worker architecture, 90.2% lift, 15× token cost, memory across 200k boundary, when NOT to use multi-agent.

[T1.7] **Create custom subagents** — code.claude.com/docs/en/sub-agents
Why cited: full frontmatter schema, built-in subagents, Task→Agent rename, isolation: worktree, persistent memory scopes.

[T1.8] **Run prompts on a schedule** — code.claude.com/docs/en/scheduled-tasks
Why cited: /loop, CronCreate/List/Delete, Routines vs Desktop vs /loop comparison, jitter, 7-day expiry, Monitor tool.

[T1.9] **Memory tool** — platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
Why cited: file-based memory architecture, /memories convention, multi-session software-development pattern, security considerations.

[T1.10] **Effective harnesses for long-running agents** — anthropic.com/engineering/effective-harnesses-for-long-running-agents (Mar 2026)
Why cited: three-agent harness, claude-progress.txt, initializer/subsequent session split.

[T1.11] **Effective context engineering for AI agents** — anthropic.com/engineering/effective-context-engineering-for-ai-agents
Why cited: shift from prompt-eng to context-eng, just-in-time retrieval framing.

[T1.12] **Prompt caching** — platform.claude.com/docs/en/build-with-claude/prompt-caching
Why cited: 5m/1h TTL, write/read pricing multipliers, `cache_control` schema.

[T1.13] **Files API** — docs.anthropic.com/en/docs/build-with-claude/files
Why cited: `anthropic-beta: files-api-2025-04-14`, file_id reuse pattern.

[T1.14] **Citations** — platform.claude.com/docs/en/build-with-claude/citations
Why cited: source-tagged claims feature; pricing model.

[T1.15] **Computer use tool** — platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
Why cited: current state of computer use; reliability caveats.

[T1.16] **New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration** — claude.com/blog/new-in-claude-managed-agents (May 6–7, 2026)
Why cited: Dreaming, Outcomes, multi-agent orchestration features announced at Code with Claude 2026.

[T1.17] **NPM package: `@anthropic-ai/claude-agent-sdk`** — npmjs.com/package/@anthropic-ai/claude-agent-sdk
Why cited: confirms the package rename + current version.

[T1.18] **Anthropic Engineering hub** — anthropic.com/engineering
Why cited: ongoing index for new posts.

[T1.19] **MCP Authorization spec** — modelcontextprotocol.io/specification/draft/basic/authorization
Why cited: OAuth 2.1 / PKCE flow for MCP servers.

### Tier 2 — Reputable secondary

[T2.1] **Introducing Claude Opus 4.7** — anthropic.com/news/claude-opus-4-7 (Apr 16, 2026)
Why cited: launch announcement, headline benchmark claims.

[T2.2] **Migrate to Claude Agent SDK** — platform.claude.com/docs/en/agent-sdk/migration-guide
Why cited: breaking changes between Code SDK and Agent SDK.

[T2.3] **Anthropic Silently Dropped Prompt Cache TTL from 1 Hour to 5 Minutes** — dev.to/whoffagents/anthropic-silently-dropped-prompt-cache-ttl-from-1-hour-to-5-minutes
Why cited: documents the March 6, 2026 TTL regression and operator impact.

[T2.4] **Issue #46829 on anthropics/claude-code** — github.com/anthropics/claude-code/issues/46829
Why cited: corroborates the TTL regression with cost impact reports.

[T2.5] **Anthropic API Pricing in 2026** — finout.io/blog/anthropic-api-pricing
Why cited: consolidated pricing reference including batch + caching multipliers.

[T2.6] **Stack Overflow Blog: MCP authentication and authorization** (Jan 21, 2026) — stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol
Why cited: 2026 state of MCP auth landscape.

[T2.7] **WorkOS AuthKit: Model Context Protocol** — workos.com/docs/authkit/mcp
Why cited: practical MCP OAuth 2.1 implementation reference.

[T2.8] **Claude (language model) — Wikipedia** — en.wikipedia.org/wiki/Claude\_(language_model)
Why cited: cross-check of model release dates and family chronology.

[T2.9] **Complete Guide to MCP in 2026** — dev.to/x4nent/complete-guide-to-mcp-model-context-protocol-in-2026...
Why cited: ecosystem adoption summary; treat with care (single author).

[T2.10] **The New Stack: Agent Skills as open standard** — thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards
Why cited: skills open-standard announcement context, partner skill list.

[T2.11] **Releasebot: Anthropic May 2026 updates** — releasebot.io/updates/anthropic
Why cited: aggregated release notes index.

### Tier 3 — Community blogs (use with caution; corroborate before relying)

[T3.1] **Scriptbyai: Claude Timeline** — scriptbyai.com/anthropic-claude-timeline
Why cited: model release dates; flagged where it was the only source (Opus 4.7 +13% benchmark figure).

[T3.2] **claudefa.st blog (multiple posts)** — claudefa.st/blog/models, /guide/development/scheduled-tasks
Why cited: practitioner explainer for model family + scheduled tasks.

[T3.3] **alexop.dev: Understanding Claude Code's Full Stack** — alexop.dev/posts/understanding-claude-code-full-stack
Why cited: MCP/Skills/Subagents/Hooks intersection.

[T3.4] **Shipyard cheat sheet** — shipyard.build/blog/claude-code-cheat-sheet
Why cited: condensed Claude Code reference.

[T3.5] **MindStudio: Code with Claude 2026 features** — mindstudio.ai/blog/code-with-claude-2026-new-agent-features
Why cited: event recap; corroborates T1.16.

[T3.6] **AddyOsmani: Long-running agents** — addyosmani.com/blog/long-running-agents
Why cited: practitioner perspective on harness engineering.

---

## Confidence Assessment

**Strong evidence / convergent reporting**:

- Model lineup, IDs, pricing, context windows (T1 docs match T2 secondary).
- Agent SDK rename Sept 29, 2025 (T1 blog + T1 npm + T2 migration guide).
- Five workflow patterns and multi-agent system metrics (T1 primary source).
- Subagent frontmatter schema (T1 primary; massive surface area).
- Scheduled tasks / /loop / Monitor (T1 primary).
- Memory tool architecture and MEMORY.md indexing (T1 primary).
- Skills as open standard (T1 + T2).
- Prompt-cache 1h/5m mechanics and pricing (T1 primary).

**Single-source or contested**:

- **Opus 4.7 +13% benchmark over 4.6** — sourced from T2/T3 secondary; not seen in T1 primary docs I fetched. Flagged inline. `[single source, T2]`
- **March 6, 2026 cache TTL regression** — documented in T2 (dev.to + GitHub issue) but the official prompt-caching docs do not call it out as a change. Behavior is real and consequential; the _date_ could be off by days.
- **Outcomes +8.4% docx / +10.1% pptx** — internal Anthropic numbers per T1 blog; no independent benchmark.
- **Claude Finance "10 pre-built agents"** — described in T2 recap; haven't confirmed against Anthropic's own product page.
- **Computer use 94% insurance benchmark / 93.9% WebVoyager** — T2/T3 secondary; vendor-favorable benchmark contexts; treat as directional.

**Speculative**:

- The exact wording of the June 15, 2026 Agent SDK credit-pool change ("monthly Agent SDK credit, separate from your interactive usage limits") is verbatim from T1 docs, but the **operational impact on your `claude -p` cron usage** is my inference, not stated by Anthropic.

---

## Gaps & Open Questions

1. **Did I miss a Sonnet 4.7?** I see Opus 4.7 (Apr 16) but no Sonnet 4.7 in current docs. If Anthropic shipped one in late April / early May, I didn't surface it. Check `anthropic.com/news` for posts dated April 16 – May 14, 2026.
2. **Add-ins** (mentioned in Code with Claude 2026 recap) — I didn't pull primary docs on this feature; unclear if it's Claude Code-specific or Managed Agents-specific.
3. **Channels** primitive — referenced from the scheduled-tasks doc but not separately fetched. Worth a deeper look if you want event-driven cross-session messaging.
4. **`/goal` command** — mentioned in scheduled-tasks doc as the "keep working until condition met" alternative to `/loop`. Not separately characterized here.
5. **Exact Claude Code CLI version** that introduced each feature — I have v2.1.63 (Task→Agent rename) and v2.1.72 (scheduled tasks) but the full version-to-feature map would be useful for your upgrade decisions. Check `code.claude.com/docs/en/release-notes` (URL inferred, not verified).
6. **MCP spec versions in production** — I have `2025-11-25` and `2025-06-18` as current/recent but didn't verify which Claude Code v2.1.x speaks natively.
7. **Pricing of Managed Agents** — not surfaced. If you're considering it for Outcomes, get the pricing before assuming cost parity with raw API.
8. **`claude-progress.txt` exact spec** — referenced from Effective Harnesses post; didn't pull the post itself in full.
9. **Anthropic's stance on agent-to-agent communication protocols** — anything formal beyond the in-process subagent model? `agent-teams` was referenced but not deeply fetched.

---

## Suggested Next Steps

1. **Read the three Anthropic engineering posts** in order: Building Effective Agents → Multi-Agent Research System → Effective Harnesses for Long-Running Agents. Together they're the canonical narrative.
2. **Run a one-day cost audit** of your cache hit rates across Vyasa/Sahadeva/Sanjaya, looking specifically at the Mar 6 boundary.
3. **Schedule a "Mahabharata refactor" planning session** for the Sanjaya→Vyasa collapse described in §7.5 — likely 1 hour of planning + ~3 hours of execution; possibly 30–40% token reduction.
4. **Decide: stay on Agent SDK (your own infra) vs evaluate Managed Agents for one workflow** (e.g., the Yudhishthira weekly data analyses where Outcomes-style rubric grading would directly improve quality). Pricing is the gating question.
5. **Write your own `dreaming.skill`** — a weekly cron skill that reads `_audit/tool-log.jsonl` + recent `memory/` files, extracts patterns, deduplicates, and writes a `_audit/this-week.md` summary. You don't need Managed Agents to do this; you have all the primitives.
6. **In 4 weeks, re-run this research** to catch the next round of changes (Sonnet 4.7 if it ships, agent-teams docs, June 15 deprecations and credit-pool launch).
