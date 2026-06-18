"""
Per-POC creator notes — local JSON storage.

Each POC has a `pocs/<slug>/creator_notes.json` file:
  {
    "<creator_handle>": [
      {"id": "...", "body_md": "...", "is_shared": false, "created_at": "..."},
      ...
    ],
    ...
  }

Privacy model (M1 decision):
  - Private by default to the POC who wrote it.
  - Per-note `is_shared` toggle promotes a note to team-visible.
  - When rendering on a creator card, we load *this POC's* notes + any
    other POC's notes that are flagged is_shared=True.

Schema is intentionally local-JSON to avoid touching production Supabase
tonight. Migrate to a `creator_notes` table later.
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


def _notes_path(poc_slug: str) -> Path:
    if not _SLUG_RE.match(poc_slug):
        raise ValueError(f"invalid POC slug: {poc_slug!r}")
    d = _POCS_ROOT / poc_slug
    d.mkdir(parents=True, exist_ok=True)
    return d / "creator_notes.json"


def _read(poc_slug: str) -> dict[str, list[dict]]:
    p = _notes_path(poc_slug)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _write(poc_slug: str, data: dict[str, list[dict]]) -> None:
    p = _notes_path(poc_slug)
    with _FILE_LOCK:
        p.write_text(json.dumps(data, indent=2, sort_keys=True))


def list_for_creator(poc_slug: str, handle: str) -> list[dict]:
    """Return notes this POC sees for `handle`: their own notes + any
    shared notes from other POCs (each tagged with author_slug).
    Sorted newest-first.
    """
    if not _HANDLE_RE.match(handle):
        return []
    own = _read(poc_slug).get(handle, [])
    own_tagged = [{**n, "author_slug": poc_slug, "is_own": True} for n in own]
    # Pull shared notes from every other POC's file.
    shared: list[dict] = []
    if _POCS_ROOT.exists():
        for sub in _POCS_ROOT.iterdir():
            if not sub.is_dir() or sub.name == poc_slug:
                continue
            if not _SLUG_RE.match(sub.name):
                continue
            other = _read(sub.name).get(handle, [])
            for n in other:
                if n.get("is_shared"):
                    shared.append({**n, "author_slug": sub.name, "is_own": False})
    combined = own_tagged + shared
    combined.sort(key=lambda n: n.get("created_at", ""), reverse=True)
    return combined


def add(poc_slug: str, handle: str, body_md: str, is_shared: bool = False) -> dict:
    if not _HANDLE_RE.match(handle):
        raise ValueError(f"invalid handle: {handle!r}")
    body_md = (body_md or "").strip()
    if not body_md:
        raise ValueError("note body cannot be empty")
    if len(body_md) > 5000:
        body_md = body_md[:5000]
    note = {
        "id": uuid.uuid4().hex[:12],
        "body_md": body_md,
        "is_shared": bool(is_shared),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data = _read(poc_slug)
    data.setdefault(handle, []).append(note)
    _write(poc_slug, data)
    return {**note, "author_slug": poc_slug, "is_own": True}


def toggle_share(poc_slug: str, handle: str, note_id: str) -> bool:
    """Flip a note's is_shared flag. Returns the new value. Raises if not found."""
    data = _read(poc_slug)
    notes = data.get(handle, [])
    for n in notes:
        if n.get("id") == note_id:
            n["is_shared"] = not n.get("is_shared", False)
            _write(poc_slug, data)
            return bool(n["is_shared"])
    raise KeyError(f"note {note_id} not found")


def delete(poc_slug: str, handle: str, note_id: str) -> None:
    """POC can only delete their own notes."""
    data = _read(poc_slug)
    notes = data.get(handle, [])
    data[handle] = [n for n in notes if n.get("id") != note_id]
    _write(poc_slug, data)
