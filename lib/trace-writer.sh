#!/usr/bin/env bash
# trace-writer.sh — append-only trace event writer for the agent ecosystem.
#
# Used by agent runners and the post-tool-use hook to record structured trace
# events that Sahadeva consumes for quantitative trend audit (P5) and adversarial
# test-set evaluation (P10).
#
# Schema: lib/trace-schema.md (v1).
#
# Invocation styles:
#
#   1. Initialise a trace (called once at run start):
#        trace-writer.sh init <agent> <run_id>
#      Creates _meta/observer/traces/<agent>/<run_id>.json with an empty skeleton.
#
#   2. Append a tool call (called per tool_use):
#        trace-writer.sh tool-call <agent> <run_id> <event-json>
#      <event-json> matches the schema's `tool_calls[]` shape. Pipe from stdin
#      OR pass as an argument.
#
#   3. Append a bhishma block:
#        trace-writer.sh bhishma-block <agent> <run_id> <rule> <attempted-action>
#
#   4. Append a decision point:
#        trace-writer.sh decision <agent> <run_id> <description> <choice>
#
#   5. Finalise (called once at run end):
#        trace-writer.sh finalise <agent> <run_id> <outcome>
#      <outcome> in {completed, errored, blocked}. Computes ended_at + duration_ms.
#
# Concurrency: in-process Python fcntl.LOCK_EX on the trace file. Cross-platform
# (Linux + macOS); does not depend on the `flock` binary which is Linux-only.
#
# Failure mode: if the trace file is missing or malformed, this script logs to
# stderr and exits non-zero. The caller decides whether to abort the run or
# continue without trace recording. Trace failures must NOT abort the agent's
# primary work — the narrative journal is the trust layer; the trace is the
# audit layer.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACES_DIR="$REPO_ROOT/.claude/agents/_meta/observer/traces"

SUBCMD="${1:-}"
AGENT="${2:-}"
RUN_ID="${3:-}"

if [[ -z "$SUBCMD" || -z "$AGENT" || -z "$RUN_ID" ]]; then
  echo "usage: trace-writer.sh <init|tool-call|bhishma-block|decision|finalise> <agent> <run_id> [...]" >&2
  exit 64
fi

mkdir -p "$TRACES_DIR/$AGENT"
TRACE_FILE="$TRACES_DIR/$AGENT/$RUN_ID.json"
LOCK_FILE="$TRACE_FILE.lock"

# Helper: compute SHA-256 of bhishma.md (used by `init`).
bhishma_hash() {
  shasum -a 256 "$REPO_ROOT/.claude/agents/_meta/conductor/bhishma.md" 2>/dev/null | awk '{print $1}'
}

# Tier lookup from agent.md frontmatter. Returns 0/1/2/audit.
agent_tier() {
  local agent="$1"
  for candidate in \
    "$REPO_ROOT/.claude/agents/$agent/agent.md" \
    "$REPO_ROOT/.claude/agents/_meta/observer/agent.md" \
    "$REPO_ROOT/.claude/agents/_meta/conductor/agent.md" \
    "$REPO_ROOT/.claude/agents/_meta/audit/agent.md"
  do
    if [[ -f "$candidate" ]] && grep -q "^name: $agent$" "$candidate"; then
      grep -m1 "^tier:" "$candidate" | sed 's/tier:[[:space:]]*//'
      return 0
    fi
  done
  echo "unknown"
}

case "$SUBCMD" in

  init)
    if [[ -f "$TRACE_FILE" ]]; then
      echo "trace-writer: trace file already exists ($TRACE_FILE) — refusing to overwrite (R5 spirit)" >&2
      exit 1
    fi
    TIER="$(agent_tier "$AGENT")"
    HASH="$(bhishma_hash)"
    STARTED="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    python3 - "$TRACE_FILE" "$AGENT" "$RUN_ID" "$TIER" "$HASH" "$STARTED" <<'PY'
import json, sys
path, agent, run_id, tier, hash_, started = sys.argv[1:7]
try:
    tier_val = int(tier)
except ValueError:
    tier_val = tier
trace = {
    "$schema": "lib/trace-schema.md#v1",
    "run_id": run_id,
    "agent_name": agent,
    "tier": tier_val,
    "parent_run_id": None,
    "bhishma_hash": hash_,
    "started_at": started,
    "ended_at": None,
    "duration_ms": None,
    "tool_calls": [],
    "decision_points": [],
    "mast_codes": [],
    "bhishma_blocks": [],
    "tokens_total": 0,
    "cost_usd": None,
    "final_outcome": None,
    "error": None,
}
with open(path, "w") as f:
    json.dump(trace, f, indent=2)
