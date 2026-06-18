"""
POC monthly targets + live achievement.

Two halves of the system:
  - Targets   = PM-curated, stored in _private/poc_targets.json
  - Achieved  = live from the DB, computed against the POC's roster

Half-month periods (Tanmita's convention):
  - H1 = days 1–15 inclusive
  - H2 = days 16 through end-of-month

Period key format: "YYYY-MM-H1" or "YYYY-MM-H2".

Products supported: "hgr", "magashwa". Adding a new product key here +
in the targets JSON is the only change needed to roll out new tracking.
"""

from __future__ import annotations

import calendar
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from .db import get_conn
from .memcache import cached
from .poc_creators import KNOWN_POCS, get_creators_for_poc

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TARGETS_PATH = _REPO_ROOT / "_private" / "poc_targets.json"

# Product registry — extend here to support new products.
# Each maps to the `rootlabs_common_name` we use in DB filters.
PRODUCTS: dict[str, dict] = {
    "hgr":      {"label": "HGR",      "db_name": "HGR",      "emoji": "🌱"},
    "magashwa": {"label": "MagAshwa", "db_name": "MagAshwa", "emoji": "💎"},
}


def _read_targets() -> dict:
    if not _TARGETS_PATH.exists():
        return {}
    try:
        data = json.loads(_TARGETS_PATH.read_text())
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except (json.JSONDecodeError, OSError):
        return {}


def write_targets(payload: dict) -> None:
    """Replace the targets file. Caller responsible for the full payload shape.
    Keeps the README key if present in the existing file."""
    existing = {}
    if _TARGETS_PATH.exists():
        try:
            existing = json.loads(_TARGETS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            existing = {}
    out = {}
    if "_README" in existing:
        out["_README"] = existing["_README"]
    out.update(payload)
    _TARGETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _TARGETS_PATH.write_text(json.dumps(out, indent=2))


# ────────────────────────────────────────────────────────────────────
# Period helpers
# ────────────────────────────────────────────────────────────────────


def current_period(today: date | None = None) -> str:
    """Return the half-month period key for `today` — "YYYY-MM-H1" or "...-H2"."""
    if today is None:
        today = date.today()
    half = "H1" if today.day <= 15 else "H2"
    return f"{today.year:04d}-{today.month:02d}-{half}"


def period_bounds(period_key: str) -> tuple[date, date]:
    """Return (start, end) dates for a period key, inclusive."""
    year_s, month_s, half = period_key.split("-")
    year, month = int(year_s), int(month_s)
    if half == "H1":
        return date(year, month, 1), date(year, month, 15)
    if half == "H2":
        last = calendar.monthrange(year, month)[1]
        return date(year, month, 16), date(year, month, last)
    raise ValueError(f"invalid period key: {period_key!r}")


def list_periods(months_back: int = 6) -> list[str]:
    """Return chronologically-ordered period keys covering the last
    `months_back` months including the current period."""
    today = date.today()
    out: list[str] = []
    cursor = today.replace(day=1)
    for _ in range(months_back):
        out.append(f"{cursor.year:04d}-{cursor.month:02d}-H1")
        out.append(f"{cursor.year:04d}-{cursor.month:02d}-H2")
        # Step back one month
        prev_month = cursor.month - 1
        prev_year = cursor.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        cursor = date(prev_year, prev_month, 1)
    out.sort()
    return out


# ────────────────────────────────────────────────────────────────────
# Live achievement query — one query per (POC × product × period).
# Aggregates GMV + videos against the POC's roster, product-filtered.
# ────────────────────────────────────────────────────────────────────


def _resolve_product_ids(product_db_name: str) -> tuple[list[str], list[str]]:
    sql = """
        SELECT DISTINCT sl.platform_product_id, sl.platform_sku_id
        FROM rootlabs_core.rootlabs_sku_listings sl
        JOIN rootlabs_core.rootlabs_products rp ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE sl.listing_source = 'tiktok' AND rp.rootlabs_common_name = %(p)s
    """
    pids: set[str] = set()
    sids: set[str] = set()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"p": product_db_name})
            for ppid, psid in cur.fetchall():
                if ppid: pids.add(ppid)
                if psid: sids.add(psid)
    return sorted(pids), sorted(sids)


