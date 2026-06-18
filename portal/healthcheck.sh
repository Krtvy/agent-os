#!/usr/bin/env bash
# Portal pilot health check — designed to run via cron every 30 minutes.
#
# What it checks:
#   1. uvicorn (portal) + ngrok processes alive
#   2. Internal :8001/healthz and public ngrok URL both return 200
#   3. NEW 500-status lines or NEW Python tracebacks since the last run
#   4. POC login count (informational only — never alerts)
#
# Output:
#   - Always appends one line to /tmp/pilot-health.log
#   - On failure: fires a macOS notification (Sosumi sound) AND exits 1
#   - On success: exits 0 silently
#
# Install (one time):
#   crontab -e
#   add: */30 * * * * /Users/mosaic/projects/observer-test/portal/healthcheck.sh > /dev/null 2>&1
#
# View history any time:
#   tail -50 /tmp/pilot-health.log

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORTAL_LOG="/tmp/portal-pilot.log"
HEALTH_LOG="/tmp/pilot-health.log"
STATE_FILE="/tmp/pilot-health.state"
NGROK_URL="https://bright-lecturer-richly.ngrok-free.dev"
INTERNAL_URL="http://127.0.0.1:8001"

now=$(date '+%Y-%m-%d %H:%M:%S')
issues=()

# ── 1. Processes ────────────────────────────────────────────────────
if ! pgrep -f "uvicorn.*portal.app:app.*8001" > /dev/null; then
    issues+=("uvicorn DOWN")
fi
if ! pgrep -f "ngrok http.*bright-lecturer-richly" > /dev/null; then
    issues+=("ngrok DOWN")
fi

# ── 2. HTTP endpoints ───────────────────────────────────────────────
internal=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$INTERNAL_URL/healthz" 2>/dev/null)
[ "$internal" != "200" ] && issues+=("internal=$internal")

# Public URL: retry once after a 5-second gap. ngrok occasionally has
# 1-2 second heartbeat blips and auto-reconnects. We only alert if the
# outage outlasts the retry window.
public=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$NGROK_URL/healthz" 2>/dev/null)
if [ "$public" != "200" ]; then
    sleep 5
    public=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$NGROK_URL/healthz" 2>/dev/null)
    [ "$public" != "200" ] && issues+=("public=$public")
fi

# ── 3. Log deltas ───────────────────────────────────────────────────
# Read previous counts. If counts grow between runs, something
# new happened — that's the alert trigger.
prev_500=0
prev_traceback=0
[ -f "$STATE_FILE" ] && . "$STATE_FILE"

if [ -f "$PORTAL_LOG" ]; then
    cur_500=$(awk '/500 Internal Server Error/ {n++} END {print n+0}' "$PORTAL_LOG" 2>/dev/null)
    cur_traceback=$(awk '/^Traceback/ {n++} END {print n+0}' "$PORTAL_LOG" 2>/dev/null)
else
    cur_500=0
    cur_traceback=0
fi
cur_500=${cur_500:-0}
cur_traceback=${cur_traceback:-0}

new_500=$(( cur_500 - prev_500 ))
new_tb=$(( cur_traceback - prev_traceback ))
[ "$new_500" -gt 0 ] && issues+=("${new_500}new500s")
[ "$new_tb"  -gt 0 ] && issues+=("${new_tb}newTracebacks")

# Save updated state.
cat > "$STATE_FILE" <<EOF
prev_500=$cur_500
prev_traceback=$cur_traceback
EOF

# ── 4. POC logins (informational only) ──────────────────────────────
poc_pwd_set=$(cd "$REPO_ROOT" && portal/.venv/bin/python -c "
from portal.lib import users
print(sum(1 for u in users.list_users() if u['has_password']))
" 2>/dev/null || echo "?")

# ── Output + alert ──────────────────────────────────────────────────
if [ ${#issues[@]} -eq 0 ]; then
    echo "$now  OK    internal=$internal public=$public pwd_set=$poc_pwd_set total500s=$cur_500 totalTracebacks=$cur_traceback" >> "$HEALTH_LOG"
    exit 0
else
    msg="${issues[*]}"
    echo "$now  FAIL  $msg  (internal=$internal public=$public)" >> "$HEALTH_LOG"
    # macOS notification — pops up on screen with Sosumi sound
    osascript -e "display notification \"$msg\" with title \"Portal Pilot Alert\" sound name \"Sosumi\"" 2>/dev/null
    exit 1
fi
