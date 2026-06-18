---
name: status
description: Show the current state of the observer-test ecosystem — last decision, pending phases, next cron firings, Sahadeva inbox, watch-list items. Use when picking up the project after a break, when a session was closed unexpectedly, or any time the user asks "where am I" / "what's next" / "what was I doing". Invoke when the user types `/status`.
---

# /status — Where am I in this ecosystem?

## What this skill does

Read-only snapshot of where the project stands right now. Designed to be scannable in 30 seconds. Reads from existing artifacts; does not modify anything.

## Procedure

Gather these signals in parallel via Bash + Read, then render the report:

### 1. Most recent decision

```bash
ls -t _audit/*.md | head -1
```

Read its frontmatter / first paragraph to get the one-line summary.

### 2. Phase state

Walk `_audit/` chronologically and find the latest `*-applied.md`, `post-phase-*-audit.md`, or `*-built.md` / `*-scheduled.md` / `*-wired.md` file. Extract the sign-off table from it — that's the canonical phase state.

### 3. Watch-list items

Read the most recent `_audit/*audit*.md` or `_audit/*-applied.md` file and pull out the §"Watch-list" or §"Open recommendations" section. Show only items still active (status: `Unchanged` or empty).

### 4. Next cron firings

```bash
crontab -l 2>/dev/null | grep -E "observer-test|run_(observer|sahadeva).sh"
```

Translate cron syntax to human-readable next-firing time. For each entry, compute the next scheduled firing relative to `date`.

### 5. Sahadeva inbox state

```bash
test -f .claude/agents/_meta/audit/inbox.md && wc -l .claude/agents/_meta/audit/inbox.md
test -f .claude/agents/_meta/audit/inbox.md && awk '/critical/{c++} END{print c+0}' .claude/agents/_meta/audit/inbox.md
```

If criticals exist, surface them. If clear, say so.

### 6. Most recent Sahadeva report (if any)

```bash
ls -t .claude/agents/_meta/audit/reports/*.md 2>/dev/null | head -1
```

If a report exists, read its summary verdict (green/amber/red) and count of findings.

### 7. Most recent Sanjaya journal activity

```bash
ls -t .claude/agents/_meta/observer/journal/*.md 2>/dev/null | head -3
```

Show last 3 modified journals and the date of each.

### 8. Recent git activity (optional, only if it adds context)

```bash
git log --oneline -5
```

## Output format

Render the report as a single scrollable block. Target length: under one screen.

```
📋 observer-test · status as of <ISO timestamp>

LAST DECISION
  <YYYY-MM-DD>_<topic>.md — <one-line summary>

PHASE STATE
  Phase 1 (Mahabharat coherence + R23)         ✅ Applied
  Phase 2 (runtime backstops + Sahadeva test)  ✅ Applied
  Phase 3 — G5/G1C (traces, hooks)             ✅ Built (wired 2026-05-12)
  Runners-build (Sahadeva + Sanjaya wiring)    ✅ Applied
  Cron + Hooks                                 ✅ Active
  Phase 3 — G7 (journal compaction)            ⏳ Trigger: any journal >200 KB
  Phase 4 — G1B (semantic validator)           ⏳ Trigger: 3 weeks Sahadeva reports

NEXT CRON FIRINGS (IST)
  Sanjaya   daily   02:00         — next: <weekday YYYY-MM-DD 02:00>
  Sahadeva  Sunday  10:00         — next: <weekday YYYY-MM-DD 10:00>

SAHADEVA INBOX
  <count> critical · <count> high · last appended <ISO>
  OR: inbox clear

LAST SAHADEVA REPORT
  reports/<YYYY-WW>.md · verdict: <green/amber/red>
  OR: none yet — first run <date>

SANJAYA RECENT JOURNALS
  arjuna.md         — last updated <date>
  hanuman.md        — last updated <date>
  ...

WATCH-LIST (active items)
  #N — <one-liner>
  #N — <one-liner>
  ...

WHAT TO LOOK AT FIRST
  <one-paragraph orientation: if inbox has criticals, point there.
   If no Sahadeva report yet, point at "wait for cron". If watch-list has
   high-priority items, name them.>
```

## When NOT to invoke

- **Mid-task.** If the user is in the middle of a focused operation, `/status` interrupts. Use only at session-boundary moments ("just got back", "where were we").
- **As a substitute for reading the actual audit files.** `/status` is a 30-second scan; the audit files are the source of truth for the decisions themselves.

## Hard rules

- **Read-only.** This skill modifies nothing. No edits, no writes, no file creations.
- **No interpretation beyond what's in the artifacts.** If the watch-list says item X is open, report it open. Don't speculate about whether it's still relevant.
- **Honest absences.** If Sahadeva has never run, say so. If the inbox doesn't exist yet, say so. Don't fabricate "all clear" when the underlying data isn't there.

## Notes for the assistant invoking this

- Skill output goes to the chat; the user reads it. Make it scannable — use the block format above, not paragraphs.
- If the user clearly wants more depth on one section, follow up after the status block — don't try to cram detail into the snapshot itself.
- Computing "next firing" for cron entries on a 5-field schedule is straightforward in Bash but tedious. If exact next-firing is hard, fall back to "Sunday 10:00 IST" (human-readable cadence) rather than a wrong date.

## Provenance

Skill added 2026-05-12 00:17 IST as part of the plugins phase. Source: user concern about session resumption ("if i by mistakenly close my terminal i would look my progress"). Companion to `lib/session-start-greeting.sh` which surfaces a 3-line subset of the same info on every session start. Removal: `rm -r .claude/skills/status/`.
