# Archive

Backups of files deleted from active locations, kept in this repo so deletions are reversible.

## `personal-skills-pre-delete-2026-05-09.tar.gz`

Snapshot of three personal skills authored by Drona with Kartavya Joshi, taken just before deletion from `~/.claude/skills/`.

**Contents:**

- `sanjaya/SKILL.md` — Rootlabs creator-ops advisor (15.6 KB)
- `drona-teaching/SKILL.md` — phase-gated teaching pattern (6.5 KB)
- `narada/SKILL.md` — daily AI update drafter for Mayank (10.0 KB)

**Why deleted:** Kartavya consolidated — drona-teaching's research/teaching role overlaps with the project's `research-agent`, and the other two were no longer needed in the active skill set.

**To restore any of them:**

```bash
cd ~/projects/observer-test/archive
tar -xzf personal-skills-pre-delete-2026-05-09.tar.gz -C ~/.claude/skills/
```

That extracts the three folders back into the active skills location with their original SKILL.md files.

**Date deleted:** 2026-05-09
