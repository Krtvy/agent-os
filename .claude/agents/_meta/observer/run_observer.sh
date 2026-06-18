#!/usr/bin/env bash
# Manual or cron-friendly invocation of the Observer agent.
# Drop this in cron to run daily; run by hand for ad-hoc observation cycles.

set -euo pipefail

OBSERVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$OBSERVER_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$OBSERVER_DIR")"

# Single-instance guard — refuse to run if another invocation is in progress
LOCKFILE="$OBSERVER_DIR/.run.lock"
if [ -f "$LOCKFILE" ]; then
  EXISTING_PID="$(cat "$LOCKFILE" 2>/dev/null || echo '')"
  if [ -n "$EXISTING_PID" ] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "Another observer run is in progress (PID $EXISTING_PID); exiting." >&2
    exit 0
  fi
  # stale lockfile from a previous crash — clear it
  rm -f "$LOCKFILE"
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

cd "$REPO_ROOT"

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_UTC="$(date -u +%Y-%m-%d)"
HHMMSS_UTC="$(date -u +%H%M%S)"
RUN_ID="${DATE_UTC}-sanjaya-${HHMMSS_UTC}"

echo "[$TIMESTAMP] Observer (sanjaya) run starting"
echo "  run_id: $RUN_ID"
echo "  cwd:    $REPO_ROOT"

# Sanity checks
if [ ! -f "$OBSERVER_DIR/config.yml" ]; then
  echo "ERROR: config.yml not found at $OBSERVER_DIR/config.yml" >&2
  exit 1
fi

if [ ! -f "$OBSERVER_DIR/agent.md" ]; then
  echo "ERROR: agent.md not found at $OBSERVER_DIR/agent.md" >&2
  exit 1
fi

# Invoke the observer agent through Claude Code.
# Adjust the binary name/path if your local install differs.
CLAUDE_CMD="${CLAUDE_CMD:-claude}"

if ! command -v "$CLAUDE_CMD" >/dev/null 2>&1; then
  echo "ERROR: '$CLAUDE_CMD' not found in PATH. Set CLAUDE_CMD env var to your Claude Code CLI binary." >&2
  exit 1
fi

# Phase 3 G5/G1C wiring — best-effort trace recording. Failure here logs but
# does not abort the run; the narrative journal remains the trust layer.
TRACE_WRITER="$REPO_ROOT/lib/trace-writer.sh"
if [ -x "$TRACE_WRITER" ]; then
  if ! "$TRACE_WRITER" init sanjaya "$RUN_ID"; then
    echo "WARNING: trace-writer init failed; continuing without trace recording." >&2
    TRACE_WRITER=""
  fi
else
  echo "INFO: $TRACE_WRITER not present or not executable; running without trace recording." >&2
  TRACE_WRITER=""
fi

# Export env vars so the PostToolUse hook (when wired into .claude/settings.json)
# can attribute tool calls to this run. The hook is currently unwired by design
# (constitutional change, R23 cooling-off); these vars are harmless until then.
export BHISHMA_AGENT=sanjaya
export BHISHMA_RUN_ID="$RUN_ID"

# The observer's daily routine is fully described in agent.md.
# We just trigger it.
OUTCOME="completed"
EXIT_CODE=0

if ! "$CLAUDE_CMD" -p --permission-mode bypassPermissions --agent observer "Run your daily observation routine: poll for approvals first, then ingest new logs and append journal entries for each watched agent, then check thresholds and emit any new pattern reports + proposals. Print the run summary."; then
  EXIT_CODE=$?
  OUTCOME="errored"
fi

# Finalise the trace (best-effort).
if [ -n "$TRACE_WRITER" ]; then
  "$TRACE_WRITER" finalise sanjaya "$RUN_ID" "$OUTCOME" || true
fi

TIMESTAMP_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ $EXIT_CODE -eq 0 ]; then
  echo "[$TIMESTAMP_END] Observer run complete. Trace: _meta/observer/traces/sanjaya/${RUN_ID}.json"
else
  echo "[$TIMESTAMP_END] Observer run FAILED with exit code $EXIT_CODE." >&2
  exit $EXIT_CODE
fi
