# Trace Event Schema — `lib/trace-schema.md`

> JSON schema for the machine-readable traces that sit alongside Sanjaya's narrative journals. Consumed by Sahadeva's P5 (quantitative trend audit) and P10 (adversarial test-set evaluation).

**Phase 3 G5.** Designed against the playbook's "you cannot debug what you can't replay" finding (`_audit/2026-05-11_multi-agent-playbook.md` §2; OpenTelemetry-style span discipline endorsed at T2). The narrative journal remains the trust layer for human review; the trace is the workflow layer for automated audit.

---

## Storage layout

```
_meta/observer/traces/
├── arjuna/
│   ├── 2026-05-12-arjuna-001.json
│   └── 2026-05-12-arjuna-002.json
├── hanuman/
│   └── 2026-05-12-hanuman-001.json
└── ...
```

One file per agent run. Filename pattern: `<YYYY-MM-DD>-<agent>-<sequence>.json`. Append-only at the directory level (Bhishma R5 applied to traces).

Each trace is a single JSON object (not JSONL — the whole run is one document).

---

## Schema (v1, 2026-05-11)

```json
{
  "$schema": "lib/trace-schema.md#v1",
  "run_id": "<YYYY-MM-DD>-<agent>-<sequence>",
  "agent_name": "<canonical name from agent.md frontmatter>",
  "tier": 0,
  "parent_run_id": null,
  "bhishma_hash": "<SHA-256 of bhishma.md loaded at session start>",
  "started_at": "<ISO 8601 UTC>",
  "ended_at": "<ISO 8601 UTC>",
  "duration_ms": 0,
  "tool_calls": [
    {
      "seq": 0,
      "tool_name": "Read | Write | Edit | Bash | WebFetch | ...",
      "tool_input_summary": "<short sanitized description; NOT the full payload>",
      "target_path": "<path if write-shaped, else null>",
      "tokens_in": 0,
      "tokens_out": 0,
      "duration_ms": 0,
      "verdict": "succeeded | failed | bhishma_blocked",
      "block_rule": "<R-rule cited if bhishma_blocked, else null>",
      "started_at": "<ISO 8601 UTC>"
    }
  ],
  "decision_points": [
    {
      "seq": 0,
      "description": "<one-line: what was decided>",
      "choice_made": "<the chosen path>",
      "alternatives_considered": [],
      "timestamp": "<ISO 8601 UTC>"
    }
  ],
  "mast_codes": [],
  "bhishma_blocks": [
    {
      "rule": "R3",
      "attempted_action": "<one-line description>",
      "timestamp": "<ISO 8601 UTC>"
    }
  ],
  "tokens_total": 0,
  "cost_usd": 0.0,
  "final_outcome": "completed | errored | blocked",
  "error": null
}
```

### Field semantics

| Field                             | Purpose                                                                                                                                                                                                                              | Required               |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| `run_id`                          | Stable identifier; matches the run_id in `logs/<agent>/` and Sanjaya's journal                                                                                                                                                       | ✓                      |
| `agent_name`                      | Canonical name from `agent.md` frontmatter (e.g. `vidura`, not `research-agent`)                                                                                                                                                     | ✓                      |
| `tier`                            | 0 / 1 / 2 / "audit" — denormalised from `agent.md` for query convenience                                                                                                                                                             | ✓                      |
| `parent_run_id`                   | If this run was invoked by another (legitimately, per Bhishma R8 — i.e. Sanjaya→runner, not Tier-0→Tier-0). `null` for top-level invocations                                                                                         | optional               |
| `bhishma_hash`                    | SHA-256 of `bhishma.md` loaded at session start. Sahadeva P2 cross-checks this                                                                                                                                                       | ✓                      |
| `tool_calls[].tool_input_summary` | Short description, **not the full payload**. Full payload lives in the narrative journal or in `logs/`. Purpose: the trace stays small enough to aggregate across thousands of runs                                                  | ✓                      |
| `tool_calls[].target_path`        | The filesystem path for write-shaped tools. Used by Sahadeva's `write_scope` retroactive audit                                                                                                                                       | conditional            |
| `tool_calls[].verdict`            | `bhishma_blocked` populates only when `bhishma-check.sh` denied the call; the trace records the _attempt_ so Sahadeva can detect repeated attempts (which would themselves be a drift signal)                                        | ✓                      |
| `tool_calls[].block_rule`         | The R-rule cited by `bhishma-check.sh` when blocking. Used by Sahadeva P4                                                                                                                                                            | conditional            |
| `decision_points`                 | Branches the agent took explicitly. Sparse — only meaningful choices, not every reasoning step. Compatible with the playbook's "CoT monitorability is fragile" guidance — we record what was _decided_, not the full reasoning chain | optional               |
| `mast_codes`                      | Failure-mode codes classified by Sanjaya (Tier-1) when reviewing this trace. Empty on first write; populated when Sanjaya journals the run                                                                                           | optional               |
| `bhishma_blocks`                  | Aggregated for fast querying. Even though each block also appears in `tool_calls[].verdict=bhishma_blocked`, surfacing them here lets Sahadeva count without iterating tool calls                                                    | ✓ (array can be empty) |
| `cost_usd`                        | Optional. Required when the underlying provider returns it; null otherwise. Sahadeva's P5 token/cost trend audit consumes this                                                                                                       | optional               |
| `final_outcome`                   | `blocked` means the run terminated because Bhishma fired and there was no recovery path                                                                                                                                              | ✓                      |

