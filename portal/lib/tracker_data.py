"""
Tracker data store — the editable, portal-managed source of truth.

Storage: `_private/trackers_data/<tracker_id>.json`.
  Shape:
    {
      "creators": [
        {
          "handle": "shopbyjake",
          "poc": "Trupti",
          "manual": { flag, retainer_usd, target_gmv_h1, ... },
          "added_by": "trupti",
          "added_at": "ISO",
          "last_edited_by": "shivangi",
          "last_edited_at": "ISO",
          "removed": false,
          "removed_at": null,
          "removed_by": null
        },
        ...
      ]
    }

Operations (all write through the lock):
  - list_rows(tracker_id, include_removed=False)
  - get_row(tracker_id, handle)
  - add_row(tracker_id, handle, poc, manual, author_slug)
  - update_field(tracker_id, handle, field_key, value, author_slug)
  - remove_row(tracker_id, handle, author_slug)        # soft
  - restore_row(tracker_id, handle, author_slug)
  - seed_from_csv(tracker_id) — one-shot migration; idempotent.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from .tracker_schema import (
    coerce_value,
    empty_manual,
    manual_field_type,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STORE_DIR = _REPO_ROOT / "_private" / "trackers_data"
_LOCK = Lock()

_HANDLE_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_POC_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 -]{0,40}$")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(tracker_id: str) -> Path:
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise ValueError(f"invalid tracker_id: {tracker_id!r}")
    _STORE_DIR.mkdir(parents=True, exist_ok=True)
    return _STORE_DIR / f"{tracker_id}.json"


def _read(tracker_id: str) -> dict:
    p = _path(tracker_id)
    if not p.exists():
        return {"creators": []}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {"creators": []}


def _write(tracker_id: str, data: dict) -> None:
    p = _path(tracker_id)
    with _LOCK:
        p.write_text(json.dumps(data, indent=2, sort_keys=True))


# ────────────────────────────────────────────────────────────────────
# Read
# ────────────────────────────────────────────────────────────────────


def list_rows(tracker_id: str, include_removed: bool = False) -> list[dict]:
    rows = _read(tracker_id).get("creators", [])
    if not include_removed:
        rows = [r for r in rows if not r.get("removed")]
    return rows


def get_row(tracker_id: str, handle: str) -> dict | None:
    for r in _read(tracker_id).get("creators", []):
        if r.get("handle", "").lower() == handle.lower():
            return r
    return None


# ────────────────────────────────────────────────────────────────────
# Write
# ────────────────────────────────────────────────────────────────────


def add_row(
    tracker_id: str, handle: str, poc: str,
    manual: dict | None = None, author_slug: str = "",
) -> dict:
    if not _HANDLE_RE.match(handle):
        raise ValueError(f"invalid handle: {handle!r}")
    if not _POC_RE.match(poc):
        raise ValueError(f"invalid poc: {poc!r}")
    data = _read(tracker_id)
    rows = data.get("creators", [])
    # Already present? Restore if soft-removed, else no-op.
    for r in rows:
        if r.get("handle", "").lower() == handle.lower():
            if r.get("removed"):
                r["removed"] = False
                r["removed_at"] = None
                r["removed_by"] = None
                r["last_edited_by"] = author_slug
                r["last_edited_at"] = _iso_now()
                _write(tracker_id, data)
            return r
    blank = empty_manual(tracker_id)
    if manual:
        for k, v in manual.items():
            if k in blank:
                blank[k] = coerce_value(manual_field_type(tracker_id, k) or "text", v)
    row = {
        "handle": handle.strip(),
        "poc": poc.strip(),
        "manual": blank,
        "added_by": author_slug,
        "added_at": _iso_now(),
        "last_edited_by": author_slug,
        "last_edited_at": _iso_now(),
        "removed": False,
        "removed_at": None,
        "removed_by": None,
    }
    rows.append(row)
    data["creators"] = rows
    _write(tracker_id, data)
    return row


def update_field(
    tracker_id: str, handle: str, field_key: str, raw_value,
    author_slug: str = "",
) -> dict:
    ftype = manual_field_type(tracker_id, field_key)
    if ftype is None:
        raise ValueError(f"unknown manual field: {field_key!r}")
    data = _read(tracker_id)
    for r in data.get("creators", []):
        if r.get("handle", "").lower() == handle.lower():
            r.setdefault("manual", empty_manual(tracker_id))
            r["manual"][field_key] = coerce_value(ftype, raw_value)
            r["last_edited_by"] = author_slug
            r["last_edited_at"] = _iso_now()
            _write(tracker_id, data)
            return r
    raise KeyError(f"handle not in tracker: {handle!r}")


def update_poc(tracker_id: str, handle: str, new_poc: str, author_slug: str = "") -> dict:
    if not _POC_RE.match(new_poc):
        raise ValueError(f"invalid poc: {new_poc!r}")
    data = _read(tracker_id)
    for r in data.get("creators", []):
        if r.get("handle", "").lower() == handle.lower():
            r["poc"] = new_poc.strip()
            r["last_edited_by"] = author_slug
            r["last_edited_at"] = _iso_now()
            _write(tracker_id, data)
            return r
    raise KeyError(f"handle not in tracker: {handle!r}")


def remove_row(tracker_id: str, handle: str, author_slug: str = "") -> dict:
    data = _read(tracker_id)
    for r in data.get("creators", []):
        if r.get("handle", "").lower() == handle.lower():
            r["removed"] = True
            r["removed_at"] = _iso_now()
            r["removed_by"] = author_slug
            _write(tracker_id, data)
            return r
    raise KeyError(f"handle not in tracker: {handle!r}")


def restore_row(tracker_id: str, handle: str, author_slug: str = "") -> dict:
    data = _read(tracker_id)
    for r in data.get("creators", []):
        if r.get("handle", "").lower() == handle.lower():
            r["removed"] = False
            r["removed_at"] = None
            r["removed_by"] = None
            r["last_edited_by"] = author_slug
            r["last_edited_at"] = _iso_now()
            _write(tracker_id, data)
            return r
    raise KeyError(f"handle not in tracker: {handle!r}")


# ────────────────────────────────────────────────────────────────────
# Seed from existing CSV (one-shot, idempotent)
# ────────────────────────────────────────────────────────────────────


_PORTAL_DIR = Path(__file__).resolve().parents[1]
_CSV_DIR = _PORTAL_DIR / "trackers"


def _parse_dollar(raw) -> float:
    if raw is None or raw == "":
        return 0.0
    s = str(raw).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_int(raw) -> int:
    try:
        return int(float(raw)) if raw not in ("", None, "#N/A") else 0
    except (TypeError, ValueError):
        return 0


def _bool_from_csv(raw) -> bool:
    if raw is None: return False
    s = str(raw).strip().lower()
    return s in ("yes", "y", "true", "1", "✓", "x")


def _seed_magashwa(csv_path: Path) -> int:
    """The CSV headers are misaligned with the data (Excel export quirk),
    so we read by POSITION for the columns that are confused, and by
    header for the ones that match.

    Positional map (verified by sampling):
      [0] Creator, [1] POC, [2] Flag(s)
      [4] Retainer $ (header lies — says "Jan Vids")
      [12] Target GMV (header says "GMV" — the real target)
      [13] Target videos (header says "Video")
      [14] Why this target (header says "15 May GMV Target")
      [22] Comment
    """
    added = 0
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # header row
        for row in reader:
            if len(row) < 14:
                continue
            handle = (row[0] or "").strip()
            poc = (row[1] or "").strip()
            if not handle or not poc or not _HANDLE_RE.match(handle):
                continue
            if get_row("magashwa", handle):
                continue
            target_gmv = _parse_dollar(row[12]) if len(row) > 12 else 0
            target_vids = _parse_int(row[13])  if len(row) > 13 else 0
            manual = {
                "flag":             (row[2] or "").strip(),
                "retainer_usd":     _parse_dollar(row[4]) if len(row) > 4 else 0,
                "target_gmv_h1":    target_gmv,
                "target_videos_h1": target_vids,
                "target_gmv_h2":    target_gmv,
                "target_videos_h2": target_vids,
                "why_target":       (row[14] or "").strip() if len(row) > 14 else "",
                "comment":          (row[22] or "").strip() if len(row) > 22 else "",
                "sample_sent":      False,
                "deal_closed":      False,
                "videos_locked":    False,
            }
            try:
                add_row("magashwa", handle, poc, manual=manual, author_slug="seed")
                added += 1
            except ValueError:
                continue
    return added


def _seed_hgr(csv_path: Path) -> int:
    """HGR headers ARE aligned with data (the first row is a totals row that
    we skip, then DictReader picks up the real header). Read by name.
    """
    added = 0
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        next(f, None)  # skip totals row above the header
        reader = csv.DictReader(f)
        for row in reader:
            handle = (row.get("Creator") or "").strip()
            poc = (row.get("POC") or "").strip()
            if not handle or not poc or not _HANDLE_RE.match(handle):
                continue
            if get_row("hgr", handle):
                continue
            target_gmv = _parse_dollar(row.get("15 May GMV Target"))
            target_vids = _parse_int(row.get("15 May video Target"))
            manual = {
                "flag":             (row.get("Flag(s)") or row.get("Flag") or "").strip(),
                "retainer_usd":     _parse_dollar(row.get("Retainer remaining")),
                "target_gmv_h1":    target_gmv,
                "target_videos_h1": target_vids,
                "target_gmv_h2":    target_gmv,
                "target_videos_h2": target_vids,
                "why_target":       (row.get("Why this target") or "").strip(),
                "comment":          "",
                "sample_sent":      _bool_from_csv(row.get("Sample")),
                "deal_closed":      _bool_from_csv(row.get("Deal Closed")),
                "videos_locked":    _bool_from_csv(row.get("Videos Locked")),
            }
            try:
                add_row("hgr", handle, poc, manual=manual, author_slug="seed")
                added += 1
            except ValueError:
                continue
    return added


SEEDERS = {
    "magashwa": ("magashwa_tracker.csv", _seed_magashwa),
    "hgr":      ("hgr_tracker.csv",     _seed_hgr),
}


def seed_from_csv(tracker_id: str) -> int:
    """Idempotent: skip handles that already exist in the store.
    Returns number of rows ADDED in this run."""
    if tracker_id not in SEEDERS:
        raise ValueError(f"no seeder for tracker: {tracker_id!r}")
    csv_name, fn = SEEDERS[tracker_id]
    csv_path = _CSV_DIR / csv_name
    if not csv_path.exists():
        return 0
    return fn(csv_path)
