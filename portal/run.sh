#!/usr/bin/env bash
# Run the portal locally. CWD-independent — resolves its own location.
#
# Usage:
#   ./portal/run.sh              # default: port 8000, localhost only, --reload
#   ./portal/run.sh --port 9000  # override the port
#   ./portal/run.sh --host 0.0.0.0 --port 8000   # expose on LAN (same-WiFi sharing)
#
# Any args you pass are forwarded to uvicorn.

set -euo pipefail

# Resolve the script's directory, regardless of how it was invoked.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_UVICORN="$SCRIPT_DIR/.venv/bin/uvicorn"

if [ ! -x "$VENV_UVICORN" ]; then
  echo "Error: $VENV_UVICORN not found." >&2
  echo "Did you run the first-time setup?" >&2
  echo "  cd $SCRIPT_DIR" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

cd "$REPO_ROOT"

# Defaults — overridable via args passed to this script.
ARGS=("portal.app:app" "--reload" "--port" "8000")
if [ $# -gt 0 ]; then
  # User supplied args: skip defaults, just pass through with app first.
  ARGS=("portal.app:app" "$@")
fi

echo "→ cd $REPO_ROOT"
echo "→ $VENV_UVICORN ${ARGS[*]}"
echo
exec "$VENV_UVICORN" "${ARGS[@]}"
