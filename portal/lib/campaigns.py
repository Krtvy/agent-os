"""
Campaign coordinator (M4) — placeholder for now.

Local JSON storage at `_private/campaigns.json` of the form:
  [
    {"id": "...", "name": "MagAshwa May Push", "product": "MagAshwa",
     "start_date": "...", "end_date": "...", "brief_md": "...",
     "assigned": [{"poc": "trupti", "handles": [...]}],
     "created_at": "..."},
    ...
  ]

This module is intentionally minimal in M4. It exposes:
  - list_campaigns()
  - get_campaign(id)
  - create_campaign(name, product, dates, brief, assignments)
  - mark_creator_status(campaign_id, handle, status)   # confirmed/declined/posted

The "posted" attribution is derived live from tt_video at view time —
we don't store it.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_PORTAL_DIR = Path(__file__).resolve().parents[1]
_STORE = _PORTAL_DIR.parent / "_private" / "campaigns.json"
_FILE_LOCK = Lock()


def _read() -> list[dict]:
    if not _STORE.exists():
        return []
    try:
        return json.loads(_STORE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _write(data: list[dict]) -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    with _FILE_LOCK:
        _STORE.write_text(json.dumps(data, indent=2, sort_keys=True))


def list_campaigns() -> list[dict]:
    return sorted(_read(), key=lambda c: c.get("start_date", ""), reverse=True)


def get_campaign(campaign_id: str) -> dict | None:
    return next((c for c in _read() if c.get("id") == campaign_id), None)


def create_campaign(
    name: str, product: str, start_date: str, end_date: str,
    brief_md: str, assignments: list[dict],
) -> dict:
    if not name.strip():
        raise ValueError("name required")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date):
        raise ValueError("start_date must be YYYY-MM-DD")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", end_date):
        raise ValueError("end_date must be YYYY-MM-DD")
    campaign = {
        "id": uuid.uuid4().hex[:12],
        "name": name.strip(),
        "product": product.strip(),
        "start_date": start_date,
        "end_date": end_date,
        "brief_md": brief_md.strip(),
        "assignments": assignments or [],
        "creator_status": {},  # {handle: "confirmed"|"declined"|"posted"|"pending"}
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data = _read()
    data.append(campaign)
    _write(data)
    return campaign


def mark_creator_status(campaign_id: str, handle: str, status: str) -> dict:
    if status not in ("pending", "confirmed", "declined", "posted"):
        raise ValueError("invalid status")
    data = _read()
    for c in data:
        if c.get("id") == campaign_id:
            c.setdefault("creator_status", {})[handle] = status
            _write(data)
            return c
    raise KeyError(f"campaign {campaign_id} not found")
