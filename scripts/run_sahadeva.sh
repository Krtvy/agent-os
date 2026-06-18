#!/usr/bin/env bash
# run_sahadeva.sh — weekly external auditor.
#
# Usage: bash scripts/run_sahadeva.sh
# Cron:  0 10 * * 0  bash ~/projects/observer-test/scripts/run_sahadeva.sh
#       (Sundays at 10:00 IST = 04:30 UTC; adjust per your local crontab.)
#
# Sahadeva is intentionally stateless. No lockfile guard is needed —
# but we still guard against double-runs in the same minute.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$HOME/projects/observer-test}"
LOG_DIR="$PROJECT_ROOT/logs/sahadeva"
LOCKFILE="$PROJECT_ROOT/.claude/agents/_meta/audit/.run.lock"

mkdir -p "$LOG_DIR" "$(dirname "$LOCKFILE")"

if [[ -f "$LOCKFILE" ]]; then
  pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "[$(date -u +%FT%TZ)] sahadeva — already running (pid $pid), skipping"
    exit 0
  fi
  rm -f "$LOCKFILE"
fi

trap 'rm -f "$LOCKFILE"' EXIT
echo $$ > "$LOCKFILE"

week=$(date -u +"%G-W%V")   # ISO 8601 week
ts=$(date -u +"%Y%m%d-%H%M%SZ")
LOGFILE="$LOG_DIR/sahadeva-$ts.log"

cd "$PROJECT_ROOT"
echo "[$(date -u +%FT%TZ)] sahadeva — starting weekly audit (week $week)" | tee -a "$LOGFILE"
claude --agent sahadeva 2>&1 | tee -a "$LOGFILE"
exit_code=${PIPESTATUS[0]}
echo "[$(date -u +%FT%TZ)] sahadeva — exit $exit_code" | tee -a "$LOGFILE"
exit "$exit_code"
