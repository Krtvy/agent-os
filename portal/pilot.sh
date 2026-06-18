#!/usr/bin/env bash
# Run the portal in PILOT mode + start the ngrok tunnel.
#
# This is the script you run for the 1-week public pilot.
# Local-dev should keep using ./portal/run.sh (port 8000, --reload).
#
# Usage:
#   ./portal/pilot.sh start         # start both, run in background
#   ./portal/pilot.sh stop          # stop both
#   ./portal/pilot.sh status        # show what's running
#   ./portal/pilot.sh logs portal   # tail portal log
#   ./portal/pilot.sh logs ngrok    # tail ngrok log
#
# State files:
#   _private/portal_pilot.env       PORTAL_SECRET_KEY + HTTPS flags (gitignored)
#   /tmp/portal-pilot.{pid,log}     uvicorn
#   /tmp/ngrok.{pid,log}            tunnel agent
#
# Public URL: https://bright-lecturer-richly.ngrok-free.dev
# Internal:   http://127.0.0.1:8001

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT=8001
NGROK_DOMAIN="bright-lecturer-richly.ngrok-free.dev"
PORTAL_VENV="$SCRIPT_DIR/.venv/bin/python"
ENV_FILE="$REPO_ROOT/_private/portal_pilot.env"

PORTAL_PID_FILE=/tmp/portal-pilot.pid
PORTAL_LOG=/tmp/portal-pilot.log
NGROK_PID_FILE=/tmp/ngrok.pid
NGROK_LOG=/tmp/ngrok.log

_wait_portal_ready() {
  # Poll /healthz for up to 30 seconds before giving up. Returns 0 on
  # success. Critical: ngrok forwards traffic immediately on tunnel
  # restart, so uvicorn must be ready *before* we exit this function or
  # the first few user requests hit ERR_NGROK_3004 ("incomplete HTTP").
  local i
  for i in $(seq 1 60); do
    if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/healthz" > /dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

cmd_start() {
  cd "$REPO_ROOT"

  if [ ! -f "$ENV_FILE" ]; then
    echo "Generating $ENV_FILE (first-time setup)..."
    {
      echo "PORTAL_SECRET_KEY=$(openssl rand -hex 32)"
      echo "PORTAL_HTTPS_ONLY=1"
    } > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
  fi

  if pid_alive "$PORTAL_PID_FILE"; then
    echo "Portal already running (PID $(cat "$PORTAL_PID_FILE")). Use 'stop' first."
  else
    echo "Starting portal on :$PORT..."
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
    nohup "$PORTAL_VENV" -m uvicorn portal.app:app \
      --host 127.0.0.1 --port "$PORT" \
      --proxy-headers --forwarded-allow-ips='*' \
      > "$PORTAL_LOG" 2>&1 &
    echo $! > "$PORTAL_PID_FILE"
    disown
    if _wait_portal_ready; then
      echo "  portal up (PID $(cat "$PORTAL_PID_FILE"))"
    else
      echo "  portal failed to become healthy in 30s — check $PORTAL_LOG"; exit 1
    fi
  fi

  if pid_alive "$NGROK_PID_FILE"; then
    echo "Tunnel already running (PID $(cat "$NGROK_PID_FILE"))."
  else
    echo "Starting ngrok tunnel..."
    nohup ngrok http "--url=https://$NGROK_DOMAIN" "$PORT" \
      --log=stdout --log-format=json \
      > "$NGROK_LOG" 2>&1 &
    echo $! > "$NGROK_PID_FILE"
    disown
    sleep 3
    if curl -fsS "https://$NGROK_DOMAIN/healthz" > /dev/null; then
      echo "  tunnel up: https://$NGROK_DOMAIN"
    else
      echo "  tunnel didn't come up — check $NGROK_LOG"; exit 1
    fi
  fi

  echo ""
  echo "Public URL: https://$NGROK_DOMAIN"
}

cmd_stop() {
  for pidfile in "$NGROK_PID_FILE" "$PORTAL_PID_FILE"; do
    if [ -f "$pidfile" ]; then
      pid=$(cat "$pidfile")
      if kill -0 "$pid" 2>/dev/null; then
        echo "Stopping PID $pid ($(basename "$pidfile" .pid))..."
        kill -INT "$pid"
      fi
      rm -f "$pidfile"
    fi
  done
  sleep 1
  echo "Stopped."
}

cmd_status() {
  printf "portal :%s — " "$PORT"
  if pid_alive "$PORTAL_PID_FILE"; then
    printf "running (PID %s)\n" "$(cat "$PORTAL_PID_FILE")"
  else
    printf "stopped\n"
  fi

  printf "tunnel   — "
  if pid_alive "$NGROK_PID_FILE"; then
    printf "running (PID %s)\n" "$(cat "$NGROK_PID_FILE")"
  else
    printf "stopped\n"
  fi

  echo ""
  echo "Internal: http://127.0.0.1:$PORT/healthz"
  echo "Public:   https://$NGROK_DOMAIN/healthz"
  curl -s -o /dev/null -w "  internal=%{http_code}  " "http://127.0.0.1:$PORT/healthz" 2>/dev/null || echo -n "  internal=DOWN  "
  curl -s -o /dev/null -w "public=%{http_code}\n"   "https://$NGROK_DOMAIN/healthz"     2>/dev/null || echo "public=DOWN"
}

cmd_logs() {
  case "${1:-}" in
    portal) tail -n 50 -f "$PORTAL_LOG" ;;
    ngrok)  tail -n 50 -f "$NGROK_LOG"  ;;
    *)      echo "usage: $0 logs portal|ngrok"; exit 1 ;;
  esac
}

pid_alive() {
  local pidfile="$1"
  [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null
}

cmd_restart_portal() {
  # Bounce uvicorn only — leave the ngrok tunnel running. ngrok will
  # serve 502/3004 for the few seconds uvicorn is restarting, BUT will
  # auto-recover the moment uvicorn is bound again. This is the right
  # command for code-only changes (no tunnel reset needed).
  if pid_alive "$PORTAL_PID_FILE"; then
    pid=$(cat "$PORTAL_PID_FILE")
    echo "Stopping portal PID $pid (keeping ngrok alive)..."
    kill -INT "$pid"
    # wait up to 10s for graceful shutdown
    for i in $(seq 1 20); do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.5
    done
    rm -f "$PORTAL_PID_FILE"
  fi
  # Reuse cmd_start which only brings up what's not already running.
  cmd_start
}

case "${1:-}" in
  start)          cmd_start          ;;
  stop)           cmd_stop           ;;
  restart-portal) cmd_restart_portal ;;
  status)         cmd_status         ;;
  logs)           cmd_logs "${2:-}"  ;;
  *)              echo "usage: $0 {start|stop|restart-portal|status|logs portal|logs ngrok}"; exit 1 ;;
esac
