"""
/creators page — per-creator summary for the POC's full roster, with
optional product filter and a daily-videos series for the inline
sparkline / click-to-expand modal.

3 queries against the live DB, all bounded to the POC's creator list
and the chosen date range. Aggregated in Python so we get one row per
creator with all metrics + daily series.
"""

from __future__ import annotations

from datetime import date, timedelta

from .db import get_conn
from .memcache import cached
from .poc_creators import get_creators_for_poc


def _empty_creator(handle: str) -> dict:
    return {
        "creator": handle,
        "videos": 0,
        "lives": 0,
        "orders": 0,
        "gmv": 0.0,
        "gmv_new": 0.0,    # GMV from orders attributed to videos posted ≤30d before order
        "gmv_tail": 0.0,   # GMV from older videos or non-video attribution (Showcase, etc.)
        "gmv_live": 0.0,   # GMV from orders attributed to a Livestream (content_type='Livestream')
        "commission": 0.0,
        "daily_videos": [],  # [{"date": "YYYY-MM-DD", "count": N}, ...]
        "new_video_content_ids": [],  # video_ids that contributed to gmv_new in the window
    }


# How recent a video has to be for its earnings to count as "new" (in days).
# Per business decision 2026-05-26: 30 days. After that the video's earnings
# are "tail" / back catalog.
NEW_VIDEO_DAYS = 30


