#!/usr/bin/env bash
# nakula-run.sh — run a named job from jobs.yml, with lock + timeout + heartbeat.
#
# Usage:
#   .claude/agents/nakula/scripts/nakula-run.sh <job-name> [--dry-run]
#
# Contract:
#   - Heartbeat at logs/heartbeat.json is written on EVERY exit path (trap).
#   - Per-job log at logs/nakula/<job>/<run_id>.log.
#   - Lockfile at .claude/agents/nakula/locks/<job>.lock prevents overlap.
#   - Exit code mirrors the wrapped command's exit code (0 on skipped).
#   - macOS-friendly: implements timeout in pure Bash (no coreutils dep).
#
# Schema: .claude/agents/nakula/agent.md §"Your outputs"
# Contract: .claude/agents/nakula/agent.md §"Constraints (hard)"

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAKULA_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$NAKULA_DIR/../../.." && pwd)"
export REPO_ROOT NAKULA_DIR

# shellcheck source=_lib.sh
source "$SCRIPT_DIR/_lib.sh"

# ---- Argument parsing ----------------------------------------------------

JOB_NAME="${1:-}"
DRY_RUN="false"
[[ "${2:-}" == "--dry-run" ]] && DRY_RUN="true"

if [[ -z "$JOB_NAME" ]]; then
  echo "usage: nakula-run.sh <job-name> [--dry-run]" >&2
  exit 64
fi

cd "$REPO_ROOT"

# ---- Lookup job in jobs.yml ----------------------------------------------

JOB_LINE="$(nakula_lookup_job "$JOB_NAME")" || exit 65
IFS='|' read -r JOB_CMD TIMEOUT_MIN ON_FAILURE UFC_PATH UFC_MAX <<< "$JOB_LINE"

# ---- Run-id, timestamps, paths -------------------------------------------

RUN_ID="$(nakula_run_id)"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
JOB_LOG_DIR="$NAKULA_LOGS_DIR/$JOB_NAME"
mkdir -p "$JOB_LOG_DIR" "$NAKULA_LOCKS_DIR"
JOB_LOG="$JOB_LOG_DIR/${RUN_ID}.log"
: > "$JOB_LOG"

# ---- Heartbeat state (referenced by trap) --------------------------------

STATUS="failure"
SKIP_REASON="n/a"
EXIT_CODE=1

emit_heartbeat() {
  local ended_at output_size
  ended_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  output_size="$(stat -f %z "$JOB_LOG" 2>/dev/null || stat -c %s "$JOB_LOG" 2>/dev/null || echo 0)"
  nakula_write_heartbeat \
    "$JOB_NAME" "$RUN_ID" "$STARTED_AT" "$ended_at" \
    "$EXIT_CODE" "$output_size" "$STATUS" "$SKIP_REASON"
}
trap emit_heartbeat EXIT

echo "[nakula] run_id=$RUN_ID job=$JOB_NAME cmd=$JOB_CMD timeout=${TIMEOUT_MIN}m" | tee -a "$JOB_LOG"

# ---- Dry-run short-circuit -----------------------------------------------

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[nakula] DRY RUN — not invoking command" | tee -a "$JOB_LOG"
  STATUS="skipped"
  SKIP_REASON="n/a"
  EXIT_CODE=0
  exit 0
fi

# ---- Lock acquisition ----------------------------------------------------

LOCKFILE="$NAKULA_LOCKS_DIR/${JOB_NAME}.lock"
if [[ -f "$LOCKFILE" ]]; then
  EXISTING_PID="$(cat "$LOCKFILE" 2>/dev/null || echo '')"
  if [[ -n "$EXISTING_PID" ]] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "[nakula] lock held by PID $EXISTING_PID — skipping" | tee -a "$JOB_LOG"
    STATUS="skipped"
    SKIP_REASON="already-running"
    EXIT_CODE=0
    exit 0
  fi
  echo "[nakula] stale lock (PID $EXISTING_PID not alive) — clearing" | tee -a "$JOB_LOG"
  rm -f "$LOCKFILE"
fi
echo "$$" > "$LOCKFILE"

cleanup_lock() {
  rm -f "$LOCKFILE"
  emit_heartbeat
}
trap cleanup_lock EXIT

# ---- Upstream freshness check --------------------------------------------

if [[ -n "$UFC_PATH" ]] && nakula_upstream_stale "$UFC_PATH" "$UFC_MAX"; then
  echo "[nakula] upstream stale ($UFC_PATH older than ${UFC_MAX}h) — skipping" | tee -a "$JOB_LOG"
  STATUS="skipped"
  SKIP_REASON="upstream-stale"
  EXIT_CODE=0
  exit 0
fi

# ---- Run command with bounded timeout ------------------------------------

TIMEOUT_SECS=$(( TIMEOUT_MIN * 60 ))
INNER_RC="$(nakula_run_bounded "$TIMEOUT_SECS" "$JOB_LOG" -- bash "$JOB_CMD")"
EXIT_CODE="$INNER_RC"

if [[ "$EXIT_CODE" == "0" ]]; then
  STATUS="success"
  SKIP_REASON="n/a"
  echo "[nakula] OK exit=$EXIT_CODE" | tee -a "$JOB_LOG"
else
  STATUS="failure"
  SKIP_REASON="n/a"
  echo "[nakula] FAIL exit=$EXIT_CODE on_failure=$ON_FAILURE" | tee -a "$JOB_LOG" >&2

  case "$ON_FAILURE" in
    alert-file)
      ALERT_DIR="$REPO_ROOT/logs/nakula/_alerts"
      mkdir -p "$ALERT_DIR"
      echo "$STARTED_AT job=$JOB_NAME run_id=$RUN_ID exit=$EXIT_CODE log=$JOB_LOG" \
        >> "$ALERT_DIR/failures.log"
      ;;
    none|"") : ;;
    *) echo "[nakula] on_failure=$ON_FAILURE not yet implemented" | tee -a "$JOB_LOG" >&2 ;;
  esac
fi

exit "$EXIT_CODE"
