"""
Creator Card — the M1 centerpiece.

Composes everything we know about ONE creator from the viewing POC's
perspective. Pulls:
  - Last 7d GMV + trend vs prior 7d (hero metric)
  - 7d / 30d / 90d performance strip (videos, GMV, commission, % change)
  - Days since last video (urgency signal)
  - Activity timeline: posts + lives + order spikes + POC events + notes
  - Top products this creator pushes

All read-only queries. Notes + events come from local JSON via
creator_notes / creator_events modules.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from statistics import median

from .creator_events import STATUS_EMOJI, STATUS_LABEL, current_status, list_for_creator as events_for
from .creator_notes import list_for_creator as notes_for
from .db import get_conn
from .memcache import cached


def _pct_change(curr: float, prev: float) -> float | None:
    if not prev:
        return None if not curr else None
    return round(((curr - prev) / prev) * 100, 1)


# How recent a video has to be for its earnings to count as "new" (in days).
# Matches creators_list.NEW_VIDEO_DAYS — keep them in sync.
NEW_VIDEO_DAYS = 30


def _windowed_metrics(handle: str, days: int, end: date) -> dict:
    """Two-window query: current `days`-day window ending at `end`,
    and the same span immediately preceding.
    Returns videos / lives / orders / gmv / commission for both periods,
    plus a new/tail GMV split for the current window (videos posted ≤30
    days before the order are "new", else "tail").
    """
    cs = end - timedelta(days=days - 1)
    pe = cs - timedelta(days=1)
    ps = pe - timedelta(days=days - 1)
    sql = """
        WITH v AS (
          SELECT
            COUNT(DISTINCT CASE WHEN DATE(post_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN video_id END) AS curr,
            COUNT(DISTINCT CASE WHEN DATE(post_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN video_id END) AS prev
          FROM tiktok_raw_data.tt_video
          WHERE video_id IS NOT NULL AND post_time IS NOT NULL
            AND DATE(post_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
            AND handle = %(h)s
        ),
        l AS (
          SELECT
            COUNT(DISTINCT CASE WHEN DATE(time_created - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN content_id END) AS curr,
            COUNT(DISTINCT CASE WHEN DATE(time_created - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN content_id END) AS prev
          FROM tiktok_raw_data.tiktok_affiliate_orders
          WHERE content_type = 'Livestream' AND content_id IS NOT NULL AND time_created IS NOT NULL
            AND DATE(time_created - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
            AND creator_username = %(h)s
        ),
        video_lookup AS (
          SELECT DISTINCT ON (video_id) video_id, post_time
          FROM tiktok_raw_data.tt_video
          WHERE handle = %(h)s AND post_time IS NOT NULL
          ORDER BY video_id, post_time DESC
        ),
        o AS (
          SELECT
            COUNT(DISTINCT CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN t.order_id END) AS orders_curr,
            COUNT(DISTINCT CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN t.order_id END) AS orders_prev,
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                     THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0) ELSE 0 END) AS gmv_curr,
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
                     THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0) ELSE 0 END) AS gmv_prev,
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                     THEN COALESCE(a.est_standard_commission_payment, 0) + COALESCE(a.est_shop_ads_commission_payment, 0) ELSE 0 END) AS comm_curr,
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
                     THEN COALESCE(a.est_standard_commission_payment, 0) + COALESCE(a.est_shop_ads_commission_payment, 0) ELSE 0 END) AS comm_prev,
            -- New/tail split for the CURRENT window only
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                          AND a.content_type = 'Video'
                          AND vl.post_time IS NOT NULL
                          AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s)
                     THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0) ELSE 0 END) AS gmv_new,
            SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                          AND NOT (a.content_type = 'Video' AND vl.post_time IS NOT NULL
                                   AND t.created_time - vl.post_time <= make_interval(days => %(new_days)s))
                     THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0) ELSE 0 END) AS gmv_tail
          FROM tiktok_raw_data.tiktok_orders t
          JOIN tiktok_raw_data.tiktok_affiliate_orders a ON t.order_id = a.order_id AND t.sku_id = a.sku_id
          LEFT JOIN video_lookup vl ON a.content_type = 'Video' AND vl.video_id = a.content_id
          WHERE t.cancellation_return_type IS NULL
            AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
            AND a.creator_username = %(h)s
        )
        SELECT
          v.curr, v.prev, l.curr, l.prev,
          o.orders_curr, o.orders_prev, o.gmv_curr, o.gmv_prev, o.comm_curr, o.comm_prev,
          o.gmv_new, o.gmv_tail
        FROM v, l, o
    """
    params = {"cs": cs, "ce": end, "ps": ps, "pe": pe, "h": handle, "new_days": NEW_VIDEO_DAYS}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            r = cur.fetchone() or [0] * 12
    vc, vp, lc, lp, oc, op_, gc, gp, cc, cp, g_new, g_tail = (r[i] for i in range(12))
    gc_f = float(gc or 0)
    g_new_f = float(g_new or 0)
    g_tail_f = float(g_tail or 0)
    new_pct = round(g_new_f / gc_f * 100) if gc_f else None
    return {
        "window_days": days,
        "videos": {"curr": int(vc or 0), "prev": int(vp or 0), "pct": _pct_change(int(vc or 0), int(vp or 0))},
        "lives": {"curr": int(lc or 0), "prev": int(lp or 0), "pct": _pct_change(int(lc or 0), int(lp or 0))},
        "orders": {"curr": int(oc or 0), "prev": int(op_ or 0), "pct": _pct_change(int(oc or 0), int(op_ or 0))},
        "gmv": {"curr": gc_f, "prev": float(gp or 0), "pct": _pct_change(gc_f, float(gp or 0)),
                "new": g_new_f, "tail": g_tail_f, "new_pct": new_pct},
        "commission": {"curr": float(cc or 0), "prev": float(cp or 0), "pct": _pct_change(float(cc or 0), float(cp or 0))},
    }


def _days_since_last_video(handle: str, today: date) -> int | None:
    sql = """
        SELECT MAX(DATE(post_time - INTERVAL '8 hours')) FROM tiktok_raw_data.tt_video
        WHERE handle = %(h)s AND post_time IS NOT NULL
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle})
            r = cur.fetchone()
    if not r or not r[0]:
        return None
    last = r[0]
    return (today - last).days


