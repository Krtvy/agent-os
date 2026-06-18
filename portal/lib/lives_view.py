"""Roster-wide lives view — every TikTok live in the window for every
creator in a POC's (or operator's) roster, with the product × GMV
breakdown for orders attributed to that live.

One row per (creator, live, product). Same denormalized shape the
HTML page renders directly.

Used by GET /lives.
"""

from __future__ import annotations

from datetime import date, timedelta

from .db import get_conn
from .memcache import cached
from .poc_creators import get_creators_for_poc


_SQL = """
SELECT
  a.creator_username                                              AS creator,
  a.content_id                                                    AS live_id,
  MIN(a.time_created)                                             AS live_at,
  COALESCE(NULLIF(rp.rootlabs_common_name, ''), '(unattributed)') AS product,
  COUNT(DISTINCT t.order_id)                                      AS orders,
  ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
          + COALESCE(t.sku_platform_discount, 0))::numeric, 2)    AS gmv,
  ROUND(SUM(COALESCE(a.est_standard_commission_payment, 0)
          + COALESCE(a.est_shop_ads_commission_payment, 0))::numeric, 2) AS commission
FROM tiktok_raw_data.tiktok_affiliate_orders a
JOIN tiktok_raw_data.tiktok_orders t
  ON t.order_id = a.order_id
 AND t.sku_id = a.sku_id
 AND t.cancellation_return_type IS NULL
LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
  ON sl.platform_sku_id = t.sku_id
 AND sl.listing_source = 'tiktok'
LEFT JOIN rootlabs_core.rootlabs_products rp
  ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
WHERE a.content_type = 'Livestream'
  AND a.creator_username = ANY(%(handles)s::text[])
  AND a.time_created IS NOT NULL
  AND DATE(a.time_created - INTERVAL '8 hours')
      BETWEEN %(start)s::date AND %(end)s::date
GROUP BY a.creator_username, a.content_id, product
ORDER BY MIN(a.time_created) DESC, gmv DESC NULLS LAST
LIMIT 2000
"""


@cached(ttl_seconds=300)
def build_lives_view(
    poc_name: str | None,
    start_date: date,
    end_date: date,
) -> dict:
    """Return lives with product-attribution rows + headline totals.

    If poc_name is None, scope to the operator (all creators across all
    POCs combined). Otherwise scope to that POC's roster.
    """
    from .poc_creators import all_pocs

    if poc_name is None:
        handles: list[str] = []
        for p in all_pocs():
            handles.extend(get_creators_for_poc(p))
        handles = sorted(set(handles))
        scope_label = "All creators"
    else:
        handles = sorted(set(get_creators_for_poc(poc_name)))
        scope_label = poc_name

    if not handles:
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "scope_label": scope_label,
            "rows": [],
            "totals": {"live_count": 0, "creator_count": 0, "orders": 0, "gmv": 0.0, "commission": 0.0},
            "products": [],
        }

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_SQL, {
                "handles": handles,
                "start": start_date,
                "end": end_date,
            })
            cols = [d.name for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    # Normalize numeric types for clean template rendering.
    for r in rows:
        r["orders"] = int(r.get("orders") or 0)
        r["gmv"] = float(r.get("gmv") or 0.0)
        r["commission"] = float(r.get("commission") or 0.0)

    # Headline totals.
    unique_lives = {(r["creator"], r["live_id"]) for r in rows}
    unique_creators = {r["creator"] for r in rows}
    totals = {
        "live_count": len(unique_lives),
        "creator_count": len(unique_creators),
        "orders": sum(r["orders"] for r in rows),
        "gmv": round(sum(r["gmv"] for r in rows), 2),
        "commission": round(sum(r["commission"] for r in rows), 2),
    }

    # Aggregate top products across all lives in the window.
    by_product: dict[str, dict] = {}
    for r in rows:
        p = r["product"]
        agg = by_product.setdefault(p, {"product": p, "orders": 0, "gmv": 0.0, "lives": set()})
        agg["orders"] += r["orders"]
        agg["gmv"] += r["gmv"]
        agg["lives"].add((r["creator"], r["live_id"]))
    products = sorted(
        (
            {"product": v["product"], "orders": v["orders"],
             "gmv": round(v["gmv"], 2), "live_count": len(v["lives"])}
            for v in by_product.values()
        ),
        key=lambda x: x["gmv"], reverse=True,
    )

    # Aggregate per-creator: total lives + daily lives series for sparklines.
    # `daily_lives` is one entry per CALENDAR DAY in the window (zero-filled),
    # counting distinct content_id per day — same pattern as /creators
    # uses for daily videos.
    all_days: list[str] = []
    d = start_date
    while d <= end_date:
        all_days.append(d.isoformat())
        d += timedelta(days=1)

    by_creator: dict[str, dict] = {}
    for r in rows:
        c = r["creator"]
        agg = by_creator.setdefault(c, {
            "creator": c,
            "lives_set": set(),
            "orders": 0,
            "gmv": 0.0,
            "commission": 0.0,
            "daily": {},  # day_iso -> set of distinct content_ids
        })
        agg["lives_set"].add(r["live_id"])
        agg["orders"] += r["orders"]
        agg["gmv"] += r["gmv"]
        agg["commission"] += r["commission"]
        if r.get("live_at"):
            # `live_at` is a timestamp; pull the local-IST date by subtracting
            # the same 8-hour offset the SQL uses for window filtering.
            try:
                day_iso = (r["live_at"] - timedelta(hours=8)).date().isoformat()
            except Exception:  # noqa: BLE001
                day_iso = r["live_at"].date().isoformat() if hasattr(r["live_at"], "date") else None
            if day_iso:
                agg["daily"].setdefault(day_iso, set()).add(r["live_id"])

    creators_summary = []
    for v in by_creator.values():
        # Zero-filled daily series across the whole window.
        daily_lives = [{"date": day, "count": len(v["daily"].get(day, set()))} for day in all_days]
        creators_summary.append({
            "creator": v["creator"],
            "lives": len(v["lives_set"]),
            "orders": v["orders"],
            "gmv": round(v["gmv"], 2),
            "commission": round(v["commission"], 2),
            "daily_lives": daily_lives,
        })
    creators_summary.sort(key=lambda x: (x["gmv"], x["lives"]), reverse=True)

    # Roster-wide daily total — sum of all creators' daily counts per day.
    daily_total = []
    for i, day in enumerate(all_days):
        total = sum(c["daily_lives"][i]["count"] for c in creators_summary)
        daily_total.append({"date": day, "count": total})

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "scope_label": scope_label,
        "rows": rows,
        "totals": totals,
        "products": products,
        "creators_summary": creators_summary,
        "daily_total": daily_total,
    }
