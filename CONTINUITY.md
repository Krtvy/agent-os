# CONTINUITY.md — How this project survives a closed terminal

> Read this first if you're picking up the project after a break, after closing the terminal accidentally, or weeks from now and can't remember where you were.

Nothing in this project lives only in the terminal. Every decision, every file change, every agent action is persisted to one of seven layers below. If a terminal closes mid-work, the worst case is losing the last few minutes of unsaved reasoning — the structural state survives.

---

## The seven persistence layers (most reliable → most ephemeral)

### 1. Git history

The repo is git-tracked. Every commit is an immutable checkpoint.

```bash
git log --oneline -20      # recent commits
git show <hash>             # what changed in any commit
git diff HEAD~5..HEAD       # last 5 commits worth of changes
```

If everything else fails, `git log` and `git diff` reconstruct what happened. The tradeoff: only committed work persists here. Unsaved drafts don't.

### 2. The `_audit/` directory

Every major decision in this project is written to `_audit/<YYYY-MM-DD>_<topic>.md` at the moment of decision. As of 2026-05-12 there are 9 files spanning the multi-agent ecosystem build-out.

```bash
ls -t _audit/                                    # chronological view
cat _audit/README.md                             # index of all files + the instrumentation stance
cat _audit/$(ls -t _audit/ | head -1)            # most recent decision
```

The discipline: **every constitutional change, every phase application, every gap analysis lives here as a dated file**. The audit chain is permanent.

### 3. Agent CHANGELOGs

Each agent under `.claude/agents/<name>/CHANGELOG.md` records its own history append-only. Mirrors Bhishma R5 (journals are append-only) but at the agent-spec level.

```bash
for f in .claude/agents/*/CHANGELOG.md .claude/agents/_meta/*/CHANGELOG.md; do
  echo "=== $f ==="; tail -10 "$f"
done
```

Granular: what changed about this agent specifically, when.

### 4. Sanjaya journals

`_meta/observer/journal/<agent>.md` records what Sanjaya observed about each watched agent on each run. Append-only.

```bash
ls -la .claude/agents/_meta/observer/journal/
```

Behavioral history per agent.

### 5. Claude Code conversation transcripts

Claude Code itself saves every conversation:

```
~/.claude/projects/-Users-mosaic-projects-observer-test/
```

Use `/resume` inside Claude Code to pick up a prior conversation, or `--resume <session-id>` from the shell to resume by ID. This is the **closest thing to "save the whole terminal"** that exists — it covers the reasoning chain, not just the file changes.

**If your terminal closes:** open a new terminal, `cd` to this project, run `claude`, then type `/resume` to pick a recent session. The conversation history comes back.

### 6. Auto-memory

Cross-session facts about the user and project live at:

```
~/.claude/projects/-Users-mosaic-projects-observer-test/memory/
```

Auto-managed by Claude Code. Surfaces relevant memories in future sessions without you having to recall them. Not for state — for _facts and preferences_.

### 7. `/status` and `/checkpoint` slash commands

- **`/status`** — one-screen scannable summary of where the project is right now. Use first when picking up after a break.
- **`/checkpoint`** — writes a structured save-point file to `_audit/<YYYY-MM-DD>_checkpoint-<slug>.md` capturing what's in flight. Use when you're about to step away and want explicit closure on the current thread.
- **`/audit-now`** — fires Sahadeva's full weekly audit manually. Use when something feels off.

---

## The "I just opened the terminal, where am I?" procedure

1. `cd /Users/mosaic/projects/observer-test`
2. `claude` (start Claude Code)
3. Type `/status` — gives you the 30-second scan
4. If you want to continue a specific recent thread: type `/resume` and pick the session
5. If `/status` says there's an active phase or pending decision, read the `_audit/` file it points to

That's it. The continuity is built in; you just have to know to ask.

---

## Session-end auto-checkpoint

A `SessionEnd` hook at `lib/session-end-checkpoint.sh` writes a tiny `_audit/.last-session.md` file every time a Claude Code session closes cleanly. This is the **automatic** safety net for "I closed the terminal by mistake." Contents:

- Timestamp of session close
- Last few `_audit/` files at session start (what was already decided)
- Files modified during the session (via `git diff --name-only HEAD`)
- Whether Sanjaya / Sahadeva ran during the session

Read `_audit/.last-session.md` at the start of the next session for a quick "what was I doing yesterday" snapshot. The file is overwritten each session — it's the rolling "where I left off", not the historical record. (The historical record stays in the dated `_audit/` files.)

---

## What CANNOT be recovered

Be honest about the limits:

- **Unsaved file edits.** If you're editing a file in your local editor and the terminal closes before save, that's gone. Standard. Not specific to this project.
- **Reasoning that never made it to disk.** If Claude Code produces a brilliant analysis in chat and you close the terminal before it's written to a file, the transcript (layer 5) still has it but the file doesn't. `/checkpoint` is the manual way to lock it in.
- **Crontab on a different machine.** The `crontab -l` entries live on this Mac. If you switch machines, you'd need to re-install. The runner scripts they invoke are in the repo, so that's quick.
- **External-service state.** Hyperagent platform state, MCP-connected service state, etc. live elsewhere. This project's `agent.md` files are the source of truth for _spec_; the platforms have their own deployment lag (e.g., Vidura body reframe from this session still needs re-export to Hyperagent — watch-list item #5).

---

## Provenance

Document created 2026-05-12 00:40 IST during the continuity-concerns phase. Source: user concern about losing context across terminal closures. Companion artifacts: `lib/session-end-checkpoint.sh`, `.claude/skills/checkpoint/SKILL.md`, `.claude/skills/status/SKILL.md`.

This file lives at the **repo root** (not under `_audit/`) intentionally — it's a reference doc for the human, not a record of a decision.
