"""
Tracker subsystem — render any CSV that has a Creator column + a POC column
as a portal-native table, with per-POC vs operator views and live DB
enrichment per row.

How to add a new tracker (≤30 seconds):
  1. Drop the CSV into `portal/trackers/`.
  2. Add one entry to TRACKERS below with id, title, filename, optional
     skip_rows, and the column names that identify Creator + POC.
  3. (Optional) set `product` to enable cross-link to the dashboard's
     product filter.
  Done — it appears at /trackers/<id> immediately.

The CSV is shown column-for-column as the team filled it in. Extra
"live" columns (current 30d GMV, days silent, status) get prepended so
the POC can compare their tracker numbers against the live DB at a
glance.
"""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from .creator_events import STATUS_EMOJI, STATUS_LABEL, current_status
from .db import get_conn
from .memcache import cached
from . import tracker_data as _tdata
from .tracker_schema import AUTO_FIELDS, MANUAL_FIELDS

_PORTAL_DIR = Path(__file__).resolve().parents[1]
TRACKERS_DIR = _PORTAL_DIR / "trackers"


# ────────────────────────────────────────────────────────────────────
# Registry — one entry per tracker. Adding a new tracker = one entry.
# ────────────────────────────────────────────────────────────────────

TRACKERS: dict[str, dict] = {
    "magashwa": {
        "id": "magashwa",
        "title": "MagAshwa Tracker",
        "emoji": "💎",
        "csv": "magashwa_tracker.csv",
        "product": "MagAshwa",
        "creator_col": "Creator",
        "poc_col": "POC",
        "skip_rows": 0,
        "description": (
            "May 2026 retainer / GMV / video targets for creators on the "
            "MagAshwa product deal."
        ),
    },
    "hgr": {
        "id": "hgr",
        "title": "HGR Tracker",
        "emoji": "🌱",
        "csv": "hgr_tracker.csv",
        "product": "HGR",
        "creator_col": "Creator",
        "poc_col": "POC",
        "skip_rows": 1,  # first row is grand-totals, second row is headers
        "description": (
            "Full HGR roster — retainer status, deals, targets, samples, "
            "and per-month video / GMV history."
        ),
    },
}


def list_trackers() -> list[dict]:
    """Trackers visible to operators + meta. Each entry has row counts
    once the CSV exists on disk."""
    out: list[dict] = []
    for t in TRACKERS.values():
        path = TRACKERS_DIR / t["csv"]
        exists = path.exists()
        n_rows = 0
        if exists:
            try:
                with path.open(newline="", encoding="utf-8-sig") as f:
                    for _ in range(t.get("skip_rows", 0)):
                        next(f, None)
                    r = csv.reader(f)
                    next(r, None)  # header
                    n_rows = sum(1 for _ in r)
            except OSError:
                pass
        out.append({**t, "exists": exists, "row_count": n_rows})
    return out


def get_tracker(tracker_id: str) -> dict | None:
    t = TRACKERS.get(tracker_id)
    if not t:
        return None
    path = TRACKERS_DIR / t["csv"]
    return {**t, "exists": path.exists(), "path": str(path)}


def _parse_csv(meta: dict) -> tuple[list[str], list[dict]]:
    """Return (column_names, rows) for the tracker, after skipping any
    pre-header rows. Strips empty/duplicate column names."""
    path = TRACKERS_DIR / meta["csv"]
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for _ in range(meta.get("skip_rows", 0)):
            next(f, None)
        reader = csv.DictReader(f)
        # csv.DictReader handles duplicate column names by appending suffixes;
        # we just need to be sure the fieldnames list isn't None.
        cols = [c for c in (reader.fieldnames or []) if c and c.strip()]
        rows = [r for r in reader]
    return cols, rows


def _filter_by_poc(rows: list[dict], poc_col: str, poc_name: str) -> list[dict]:
    """Return only rows where the POC column matches the given POC name,
    case-insensitive, stripped."""
    needle = (poc_name or "").strip().lower()
    return [
        r for r in rows
        if (r.get(poc_col) or "").strip().lower() == needle
    ]


# ────────────────────────────────────────────────────────────────────
# Live enrichment — pull current numbers per creator from the DB.
# Cheap because we batch one query for the entire creator set.
# ────────────────────────────────────────────────────────────────────


