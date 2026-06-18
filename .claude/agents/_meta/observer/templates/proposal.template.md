---
id: <YYYYMMDD>-<agent>-<short-slug>
target_agent: <name>
target_file: .claude/agents/<name>/skill.md
mode: bootstrap            # bootstrap | adaptation
created_at: <ISO-8601>
confidence: medium         # low | medium | high
status: pending            # pending | approved | applied | rejected
applied_at: null
report_id: <agent>-<YYYY-MM-DD>
---

# Proposal: <short, action-oriented title>

A proposed change to `<target_file>`. Read the linked Pattern Report first; that's the evidence. This document is the *recommended action*.

---

## Pattern Report
**See:** `reports/<report_id>.md`

(One-paragraph summary of what was observed and why it warrants this change.)

---

## Proposed change

```diff
--- a/.claude/agents/<name>/skill.md
+++ b/.claude/agents/<name>/skill.md
@@ ...
- (lines being removed)
+ (lines being added)
```

> For Bootstrap mode (no existing skill.md), the diff is against `/dev/null` and creates the file.

---

## Rationale

- **<observation 1>** — supported by run IDs `r-0429-01`, `r-0501-03`, `r-0503-07` (see Pattern Report §1)
- **<observation 2>** — supported by ...
- **<observation 3>** — supported by ...

(3–5 bullets. Each must cite specific observations.)

---

## Risk

What could go wrong if this is approved blindly:
- ...
- ...

---

## How to act on this proposal

| Action | How |
|--------|-----|
| Approve | `mv proposals/<id>.md approved/<id>.md` (or set `status: approved` above) |
| Reject  | `mv proposals/<id>.md rejected/<id>.md` (or set `status: rejected` above) |
| Edit    | Change the diff above, leave the file in `proposals/`. Observer re-evaluates next run. |
