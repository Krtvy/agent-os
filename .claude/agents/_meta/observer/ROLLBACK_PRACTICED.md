# Rollback drill: PASSED

Date: 2026-05-08
Repo: ~/projects/observer-test
Baseline commit: 4a331bf (initial install)
Preflight commit: 6846120 (frontmatter + lockfile)

Drill performed:

1. Appended `OBSERVER_BROKE_THIS` to `.claude/agents/research-agent/agent.md`
2. `git diff` confirmed the corruption was tracked
3. `git checkout .claude/agents/research-agent/agent.md` reverted cleanly
4. `grep OBSERVER_BROKE_THIS` returned no matches

The kill-switch works. If a future Observer-applied diff misfires, the recovery path is:

```bash
cd ~/projects/observer-test
git diff .claude/agents/<agent>/skill.md   # see what Observer changed
git checkout .claude/agents/<agent>/skill.md   # revert to last committed state
```

If you need to revert the Observer install itself, every file Observer touches is under
`.claude/agents/_meta/observer/` (write scope) or a worker's `skill.md` (post-approval only).
None of those land outside the repo, so `git reset --hard <commit>` always pulls you back to
a known-good state.