def _video_posts(handle: str, since: date, until: date, limit: int = 30) -> list[dict]:
    sql = """
        SELECT
          DATE(v.post_time - INTERVAL '8 hours') AS d,
          v.post_time, v.video_id,
          COALESCE(NULLIF(rp.rootlabs_common_name, ''), v.product, '(unknown)') AS product
        FROM tiktok_raw_data.tt_video v
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_product_id = v.product AND sl.listing_source = 'tiktok' AND sl.is_active = true
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE v.handle = %(h)s AND v.video_id IS NOT NULL AND v.post_time IS NOT NULL
          AND DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
        ORDER BY v.post_time DESC
        LIMIT %(lim)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle, "ps": since, "pe": until, "lim": limit})
            return [
                {
                    "kind": "video",
                    "date": str(r[0]),
                    "at": r[1].isoformat() if r[1] else None,
                    "video_id": r[2],
                    "product": r[3],
                }
                for r in cur.fetchall()
            ]


def _order_spikes(handle: str, since: date, until: date) -> list[dict]:
    """Days where orders were >= 2× the 30-day median (rolling). Cheap heuristic."""
    sql = """
        SELECT DATE(t.created_time - INTERVAL '8 hours') AS d,
               COUNT(DISTINCT t.order_id) AS orders,
               ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                       + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
          AND a.creator_username = %(h)s
        GROUP BY d
        ORDER BY d
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle, "ps": since, "pe": until})
            rows = cur.fetchall()
    daily = [(r[0], int(r[1] or 0), float(r[2] or 0)) for r in rows]
    if len(daily) < 5:
        return []
    counts = [o for _, o, _ in daily]
    med = median(counts) if counts else 0
    threshold = max(med * 2, med + 3)
    return [
        {
            "kind": "spike",
            "date": str(d),
            "orders": o,
            "gmv": g,
            "vs_median": round(o / med, 1) if med else None,
        }
        for d, o, g in daily
        if o >= threshold and o >= 3
    ]


