"""
Result cache for static reports + pivot runs.

Per-POC cache index at pocs/<poc>/cache.json mapping a stable hash of
(report_slug + params) → an existing task_id. When the POC submits the
same query within TTL, we redirect them to the already-completed
deliverable instead of re-executing the SQL.

Cache is scoped per POC so trupti's cache hits don't leak kartavvya's
task_ids (per-POC isolation that the runtime already enforces).

Bypass: append ?refresh=1 to the run URL.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .status import read_status
from .storage import POCS_ROOT, find_deliverable

CACHE_TTL_HOURS = int(os.getenv("PORTAL_CACHE_TTL_HOURS", "24"))


def _cache_path(poc_slug: str) -> Path:
    d = POCS_ROOT / poc_slug
    d.mkdir(parents=True, exist_ok=True)
    return d / "cache.json"


def _read(poc_slug: str) -> dict:
    p = _cache_path(poc_slug)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def _write(poc_slug: str, data: dict) -> None:
    p = _cache_path(poc_slug)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str))
    os.replace(tmp, p)


def query_hash(kind: str, slug: str, params: dict) -> str:
    """Stable 16-char hash from (kind, slug, sorted params).

    `kind` distinguishes "report" from "pivot" so the namespaces never
    collide even if a pivot happens to have the same slug shape.
    """
    # Drop volatile internal params (anything starting with _) so the
    # cache key is stable across runs even when bound list params change
    # order. We hash the canonical user-facing inputs only.
    clean = {k: v for k, v in (params or {}).items() if not k.startswith("_")}
    blob = f"{kind}::{slug}::" + json.dumps(clean, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def get_cached(poc_slug: str, q_hash: str) -> str | None:
    """Return a task_id if the query is cached AND the deliverable still
    exists AND status is ok or running. Otherwise None.

    Running tasks are returned so that a duplicate submission during a
    long-running query redirects to the same task instead of starting a
    second one.
    """
    cache = _read(poc_slug)
    entry = cache.get(q_hash)
    if not entry:
        return None
    try:
        cached_at = datetime.fromisoformat(entry["cached_at"])
    except (KeyError, ValueError):
        return None
    if datetime.now(timezone.utc) - cached_at > timedelta(hours=CACHE_TTL_HOURS):
        return None
    task_id = entry.get("task_id")
    if not task_id:
        return None
    deliv = find_deliverable(poc_slug, task_id)
    if deliv is None:
        return None
    status_doc = read_status(deliv) or {}
    if status_doc.get("status") not in ("ok", "running"):
        return None
    return task_id


def set_cached(poc_slug: str, q_hash: str, task_id: str, summary: str = "") -> None:
    cache = _read(poc_slug)
    cache[q_hash] = {
        "task_id": task_id,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }
    # Trim to last 200 entries per POC to keep file tiny.
    if len(cache) > 200:
        cache = dict(sorted(cache.items(), key=lambda kv: kv[1].get("cached_at", ""), reverse=True)[:200])
    _write(poc_slug, cache)


def invalidate(poc_slug: str, q_hash: str) -> None:
    cache = _read(poc_slug)
    if cache.pop(q_hash, None) is not None:
        _write(poc_slug, cache)
