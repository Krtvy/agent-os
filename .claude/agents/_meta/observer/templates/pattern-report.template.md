---
report_id: <agent>-<YYYY-MM-DD>
agent: <target-agent-name>
mode: bootstrap            # bootstrap | adaptation
window_start: <YYYY-MM-DD>
window_end: <YYYY-MM-DD>
runs_observed: <int>
days_observed: <int>
data_sources_used: [transcripts, tool_calls, errors, outputs, git_history]
---

# Pattern Report: <target-agent-name>

A snapshot of what the observer has seen for this agent over the observation window. This report is the evidence base for the proposal that follows.

---

## 1. Recurring task patterns

| # | Pattern | Count | Confidence | Example runs |
|---|---------|-------|------------|--------------|
| 1 | <e.g. "summarize a git diff into a release note"> | 12 | high | r-0429-01, r-0501-03, r-0503-07 |
| 2 | <pattern> | 7 | medium | ... |

---

## 2. Tool usage

| Tool | Invocations | Common preceding tools | Common arguments |
|------|-------------|------------------------|------------------|
| Bash | 47 | Read, Glob | git log, git diff |
| Read | 38 | Glob | .md files |

### Tool sequences (n-grams ≥ 3 occurrences)
- Glob → Read → Edit (15×)
- Bash → Read → Write (8×)

---

## 3. Failure patterns

| # | Error category | Count | First seen | Sample message |
|---|----------------|-------|------------|----------------|
| 1 | <e.g. "missing file path"> | 5 | 2026-04-29 | "ENOENT: no such file or directory" |

---

## 4. Drift signals
*(Adaptation mode only — leave blank in Bootstrap mode)*

### 4a. Undocumented behavior
> Behaviors observed ≥3 times that are NOT in the current `skill.md`.
- ...

### 4b. Documented-but-unused
> Skills described in `skill.md` that were NOT invoked in this window.
- ...

### 4c. Errors suggesting missing skill
> Recurring failures that look like a missing capability.
- ...

---

## 5. Notes & caveats
- Data gaps in the window? List them here.
- Any anomalies the observer can't explain? Flag here for human eyes.
