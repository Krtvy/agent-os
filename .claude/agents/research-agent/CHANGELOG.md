# Research Agent (Vidura) — Changelog

Append-only log of **agent-level** changes (identity, file structure, scope, tooling). Skill-level changes track in `skill.md` § "Change log".

## 2026-05-11

- Added `README.md`, `CHANGELOG.md`, and the missing `skill.md` per agent-template standard.
- Cleanup pass: removed dev cruft (`agent.md.bak`, `docs.zip`, `research-agent-complete.tar.gz`, `.DS_Store`). Moved `2026-05-06_rootlab_growth_playbook.html` into `docs/` where the rest of the research deliverables live.
- **Self-audit fix I1+I3+I4.** Frontmatter standardised: `tools:` converted from CSV scalar to list form; `model:` expanded from `sonnet` to `claude-opus-4-6` (matching the model the body advertises); added missing keys (`icon`, `effort`, `runtime`, `hyperagent_agent_id`, `read_scope`, `write_scope`, `upstream`, `downstream`, `mcps`). Scope lifted conservatively from existing prose.
- **Phase 1 G8 — Vidura reframe applied.** `agent.md` body fully rewritten in Mahabharat shape:
  - Frontmatter `name:` renamed `research-agent` → `vidura`. Added `aliases: [research-agent]` so the historical symlink remains machine-readable and Sanjaya's existing journal at `_meta/observer/journal/research-agent.md` continues to apply (directory name unchanged).
  - Body title `# Research Agent — Agent Configuration` → `# Vidura — Tier-0 Researcher`, matching Arjuna/Hanuman/Nakula/Narada/Yudhishthira shape.
  - New `## Your character` section grounding Vidura as the wise counselor at Hastinapura — source-disciplined, dissent-surfacing, refusing to soften facts to gain compliance.
  - New `## Failure modes` section: citation fabrication under social pressure, consensus seduction, tier inflation, bluntness alienating the listener.
  - System-prompt content (research loop, source tiers, output format, hard rules, tone) preserved verbatim — no behavioural change.
  - Hyperagent deployment metadata (tools enabled, model/learning settings, attached context) moved into "Appendix A — Hyperagent deployment metadata."
  - Source: `_audit/2026-05-11_gap-analysis.md` G8 + playbook `2026-05-11_multi-agent-playbook.md`. Authorisation: Kartavya selected "approve all four" via AskUserQuestion at 22:55 IST.
  - **Re-deploy.** The system prompt deployed to Hyperagent should be re-exported from this updated body so the platform reflects the Vidura framing. Until that happens, the body here is authoritative and Hyperagent is a deployment lag.

## 2026-05-07

- Aliased as **vidura** via `.claude/agents/vidura.md → research-agent/agent.md` (consistent with Mahabharat naming across the ecosystem).

## 2026-05-06

- Bootstrap — initial agent definition committed. Hyperagent agent ID `cmoj3vy4005lk07adlyj2e8l0`.
