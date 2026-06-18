---
agent: <target-agent-name>
created: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD>
mode: bootstrap # bootstrap | adaptation
runs_observed: 0
days_observed: 0
threshold_reached: false
open_proposal_id: null
rejection_cooldowns: {} # { proposal_topic: runs_remaining }
---

# Journal: <target-agent-name>

> Running log of observations. Append-only. Read top-down for newest-first if helpful, but new entries go at the END of the Daily Entries section.

## Daily Entries

<!--
One entry per observed day. Skip days with no activity (and note it in the next entry's `notes:` field).

Entry shape:

### YYYY-MM-DD
- runs_today: <int>
- new_patterns: ["short pattern label", ...]
- new_errors: ["short error label", ...]
- mast_codes: [FM-1.1, FM-2.4, ...]   # see skill.md § mast_classification — leave [] if no failure mode triggered today
- notes: free text (1–3 lines)
-->

### <YYYY-MM-DD>

- runs_today: 0
- new_patterns: []
- new_errors: []
- mast_codes: []
- notes: First observation day. No prior data.

## Calibration

<!--
Append-only record of accepted/rejected proposals and what was learned.

Entry shape:

### YYYY-MM-DD — Proposal <id>
- trigger: what observation drove this
- outcome: applied | rejected
- reason (if any from human): ...
- lesson: 1–2 sentences on what this teaches future proposals
-->
