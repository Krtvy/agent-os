"""
POC ↔ creator mapping loader.

Source of truth: portal/May Sheet PoC.csv (header: Creator,POC).

Loaded once at import time, cached in-process. Handles the data-quality
quirks in the source file:
  - leading/trailing whitespace on handle and POC name
  - stray double-quotes in handle field
  - "#N/A" / empty POC values → row skipped
  - "Unassigned" POC value → kept in the map but excluded from the
    POC dropdown (so you can still see who's unassigned in audits)
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

PORTAL_DIR = Path(__file__).resolve().parents[1]
SHEET_PATH = PORTAL_DIR / "May Sheet PoC.csv"
POCS_ROOT = PORTAL_DIR.parent / "pocs"

_cache: dict[str, str] | None = None


def _load() -> dict[str, str]:
    """Return {creator_handle (lowercase): poc_name (original case)}."""
    global _cache
    if _cache is not None:
        return _cache
    out: dict[str, str] = {}
    if not SHEET_PATH.exists():
        _cache = out
        return out
    with SHEET_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            creator = (row.get("Creator") or "").strip().strip('"').lower()
            poc = (row.get("POC") or "").strip()
            if not creator or not poc:
                continue
            if poc in ("#N/A", "N/A"):
                continue
            out[creator] = poc
    _cache = out
    return out


def get_poc_for_creator(handle: str) -> str | None:
    if not handle:
        return None
    return _load().get(handle.strip().lower())


def get_creators_for_poc(poc: str) -> list[str]:
    """Return creators owned by `poc`.

    The portal-managed JSON at pocs/<slug>/creators.json is the source
    of truth. First time a POC's roster is accessed, we seed it ONCE
    from the historical May Sheet PoC.csv so they don't start empty —
    after that, every add/remove flows through the JSON; the CSV is
    never re-consulted.
    """
    target_name = (poc or "").strip()
    if not target_name:
        return []
    slug = poc_slug_from_name(target_name)
    return _read_managed_or_seed(slug, target_name)


# ─── Managed roster (per-POC, editable) ──────────────────────────────


CREATORS_FILE = "creators.json"


def poc_slug_from_name(poc_name: str) -> str:
    """'Trupti' → 'trupti'."""
    return (poc_name or "").strip().lower()


def poc_name_from_slug(slug: str) -> str:
    """'trupti' → 'Trupti'. Convention: title-cased single token."""
    return (slug or "").strip().lower().title()


def _managed_path(slug: str) -> Path:
    d = POCS_ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d / CREATORS_FILE


def _read_managed(slug: str) -> list[str] | None:
    """Return the list if creators.json exists, else None (not seeded yet)."""
    p = _managed_path(slug)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        return [c for c in data.get("creators", []) if c]
    except json.JSONDecodeError:
        return None


def _write_managed(slug: str, creators: list[str]) -> None:
    """Atomic write of pocs/<slug>/creators.json. Also invalidates any
    cached dashboard payloads for this POC — roster changed, every
    aggregate that used the old creator set is now stale."""
    cleaned = sorted({c.strip().lower().lstrip("@") for c in creators if c and c.strip()})
    payload = {
        "creators": cleaned,
        "count": len(cleaned),
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    p = _managed_path(slug)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(p)
    _invalidate_dashboard_cache(slug)


def _invalidate_dashboard_cache(slug: str) -> None:
    """Delete all dashboard_cache_*.json files for this POC. Called from
    _write_managed so every roster add/remove/bulk path invalidates."""
    d = POCS_ROOT / slug
    if not d.exists():
        return
    for cache_file in d.glob("dashboard_cache_*.json"):
        try:
            cache_file.unlink()
        except OSError:
            pass


def _seed_from_csv(slug: str, poc_name: str) -> list[str]:
    """One-time seed of pocs/<slug>/creators.json from the historical
    May Sheet PoC.csv. Called ONLY when the JSON file does not yet
    exist. After this, the CSV is never read again for this POC.
    """
    csv_map = _load()
    seed = sorted({c for c, n in csv_map.items() if n.lower() == poc_name.lower()})
    _write_managed(slug, seed)
    return seed


def _read_managed_or_seed(slug: str, poc_name: str) -> list[str]:
    existing = _read_managed(slug)
    if existing is not None:
        return existing
    return _seed_from_csv(slug, poc_name)


def add_creator(slug: str, handle: str) -> list[str]:
    """Add a creator handle to a POC's roster. Returns the new full list.
    Seeds from CSV first if this POC's roster doesn't exist yet, so the
    historical creators aren't lost when they add a new one."""
    poc_name = poc_name_from_slug(slug)
    cur = _read_managed_or_seed(slug, poc_name)
    handle = handle.strip().lower().lstrip("@")
    if handle and handle not in cur:
        cur = sorted(set(cur) | {handle})
    _write_managed(slug, cur)
    return cur


