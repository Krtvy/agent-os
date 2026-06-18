#!/usr/bin/env bash
# run_sanjaya.sh — invoke the Tier-1 Observer with a lockfile guard.
#
# Usage: bash scripts/run_sanjaya.sh
# Cron:  */30 * * * *  bash ~/projects/observer-test/scripts/run_sanjaya.sh
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$HOME/projects/observer-test}"
LOCKFILE="$PROJECT_ROOT/.claude/agents/_meta/observer/.run.lock"
LOG_DIR="$PROJECT_ROOT/logs/sanjaya"

mkdir -p "$LOG_DIR" "$(dirname "$LOCKFILE")"

# Stale-lock cleanup
if [[ -f "$LOCKFILE" ]]; then
  pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "[$(date -u +%FT%TZ)] sanjaya — already running (pid $pid), skipping"
    exit 0
  fi
  echo "[$(date -u +%FT%TZ)] sanjaya — clearing stale lock (dead pid $pid)"
  rm -f "$LOCKFILE"
fi

trap 'rm -f "$LOCKFILE"' EXIT
echo $$ > "$LOCKFILE"

ts=$(date -u +"%Y%m%d-%H%M%SZ")
LOGFILE="$LOG_DIR/sanjaya-$ts.log"

cd "$PROJECT_ROOT"
echo "[$(date -u +%FT%TZ)] sanjaya — starting" | tee -a "$LOGFILE"
claude --agent sanjaya 2>&1 | tee -a "$LOGFILE"
exit_code=${PIPESTATUS[0]}
echo "[$(date -u +%FT%TZ)] sanjaya — exit $exit_code" | tee -a "$LOGFILE"
exit "$exit_code"