def _achievement(creators: list[str], product_db_name: str, start: date, end: date) -> dict:
    """Return {gmv: float, videos: int, orders: int} achieved for this
    creator set, filtered to this product, within [start, end] (IST days).
    Single SQL round trip combining the video count and orders sum via
    CROSS JOIN of two CTEs.
    """
    if not creators:
        return {"gmv": 0.0, "videos": 0, "orders": 0}
    vpids, osids = _resolve_product_ids(product_db_name)
    if not vpids and not osids:
        return {"gmv": 0.0, "videos": 0, "orders": 0}
    sql = """
        WITH v AS (
          SELECT COUNT(DISTINCT video_id) AS n FROM tiktok_raw_data.tt_video
          WHERE video_id IS NOT NULL AND post_time IS NOT NULL
            AND DATE(post_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND handle = ANY(%(c)s::text[])
            AND product = ANY(%(vpids)s::text[])
        ),
        o AS (
          SELECT COUNT(DISTINCT t.order_id) AS orders,
                 SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                   + COALESCE(t.sku_platform_discount, 0)) AS gmv
          FROM tiktok_raw_data.tiktok_orders t
          JOIN tiktok_raw_data.tiktok_affiliate_orders a
            ON t.order_id = a.order_id AND t.sku_id = a.sku_id
          WHERE t.cancellation_return_type IS NULL
            AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND a.creator_username = ANY(%(c)s::text[])
            AND t.sku_id = ANY(%(osids)s::text[])
        )
        SELECT v.n, o.orders, o.gmv FROM v, o
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {
                "cs": start, "ce": end, "c": creators,
                "vpids": vpids, "osids": osids,
            })
            r = cur.fetchone() or (0, 0, 0)
    return {"videos": int(r[0] or 0), "orders": int(r[1] or 0), "gmv": float(r[2] or 0)}


# Process-wide cache for product ID resolution — small set, changes rarely.
_PRODUCT_ID_CACHE: dict[str, tuple[list[str], list[str]]] = {}
_orig_resolve = _resolve_product_ids
def _resolve_product_ids_cached(product_db_name: str) -> tuple[list[str], list[str]]:
    if product_db_name in _PRODUCT_ID_CACHE:
        return _PRODUCT_ID_CACHE[product_db_name]
    result = _orig_resolve(product_db_name)
    _PRODUCT_ID_CACHE[product_db_name] = result
    return result
_resolve_product_ids = _resolve_product_ids_cached  # noqa: F811


# ────────────────────────────────────────────────────────────────────
# Top-level entry points used by routes.
# ────────────────────────────────────────────────────────────────────


@cached(ttl_seconds=1800)  # 30 min — coordinator scorecard, freshness not critical
def for_poc(poc_slug: str, product_key: str, period_key: str | None = None) -> dict:
    """One POC × one product × one period.
    Returns: target, achieved, gmv_pct, videos_pct, period, dates.
    """
    if period_key is None:
        period_key = current_period()
    if product_key not in PRODUCTS:
        raise ValueError(f"unknown product: {product_key!r}")
    targets = _read_targets()
    poc_targets = targets.get(period_key, {}).get(poc_slug, {}).get(product_key, {})
    gmv_target = float(poc_targets.get("gmv") or 0)
    vid_target = int(poc_targets.get("videos") or 0)
    start, end = period_bounds(period_key)
    creators = get_creators_for_poc(poc_slug.capitalize())  # poc_name expected with capital
    ach = _achievement(creators, PRODUCTS[product_key]["db_name"], start, end)
    return {
        "poc_slug": poc_slug,
        "product_key": product_key,
        "product_label": PRODUCTS[product_key]["label"],
        "product_emoji": PRODUCTS[product_key]["emoji"],
        "period": period_key,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "target": {"gmv": gmv_target, "videos": vid_target},
        "achieved": ach,
        "gmv_pct":  round(ach["gmv"]    / gmv_target * 100) if gmv_target else None,
        "videos_pct": round(ach["videos"] / vid_target * 100) if vid_target else None,
        "creator_count": len(creators),
    }


@cached(ttl_seconds=1800)  # 30 min — coordinator scorecard, freshness not critical
def for_all_pocs(product_key: str, period_key: str | None = None) -> dict:
    """One row per POC, for one product × one period. Used by the Coordinator page."""
    if period_key is None:
        period_key = current_period()
    if product_key not in PRODUCTS:
        raise ValueError(f"unknown product: {product_key!r}")
    targets = _read_targets()
    period_targets = targets.get(period_key, {})
    start, end = period_bounds(period_key)
    db_name = PRODUCTS[product_key]["db_name"]
    # Fan out the per-POC achievement queries; each opens its own DB connection
    # so threads don't race. With 8 POCs and 1 query per call, total wall-time
    # drops from sum(per_poc) to max(per_poc).
    def _row_for(poc_name: str) -> dict:
        slug = poc_name.lower()
        creators = get_creators_for_poc(poc_name)
        pt = period_targets.get(slug, {}).get(product_key, {})
        gmv_target = float(pt.get("gmv") or 0)
        vid_target = int(pt.get("videos") or 0)
        ach = _achievement(creators, db_name, start, end)
        return {
            "poc_name": poc_name,
            "poc_slug": slug,
            "roster": len(creators),
            "target": {"gmv": gmv_target, "videos": vid_target},
            "achieved": ach,
            "gmv_pct":  round(ach["gmv"]    / gmv_target * 100) if gmv_target else None,
            "videos_pct": round(ach["videos"] / vid_target * 100) if vid_target else None,
        }
    with ThreadPoolExecutor(max_workers=len(KNOWN_POCS)) as pool:
        rows: list[dict] = list(pool.map(_row_for, KNOWN_POCS))
    # Sort by GMV achieved desc so high-performers are visible at top
    rows.sort(key=lambda r: r["achieved"]["gmv"], reverse=True)
    return {
        "product_key": product_key,
        "product_label": PRODUCTS[product_key]["label"],
        "product_emoji": PRODUCTS[product_key]["emoji"],
        "period": period_key,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "rows": rows,
        "totals": {
            "target_gmv":      sum(r["target"]["gmv"]     for r in rows),
            "target_videos":   sum(r["target"]["videos"]  for r in rows),
            "achieved_gmv":    sum(r["achieved"]["gmv"]    for r in rows),
            "achieved_videos": sum(r["achieved"]["videos"] for r in rows),
        },
    }