def _top_products(handle: str, since: date, until: date, limit: int = 5) -> list[dict]:
    sql = """
        SELECT
          COALESCE(NULLIF(rp.rootlabs_common_name, ''), '(unknown)') AS product,
          COUNT(DISTINCT t.order_id) AS orders,
          ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                  + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
          ON sl.platform_sku_id = t.sku_id AND sl.listing_source = 'tiktok'
        LEFT JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
          AND a.creator_username = %(h)s
        GROUP BY product
        ORDER BY gmv DESC NULLS LAST
        LIMIT %(lim)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"h": handle, "ps": since, "pe": until, "lim": limit})
            return [
                {"product": r[0], "orders": int(r[1] or 0), "gmv": float(r[2] or 0)}
                for r in cur.fetchall()
            ]


@cached(ttl_seconds=300)
def build_card(poc_slug: str, handle: str) -> dict:
    """The one entry point a route calls. Parallel fan-out where it pays."""
    from concurrent.futures import ThreadPoolExecutor
    today = date.today()
    with ThreadPoolExecutor(max_workers=6) as pool:
        f_7 = pool.submit(_windowed_metrics, handle, 7, today)
        f_30 = pool.submit(_windowed_metrics, handle, 30, today)
        f_90 = pool.submit(_windowed_metrics, handle, 90, today)
        f_last = pool.submit(_days_since_last_video, handle, today)
        f_posts = pool.submit(_video_posts, handle, today - timedelta(days=90), today)
        f_spikes = pool.submit(_order_spikes, handle, today - timedelta(days=90), today)
        f_top_products = pool.submit(_top_products, handle, today - timedelta(days=90), today)
        m7 = f_7.result()
        m30 = f_30.result()
        m90 = f_90.result()
        days_silent = f_last.result()
        posts = f_posts.result()
        spikes = f_spikes.result()
        products = f_top_products.result()
    # Notes + events from local JSON
    notes = notes_for(poc_slug, handle)
    events = events_for(poc_slug, handle)
    status_key = current_status(poc_slug, handle)
    # Build a unified timeline: posts + spikes + events + notes, sorted desc.
    timeline: list[dict] = []
    for p in posts:
        timeline.append({"kind": "video", "at": p.get("at") or p["date"], "ts": p.get("at") or p["date"], "payload": p})
    for s in spikes:
        timeline.append({"kind": "spike", "at": s["date"], "ts": s["date"], "payload": s})
    for e in events:
        timeline.append({"kind": "event", "at": e.get("created_at"), "ts": e.get("created_at", ""), "payload": e})
    for n in notes:
        timeline.append({"kind": "note", "at": n.get("created_at"), "ts": n.get("created_at", ""), "payload": n})
    timeline.sort(key=lambda x: str(x.get("ts") or ""), reverse=True)
    timeline = timeline[:50]
    return {
        "handle": handle,
        "viewing_poc": poc_slug,
        "status_key": status_key,
        "status_label": STATUS_LABEL.get(status_key, status_key),
        "status_emoji": STATUS_EMOJI.get(status_key, ""),
        "days_silent": days_silent,
        "hero": {
            "gmv_7d": m7["gmv"]["curr"],
            "gmv_7d_prev": m7["gmv"]["prev"],
            "gmv_7d_pct": m7["gmv"]["pct"],
            "videos_7d": m7["videos"]["curr"],
            "videos_7d_pct": m7["videos"]["pct"],
        },
        "perf": {"7d": m7, "30d": m30, "90d": m90},
        "top_products": products,
        "timeline": timeline,
        "raw_notes": notes,  # for the notes panel rendering
        "raw_events": events,
    }
