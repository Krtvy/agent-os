#!/usr/bin/env bash
# _lib.sh — shared helpers for Nakula scripts. Source this; do not invoke.

# ---- Paths -----------------------------------------------------------------

# Caller sets REPO_ROOT and NAKULA_DIR before sourcing.
: "${REPO_ROOT:?REPO_ROOT must be set before sourcing _lib.sh}"
: "${NAKULA_DIR:?NAKULA_DIR must be set before sourcing _lib.sh}"

LOGS_DIR="$REPO_ROOT/logs"
HEARTBEAT_JSON="$LOGS_DIR/heartbeat.json"
NAKULA_LOGS_DIR="$LOGS_DIR/nakula"
NAKULA_LOCKS_DIR="$NAKULA_DIR/locks"
JOBS_YML="$NAKULA_DIR/jobs.yml"
# Use system Python (Windows: python, Unix: venv or python3)
if [[ -f "$REPO_ROOT/.venv/bin/python3" ]]; then
  VENV_PY="$REPO_ROOT/.venv/bin/python3"
elif command -v python &>/dev/null; then
  VENV_PY="$(command -v python)"
else
  VENV_PY="$(command -v python3)"
fi

# ---- run_id ---------------------------------------------------------------

# Format per Sahadeva W20 §5: ^[a-z]+-\d{8}-\d{6}Z-[0-9a-f]{6}$
nakula_run_id() {
  local agent="nakula"
  local stamp
  stamp="$(date -u +%Y%m%d-%H%M%SZ)"
  local rand
  rand="$(LC_ALL=C tr -dc '0-9a-f' </dev/urandom | head -c 6 || true)"
  printf '%s-%s-%s\n' "$agent" "$stamp" "$rand"
}

# ---- jobs.yml lookup ------------------------------------------------------

# nakula_lookup_job <name> → prints `command|timeout_minutes|on_failure|ufc_path|ufc_max_age_hours`
# (pipe-separated; missing fields empty). Exits 1 if job not found.
nakula_lookup_job() {
  local name="$1"
  "$VENV_PY" - "$JOBS_YML" "$name" <<'PY'
import sys
from pathlib import Path
import yaml

path = Path(sys.argv[1])
target = sys.argv[2]
with path.open() as f:
    data = yaml.safe_load(f)
for job in data.get("jobs", []):
    if job.get("name") == target:
        cmd = job.get("command", "")
        tm = job.get("timeout_minutes", 0)
        of = job.get("on_failure", "none")
        ufc = job.get("upstream_freshness_check") or {}
        ufc_path = ufc.get("path", "")
        ufc_max = ufc.get("max_age_hours", "")
        print(f"{cmd}|{tm}|{of}|{ufc_path}|{ufc_max}")
        sys.exit(0)
print(f"ERROR: job '{target}' not found in {path}", file=sys.stderr)
sys.exit(1)
PY
}

# ---- Heartbeat ------------------------------------------------------------

# nakula_write_heartbeat <job> <run_id> <started_iso> <ended_iso> <exit_code> <output_size> <status> <skip_reason>
# Atomic (write to .tmp, mv into place). Single-writer rule preserved.
nakula_write_heartbeat() {
  local job="$1" run_id="$2" started="$3" ended="$4" exit_code="$5"
  local output_size="$6" status="$7" skip_reason="$8"
  mkdir -p "$LOGS_DIR"
  local tmp="${HEARTBEAT_JSON}.tmp.$$"
  cat >"$tmp" <<EOF
{
  "job_name": "${job}",
  "run_id": "${run_id}",
  "started_at": "${started}",
  "ended_at": "${ended}",
  "exit_code": ${exit_code},
  "output_size_bytes": ${output_size},
  "status": "${status}",
  "skip_reason": "${skip_reason}"
}
EOF
  mv -f "$tmp" "$HEARTBEAT_JSON"
}

# ---- Upstream freshness check --------------------------------------------

# nakula_upstream_stale <ufc_path> <ufc_max_age_hours>
# Returns 0 (stale, skip job) if path missing or older than max_age_hours.
# Returns 1 (fresh, proceed) otherwise. Empty ufc_path = no check = fresh.
nakula_upstream_stale() {
  local p="$1" max_hours="$2"
  [[ -z "$p" || -z "$max_hours" ]] && return 1
  local resolved="${p/#\~/$HOME}"
  [[ -e "$resolved" ]] || return 0
  local file_epoch now_epoch age_hours
  file_epoch="$(stat -f %m "$resolved" 2>/dev/null || stat -c %Y "$resolved" 2>/dev/null)"
  now_epoch="$(date -u +%s)"
  age_hours=$(( (now_epoch - file_epoch) / 3600 ))
  (( age_hours >= max_hours ))
}

# ---- Bounded subprocess (Bash-only timeout for macOS) --------------------

# nakula_run_bounded <timeout_seconds> <log_file> -- <command> [args...]
# Runs the command with stdout+stderr tee'd to log_file. Kills it with TERM
# then KILL on timeout. Echoes the inner exit code on stdout. Returns 0 always
# so caller can capture exit code via command substitution.
nakula_run_bounded() {
  local timeout_secs="$1" log_file="$2"
  shift 2
  [[ "$1" == "--" ]] && shift

  (
    "$@" >>"$log_file" 2>&1
  ) &
  local cmd_pid=$!

  (
    sleep "$timeout_secs"
    if kill -0 "$cmd_pid" 2>/dev/null; then
      kill -TERM "$cmd_pid" 2>/dev/null || true
      sleep 5
      kill -KILL "$cmd_pid" 2>/dev/null || true
    fi
  ) &
  local watchdog_pid=$!

  local rc=0
  wait "$cmd_pid" 2>/dev/null || rc=$?
  kill -KILL "$watchdog_pid" 2>/dev/null || true
  wait "$watchdog_pid" 2>/dev/null || true
  printf '%s\n' "$rc"
}