# Cached for 300s. The `creators` list is normalized to a sorted tuple in
# the key_fn so two callers with the same roster (same date range) share
# the cached result. Only the DB-derived auto columns are cached here —
# manual POC edits live in tracker_data JSON and are read fresh on every
# render, so cell edits remain instant.
@cached(
    ttl_seconds=300,
    key_fn=lambda creators, today, range_start=None, range_end=None:
        (tuple(sorted(creators)), today, range_start, range_end),
)
def _live_metrics_batch(
    creators: list[str],
    today: date,
    range_start: date | None = None,
    range_end: date | None = None,
) -> dict[str, dict]:
    """For each creator, compute window-aware metrics:
      - videos_in_range: videos posted in [range_start, range_end]
      - gmv_in_range:    GMV for orders dated in window (any source)
      - nv_gmv_in_range: GMV for orders in window FROM videos also posted in window
                         (== the canonical "New Video GMV" per the glossary)
      - last_post / days_silent: roster-wide, not window-bounded
    Single trip per metric (3 queries total).
    """
    if not creators:
        return {}
    rs = range_start or (today - timedelta(days=29))
    re_ = range_end or today
    # 1) GMV in range + NV GMV in range (joins to a video lookup of post times)
    gmv_sql = """
        WITH video_lookup AS (
          SELECT DISTINCT ON (video_id) video_id, handle, post_time
          FROM tiktok_raw_data.tt_video
          WHERE handle = ANY(%(c)s::text[]) AND post_time IS NOT NULL
          ORDER BY video_id, post_time DESC
        )
        SELECT a.creator_username,
               COUNT(DISTINCT t.order_id) AS orders_in_range,
               SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                 + COALESCE(t.sku_platform_discount, 0)) AS gmv_in_range,
               SUM(CASE WHEN a.content_type = 'Video'
                          AND vl.post_time IS NOT NULL
                          AND DATE(vl.post_time - INTERVAL '8 hours') BETWEEN %(rs)s AND %(re)s
                        THEN COALESCE(t.sku_subtotal_after_discount, 0)
                           + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS nv_gmv_in_range
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        LEFT JOIN video_lookup vl
          ON a.content_type = 'Video' AND vl.video_id = a.content_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(rs)s AND %(re)s
          AND a.creator_username = ANY(%(c)s::text[])
        GROUP BY a.creator_username
    """
    # 2) Posts: last_post (no bound) + videos in range
    posts_sql = """
        SELECT handle,
               MAX(DATE(post_time - INTERVAL '8 hours')) AS last_d,
               COUNT(DISTINCT CASE WHEN DATE(post_time - INTERVAL '8 hours') BETWEEN %(rs)s AND %(re)s THEN video_id END) AS vids_in_range
        FROM tiktok_raw_data.tt_video
        WHERE handle = ANY(%(c)s::text[]) AND post_time IS NOT NULL
        GROUP BY handle
    """
    out: dict[str, dict] = {
        h: {
            "gmv_in_range": 0.0, "orders_in_range": 0, "nv_gmv_in_range": 0.0,
            "videos_in_range": 0, "last_post": None, "days_silent": None,
        }
        for h in creators
    }
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(gmv_sql, {"rs": rs, "re": re_, "c": creators})
            for h, n_ord, gmv, nv_gmv in cur.fetchall():
                if h in out:
                    out[h]["orders_in_range"] = int(n_ord or 0)
                    out[h]["gmv_in_range"]    = float(gmv or 0)
                    out[h]["nv_gmv_in_range"] = float(nv_gmv or 0)
            cur.execute(posts_sql, {"rs": rs, "re": re_, "c": creators})
            for h, last, n_vid in cur.fetchall():
                if h in out:
                    out[h]["last_post"] = last.isoformat() if last else None
                    out[h]["videos_in_range"] = int(n_vid or 0)
                    out[h]["days_silent"] = (today - last).days if last else None
    return out


def enrich_rows(rows: list[dict], creator_col: str, poc_slug_for_status: str | None = None) -> list[dict]:
    """Add `_live` block to each row keyed by creator. `_live` contains:
        gmv_30d, orders_30d, videos_30d, last_post, days_silent, status_*
    """
    today = date.today()
    handles = sorted({
        (r.get(creator_col) or "").strip().lower()
        for r in rows
        if r.get(creator_col)
    } - {""})
    metrics = _live_metrics_batch(list(handles), today)
    for r in rows:
        h = (r.get(creator_col) or "").strip().lower()
        live = metrics.get(h, {"gmv_30d": 0.0, "orders_30d": 0, "videos_30d": 0, "last_post": None, "days_silent": None})
        # Status: read from creator_events for the viewing POC if available
        if poc_slug_for_status and h:
            key = current_status(poc_slug_for_status, h)
            live["status_key"] = key
            live["status_label"] = STATUS_LABEL.get(key, key)
            live["status_emoji"] = STATUS_EMOJI.get(key, "")
        r["_live"] = live
        r["_handle"] = h
    return rows


# ────────────────────────────────────────────────────────────────────
# Top-level entry point used by the route.
# ────────────────────────────────────────────────────────────────────


