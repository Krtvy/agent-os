"""Per-creator GMV drill-down queries for the /creators page modals.

When a POC clicks the "% new" badge or the Live GMV line on a creator
row, the page fires a fetch() to /creator/<handle>/new-video-breakdown
or .../live-breakdown — these endpoints call the functions below to
return a JSON list of content_ids with their GMV contribution.

Cached for 5 min — same as the rest of the read-only views.
"""

from __future__ import annotations

from datetime import date

from .db import get_conn
from .memcache import cached

NEW_VIDEO_DAYS = 30


@cached(ttl_seconds=300)
def new_video_breakdown(handle: str, start_date: str, end_date: str) -> list[dict]:
    """Per-video GMV for orders attributed to videos posted within the
    window (the "new video" portion of the creator's GMV).

    Returns list of {video_id, post_date, gmv, orders}, sorted by GMV desc.
    """
    sql = """
        WITH video_lookup AS (
          SELECT DISTINCT ON (video_id) video_id, post_time
          FROM tiktok_raw_data.tt_video
          WHERE handle = %(h)s AND post_time IS NOT NULL
          ORDER BY video_id, post_time DESC
        )
        SELECT a.content_id AS video_id,
               DATE(vl.post_time - INTERVAL '8 hours') AS post_date,
               COUNT(DISTINCT t.order_id) AS orders,
               ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                       + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        JOIN video_lookup vl ON vl.video_id = a.content_id
        WHERE t.cancellation_return_type IS NULL
          AND a.content_type = 'Video'
          AND a.creator_username = %(h)s
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(s)s::date AND %(e)s::date
          AND t.created_time - vl.post_time <= make_interval(days => %(nd)s)
        GROUP BY a.content_id, post_date
        ORDER BY gmv DESC NULLS LAST
        LIMIT 200
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle, "s": start_date, "e": end_date, "nd": NEW_VIDEO_DAYS})
            cols = [d.name for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for r in rows:
        r["orders"] = int(r.get("orders") or 0)
        r["gmv"] = float(r.get("gmv") or 0.0)
        r["post_date"] = r["post_date"].isoformat() if r.get("post_date") else None
    return rows


@cached(ttl_seconds=300)
def live_breakdown(handle: str, start_date: str, end_date: str) -> list[dict]:
    """Per-live GMV for orders attributed to a Livestream content_type.

    Returns list of {live_id, started_at, gmv, orders}, sorted by GMV desc.
    """
    sql = """
        SELECT a.content_id AS live_id,
               MIN(a.time_created) AS started_at,
               COUNT(DISTINCT t.order_id) AS orders,
               ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                       + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND a.content_type = 'Livestream'
          AND a.creator_username = %(h)s
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(s)s::date AND %(e)s::date
        GROUP BY a.content_id
        ORDER BY gmv DESC NULLS LAST
        LIMIT 200
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle, "s": start_date, "e": end_date})
            cols = [d.name for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for r in rows:
        r["orders"] = int(r.get("orders") or 0)
        r["gmv"] = float(r.get("gmv") or 0.0)
        r["started_at"] = r["started_at"].isoformat() if r.get("started_at") else None
    return rows
