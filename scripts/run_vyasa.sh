#!/usr/bin/env bash
# run_vyasa.sh — invoke the Tier-2 Conductor with a lockfile guard.
#
# Usage: bash scripts/run_vyasa.sh
# Cron:  0 */6 * * *  bash ~/projects/observer-test/scripts/run_vyasa.sh
#
# Vyasa runs less often than Sanjaya — it watches over weeks, not minutes.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$HOME/projects/observer-test}"
LOCKFILE="$PROJECT_ROOT/.claude/agents/_meta/conductor/.run.lock"
LOG_DIR="$PROJECT_ROOT/logs/vyasa"

mkdir -p "$LOG_DIR" "$(dirname "$LOCKFILE")"

if [[ -f "$LOCKFILE" ]]; then
  pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "[$(date -u +%FT%TZ)] vyasa — already running (pid $pid), skipping"
    exit 0
  fi
  echo "[$(date -u +%FT%TZ)] vyasa — clearing stale lock (dead pid $pid)"
  rm -f "$LOCKFILE"
fi

trap 'rm -f "$LOCKFILE"' EXIT
echo $$ > "$LOCKFILE"

ts=$(date -u +"%Y%m%d-%H%M%SZ")
LOGFILE="$LOG_DIR/vyasa-$ts.log"

cd "$PROJECT_ROOT"
echo "[$(date -u +%FT%TZ)] vyasa — starting" | tee -a "$LOGFILE"
claude --agent vyasa 2>&1 | tee -a "$LOGFILE"
exit_code=${PIPESTATUS[0]}
echo "[$(date -u +%FT%TZ)] vyasa — exit $exit_code" | tee -a "$LOGFILE"
exit "$exit_code"
