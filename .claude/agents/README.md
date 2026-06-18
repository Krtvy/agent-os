# Agent location convention

All Claude Code agents on this system are observed by the Observer
(Tier-1 meta-agent at `_meta/observer/`).

**Rule: every agent lives here, under `.claude/agents/<agent-name>/`.**

To add a new agent:
1. `mkdir -p .claude/agents/<name>`
2. Add `agent.md` (required), optionally `skill.md`
3. Observer auto-discovers on next nightly run — no config change needed
4. Bootstrap threshold: 10 days or 20 runs — first proposal lands then

Do NOT create agents at `~/<name>/` or `~/Documents/...` — they will not be
observed. If you find an agent outside this directory, move it here.
