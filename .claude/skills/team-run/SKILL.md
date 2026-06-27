---
name: team-run
version: 1.0.0
description: Coordinate all agent-os agents as a team on a single task. Agents pass work to each other through a shared session workspace. Use when a task needs multiple agents working together.
triggers:
  - run the team
  - coordinate agents
  - team run
  - all agents
  - full pipeline
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - AskUserQuestion
---

# /team-run — Full Agent Team Coordination

## What this skill does

Runs all relevant agents on a single task in a coordinated pipeline. Each agent reads the previous agent's output before starting. All outputs go to a shared session workspace so nothing is lost.

## The Pipeline

```
Task Input
    │
    ▼
Yudhishthira  → Is this worth doing? What's the strategic angle?
    │             Writes: SESSION/01-strategy.md
    ▼
Vidura         → What's the technical approach? What resources/docs exist?
    │             Writes: SESSION/02-research.md
    ▼
Hanuman        → What already exists? What should we know before building?
    │             Writes: SESSION/03-recon.md
    ▼
Arjuna         → Execute. Build it. Call the APIs. Make it happen.
    │             Writes: SESSION/04-execution.md
    ▼
Narada         → Draft the output. Write the announcement, docs, or message.
    │             Writes: SESSION/05-draft.md
    ▼
Nakula         → What should be scheduled? What repeats?
    │             Writes: SESSION/06-schedule.md
    ▼
Sanjaya        → Journal this session. What was done? What to watch?
                  Writes: SESSION/07-journal.md
```

## Procedure

### Step 1 — Create session workspace

```bash
SESSION_ID="team-$(date +%Y%m%d-%H%M%S)"
SESSION_DIR="$HOME/.agent-os/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"
echo "Session: $SESSION_DIR"
echo "$TASK" > "$SESSION_DIR/00-task.md"
```

### Step 2 — Ask what the task is (if not already specified)

If the user hasn't described the task, ask:
"What do you want the team to work on? Describe it in 1-3 sentences."

### Step 3 — Run each agent in sequence

For each agent, read ALL previous outputs from the session directory before starting.

**Yudhishthira (Strategy):**
Read: 00-task.md
Question to answer: "Is this worth doing? What's the priority? What would success look like? What are the risks?"
Write to: SESSION/01-strategy.md

**Vidura (Research):**
Read: 00-task.md + 01-strategy.md
Question to answer: "What technical approach should we use? What docs/resources are most relevant? What are the options and tradeoffs?"
Write to: SESSION/02-research.md

**Hanuman (Recon):**
Read: 00-task.md + 01-strategy.md + 02-research.md
Question to answer: "What already exists that's similar? What can we learn from the top GitHub repos? What should we know before building?"
Use: WebSearch, WebFetch, mcp__agent_reach__*
Write to: SESSION/03-recon.md

**Arjuna (Execute):**
Read: 00-task.md + 01-strategy.md + 02-research.md + 03-recon.md
Action: Execute the task. Make API calls. Run scripts. Build the thing.
Write to: SESSION/04-execution.md

**Narada (Draft):**
Read: 00-task.md + 04-execution.md
Action: Draft any needed output — announcement, documentation, email, message.
Write to: SESSION/05-draft.md

**Nakula (Schedule):**
Read: 00-task.md + 04-execution.md
Question to answer: "What from this task should repeat? What cron jobs or reminders are needed?"
Write to: SESSION/06-schedule.md

**Sanjaya (Journal):**
Read: ALL files in session directory
Action: Write a complete journal of this session — what was done, what worked, what to watch, what proposals to make.
Write to: SESSION/07-journal.md

### Step 4 — Summary

After all agents complete, print:
```
Team session complete: $SESSION_ID
─────────────────────────────────────
Strategy:  SESSION/01-strategy.md
Research:  SESSION/02-research.md
Recon:     SESSION/03-recon.md
Execution: SESSION/04-execution.md
Draft:     SESSION/05-draft.md
Schedule:  SESSION/06-schedule.md
Journal:   SESSION/07-journal.md

Key outcome: [one line from 04-execution.md]
Next action: [one line from 07-journal.md]
```

## Which agents to skip

Not every task needs every agent. Use judgment:
- Skip Hanuman if no recon is needed (internal tasks)
- Skip Narada if no communication output is needed
- Skip Nakula if nothing should repeat
- Always run Yudhishthira, Vidura, Arjuna, Sanjaya

## Session persistence

All sessions are stored at `~/.agent-os/sessions/`. Each has a unique timestamp ID. The next session can reference previous sessions:
```bash
ls ~/.agent-os/sessions/
```
