#!/usr/bin/env bash
# post-tool-hook.sh — Claude Code PostToolUse hook for structured trace recording.
#
# Reads the tool-result JSON from stdin and writes a structured trace event via
# lib/trace-writer.sh. Same opt-in activation discipline as bhishma-pretool-hook.sh:
#
#   - $BHISHMA_AGENT unset      → exit 0 (no-op; Kartavya session).
#   - $BHISHMA_AGENT + $BHISHMA_RUN_ID set → record the event.
#
# Both env vars are required for recording; setting only $BHISHMA_AGENT is
# treated as a configuration error (we don't know which run to attribute to).
#
# Schema: lib/trace-schema.md (v1).
#
# Failure mode: this hook MUST NOT block the agent's primary work. If trace
# recording fails (writer error, disk full, malformed input), this hook logs
# to stderr and exits 0. The narrative journal remains the trust layer; the
# trace is best-effort.
#
# Wire-up (when ready — same constitutional cooling-off as bhishma-pretool-hook.sh):
#   Add to `.claude/settings.json`:
#     {
#       "hooks": {
#         "PostToolUse": [
#           {
#             "matcher": ".*",
#             "hooks": [
#               { "type": "command", "command": "lib/post-tool-hook.sh" }
#             ]
#           }
#         ]
#       }
#     }

set -uo pipefail   # NOT -e — we never want to bubble failures back to claude

PAYLOAD="$(cat || echo '{}')"

# No-op when not in an opt-in agent session.
if [[ -z "${BHISHMA_AGENT:-}" ]]; then
  exit 0
fi

if [[ -z "${BHISHMA_RUN_ID:-}" ]]; then
  echo "post-tool-hook: BHISHMA_AGENT set but BHISHMA_RUN_ID is not — cannot attribute trace" >&2
  exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Build the event JSON from the Claude Code payload. We sanitise — drop full
# tool input/output, keep shape.
EVENT_JSON=$(python3 - "$PAYLOAD" <<'PY'
import json
import sys

try:
    p = json.loads(sys.argv[1])
except Exception:
    print("{}")
    sys.exit(0)

tool_name = p.get("tool_name", "unknown")
ti = p.get("tool_input", {}) or {}
tr = p.get("tool_response", {}) or {}

# Target path for write-shaped tools.
target = None
for k in ("file_path", "notebook_path", "path"):
    if k in ti and isinstance(ti[k], str):
        target = ti[k]
        break

# Short summary; never include credentials, full payloads, or PII.
# We take the tool name + the first 80 chars of any 'description' or 'command' field.
summary_bits = [tool_name]
for k in ("description", "command", "pattern", "query"):
    if k in ti and isinstance(ti[k], str):
        snippet = ti[k][:80].replace("\n", " ")
        summary_bits.append(f"{k}={snippet}")
        break
summary = " · ".join(summary_bits)[:200]

# Verdict — succeeded unless the response carries an error signal.
verdict = "succeeded"
if isinstance(tr, dict):
    if tr.get("is_error") or tr.get("error"):
        verdict = "failed"

# Token/duration data — Claude Code may or may not provide these; default 0.
usage = p.get("usage", {}) or {}
tokens_in = int(usage.get("input_tokens", 0)) if isinstance(usage, dict) else 0
tokens_out = int(usage.get("output_tokens", 0)) if isinstance(usage, dict) else 0
duration_ms = int(p.get("duration_ms", 0))

import datetime
ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

event = {
    "tool_name": tool_name,
    "tool_input_summary": summary,
    "target_path": target,
    "tokens_in": tokens_in,
    "tokens_out": tokens_out,
    "duration_ms": duration_ms,
    "verdict": verdict,
    "block_rule": None,
    "started_at": ts,
}

print(json.dumps(event))
PY
)

# Append the event via trace-writer.
if ! "$REPO_ROOT/lib/trace-writer.sh" tool-call "$BHISHMA_AGENT" "$BHISHMA_RUN_ID" "$EVENT_JSON" 2>/dev/null; then
  echo "post-tool-hook: trace-writer failed for run $BHISHMA_RUN_ID — continuing without recording" >&2
fi

exit 0