PY
    ;;

  tool-call)
    EVENT_JSON="${4:-}"
    if [[ -z "$EVENT_JSON" ]]; then
      EVENT_JSON="$(cat || echo '{}')"
    fi
    if [[ ! -f "$TRACE_FILE" ]]; then
      echo "trace-writer: trace file not found ($TRACE_FILE); did you call init first?" >&2
      exit 1
    fi
    python3 - "$TRACE_FILE" "$EVENT_JSON" <<'PY'
import json, sys, fcntl
path, event_json = sys.argv[1], sys.argv[2]
try:
    event = json.loads(event_json)
except Exception as e:
    print(f"trace-writer: invalid event JSON: {e}", file=sys.stderr)
    sys.exit(1)
with open(path, "r+") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    trace = json.load(f)
    event["seq"] = len(trace["tool_calls"])
    trace["tool_calls"].append(event)
    trace["tokens_total"] += int(event.get("tokens_in", 0)) + int(event.get("tokens_out", 0))
    f.seek(0)
    f.truncate()
    json.dump(trace, f, indent=2)
PY
    ;;

  bhishma-block)
    RULE="${4:-}"
    ATTEMPT="${5:-}"
    if [[ -z "$RULE" || -z "$ATTEMPT" ]]; then
      echo "usage: trace-writer.sh bhishma-block <agent> <run_id> <rule> <attempted-action>" >&2
      exit 64
    fi
    if [[ ! -f "$TRACE_FILE" ]]; then
      echo "trace-writer: trace file not found ($TRACE_FILE)" >&2
      exit 1
    fi
    TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    python3 - "$TRACE_FILE" "$RULE" "$ATTEMPT" "$TS" <<'PY'
import json, sys, fcntl
path, rule, attempt, ts = sys.argv[1:5]
with open(path, "r+") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    trace = json.load(f)
    trace["bhishma_blocks"].append({
        "rule": rule,
        "attempted_action": attempt,
        "timestamp": ts,
    })
    f.seek(0)
    f.truncate()
    json.dump(trace, f, indent=2)
PY
    ;;

  decision)
    DESC="${4:-}"
    CHOICE="${5:-}"
    if [[ -z "$DESC" || -z "$CHOICE" ]]; then
      echo "usage: trace-writer.sh decision <agent> <run_id> <description> <choice>" >&2
      exit 64
    fi
    if [[ ! -f "$TRACE_FILE" ]]; then
      echo "trace-writer: trace file not found ($TRACE_FILE)" >&2
      exit 1
    fi
    TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    python3 - "$TRACE_FILE" "$DESC" "$CHOICE" "$TS" <<'PY'
import json, sys, fcntl
path, desc, choice, ts = sys.argv[1:5]
with open(path, "r+") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    trace = json.load(f)
    trace["decision_points"].append({
        "seq": len(trace["decision_points"]),
        "description": desc,
        "choice_made": choice,
        "alternatives_considered": [],
        "timestamp": ts,
    })
    f.seek(0)
    f.truncate()
    json.dump(trace, f, indent=2)
PY
    ;;

  finalise)
    OUTCOME="${4:-completed}"
    if [[ "$OUTCOME" != "completed" && "$OUTCOME" != "errored" && "$OUTCOME" != "blocked" ]]; then
      echo "trace-writer: outcome must be one of {completed, errored, blocked}" >&2
      exit 64
    fi
    if [[ ! -f "$TRACE_FILE" ]]; then
      echo "trace-writer: trace file not found ($TRACE_FILE)" >&2
      exit 1
    fi
    ENDED="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    python3 - "$TRACE_FILE" "$ENDED" "$OUTCOME" <<'PY'
import json, sys, fcntl
from datetime import datetime
path, ended, outcome = sys.argv[1:4]
with open(path, "r+") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    trace = json.load(f)
    trace["ended_at"] = ended
    try:
        started_dt = datetime.fromisoformat(trace["started_at"].replace("Z", "+00:00"))
        ended_dt = datetime.fromisoformat(ended.replace("Z", "+00:00"))
        trace["duration_ms"] = int((ended_dt - started_dt).total_seconds() * 1000)
    except Exception:
        trace["duration_ms"] = None
    trace["final_outcome"] = outcome
    f.seek(0)
    f.truncate()
    json.dump(trace, f, indent=2)
PY
    rm -f "$LOCK_FILE"
    ;;

  *)
    echo "trace-writer: unknown subcommand '$SUBCMD'" >&2
    echo "usage: trace-writer.sh <init|tool-call|bhishma-block|decision|finalise> <agent> <run_id> [...]" >&2
    exit 64
    ;;
esac
