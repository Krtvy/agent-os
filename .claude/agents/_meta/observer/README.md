# Observer Agent

A **Tier-1 meta-agent** for Claude Code. It watches your Tier-0 worker agents under `.claude/agents/` and proposes `skill.md` changes for your approval. It never modifies a worker's files until you explicitly approve a proposal.

---

## How it operates

| Mode | When | Trigger | Output |
|------|------|---------|--------|
| **Bootstrap** | Target has NO `skill.md` | 10 days OR 20 runs (whichever first) | A drafted initial `skill.md` |
| **Adaptation** | Target HAS a `skill.md` | 18 days OR 40 runs (whichever first) | Proposed additions, edits, or deprecations |

The observer reads:
- Conversation transcripts / chat logs
- Output files the agent produced
- Git commit history of agent files
- Existing `skill.md` and config files
- Tool-call logs (tool name + args)
- Error logs / failure reports

---

## Install

1. **Copy** the entire `_meta/` folder into your repo's `.claude/agents/`:
   ```
   cp -r _meta /path/to/your/repo/.claude/agents/
   ```
2. **Edit** `_meta/observer/config.yml`:
   - Set `watched_agents:` (or leave `[]` to observe all non-meta agents).
   - Confirm `input_sources:` paths match your actual log layout.
3. **Make the script executable:**
   ```
   chmod +x _meta/observer/run_observer.sh
   ```
4. **Optional — schedule via cron:**
   ```
   # Daily at 02:00 UTC
   0 2 * * * cd /path/to/repo && .claude/agents/_meta/observer/run_observer.sh >> .claude/agents/_meta/observer/run.log 2>&1
   ```

---

## Daily flow

```
┌──────────────────────────────────────────────────────────────┐
│                   Observer daily run cycle                   │
└──────────────────────────────────────────────────────────────┘

1. run_observer.sh fires (cron or manual)
2. Observer reads config.yml → list of watched agents
3. Poll for approvals first:
     proposals/<id>.md moved to approved/  → apply diff to skill.md
     proposals/<id>.md moved to rejected/  → log calibration note
4. For each watched agent:
     - ingest new logs/outputs/git history since last journal entry
     - append a dated journal entry
     - update counters (days_observed, runs_observed)
     - if threshold reached AND no open proposal:
         generate Pattern Report → reports/<agent>-<date>.md
         generate Proposal       → proposals/<id>.md
5. Print run summary
```

---

## Approval flow (this is the important one)

When you see a new proposal in `_meta/observer/proposals/`:

1. **Read it.** It contains: a link to the Pattern Report (what was observed), the proposed unified diff, rationale bullets (each citing observations), and a risk note.

2. **Decide.** One of three actions:

   | Action | How |
   |--------|-----|
   | **Approve** | `mv proposals/<id>.md approved/<id>.md` (or change `status: pending` → `status: approved` in the file) |
   | **Reject** | `mv proposals/<id>.md rejected/<id>.md` (or change `status: pending` → `status: rejected`) |
   | **Edit & resubmit** | Change the diff in the proposal file, leave it in `proposals/`. The observer will re-evaluate next run. |

3. **Next run** the observer will:
   - On approval: apply the diff to the target's `skill.md`, update proposal frontmatter to `status: applied`, append a calibration note.
   - On rejection: append a calibration note, set a 5-run cooldown so it doesn't immediately re-propose the same thing.

---

## Files in this directory

```
_meta/observer/
├── agent.md                    # Observer's identity & system prompt (the agent itself)
├── skill.md                    # Observer's own skills (what it knows how to do)
├── config.yml                  # Thresholds, watched agents, paths
├── run_observer.sh             # Invocation script (manual + cron)
├── README.md                   # This file
├── templates/
│   ├── journal.template.md         # Shape of journal/<agent>.md
│   ├── pattern-report.template.md  # Shape of reports/<agent>-<date>.md
│   └── proposal.template.md        # Shape of proposals/<id>.md
├── journal/                    # One running journal per watched agent
├── reports/                    # Pattern reports, dated
├── proposals/                  # Awaiting your decision
├── approved/                   # Archive of accepted proposals
└── rejected/                   # Archive of rejected proposals
```

---

## Hierarchy & future-proofing

This agent is **Tier 1**. The slot for **Tier 2 (Conductor)** is reserved at `_meta/conductor/` — see that folder's README for what a Conductor would do.

The observer's outputs (journal, reports, proposals) all use **YAML frontmatter + markdown** so a future Tier-2 agent can parse them programmatically with no changes to this layer.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| No journal entries appearing | `input_sources` paths don't match your logs | Edit `config.yml`, confirm paths exist |
| Threshold never reached | `runs_observed` not incrementing | Check that transcripts/tool logs land in the configured paths |
| Approved proposal not applied | Diff doesn't apply cleanly to current `skill.md` | Look at `journal/_observer-self.md` for the conflict note; edit the proposal and re-approve |
| Same change keeps getting re-proposed | Rejection cooldown not honored | Check `journal/<agent>.md` `## Calibration` for the rejection record |
| Observer wants to watch itself | Excluded by `excluded_agents: [_meta]` | Already prevented; if you see this, the config was edited |

---

## Design rules (don't change without thinking)

1. **Read-only on Tier-0 until approval.** This is the safety contract.
2. **One open proposal per agent at a time.** Prevents stacking conflicting changes.
3. **Confidence ≥ 3 supporting observations.** Filters noise.
4. **5-run cooldown after rejection.** Stops re-litigating the same idea.
5. **Calibration journal is the only memory.** Read it before drafting new proposals.

If you find yourself wanting to break one of these, that's probably a sign you want a Tier-2 Conductor instead.