def get_all_db_creators() -> list[str]:
    """All distinct creator handles that have ever appeared in affiliate orders."""
    sql = """
        SELECT DISTINCT creator_username
        FROM tiktok_raw_data.tiktok_affiliate_orders
        WHERE creator_username IS NOT NULL
        ORDER BY creator_username
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [row[0] for row in cur.fetchall()]


@cached(ttl_seconds=300)
def build_creators_list(
    poc_name: str,
    start_date: date,
    end_date: date,
    product_filter: str = "",
    creator_list_override: list[str] | None = None,
) -> dict:
    """Return {date range info, creators: [{handle, videos, lives, orders,
    gmv, commission, daily_videos}, ...]}. Sorted by GMV descending.

    product_filter: if non-empty, restricts videos to only those tagged
    with that product name (via tt_video.product → sku_listings →
    rootlabs_products). Lives and orders are NOT filtered by product
    because content_type='Livestream' rows don't carry a clean product
    link (would need t.sku_id join — too expensive for this view).
    """
    creators = creator_list_override if creator_list_override is not None else get_creators_for_poc(poc_name)
    if not creators:
        return {
            "poc_name": poc_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "product_filter": product_filter,
            "creators": [],
            "roster_size": 0,
        }

    span_days = (end_date - start_date).days + 1
    # Generate the list of dates we expect (for filling gaps in sparkline data)
    all_dates = [(start_date + timedelta(days=i)).isoformat() for i in range(span_days)]

    # --- 1. videos per creator per day (with optional product filter) ---
    video_sql = """
        SELECT v.handle AS creator,
               DATE(v.post_time - INTERVAL '8 hours') AS d,
               COUNT(DISTINCT v.video_id) AS n
        FROM tiktok_raw_data.tt_video v
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_product_id = v.product
         AND sl.listing_source = 'tiktok'
         AND sl.is_active = true
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE v.video_id IS NOT NULL AND v.post_time IS NOT NULL
          AND DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
          AND v.handle = ANY(%(creators)s::text[])
          AND (%(product)s = '' OR rp.rootlabs_common_name = %(product)s)
        GROUP BY v.handle, d
    """

    # --- 2. lives per creator (totals only — daily not needed) ---
    lives_sql = """
        SELECT creator_username AS creator,
               COUNT(DISTINCT content_id) AS n
        FROM tiktok_raw_data.tiktok_affiliate_orders
        WHERE content_type = 'Livestream'
          AND content_id IS NOT NULL AND time_created IS NOT NULL
          AND DATE(time_created - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
          AND creator_username = ANY(%(creators)s::text[])
        GROUP BY creator_username
    """

    # --- 3. orders + GMV + commission per creator (totals + new/tail split) ---
    # New = order linked to a Video whose post_time was ≤ NEW_VIDEO_DAYS
    # before the order. Tail = everything else (older video, Showcase, etc.)
    # Join: affiliate_orders.content_id maps to tt_video.video_id when
    # content_type = 'Video'. Use DISTINCT ON to dedupe tt_video which
    # has duplicate rows per video_id.
    orders_sql = """
        WITH video_lookup AS (
          SELECT DISTINCT ON (video_id) video_id, post_time
          FROM tiktok_raw_data.tt_video
          WHERE handle = ANY(%(creators)s::text[]) AND post_time IS NOT NULL
          ORDER BY video_id, post_time DESC
        )
        SELECT a.creator_username AS creator,
               COUNT(DISTINCT t.order_id) AS orders,
               SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                 + COALESCE(t.sku_platform_discount, 0)) AS gmv,
               SUM(COALESCE(a.est_standard_commission_payment, 0)
                 + COALESCE(a.est_shop_ads_commission_payment, 0)) AS commission,
               SUM(CASE WHEN a.content_type = 'Video'
                          AND vl.post_time IS NOT NULL
                          AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s)
                        THEN COALESCE(t.sku_subtotal_after_discount, 0)
                           + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_new,
               SUM(CASE WHEN NOT (a.content_type = 'Video'
                          AND vl.post_time IS NOT NULL
                          AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s))
                        THEN COALESCE(t.sku_subtotal_after_discount, 0)
                           + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_tail,
               SUM(CASE WHEN a.content_type = 'Livestream'
                        THEN COALESCE(t.sku_subtotal_after_discount, 0)
                           + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_live,
               ARRAY_AGG(DISTINCT a.content_id) FILTER (
                 WHERE a.content_type = 'Video'
                   AND vl.post_time IS NOT NULL
                   AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s)
                   AND a.content_id IS NOT NULL
               ) AS new_video_content_ids
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        LEFT JOIN video_lookup vl
          ON a.content_type = 'Video' AND vl.video_id = a.content_id
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_sku_id = t.sku_id AND sl.listing_source = 'tiktok'
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
          AND a.creator_username = ANY(%(creators)s::text[])
          AND (%(product)s = '' OR rp.rootlabs_common_name = %(product)s)
        GROUP BY a.creator_username
    """

    params = {
        "cs": start_date, "ce": end_date,
        "creators": creators, "product": product_filter or "",
        "new_days": NEW_VIDEO_DAYS,
    }
    by_creator: dict[str, dict] = {}

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(video_sql, params)
            for handle, d, n in cur.fetchall():
                row = by_creator.setdefault(handle, _empty_creator(handle))
                row["videos"] += int(n or 0)
                row["daily_videos"].append({"date": str(d), "count": int(n or 0)})
            cur.execute(lives_sql, params)
            for handle, n in cur.fetchall():
                row = by_creator.setdefault(handle, _empty_creator(handle))
                row["lives"] = int(n or 0)
            cur.execute(orders_sql, params)
            for handle, orders, gmv, commission, gmv_new, gmv_tail, gmv_live, new_ids in cur.fetchall():
                row = by_creator.setdefault(handle, _empty_creator(handle))
                row["orders"] = int(orders or 0)
                row["gmv"] = round(float(gmv or 0), 2)
                row["commission"] = round(float(commission or 0), 2)
                row["gmv_new"] = round(float(gmv_new or 0), 2)
                row["gmv_tail"] = round(float(gmv_tail or 0), 2)
                row["gmv_live"] = round(float(gmv_live or 0), 2)
                row["new_video_content_ids"] = [str(v) for v in (new_ids or []) if v]

    # Fill missing days with zeros for clean sparkline + sort by date
    for row in by_creator.values():
        existing = {d["date"]: d["count"] for d in row["daily_videos"]}
        row["daily_videos"] = [
            {"date": d, "count": existing.get(d, 0)} for d in all_dates
        ]

    rows = sorted(
        by_creator.values(),
        key=lambda r: (r["gmv"], r["videos"]),
        reverse=True,
    )

    return {
        "poc_name": poc_name,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "span_days": span_days,
        "product_filter": product_filter,
        "creators": rows,
        "roster_size": len(creators),
        "shown_count": len(rows),
    }


def get_content_id_gmv(
    creators: list[str],
    start_date: date,
    end_date: date,
    product_filter: str | None = None,
) -> list[dict]:
    """Per-content-id GMV for the given creator list and date range.

    Returns a list of dicts sorted by creator then gmv desc:
      [{"creator": str, "content_id": str, "content_type": str, "gmv": float}, ...]
    """
    if not creators:
        return []

    sql = """
        WITH video_lookup AS (
            SELECT DISTINCT ON (video_id) video_id, post_time
            FROM tiktok_raw_data.tt_video
            WHERE handle = ANY(%(creators)s::text[]) AND post_time IS NOT NULL
            ORDER BY video_id, post_time DESC
        )
        SELECT
            a.creator_username                                              AS creator,
            a.content_id,
            a.content_type,
            CASE
              WHEN a.content_type = 'Livestream'
                THEN 'live'
              WHEN a.content_type = 'Video'
                AND vl.post_time IS NOT NULL
                AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s)
                THEN 'new_video'
              ELSE 'tail'
            END                                                             AS gmv_type,
            SUM(COALESCE(t.sku_subtotal_after_discount, 0)
              + COALESCE(t.sku_platform_discount, 0))                      AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        LEFT JOIN video_lookup vl
          ON a.content_type = 'Video' AND vl.video_id = a.content_id
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_sku_id = t.sku_id AND sl.listing_source = 'tiktok'
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
          AND a.creator_username = ANY(%(creators)s::text[])
          AND a.content_id IS NOT NULL
          AND (%(product)s = '' OR rp.rootlabs_common_name = %(product)s)
        GROUP BY a.creator_username, a.content_id, a.content_type, 4
        ORDER BY a.creator_username, gmv DESC
    """
    params = {
        "cs": start_date,
        "ce": end_date,
        "creators": creators,
        "product": product_filter or "",
        "new_days": NEW_VIDEO_DAYS,
    }
    out = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            for creator, content_id, content_type, gmv_type, gmv in cur.fetchall():
                out.append({
                    "creator": creator,
                    "content_id": str(content_id),
                    "content_type": content_type or "",
                    "gmv_type": gmv_type,
                    "gmv": round(float(gmv or 0), 2),
                })
    return out
