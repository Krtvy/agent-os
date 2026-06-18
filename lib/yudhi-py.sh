#!/usr/bin/env bash
# yudhi-py.sh — invoke Python with Yudhishthira's pandas venv.
#
# Why: system `python3` does not have pandas. Yudhishthira's P5b (pandas path)
# needs the `.venv` Python (Python 3.12 + pandas 3.0.x, installed via `uv`).
# Skill manual references this wrapper so the dependency is explicit and the
# agent does not silently fail on `import pandas`.
#
# Usage:
#   lib/yudhi-py.sh -c "import pandas; print(pandas.__version__)"
#   lib/yudhi-py.sh path/to/script.py arg1 arg2
#   cat script.py | lib/yudhi-py.sh -    (stdin pipe; '-' is required)
#
# Exit codes:
#   0  — Python ran (its own exit code is preserved)
#   1  — .venv/bin/python3 not found or not executable (setup hint emitted)
#   64 — usage error (no args)
#
# Reproducing the venv if missing:
#   cd <repo-root>
#   uv venv
#   uv pip install pandas

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/.venv/bin/python3"

if [[ "$#" -lt 1 ]]; then
  echo "usage: yudhi-py.sh <python-args>" >&2
  echo "  e.g.  yudhi-py.sh -c 'import pandas; print(pandas.__version__)'" >&2
  exit 64
fi

if [[ ! -x "$VENV_PY" ]]; then
  cat >&2 <<EOF
yudhi-py: $VENV_PY not found or not executable.

To rebuild the venv:
  cd $REPO_ROOT
  uv venv
  uv pip install pandas

Or, if you prefer pip directly:
  python3.12 -m venv .venv
  .venv/bin/pip install pandas
EOF
  exit 1
fi

exec "$VENV_PY" "$@"
