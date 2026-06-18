#!/usr/bin/env bash
# Manual or cron-friendly invocation of the Sahadeva agent.
#
# Sahadeva is the Tier-Audit external auditor. It runs **weekly** with completely
# stateless context, reads the past week's journals/proposals/approvals across
# every agent, applies its P1–P11 audit procedure, and writes a single weekly
# report addressed to Kartavya.
#
# Recommended cron entry — the specific cron fields depend on the host's
# timezone (cron uses the system's local TZ, not UTC):
#
#   If the host is in IST (Asia/Kolkata):
#     0 10 * * 0 cd /Users/mosaic/projects/observer-test && \
#         .claude/agents/_meta/audit/run_sahadeva.sh >> \
#         .claude/agents/_meta/audit/run.log 2>&1
#
#   If the host is in UTC:
#     30 4 * * 0 cd /Users/mosaic/projects/observer-test && \
#         .claude/agents/_meta/audit/run_sahadeva.sh >> \
#         .claude/agents/_meta/audit/run.log 2>&1
#
# Both forms target Sunday 10:00 IST = Sunday 04:30 UTC. Pick the one matching
# the host's `date +%Z` output.
#
# Manual invocation: just run the script. Sahadeva does not need any arguments —
# the cadence and rubric are fully described in agent.md and skill.md.

set -euo pipefail

AUDIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$AUDIT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$AUDIT_DIR")"

# Single-instance guard. Sahadeva runs once weekly; overlapping invocations
# are always a bug.
LOCKFILE="$AUDIT_DIR/.run.lock"
if [ -f "$LOCKFILE" ]; then
  EXISTING_PID="$(cat "$LOCKFILE" 2>/dev/null || echo '')"
  if [ -n "$EXISTING_PID" ] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "Another sahadeva run is in progress (PID $EXISTING_PID); exiting." >&2
    exit 0
  fi
  rm -f "$LOCKFILE"
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

cd "$REPO_ROOT"

TIMESTAMP_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_UTC="$(date -u +%Y-%m-%d)"
HHMMSS_UTC="$(date -u +%H%M%S)"
ISO_WEEK="$(date -u +%G-W%V)"  # e.g., 2026-W19

RUN_ID="${DATE_UTC}-sahadeva-${HHMMSS_UTC}"

echo "[$TIMESTAMP_UTC] Sahadeva run starting"
echo "  run_id:   $RUN_ID"
echo "  iso_week: $ISO_WEEK"
echo "  cwd:      $REPO_ROOT"

# Sanity checks
if [ ! -f "$AUDIT_DIR/agent.md" ]; then
  echo "ERROR: agent.md not found at $AUDIT_DIR/agent.md" >&2
  exit 1
fi

if [ ! -f "$AUDIT_DIR/skill.md" ]; then
  echo "ERROR: skill.md not found at $AUDIT_DIR/skill.md" >&2
  exit 1
fi

# Verify the current quarter's test set exists. Sahadeva's P10 procedure needs
# this; missing test set is a critical configuration error.
CURRENT_QUARTER="$(date -u +%Y)-Q$(( ( $(date -u +%-m) - 1 ) / 3 + 1 ))"
TEST_SET="$AUDIT_DIR/test-set/${CURRENT_QUARTER}.md"
if [ ! -f "$TEST_SET" ]; then
  echo "WARNING: test set $TEST_SET not found." >&2
  echo "         Sahadeva will run without P10 (test-set evaluation). Detection rate metric will be absent from this week's report." >&2
fi

# Claude CLI presence
CLAUDE_CMD="${CLAUDE_CMD:-claude}"
if ! command -v "$CLAUDE_CMD" >/dev/null 2>&1; then
  echo "ERROR: '$CLAUDE_CMD' not found in PATH. Set CLAUDE_CMD env var to your Claude Code CLI binary." >&2
  exit 1
fi

# Initialise the trace (best-effort — failure here logs but does not abort).
TRACE_WRITER="$REPO_ROOT/lib/trace-writer.sh"
if [ -x "$TRACE_WRITER" ]; then
  if ! "$TRACE_WRITER" init sahadeva "$RUN_ID"; then
    echo "WARNING: trace-writer init failed; continuing without trace recording." >&2
    TRACE_WRITER=""
  fi
else
  echo "INFO: $TRACE_WRITER not present or not executable; running without trace recording." >&2
  TRACE_WRITER=""
fi

# Export env vars so the (currently-not-wired-in) PreToolUse + PostToolUse hooks
# can attribute tool calls correctly when activated.
export BHISHMA_AGENT=sahadeva
export BHISHMA_RUN_ID="$RUN_ID"

# Invoke Sahadeva. Note: --permission-mode bypassPermissions is used because
# Sahadeva is read-only on the entire repo by design (skill.md). Until the
# Bhishma runtime hook is wired in, the only enforcement is the agent's
# internal discipline against its declared write_scope.
#
# The prompt tells Sahadeva to run its full P1–P11 routine; everything else
# (rubric, output format, inbox discipline) is described in agent.md + skill.md
# which Sahadeva reads at session start.
SAHADEVA_PROMPT="Run your weekly audit routine. Read bhishma.md, then execute P1 through P11 in order. Produce the weekly report at \`_meta/audit/reports/${ISO_WEEK}.md\` and append any critical findings to \`_meta/audit/inbox.md\` per P9. Use the test set at \`_meta/audit/test-set/${CURRENT_QUARTER}.md\` for P10. The audit week is the 7 days ending today UTC. Print a one-line completion summary."

OUTCOME="completed"
EXIT_CODE=0

if ! "$CLAUDE_CMD" -p --permission-mode bypassPermissions --agent sahadeva "$SAHADEVA_PROMPT"; then
  EXIT_CODE=$?
  OUTCOME="errored"
fi

# Finalise the trace if we initialised one.
if [ -n "$TRACE_WRITER" ]; then
  "$TRACE_WRITER" finalise sahadeva "$RUN_ID" "$OUTCOME" || true
fi

TIMESTAMP_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ $EXIT_CODE -eq 0 ]; then
  echo "[$TIMESTAMP_END] Sahadeva run complete. Report: _meta/audit/reports/${ISO_WEEK}.md"
else
  echo "[$TIMESTAMP_END] Sahadeva run FAILED (exit $EXIT_CODE). Check stderr above." >&2
  exit $EXIT_CODE
fi
