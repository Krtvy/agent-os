"""
status.json — written next to result.csv + audit.md, polled by /result page.

Schema:
{
  "status": "running" | "ok" | "error",
  "task_id": "...",
  "poc_slug": "...",
  "report_slug": "...",
  "started_at": "ISO8601",
  "ended_at":   "ISO8601 | null",
  "row_count":  int | null,
  "error":      "str | null"
}

Atomic writes: write to a tmp file, then rename. Prevents the /result page
from reading a half-written file mid-update.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def write_status(out_dir: Path, **fields) -> None:
    path = out_dir / "status.json"
    tmp = path.with_suffix(".json.tmp")
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing.update(fields)
    tmp.write_text(json.dumps(existing, indent=2))
    os.replace(tmp, path)


def read_status(out_dir: Path) -> dict | None:
    path = out_dir / "status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