### Field sanitisation rules

- Never put credentials, tokens, or full API keys in `tool_input_summary`.
- Never put PII in `decision_points[].description`.
- File contents go to logs, not to the trace. The trace is for _shape_, not _substance_.
- If a tool's output is >1 KB, summarise to a single sentence + a pointer (`output_ref: logs/<agent>/<run_id>.log`).

---

## Example trace (synthetic)

```json
{
  "$schema": "lib/trace-schema.md#v1",
  "run_id": "2026-05-12-sanjaya-001",
  "agent_name": "sanjaya",
  "tier": 1,
  "parent_run_id": null,
  "bhishma_hash": "a7f3...",
  "started_at": "2026-05-12T02:00:14Z",
  "ended_at": "2026-05-12T02:14:33Z",
  "duration_ms": 859000,
  "tool_calls": [
    {
      "seq": 0,
      "tool_name": "Read",
      "tool_input_summary": "read bhishma.md",
      "target_path": null,
      "tokens_in": 50,
      "tokens_out": 2400,
      "duration_ms": 80,
      "verdict": "succeeded",
      "block_rule": null,
      "started_at": "2026-05-12T02:00:14Z"
    },
    {
      "seq": 1,
      "tool_name": "Glob",
      "tool_input_summary": "find all sibling agent journals",
      "target_path": null,
      "tokens_in": 30,
      "tokens_out": 800,
      "duration_ms": 50,
      "verdict": "succeeded",
      "block_rule": null,
      "started_at": "2026-05-12T02:00:15Z"
    },
    {
      "seq": 2,
      "tool_name": "Write",
      "tool_input_summary": "append daily entry to arjuna journal",
      "target_path": "/Users/mosaic/projects/observer-test/.claude/agents/_meta/observer/journal/arjuna.md",
      "tokens_in": 200,
      "tokens_out": 0,
      "duration_ms": 120,
      "verdict": "succeeded",
      "block_rule": null,
      "started_at": "2026-05-12T02:14:30Z"
    }
  ],
  "decision_points": [
    {
      "seq": 0,
      "description": "Threshold check for arjuna — bootstrap mode, runs_observed=14, days_observed=5",
      "choice_made": "continue observation; do not draft proposal yet",
      "alternatives_considered": ["draft proposal at low confidence"],
      "timestamp": "2026-05-12T02:13:55Z"
    }
  ],
  "mast_codes": [],
  "bhishma_blocks": [],
  "tokens_total": 3480,
  "cost_usd": null,
  "final_outcome": "completed",
  "error": null
}
```

---

## Versioning

This file is `v1`. Field additions are backwards compatible. Field removals or semantic changes require a version bump (`v2`), at which point Sahadeva must handle both versions during a deprecation window.

The `$schema` field in each trace pins it to a version of this document. Sahadeva refuses to ingest traces with an unknown `$schema` value.

---

## What this schema deliberately does NOT include

- **Full CoT (chain-of-thought reasoning).** Playbook §3 calls CoT monitorability "fragile" — relying on it permanently is a known anti-pattern. We record decision _points_ (sparse, structured) rather than the full reasoning trace. CoT remains in logs for now; if we ever instrument against it, that's a deliberate decision recorded in `_audit/`.
- **Full tool output payloads.** Bloats the trace; defeats aggregation. Output stays in `logs/<agent>/`.
- **User-identifying data.** PII discipline.
- **Cost data when the provider doesn't return it.** Better to be null than wrong.

---

## Consumers

| Consumer                               | Procedure                       | What it uses                                                                                                  |
| -------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Sahadeva P2                            | Cross-agent hash audit          | `bhishma_hash` per agent per run                                                                              |
| Sahadeva P3                            | R23 approval-tier compliance    | not directly; proposals live in `_meta/observer/`                                                             |
| Sahadeva P4                            | Bhishma compliance              | `bhishma_blocks[]` + `tool_calls[].verdict=bhishma_blocked`                                                   |
| Sahadeva P5                            | Quantitative trend audit        | `tokens_total`, `duration_ms`, `tool_calls[].duration_ms`, count of tool calls per run, `bhishma_blocks` rate |
| Sahadeva P7                            | Anomaly scan                    | `final_outcome`, `error`, `run_id` format conformance                                                         |
| Sahadeva P10                           | Adversarial test-set evaluation | Implanted traces in the sandbox should appear here; detection rate = found / total                            |
| Replay tool (`lib/replay.sh`, planned) | Debugging                       | The full trace, reconstructed as a sequence of events                                                         |

---

## When this schema activates

The schema is defined; the writer (`lib/trace-writer.sh`) is provided; the PostToolUse hook (`lib/post-tool-hook.sh`) is provided. **Activation is deferred** until:

1. Sahadeva produces its first weekly report (currently never run), OR
2. The first proposal flow exercise demonstrates an integration need

Per Bhishma R23, wiring the hook into `.claude/settings.json` is a constitutional change requiring Sahadeva endorsement + 24-hour cooling-off — neither available pre-first-Sahadeva-run.

Until activation, no traces exist. Sahadeva's P2/P4/P5/P10 procedures already gracefully handle the empty case.
