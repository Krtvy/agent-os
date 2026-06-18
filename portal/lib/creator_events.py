"""
Per-POC creator event log — local JSON storage.

Events are durable, append-only records of POC actions on a creator:
  - status change (cooling_off, active, lost, top_performer, etc.)
  - tag for campaign
  - drafted outreach DM
  - manual data correction
  - anything else worth a timestamp + actor

Each POC has `pocs/<slug>/creator_events.json`:
  {
    "<handle>": [
      {"id": "...", "event_type": "...", "payload": {...},
       "created_at": "...", "author_slug": "..."},
      ...
    ]
  }

Cross-POC visibility: events are PUBLIC across POCs (unlike notes which
are private by default). The whole point of an event log is that anyone
on the team can see what's been happening to a creator.

Status taxonomy used by M3 (Outreach pipeline):
  discovered → outreach_sent → onboarding → active → top_performer
                                              ↓        ↓
                                          cooling_off  lost
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_PORTAL_DIR = Path(__file__).resolve().parents[1]
_POCS_ROOT = _PORTAL_DIR.parent / "pocs"
_HANDLE_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_SLUG_RE = re.compile(r"^[a-z0-9_-]{1,64}$")
_FILE_LOCK = Lock()

# Status taxonomy — the canonical pipeline columns for M3.
STATUSES = (
    "discovered",
    "outreach_sent",
    "onboarding",
    "active",
    "top_performer",
    "cooling_off",
    "lost",
)
STATUS_LABEL = {
    "discovered": "Discovered",
    "outreach_sent": "Outreach sent",
    "onboarding": "Onboarding",
    "active": "Active",
    "top_performer": "Top performer",
    "cooling_off": "Cooling off",
    "lost": "Lost",
}
STATUS_EMOJI = {
    "discovered": "🔍",
    "outreach_sent": "📨",
    "onboarding": "🛬",
    "active": "✅",
    "top_performer": "⭐",
    "cooling_off": "🥶",
    "lost": "💔",
}


def _events_path(poc_slug: str) -> Path:
    if not _SLUG_RE.match(poc_slug):
        raise ValueError(f"invalid POC slug: {poc_slug!r}")
    d = _POCS_ROOT / poc_slug
    d.mkdir(parents=True, exist_ok=True)
    return d / "creator_events.json"


def _read(poc_slug: str) -> dict[str, list[dict]]:
    p = _events_path(poc_slug)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _write(poc_slug: str, data: dict[str, list[dict]]) -> None:
    p = _events_path(poc_slug)
    with _FILE_LOCK:
        p.write_text(json.dumps(data, indent=2, sort_keys=True))


def list_for_creator(poc_slug: str, handle: str, include_other_pocs: bool = True) -> list[dict]:
    """Events for one creator. By default, merges the viewing POC's own
    events with all other POCs' events on this creator (events are
    public across the team).
    """
    if not _HANDLE_RE.match(handle):
        return []
    out: list[dict] = []
    own = _read(poc_slug).get(handle, [])
    out.extend({**e, "author_slug": e.get("author_slug", poc_slug), "is_own": True} for e in own)
    if include_other_pocs and _POCS_ROOT.exists():
        for sub in _POCS_ROOT.iterdir():
            if not sub.is_dir() or sub.name == poc_slug:
                continue
            if not _SLUG_RE.match(sub.name):
                continue
            others = _read(sub.name).get(handle, [])
            out.extend({**e, "author_slug": e.get("author_slug", sub.name), "is_own": False} for e in others)
    out.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    return out


def record(
    poc_slug: str, handle: str, event_type: str,
    payload: dict | None = None,
) -> dict:
    if not _HANDLE_RE.match(handle):
        raise ValueError(f"invalid handle: {handle!r}")
    event_type = (event_type or "").strip()
    if not event_type or not re.match(r"^[a-z_]{1,40}$", event_type):
        raise ValueError(f"invalid event_type: {event_type!r}")
    evt = {
        "id": uuid.uuid4().hex[:12],
        "event_type": event_type,
        "payload": payload or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "author_slug": poc_slug,
    }
    data = _read(poc_slug)
    data.setdefault(handle, []).append(evt)
    _write(poc_slug, data)
    return evt


def current_status(poc_slug: str, handle: str) -> str:
    """Return the most recent status_change event's status, or "discovered"
    if none. Looks across ALL POCs since status is shared.
    """
    events = list_for_creator(poc_slug, handle, include_other_pocs=True)
    for e in events:
        if e.get("event_type") == "status_change":
            s = (e.get("payload") or {}).get("status")
            if s in STATUSES:
                return s
    return "discovered"


def set_status(poc_slug: str, handle: str, new_status: str) -> dict:
    if new_status not in STATUSES:
        raise ValueError(f"invalid status: {new_status!r}")
    return record(poc_slug, handle, "status_change", {"status": new_status})


def all_creator_statuses_for_poc(poc_slug: str, handles: list[str]) -> dict[str, str]:
    """Bulk status lookup for a POC's whole roster — used by the outreach
    kanban so we don't run N queries.
    """
    return {h: current_status(poc_slug, h) for h in handles}