def load_tracker_view(
    tracker_id: str,
    poc_name: str | None = None,
    poc_slug_for_status: str | None = None,
) -> dict:
    """Compose the full view context for /trackers/<id>.

    Args:
      tracker_id: registry key
      poc_name: if given, filter rows where POC col matches; otherwise show all
      poc_slug_for_status: slug used to look up creator_events for status pills

    Returns context: {tracker, columns, rows, totals, view, error?}
    """
    meta = get_tracker(tracker_id)
    if not meta:
        return {"error": f"Unknown tracker: {tracker_id}", "tracker": None}
    if not meta["exists"]:
        return {
            "error": f"CSV file missing: {meta['csv']}. Drop it in portal/trackers/.",
            "tracker": meta,
        }
    cols, rows = _parse_csv(meta)
    # Filter by POC if asked
    if poc_name:
        rows = _filter_by_poc(rows, meta["poc_col"], poc_name)
    # Enrich
    rows = enrich_rows(rows, meta["creator_col"], poc_slug_for_status)
    # Aggregate totals across visible rows
    total_gmv_30d = sum(float(r["_live"].get("gmv_30d") or 0) for r in rows)
    total_orders_30d = sum(int(r["_live"].get("orders_30d") or 0) for r in rows)
    total_videos_30d = sum(int(r["_live"].get("videos_30d") or 0) for r in rows)
    silent_count = sum(1 for r in rows if (r["_live"].get("days_silent") or 0) >= 14)
    return {
        "tracker": meta,
        "columns": cols,
        "rows": rows,
        "totals": {
            "rows": len(rows),
            "gmv_30d": total_gmv_30d,
            "orders_30d": total_orders_30d,
            "videos_30d": total_videos_30d,
            "silent_count": silent_count,
        },
        "view": "poc" if poc_name else "operator",
        "viewing_poc": poc_name,
    }


# ════════════════════════════════════════════════════════════════════
# Editable tracker view — reads from the portal-managed JSON store
# (tracker_data.py), enriched with live DB columns per row.
# ════════════════════════════════════════════════════════════════════

def _default_half_month_bounds(today: date) -> tuple[date, date]:
    """Return current half-month [start, end] for the date range default."""
    import calendar
    if today.day <= 15:
        return date(today.year, today.month, 1), date(today.year, today.month, 15)
    last = calendar.monthrange(today.year, today.month)[1]
    return date(today.year, today.month, 16), date(today.year, today.month, last)


def load_editable_view(
    tracker_id: str,
    poc_name: str | None = None,
    poc_slug_for_status: str | None = None,
    include_removed: bool = False,
    range_start: date | None = None,
    range_end: date | None = None,
) -> dict:
    """Compose the editable tracker context. Auto-columns are computed
    against [range_start, range_end] — defaults to the current half-month
    when callers don't supply dates.
    """
    meta = get_tracker(tracker_id)
    if not meta:
        return {"error": f"Unknown tracker: {tracker_id}", "tracker": None}
    stored = _tdata.list_rows(tracker_id, include_removed=include_removed)
    if poc_name:
        needle = poc_name.strip().lower()
        stored = [r for r in stored if (r.get("poc") or "").strip().lower() == needle]
    today = date.today()
    if not (range_start and range_end):
        range_start, range_end = _default_half_month_bounds(today)
    handles = sorted({(r.get("handle") or "").strip().lower() for r in stored if r.get("handle")} - {""})
    metrics = _live_metrics_batch(list(handles), today, range_start, range_end)
    for r in stored:
        h = (r.get("handle") or "").strip().lower()
        live = metrics.get(h, {
            "gmv_in_range": 0.0, "orders_in_range": 0, "nv_gmv_in_range": 0.0,
            "videos_in_range": 0, "last_post": None, "days_silent": None,
        })
        if poc_slug_for_status and h:
            key = current_status(poc_slug_for_status, h)
            live["status_key"] = key
            live["status_label"] = STATUS_LABEL.get(key, key)
            live["status_emoji"] = STATUS_EMOJI.get(key, "")
        r["_live"] = live
    total_gmv      = sum(float(r["_live"].get("gmv_in_range")    or 0) for r in stored)
    total_nv_gmv   = sum(float(r["_live"].get("nv_gmv_in_range") or 0) for r in stored)
    total_videos   = sum(int(r["_live"].get("videos_in_range")   or 0) for r in stored)
    silent_count   = sum(1 for r in stored if (r["_live"].get("days_silent") or 0) >= 14)
    return {
        "tracker": meta,
        "columns_auto":   list(AUTO_FIELDS),
        "columns_manual": MANUAL_FIELDS.get(tracker_id, []),
        "rows": stored,
        "range_start": range_start.isoformat(),
        "range_end": range_end.isoformat(),
        "totals": {
            "rows": len(stored),
            "gmv_in_range": total_gmv,
            "nv_gmv_in_range": total_nv_gmv,
            "videos_in_range": total_videos,
            "silent_count": silent_count,
        },
        "view": "poc" if poc_name else "operator",
        "viewing_poc": poc_name,
    }

