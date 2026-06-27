# 🔬 Research Agent (Vidura) — Source-Disciplined Researcher

> Tier 0 · Mahabharat: Vidura, the wise counselor who tells truth to power
>
> Also addressed as **vidura** via the symlink `vidura.md → research-agent/agent.md`.

Thorough, source-disciplined researcher. Every claim is tied to a tier-tagged source (`[T1]` peer-reviewed / authoritative → `[T5]` avoid). Triangulates non-trivial claims across ≥2 independent sources, surfaces dissent, never fabricates citations.

The deployed agent runs on the **Hyperagent** platform. Local files document identity, methodology, and rules so Sanjaya can observe.

## Capabilities

- Adaptive output: chat markdown, persistent document, webpage artifact, slides, or table — picked per request.
- Source-tier badges on every cited source (`[T1]`–`[T5]`, plus `[stale]`, `[T4 — vendor]`, `[translated]`, `[single source]`, `[contested]`).
- Standard report shape: TL;DR → Key Findings → Detailed Analysis → Source Bibliography → Confidence → Gaps → Next Steps.
- Domain rules auto-load from `.claude/rules/` (add domain-specific `.md` files there to inject context automatically).
- Standing competitive-monitoring template at `docs/competitor_profiles/` (adapt to any domain via the schema in `.claude/templates/`).

## Files

| File / dir           | Purpose                                                     |
| -------------------- | ----------------------------------------------------------- |
| `agent.md`           | Identity + system prompt (Hyperagent platform format)       |
| `skill.md`           | Operational procedures for research workflows               |
| `README.md`          | This file                                                   |
| `CHANGELOG.md`       | Append-only agent-level history                             |
| `CLAUDE.md`          | Compact identity for Claude Code sessions in this dir       |
| `ARCHITECTURE.md`    | How the agent is organised on Hyperagent                    |
| `HANDOFF.md`         | Operating notes for handing off the agent                   |
| `docs/`              | Research outputs + competitor profiles + brand case studies |
| `.claude/rules/`     | Domain rules auto-loaded by the agent                       |
| `.mcp.json`          | MCP server config                                           |
| `.bundle-reference/` | Reference bundle (do not edit)                              |

## Upstream / Downstream

- **Upstream:** kartavya (and any other agent that delegates research)
- **Downstream:** Exa search/research/contents, WebSearch, WebFetch, Browser session (read-only)

## Watched by

- Sanjaya at `_meta/observer/journal/research-agent.md`

## See also

- `agent.md` — full system prompt, methodology, tier definitions, output format
- `skill.md` — operational procedures
- `CLAUDE.md` — compact identity for in-folder sessions
- `.claude/rules/source-tiers.md` — detailed source-classification guide
- `.claude/rules/source-tiers.md` — detailed source-classification guide (add domain rule files here as needed)
