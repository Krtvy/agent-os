#!/usr/bin/env bash
# run_nakula.sh — invoke the automation/pipeline owner.
#
# Usage: bash scripts/run_nakula.sh
# Cron:  * * * * *  bash ~/projects/observer-test/scripts/run_nakula.sh
#
# Nakula runs every minute; it determines internally which jobs (if any) are due.
# A short lockfile prevents overlapping invocations.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$HOME/projects/observer-test}"
LOCKFILE="$PROJECT_ROOT/.claude/agents/nakula/.run.lock"
LOG_DIR="$PROJECT_ROOT/logs/nakula/_dispatch"

mkdir -p "$LOG_DIR" "$(dirname "$LOCKFILE")"

if [[ -f "$LOCKFILE" ]]; then
  pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    exit 0   # still running, silent skip — cron will retry next minute
  fi
  rm -f "$LOCKFILE"
fi

trap 'rm -f "$LOCKFILE"' EXIT
echo $$ > "$LOCKFILE"

ts=$(date -u +"%Y%m%d-%H%M%SZ")
LOGFILE="$LOG_DIR/dispatch-$ts.log"

cd "$PROJECT_ROOT"
claude --agent nakula >> "$LOGFILE" 2>&1
exit "${PIPESTATUS[0]:-0}"
