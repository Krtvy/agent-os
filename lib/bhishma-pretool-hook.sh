#!/usr/bin/env bash
# bhishma-pretool-hook.sh — Claude Code PreToolUse hook for write_scope enforcement.
#
# Reads tool-call JSON from stdin, extracts the target path for write/edit-shaped
# tools, and dispatches to bhishma-check.sh against the agent declared in the
# `$BHISHMA_AGENT` environment variable.
#
# Activation discipline:
#   - If `$BHISHMA_AGENT` is UNSET → exit 0 (no-op). This is the safe default for
#     Kartavya's interactive sessions, where the human has full repo access by
#     design and is not a member of the Tier-0/1/2/Audit chain.
#   - If `$BHISHMA_AGENT` is SET → dispatch to bhishma-check.sh. This is the
#     opt-in path: agent runners (run_observer.sh, etc.) set the variable
#     before invoking claude, and the hook enforces scope only for those runs.
#
# Wire-up (when you're ready to enable):
#   Add to `.claude/settings.json`:
#     {
#       "hooks": {
#         "PreToolUse": [
#           {
#             "matcher": "Edit|Write|MultiEdit|NotebookEdit",
#             "hooks": [
#               { "type": "command", "command": "lib/bhishma-pretool-hook.sh" }
#             ]
#           }
#         ]
#       }
#     }
#
#   Then in each agent runner, set the env var:
#     export BHISHMA_AGENT=sanjaya
#     claude -p --agent observer ...
#
#   Until the settings.json wiring is added, this script is dormant.

set -euo pipefail

# Read tool-call payload from stdin. Claude Code passes a JSON envelope.
PAYLOAD="$(cat || echo '{}')"

# If no agent is set, this is a Kartavya session — allow without enforcement.
if [[ -z "${BHISHMA_AGENT:-}" ]]; then
  exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Extract the target path. For Edit, Write, NotebookEdit, MultiEdit the field is
# `tool_input.file_path` (or `notebook_path`). Use Python for robust JSON parsing.
TARGET=$(python3 - "$PAYLOAD" <<'PY'
import json
import sys
try:
    p = json.loads(sys.argv[1])
except Exception:
    print("")
    sys.exit(0)

ti = p.get("tool_input", {}) or {}
# Try the standard field names in order.
for k in ("file_path", "notebook_path", "path"):
    if k in ti and isinstance(ti[k], str):
        print(ti[k])
        sys.exit(0)

# MultiEdit nests edits — but file_path is still at the top level of tool_input.
# Fall through to empty.
print("")
PY
)

if [[ -z "$TARGET" ]]; then
  # Tool call we don't have a target for — let it through. (The matcher in
  # settings.json should restrict this hook to write-shaped tools, so an empty
  # target probably means a tool shape we don't enforce.)
  exit 0
fi

# Dispatch to bhishma-check.sh. It returns 0 for allow, non-zero for block.
"$REPO_ROOT/lib/bhishma-check.sh" "$BHISHMA_AGENT" "$TARGET"
