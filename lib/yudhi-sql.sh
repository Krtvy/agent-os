#!/usr/bin/env bash
# yudhi-sql.sh — run a read-only SQL query against Rootlabs Supabase.
#
# Why: Yudhishthira's natural compute path is pandas on CSV/Sheets, but many POC
# asks need a database lookup to enrich a CSV (e.g., resolve `creator_username`
# → live-GMV, or `sku_id` → product name). This wrapper gives him a safe SQL
# escape hatch without ever showing him the connection string. It enforces:
#
#   - read-only session (default_transaction_read_only = on)
#   - 30-second statement timeout (configurable via YUDHI_SQL_TIMEOUT_MS)
#   - destructive-SQL pre-flight (rejects INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER/GRANT/REVOKE/CREATE)
#   - credential isolation (.env loaded in the Python subprocess; not echoed,
#     not interpolated by the shell)
#   - CSV output (default) or JSON (--json), to stdout (default) or --out FILE
#
# Usage:
#   lib/yudhi-sql.sh --probe                          # health check (SELECT 1 + schemas)
#   lib/yudhi-sql.sh -c "SELECT 1 AS ok"              # inline query
#   lib/yudhi-sql.sh -f training/queries/median_price.sql
#   echo "SELECT NOW() AT TIME ZONE 'Asia/Kolkata' AS ist" | lib/yudhi-sql.sh -
#   lib/yudhi-sql.sh -f q.sql --out out.csv           # write to file
#   lib/yudhi-sql.sh -f q.sql --json                  # JSON instead of CSV
#   lib/yudhi-sql.sh -f q.sql -p start=2026-05-01 -p end=2026-05-15
#
# Environment:
#   YUDHI_SQL_ENV         path to .env (default: _private/daily_reporting/.env)
#   YUDHI_SQL_TIMEOUT_MS  statement timeout in ms (default: 30000)
#
# Exit codes:
#   0   — query executed successfully
#   1   — runtime error (DB connect failure, SQL error, etc.)
#   2   — destructive SQL rejected by pre-flight
#   64  — usage error
#
# Read-only enforcement is server-side AND regex-side. Even if the server-side
# flag fails to bind, the regex catches destructive verbs. Yudhishthira should
# never need to disable this — if a task requires a write, escalate to a human.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/.venv/bin/python3"
ENV_FILE="${YUDHI_SQL_ENV:-$REPO_ROOT/_private/daily_reporting/.env}"
TIMEOUT_MS="${YUDHI_SQL_TIMEOUT_MS:-30000}"

usage() {
  sed -n '2,32p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 64
}

if [[ "$#" -lt 1 ]]; then usage; fi
if [[ ! -x "$VENV_PY" ]]; then
  echo "yudhi-sql: venv not found at $VENV_PY (run: uv venv && uv pip install psycopg2-binary)" >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "yudhi-sql: env file not found at $ENV_FILE" >&2
  echo "  Override with YUDHI_SQL_ENV=/path/to/.env" >&2
  exit 1
fi

PROBE=0
SQL=""
SQL_FILE=""
OUT_FILE=""
FORMAT="csv"
declare -a PARAMS

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --probe) PROBE=1; shift ;;
    -c)      SQL="$2"; shift 2 ;;
    -f)      SQL_FILE="$2"; shift 2 ;;
    -)       SQL="$(cat -)"; shift ;;
    --out|-o) OUT_FILE="$2"; shift 2 ;;
    --json)  FORMAT="json"; shift ;;
    --csv)   FORMAT="csv"; shift ;;
    -p)      PARAMS+=("$2"); shift 2 ;;
    -h|--help) usage ;;
    *)       echo "yudhi-sql: unknown arg: $1" >&2; exit 64 ;;
  esac
done

# Pass params to Python via env var (NUL-separated key=value pairs)
PARAMS_ENV=""
for kv in "${PARAMS[@]+"${PARAMS[@]}"}"; do
  PARAMS_ENV+="${kv}"$'\x1f'
done

# Read SQL from file if requested
if [[ -n "$SQL_FILE" ]]; then
  if [[ ! -f "$SQL_FILE" ]]; then
    echo "yudhi-sql: SQL file not found: $SQL_FILE" >&2
    exit 1
  fi
  SQL="$(cat "$SQL_FILE")"
fi

# Probe mode uses a fixed read-only query
if [[ "$PROBE" -eq 1 ]]; then
  SQL="SELECT 1 AS ok, current_database() AS db, current_user AS usr, NOW() AT TIME ZONE 'Asia/Kolkata' AS ist_now"
fi

if [[ -z "$SQL" ]]; then
  echo "yudhi-sql: no SQL provided (use -c, -f, --probe, or stdin via -)" >&2
  exit 64
fi

# Destructive-SQL pre-flight. Match whole words at statement start or after ; or whitespace.
# Use a sub-call to grep so the pattern is unambiguous and locale-stable.
if printf '%s' "$SQL" | LC_ALL=C grep -qiE '(^|[[:space:];])\s*(insert|update|delete|drop|truncate|alter|grant|revoke|create|comment|reindex|cluster|vacuum|copy|merge|replace)\b'; then
  echo "yudhi-sql: REJECTED — destructive SQL verb detected. This wrapper is read-only." >&2
  echo "  If a write is genuinely required, escalate to a human; never bypass this check." >&2
  exit 2
fi

# Hand off to Python. SQL travels via stdin to avoid arg-list size limits.
exec env \
  YUDHI_ENV_FILE="$ENV_FILE" \
  YUDHI_TIMEOUT_MS="$TIMEOUT_MS" \
  YUDHI_FORMAT="$FORMAT" \
  YUDHI_OUT_FILE="$OUT_FILE" \
  YUDHI_PARAMS="$PARAMS_ENV" \
  "$VENV_PY" "$REPO_ROOT/lib/yudhi_sql_runner.py" <<<"$SQL"