def remove_creator(slug: str, handle: str) -> list[str]:
    """Remove a handle from a POC's roster. Returns the new full list.
    Seeds from CSV first if this POC's roster doesn't exist yet."""
    poc_name = poc_name_from_slug(slug)
    cur = _read_managed_or_seed(slug, poc_name)
    handle = handle.strip().lower().lstrip("@")
    cur = [c for c in cur if c != handle]
    _write_managed(slug, cur)
    return cur


def bulk_add_creators(slug: str, handles: list[str]) -> dict:
    """Add many creators at once. Returns {added, skipped, invalid} counts
    and the resulting full roster.

    - Normalises each handle (lowercase, strip whitespace + leading @)
    - Skips empties and handles that don't match the safe charset
    - Skips handles already in the roster
    - One file write at the end instead of one per handle
    """
    poc_name = poc_name_from_slug(slug)
    cur_list = _read_managed_or_seed(slug, poc_name)
    cur_set = set(cur_list)
    added = 0
    skipped_existing = 0
    invalid = 0
    seen_in_input: set[str] = set()
    for raw in handles:
        clean = (raw or "").strip().lower().lstrip("@")
        if not clean:
            continue
        # Permissive validation — TikTok handles: letters, digits, dot,
        # underscore, hyphen. 1–64 chars.
        import re
        if not re.match(r"^[a-z0-9._-]{1,64}$", clean):
            invalid += 1
            continue
        if clean in cur_set:
            skipped_existing += 1
            continue
        if clean in seen_in_input:
            skipped_existing += 1
            continue
        seen_in_input.add(clean)
        cur_set.add(clean)
        added += 1
    _write_managed(slug, sorted(cur_set))
    return {
        "added": added,
        "skipped_existing": skipped_existing,
        "invalid": invalid,
        "total_after": len(cur_set),
    }


def roster_meta(slug: str) -> dict:
    """Return the full payload (creators + updated_at + count). For UI.

    If the POC's roster doesn't exist yet, seeds it from the historical
    CSV so they see their existing creators on first visit. After that,
    the roster is portal-managed and the CSV is never re-read.
    """
    p = _managed_path(slug)
    if not p.exists():
        _read_managed_or_seed(slug, poc_name_from_slug(slug))
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {"creators": [], "count": 0, "updated_at": None}


# Canonical POC list — the 8 POCs at Rootlabs. Update this tuple if the
# team changes. The portal does NOT derive this from any CSV; each POC's
# roster lives at pocs/<slug>/creators.json and is portal-managed.
KNOWN_POCS: tuple[str, ...] = (
    "Trupti",
    "Khushi",
    "Manini",
    "Rachit",
    "Vansh",
    "Chanchal",
    "Shivangi",
    "Saniya",
)


def all_pocs() -> list[str]:
    """The 8 POCs at Rootlabs."""
    return list(KNOWN_POCS)


def total_creators() -> int:
    """Sum of all managed rosters across all POCs."""
    n = 0
    for poc in KNOWN_POCS:
        slug = poc_slug_from_name(poc)
        n += len(_read_managed(slug) or [])
    return n


def reload_cache() -> None:
    global _cache
    _cache = None
