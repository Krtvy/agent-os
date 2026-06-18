# `_meta/` — Meta-tier agents

This directory holds agents that watch *other* agents. They do not perform end-user work; they observe, analyze, and propose changes to Tier-0 worker agents.

> **Install location:** This folder belongs at `.claude/agents/_meta/` in your repo. The bundle ships without the `.claude/agents/` prefix so it's easy to drop into any Claude Code project.

## Tiers

| Tier | Role | Examples |
|------|------|----------|
| **Tier 0** | Workers — do user-facing tasks | `code-reviewer/`, `researcher/`, `writer/` |
| **Tier 1** | Meta — observe Tier 0, propose skill.md changes | `_meta/observer/` |
| **Tier 2** | Conductor — coordinates Tier 1 agents (future) | `_meta/conductor/` (reserved) |

## Why this layout

- Tier-0 agents stay flat under `.claude/agents/` (Claude-Code-conventional, easy to scan).
- Tier-1+ agents cluster under `_meta/` so the hierarchy is visible at a glance.
- The `_` prefix sorts first in `ls`, making the meta layer obvious.
- Adding more tiers later (Tier 2 Conductor, Tier 3 Supervisor) requires no restructuring.

## Approval-gate philosophy

Every meta-agent here is bound by the same rule: **read-only on sibling agents until a human approves a change**. Meta-agents draft proposals; humans approve them; only then can the meta-agent apply the change.

This rule scales up the tiers — a future Conductor watches the Observer the same way the Observer watches workers, and never modifies the Observer without your approval.
