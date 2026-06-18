"""
Per-creator drill-down — runs two queries (videos + lives) for one creator
on demand. Cheap (single-handle filter cuts the scan dramatically vs the
all-creators aggregation) so we run synchronously instead of going
through the async task pipeline.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from .db import get_conn
from .memcache import cached


def _round(v) -> Decimal:
    return round(Decimal(v or 0), 2)


@cached(ttl_seconds=300)
def videos_for_creator(handle: str, start_date: str, end_date: str) -> list[dict]:
    """Per-video stats for one creator in the date range."""
    sql = """
        WITH videos_unique AS (
          SELECT DISTINCT ON (video_id)
            video_id, handle, post_time, product
          FROM tiktok_raw_data.tt_video
          WHERE handle = %(handle)s
            AND video_id IS NOT NULL AND post_time IS NOT NULL
            AND DATE(post_time - INTERVAL '8 hours')
                BETWEEN %(start)s::date AND %(end)s::date
          ORDER BY video_id, post_time DESC
        )
        SELECT
          v.video_id,
          v.post_time,
          COALESCE(NULLIF(rp.rootlabs_common_name, ''), v.product, '(unknown)') AS product,
          COUNT(DISTINCT t.order_id) AS orders,
          ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                  + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv,
          ROUND(SUM(COALESCE(a.est_standard_commission_payment, 0))::numeric, 2) AS commission_organic,
          ROUND(SUM(COALESCE(a.est_shop_ads_commission_payment, 0))::numeric, 2) AS commission_shop_ads
        FROM videos_unique v
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_product_id = v.product
         AND sl.listing_source = 'tiktok'
         AND sl.is_active = true
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        LEFT JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON a.content_id = v.video_id AND a.content_type = 'Video'
        LEFT JOIN tiktok_raw_data.tiktok_orders t
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
         AND t.cancellation_return_type IS NULL
        GROUP BY v.video_id, v.post_time, v.product, rp.rootlabs_common_name
        ORDER BY v.post_time DESC
        LIMIT 500
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"handle": handle, "start": start_date, "end": end_date})
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]


@cached(ttl_seconds=300)
def lives_for_creator(handle: str, start_date: str, end_date: str) -> list[dict]:
    """Per-livestream stats for one creator in the date range."""
    sql = """
        SELECT
          a.content_id,
          MIN(a.time_created) AS first_order_at,
          COUNT(DISTINCT t.order_id) AS orders,
          ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                  + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv,
          ROUND(SUM(COALESCE(a.est_standard_commission_payment, 0))::numeric, 2) AS commission_organic,
          ROUND(SUM(COALESCE(a.est_shop_ads_commission_payment, 0))::numeric, 2) AS commission_shop_ads
        FROM tiktok_raw_data.tiktok_affiliate_orders a
        LEFT JOIN tiktok_raw_data.tiktok_orders t
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
         AND t.cancellation_return_type IS NULL
        WHERE a.creator_username = %(handle)s
          AND a.content_type = 'Livestream'
          AND a.time_created IS NOT NULL
          AND DATE(a.time_created - INTERVAL '8 hours')
              BETWEEN %(start)s::date AND %(end)s::date
        GROUP BY a.content_id
        ORDER BY first_order_at DESC
        LIMIT 500
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"handle": handle, "start": start_date, "end": end_date})
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]


def summary_for_creator(videos: list[dict], lives: list[dict]) -> dict:
    """Roll-up totals shown at the top of the detail page."""
    return {
        "videos_count": len(videos),
        "lives_count": len(lives),
        "total_orders": sum(int(v.get("orders") or 0) for v in videos)
                       + sum(int(l.get("orders") or 0) for l in lives),
        "total_gmv": _round(
            sum(Decimal(v.get("gmv") or 0) for v in videos)
            + sum(Decimal(l.get("gmv") or 0) for l in lives)
        ),
        "total_commission_organic": _round(
            sum(Decimal(v.get("commission_organic") or 0) for v in videos)
            + sum(Decimal(l.get("commission_organic") or 0) for l in lives)
        ),
        "total_commission_shop_ads": _round(
            sum(Decimal(v.get("commission_shop_ads") or 0) for v in videos)
            + sum(Decimal(l.get("commission_shop_ads") or 0) for l in lives)
        ),
    }


def default_range() -> tuple[str, str]:
    """Last 30 days ending today (IST-ish)."""
    today = date.today()
    return ((today - timedelta(days=30)).isoformat(), today.isoformat())


@cached(ttl_seconds=300)
def daily_gmv_for_creator(handle: str, start_date: str, end_date: str) -> list[dict]:
    """One row per day in the range: {date, gmv} for a single creator."""
    sql = """
        SELECT DATE(t.created_time - INTERVAL '8 hours') AS d,
               ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                       + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(start)s::date AND %(end)s::date
          AND a.creator_username = %(handle)s
        GROUP BY d
        ORDER BY d
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"handle": handle, "start": start_date, "end": end_date})
            return [{"date": str(r[0]), "gmv": float(r[1] or 0)} for r in cur.fetchall()]
