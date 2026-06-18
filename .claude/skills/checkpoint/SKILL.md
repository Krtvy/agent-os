---
name: checkpoint
description: Write a structured save-point capturing what's in flight RIGHT NOW so the next session can pick up cleanly. Use when about to step away mid-task, when a phase completes, or any time the user wants explicit closure on a thread before context might be lost. Invoke when the user types `/checkpoint` or asks to "save state" / "checkpoint" / "lock in where we are".
---

# /checkpoint — Lock in current state

## What this skill does

Writes a single markdown file to `_audit/<YYYY-MM-DD>_checkpoint-<slug>.md` summarising what's actively in flight, what was just decided, and what to resume on. Different from `/status` (read-only snapshot) — `/checkpoint` is **write**, and the file becomes part of the permanent audit chain.

## Procedure

1. **Gather signal in parallel.**

   ```bash
   git status --short                              # what's modified locally
   git log --oneline -5                            # recent commits
   ls -t _audit/*.md | head -3                     # recent decisions
   crontab -l 2>/dev/null | grep observer-test     # scheduled work
   ```

2. **Ask the user (one short question) what to name the checkpoint slug.** Examples: `mid-vidura-rewrite`, `before-sahadeva-first-run`, `end-of-day-2026-05-12`. Keep it ≤30 chars. If the user is in a hurry or doesn't reply, default to `<HHMM>-snapshot`.

3. **Compose the checkpoint file** with sections:

   ```markdown
   # Checkpoint — <YYYY-MM-DD> <HH:MM> IST — <slug>

   > Save-point written at user request. Captures what's in flight at this moment so the next session resumes cleanly.

   ## What's in flight

   <one to three paragraphs: what was being worked on, why, what's left to do.
   Be specific — file paths, function names, decision points. Pretend you're
   leaving a note for a colleague who'll pick this up tomorrow with no context.>

   ## What was just decided (last 24 hours)

   - <latest `_audit/` file name>: <one-line summary>
   - <previous `_audit/` file>: <one-line summary>
   - <previous>: <one-line>

   ## Files currently modified (uncommitted)
   ```

   <output of `git status --short`>

   ```

   ## Files modified in the last commit

   ```

   <output of `git show --stat HEAD`>

   ```

   ## Open questions or pending decisions

   <bullet list — explicit things the next session needs to resolve.
    Empty list is fine; say "none" rather than fabricate.>

   ## Suggested first action next session

   <one-line: the literal first thing to do on resume. e.g., "Read this file, then re-read `_audit/2026-05-12_hooks-wired.md` § Watch-list."

   ## Provenance

   Checkpoint written 2026-05-12 HH:MM IST via `/checkpoint`. User-directed save-point.
   ```

4. **Save to** `_audit/<YYYY-MM-DD>_checkpoint-<slug>.md`. Confirm to the user with the absolute path.

5. **Update `_audit/README.md` file index** to include this checkpoint as a new row. Mark status `checkpoint`.

## When NOT to invoke

- **Trivially short context.** If literally one line of context exists, the user can just type it into the next session. Don't bloat the audit chain with "I am about to read a file" checkpoints.
- **Pure read-only sessions.** If nothing was modified and no decision was made, a checkpoint adds no value.
- **Right after another checkpoint.** If `_audit/` already has a checkpoint from this session within the last 30 minutes, ask the user if they want to overwrite (delete + replace) rather than create N nearly-identical files.

## Hard rules

- **Never invent the "what's in flight" content.** Only describe what you actually have evidence of from the current session's conversation and the file system. Fabricated continuity notes are worse than missing ones.
- **Append-only at the audit level.** Once written, the checkpoint file is not edited in place. If something changes, write a new checkpoint with the same date, a different time-suffix slug.
- **Do not run any agents.** This skill writes one file. It does not invoke Claude Code agents, does not fire cron-style work, does not modify Bhishma.

## Notes for the assistant invoking this

- The user is asking for closure on a thread. Mirror that posture: brief, decisive, specific. Don't write a 2000-word checkpoint when 200 words capture what matters.
- If the user has not explicitly named what's in flight, ask **one** focused question to learn it. Then save.
- After saving, give the user **two** lines: the file path, and the literal command to read the checkpoint next session (`cat _audit/<file>`).

## Provenance

Skill added 2026-05-12 00:40 IST in the continuity-concerns phase. Source: user concern about losing context across terminal closures. Companion to `CONTINUITY.md` (project-root doc), `/status` skill (read snapshot), and `lib/session-end-checkpoint.sh` (auto checkpoint on session close). Removal: `rm -r .claude/skills/checkpoint/`.
