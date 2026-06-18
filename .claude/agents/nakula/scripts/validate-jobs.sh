#!/usr/bin/env bash
# validate-jobs.sh — schema-check .claude/agents/nakula/jobs.yml
# Schema source: .claude/agents/nakula/agent.md §"jobs.yml schema validator"
# Exit 0 = clean. Exit 1 = schema violation (prints details to stderr).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAKULA_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$NAKULA_DIR/../../.." && pwd)"
JOBS_YML="$NAKULA_DIR/jobs.yml"
VENV_PY="$REPO_ROOT/.venv/bin/python3"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: $VENV_PY not found. Set up the repo venv (see lib/yudhi-py.sh)." >&2
  exit 2
fi

exec "$VENV_PY" - "$JOBS_YML" <<'PY'
import re
import sys
from pathlib import Path

import yaml

VALID_ON_FAILURE = {"alert-slack", "alert-file", "alert-email", "none"}
CRON_RE = re.compile(r"^[\d*/,\-]+\s+[\d*/,\-]+\s+[\d*/,\-]+\s+[\d*/,\-]+\s+[\d*/,\-]+$")


def fail(msg: str) -> None:
    print(f"jobs.yml ✗ {msg}", file=sys.stderr)
    sys.exit(1)


path = Path(sys.argv[1])
if not path.exists():
    fail(f"file not found: {path}")

with path.open() as f:
    data = yaml.safe_load(f)

if not isinstance(data, dict) or "jobs" not in data:
    fail("top-level must be a mapping with a 'jobs' key")
jobs = data["jobs"]
if not isinstance(jobs, list):
    fail("'jobs' must be a list")
if not jobs:
    fail("'jobs' is empty — at least one job required")

seen_names = set()
for idx, job in enumerate(jobs):
    where = f"jobs[{idx}]"
    if not isinstance(job, dict):
        fail(f"{where} must be a mapping")

    name = job.get("name")
    if not isinstance(name, str) or not name:
        fail(f"{where}.name must be a non-empty string")
    where = f"jobs[{idx}] ({name})"
    if name in seen_names:
        fail(f"{where}: duplicate job name")
    seen_names.add(name)

    schedule = job.get("schedule")
    if not isinstance(schedule, str) or not CRON_RE.match(schedule):
        fail(f"{where}.schedule must be a 5-field cron expression, got {schedule!r}")

    command = job.get("command")
    if not isinstance(command, str) or not command:
        fail(f"{where}.command must be a non-empty string")

    tm = job.get("timeout_minutes")
    if not isinstance(tm, int) or isinstance(tm, bool) or tm <= 0:
        fail(f"{where}.timeout_minutes must be a positive int, got {tm!r}")

    retry = job.get("retry")
    if not isinstance(retry, bool):
        fail(f"{where}.retry must be a bool, got {retry!r}")

    on_failure = job.get("on_failure", "none")
    if on_failure not in VALID_ON_FAILURE:
        fail(f"{where}.on_failure must be one of {sorted(VALID_ON_FAILURE)}, got {on_failure!r}")

    ufc = job.get("upstream_freshness_check")
    if ufc is not None:
        if not isinstance(ufc, dict):
            fail(f"{where}.upstream_freshness_check must be a mapping")
        ufc_path = ufc.get("path")
        if not isinstance(ufc_path, str) or not ufc_path:
            fail(f"{where}.upstream_freshness_check.path must be a non-empty string")
        max_age = ufc.get("max_age_hours")
        if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age <= 0:
            fail(f"{where}.upstream_freshness_check.max_age_hours must be a positive int")

print(f"jobs.yml ✓ {len(jobs)} job(s): {', '.join(sorted(seen_names))}")
PY
