"""
POC dashboard — current period + previous period summary, top creators,
daily sparkline. Reads from the same tables as creator-content-counts
but pre-aggregated to a single row per period for speed.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from .db import get_conn
import hashlib
import json
import os
from pathlib import Path
import time

from .poc_creators import get_creators_for_poc


def _periods(end: date | None = None, span_days: int = 30) -> tuple[date, date, date, date]:
    """Return (curr_start, curr_end, prev_start, prev_end) for two back-to-back windows."""
    if end is None:
        end = date.today()
    curr_end = end
    curr_start = end - timedelta(days=span_days - 1)
    prev_end = curr_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=span_days - 1)
    return curr_start, curr_end, prev_start, prev_end


def _pct_change(curr: Decimal | int | None, prev: Decimal | int | None) -> float | None:
    if curr is None or prev is None or prev == 0:
        return None
    return round(float((Decimal(curr) - Decimal(prev)) / Decimal(prev) * 100), 1)


_PRODUCT_ID_CACHE: dict[str, tuple[list[str], list[str]]] = {}


def _resolve_product_ids(product_filter: str) -> tuple[list[str], list[str]]:
    """Resolve a product name into (platform_product_ids, platform_sku_ids).
    Cached process-wide since the mapping changes rarely.
    """
    if not product_filter:
        return [], []
    if product_filter in _PRODUCT_ID_CACHE:
        return _PRODUCT_ID_CACHE[product_filter]
    sql = """
        SELECT DISTINCT sl.platform_product_id, sl.platform_sku_id
        FROM rootlabs_core.rootlabs_sku_listings sl
        JOIN rootlabs_core.rootlabs_products rp
          ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
        WHERE sl.listing_source = 'tiktok'
          AND rp.rootlabs_common_name = %(p)s
    """
    pids: set[str] = set()
    sids: set[str] = set()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"p": product_filter})
            for ppid, psid in cur.fetchall():
                if ppid: pids.add(ppid)
                if psid: sids.add(psid)
    result = (sorted(pids), sorted(sids))
    _PRODUCT_ID_CACHE[product_filter] = result
    return result


def _product_filter_fragments(product_filter: str) -> tuple[str, str]:
    """Return (video_where, order_where) SQL fragments that restrict by the
    pre-resolved platform IDs. Empty when no filter. Caller passes the IDs
    via %(_video_pids)s and %(_order_sids)s in params."""
    if not product_filter:
        return "", ""
    return (
        " AND v.product = ANY(%(_video_pids)s::text[]) ",
        " AND t.sku_id = ANY(%(_order_sids)s::text[]) ",
    )


def headline_stats(
    creators: list[str], cs: date, ce: date, ps: date, pe: date,
    product_filter: str = "",
) -> dict:
    """One query for videos + lives + GMV + commission + orders, current + previous.
    Lives don't carry a clean product link, so the product filter is ignored
    for the lives count (it stays a roster-wide count)."""
    if not creators:
        return _empty_stats()
    vpids, osids = _resolve_product_ids(product_filter)
    vwhere, owhere = _product_filter_fragments(product_filter)
    # Videos query (tt_video) — aliased to v so the WHERE fragment lines up
    video_sql = f"""
        SELECT
          COUNT(DISTINCT CASE WHEN DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN v.video_id END) AS curr,
          COUNT(DISTINCT CASE WHEN DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN v.video_id END) AS prev
        FROM tiktok_raw_data.tt_video v
        WHERE v.video_id IS NOT NULL AND v.post_time IS NOT NULL
          AND DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
          AND v.handle = ANY(%(creators)s::text[])
          {vwhere}
    """
    # Lives query (affiliate orders)
    lives_sql = """
        SELECT
          COUNT(DISTINCT CASE WHEN DATE(time_created - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN content_id END) AS curr,
          COUNT(DISTINCT CASE WHEN DATE(time_created - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN content_id END) AS prev
        FROM tiktok_raw_data.tiktok_affiliate_orders
        WHERE content_type = 'Livestream' AND content_id IS NOT NULL AND time_created IS NOT NULL
          AND DATE(time_created - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
          AND creator_username = ANY(%(creators)s::text[])
    """
    # Orders + GMV + commission (orders × affiliate_orders)
    orders_sql = f"""
        SELECT
          COUNT(DISTINCT CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s THEN t.order_id END) AS orders_curr,
          COUNT(DISTINCT CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s THEN t.order_id END) AS orders_prev,
          SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                   THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0)
                   ELSE 0 END) AS gmv_curr,
          SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
                   THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0)
                   ELSE 0 END) AS gmv_prev,
          SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                   THEN COALESCE(a.est_standard_commission_payment, 0) + COALESCE(a.est_shop_ads_commission_payment, 0)
                   ELSE 0 END) AS comm_curr,
          SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
                   THEN COALESCE(a.est_standard_commission_payment, 0) + COALESCE(a.est_shop_ads_commission_payment, 0)
                   ELSE 0 END) AS comm_prev
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND t.created_time IS NOT NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
          AND a.creator_username = ANY(%(creators)s::text[])
          {owhere}
    """
    params = {
        "cs": cs, "ce": ce, "ps": ps, "pe": pe, "creators": creators,
        "_video_pids": vpids, "_order_sids": osids,
    }
    out = _empty_stats()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(video_sql, params)
            r = cur.fetchone()
            out["videos"] = {"curr": int(r[0] or 0), "prev": int(r[1] or 0)}
            cur.execute(lives_sql, params)
            r = cur.fetchone()
            out["lives"] = {"curr": int(r[0] or 0), "prev": int(r[1] or 0)}
            cur.execute(orders_sql, params)
            r = cur.fetchone()
            out["orders"] = {"curr": int(r[0] or 0), "prev": int(r[1] or 0)}
            out["gmv"] = {"curr": float(r[2] or 0), "prev": float(r[3] or 0)}
            out["commission"] = {"curr": float(r[4] or 0), "prev": float(r[5] or 0)}
    # Compute % changes
    for k in ("videos", "lives", "orders", "gmv", "commission"):
        out[k]["pct"] = _pct_change(out[k]["curr"], out[k]["prev"])
    return out


def _empty_stats() -> dict:
    return {
        "videos": {"curr": 0, "prev": 0, "pct": None},
        "lives": {"curr": 0, "prev": 0, "pct": None},
        "orders": {"curr": 0, "prev": 0, "pct": None},
        "gmv": {"curr": 0, "prev": 0, "pct": None},
        "commission": {"curr": 0, "prev": 0, "pct": None},
    }


def top_creators(
    creators: list[str], cs: date, ce: date, limit: int = 5,
    product_filter: str = "",
) -> list[dict]:
    """Top N creators by GMV in the current period."""
    if not creators:
        return []
    _, osids = _resolve_product_ids(product_filter)
    _, owhere = _product_filter_fragments(product_filter)
    sql = f"""
        SELECT a.creator_username,
               COUNT(DISTINCT t.order_id) AS orders,
               ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                       + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
          AND a.creator_username = ANY(%(creators)s::text[])
          {owhere}
        GROUP BY a.creator_username
        ORDER BY gmv DESC
        LIMIT %(limit)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {
                "cs": cs, "ce": ce, "creators": creators, "limit": limit,
                "_order_sids": osids,
            })
            return [
                {"creator": r[0], "orders": int(r[1] or 0), "gmv": float(r[2] or 0)}
                for r in cur.fetchall()
            ]


def videos_by_product(creators: list[str], cs: date, ce: date) -> list[dict]:
    """Per-product video count + GMV for the POC's creators in the period.
    Joins tt_video → sku_listings → products to get readable names.
    Returns list of {product, videos, gmv} sorted by videos desc.
    """
    if not creators:
        return []
    sql = """
        WITH video_counts AS (
          SELECT
            COALESCE(NULLIF(rp.rootlabs_common_name, ''), v.product, '(unknown)') AS product,
            COUNT(DISTINCT v.video_id) AS videos
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
          GROUP BY COALESCE(NULLIF(rp.rootlabs_common_name, ''), v.product, '(unknown)')
        ),
        gmv_per_product AS (
          SELECT
            COALESCE(NULLIF(rp.rootlabs_common_name, ''), '(unknown)') AS product,
            ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                    + COALESCE(t.sku_platform_discount, 0))::numeric, 2) AS gmv
          FROM tiktok_raw_data.tiktok_orders t
          JOIN tiktok_raw_data.tiktok_affiliate_orders a
            ON t.order_id = a.order_id AND t.sku_id = a.sku_id
          LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
            ON sl.platform_sku_id = t.sku_id AND sl.listing_source = 'tiktok'
          LEFT JOIN rootlabs_core.rootlabs_products rp
            ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
          WHERE t.cancellation_return_type IS NULL
            AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND a.creator_username = ANY(%(creators)s::text[])
          GROUP BY COALESCE(NULLIF(rp.rootlabs_common_name, ''), '(unknown)')
        )
        SELECT
          COALESCE(vc.product, gp.product) AS product,
          COALESCE(vc.videos, 0) AS videos,
          COALESCE(gp.gmv, 0) AS gmv
        FROM video_counts vc
        FULL OUTER JOIN gmv_per_product gp USING (product)
        WHERE COALESCE(vc.product, gp.product) IS NOT NULL
        ORDER BY videos DESC, gmv DESC
        LIMIT 20
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"cs": cs, "ce": ce, "creators": creators})
            return [
                {"product": r[0], "videos": int(r[1] or 0), "gmv": float(r[2] or 0)}
                for r in cur.fetchall()
            ]


def daily_series(
    creators: list[str], cs: date, ce: date, product_filter: str = "",
) -> list[dict]:
    """One row per day in the period, with all 5 metrics. Drives per-tile
    sparklines + the main GMV trend chart. One query (3 CTEs UNION-aligned)
    to keep latency reasonable.
    """
    if not creators:
        return []
    vpids, osids = _resolve_product_ids(product_filter)
    vwhere, owhere = _product_filter_fragments(product_filter)
    sql = f"""
        WITH order_daily AS (
          SELECT DATE(t.created_time - INTERVAL '8 hours') AS d,
                 COUNT(DISTINCT t.order_id) AS orders,
                 SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                   + COALESCE(t.sku_platform_discount, 0)) AS gmv,
                 SUM(COALESCE(a.est_standard_commission_payment, 0)
                   + COALESCE(a.est_shop_ads_commission_payment, 0)) AS commission
          FROM tiktok_raw_data.tiktok_orders t
          JOIN tiktok_raw_data.tiktok_affiliate_orders a
            ON t.order_id = a.order_id AND t.sku_id = a.sku_id
          WHERE t.cancellation_return_type IS NULL
            AND t.created_time IS NOT NULL
            AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND a.creator_username = ANY(%(creators)s::text[])
            {owhere}
          GROUP BY d
        ),
        video_daily AS (
          SELECT DATE(v.post_time - INTERVAL '8 hours') AS d,
                 COUNT(DISTINCT v.video_id) AS videos
          FROM tiktok_raw_data.tt_video v
          WHERE v.video_id IS NOT NULL AND v.post_time IS NOT NULL
            AND DATE(v.post_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND v.handle = ANY(%(creators)s::text[])
            {vwhere}
          GROUP BY d
        ),
        live_daily AS (
          SELECT DATE(time_created - INTERVAL '8 hours') AS d,
                 COUNT(DISTINCT content_id) AS lives
          FROM tiktok_raw_data.tiktok_affiliate_orders
          WHERE content_type = 'Livestream' AND content_id IS NOT NULL
            AND time_created IS NOT NULL
            AND DATE(time_created - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
            AND creator_username = ANY(%(creators)s::text[])
          GROUP BY d
        ),
        all_days AS (
          SELECT d FROM order_daily
          UNION SELECT d FROM video_daily
          UNION SELECT d FROM live_daily
        )
        SELECT
          d.d AS day,
          COALESCE(v.videos, 0) AS videos,
          COALESCE(l.lives, 0) AS lives,
          COALESCE(o.orders, 0) AS orders,
          ROUND(COALESCE(o.gmv, 0)::numeric, 2) AS gmv,
          ROUND(COALESCE(o.commission, 0)::numeric, 2) AS commission
        FROM all_days d
        LEFT JOIN video_daily v ON v.d = d.d
        LEFT JOIN live_daily  l ON l.d = d.d
        LEFT JOIN order_daily o ON o.d = d.d
        ORDER BY d.d
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {
                "cs": cs, "ce": ce, "creators": creators,
                "_video_pids": vpids, "_order_sids": osids,
            })
            return [
                {
                    "date": str(r[0]),
                    "videos": int(r[1] or 0),
                    "lives": int(r[2] or 0),
                    "orders": int(r[3] or 0),
                    "gmv": float(r[4] or 0),
                    "commission": float(r[5] or 0),
                }
                for r in cur.fetchall()
            ]


# Backwards-compat alias (some templates may still call this name).
def daily_gmv(creators: list[str], cs: date, ce: date) -> list[dict]:
    return [{"date": d["date"], "gmv": d["gmv"]} for d in daily_series(creators, cs, ce)]


def sparkline_svg(
    values: list[float],
    labels: list[str] | None = None,
    width: int = 240,
    height: int = 50,
    color: str = "#2d6a4f",
    value_prefix: str = "",
    show_dots: bool = True,
) -> str:
    """Inline SVG polyline + invisible hit-circles with <title> tooltips.

    `labels`: parallel list (e.g. dates) shown in the per-point tooltip.
    `value_prefix`: e.g. "$" for currency.
    `show_dots`: render hit-circles for hover tooltip; falsey for the very
    smallest tiles where hovering isn't useful.
    """
    if not values or all((v or 0) == 0 for v in values):
        return (
            f'<svg viewBox="0 0 {width} {height}" '
            f'style="width:100%;height:{height}px">'
            f'<text x="50%" y="50%" text-anchor="middle" fill="#999" '
            f'font-size="10">no data</text></svg>'
        )
    n = len(values)
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    pts = []
    coords: list[tuple[float, float]] = []
    for i, v in enumerate(values):
        x = (i / max(1, n - 1)) * width
        y = height - ((v - lo) / rng) * (height - 4) - 2
        pts.append(f"{x:.1f},{y:.1f}")
        coords.append((x, y))
    pts_str = " ".join(pts)
    out = [
        f'<svg viewBox="0 0 {width} {height}" '
        f'style="width:100%;height:{height}px" '
        f'preserveAspectRatio="none">',
        f'<polyline fill="none" stroke="{color}" stroke-width="1.5" '
        f'points="{pts_str}" />',
    ]
    if show_dots:
        for (x, y), v, lbl in zip(
            coords, values, labels or [""] * n
        ):
            # Invisible larger hit area + visible tiny dot for affordance.
            vstr = _fmt_value(v, value_prefix)
            tip = f"{lbl}: {vstr}" if lbl else vstr
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                f'fill="transparent"><title>{tip}</title></circle>'
            )
    out.append("</svg>")
    return "".join(out)


def _fmt_value(v: float, prefix: str) -> str:
    if prefix == "$":
        return f"${v:,.2f}"
    if isinstance(v, float) and v.is_integer():
        return f"{int(v):,}"
    if isinstance(v, int):
        return f"{v:,}"
    return f"{v:,.2f}"


def sparkline_overlay_svg(
    curr: list[float],
    prev: list[float],
    labels_curr: list[str] | None = None,
    width: int = 480,
    height: int = 100,
    value_prefix: str = "$",
) -> str:
    """Two polylines on the same axes — current (solid green) and
    previous (dashed gray). Both series normalised against the combined
    min/max so they're directly comparable.
    """
    if not curr and not prev:
        return sparkline_svg([])  # delegate to "no data"
    all_vals = [v for v in (curr + prev) if v is not None]
    if not all_vals or all(v == 0 for v in all_vals):
        return sparkline_svg([])
    lo, hi = min(all_vals), max(all_vals)
    rng = (hi - lo) or 1

    def _poly(series: list[float]) -> str:
        n = len(series)
        if n < 2:
            return ""
        pts = []
        for i, v in enumerate(series):
            x = (i / (n - 1)) * width
            y = height - ((v - lo) / rng) * (height - 4) - 2
            pts.append(f"{x:.1f},{y:.1f}")
        return " ".join(pts)

    out = [
        f'<svg viewBox="0 0 {width} {height}" '
        f'style="width:100%;height:{height}px" '
        f'preserveAspectRatio="none">'
    ]
    if prev:
        out.append(
            f'<polyline fill="none" stroke="#999" stroke-width="1.2" '
            f'stroke-dasharray="3,3" points="{_poly(prev)}" />'
        )
    if curr:
        out.append(
            f'<polyline fill="none" stroke="#2d6a4f" stroke-width="1.8" '
            f'points="{_poly(curr)}" />'
        )
        # Hit dots on the current series only
        n = len(curr)
        for i, v in enumerate(curr):
            x = (i / max(1, n - 1)) * width
            y = height - ((v - lo) / rng) * (height - 4) - 2
            lbl = labels_curr[i] if labels_curr and i < len(labels_curr) else ""
            tip = f"{lbl}: {_fmt_value(v, value_prefix)}" if lbl else _fmt_value(v, value_prefix)
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                f'fill="transparent"><title>{tip}</title></circle>'
            )
    out.append("</svg>")
    return "".join(out)


_PORTAL_DIR = Path(__file__).resolve().parents[1]
_POCS_ROOT = _PORTAL_DIR.parent / "pocs"
_DASHBOARD_CACHE_TTL_S = int(os.getenv("PORTAL_DASHBOARD_CACHE_TTL_S", "1800"))  # 30 min default


def _dashboard_cache_path(poc_name: str, cs: date, ce: date) -> Path:
    slug = poc_name.strip().lower()
    key = f"{slug}:{cs.isoformat()}:{ce.isoformat()}"
    h = hashlib.sha256(key.encode()).hexdigest()[:12]
    d = _POCS_ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d / f"dashboard_cache_{h}.json"


def _read_cached(poc_name: str, cs: date, ce: date) -> dict | None:
    p = _dashboard_cache_path(poc_name, cs, ce)
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text())
        if time.time() - payload.get("_cached_at", 0) > _DASHBOARD_CACHE_TTL_S:
            return None
        return payload.get("ctx")
    except (json.JSONDecodeError, OSError):
        return None


def _write_cached(poc_name: str, cs: date, ce: date, ctx: dict) -> None:
    p = _dashboard_cache_path(poc_name, cs, ce)
    try:
        p.write_text(json.dumps({"_cached_at": time.time(), "ctx": ctx}, default=str))
    except OSError:
        pass


def build_for_poc(
    poc_name: str,
    start_date: date | None = None,
    end_date: date | None = None,
    refresh: bool = False,
    product_filter: str = "",
) -> dict:
    """Top-level entry point — assembles the full dashboard context.

    Date selection:
      - If both start_date and end_date provided: use that explicit window.
      - If only end_date: 30-day window ending then.
      - If neither: last 30 days ending today.
    Comparison window is always the same span immediately preceding.
    """
    if start_date and end_date:
        cs, ce = start_date, end_date
        span_days = (ce - cs).days + 1
        pe = cs - timedelta(days=1)
        ps = pe - timedelta(days=span_days - 1)
    else:
        span_days = 30
        cs, ce, ps, pe = _periods(end_date, span_days)
    # Cache key includes product filter so different filters don't collide.
    cache_key = poc_name if not product_filter else f"{poc_name}::p={product_filter}"
    if not refresh:
        cached = _read_cached(cache_key, cs, ce)
        if cached is not None:
            cached["_from_cache"] = True
            return cached
    creators = get_creators_for_poc(poc_name)
    # SPEED: the four sub-queries are independent — fan them out to a thread
    # pool so total wall-time = max(per-query) instead of sum(per-query).
    # Each get_conn() opens its own connection, so threads don't race.
    from concurrent.futures import ThreadPoolExecutor
    def _run_daily():
        # One query spanning BOTH periods → Python splits by date.
        return daily_series(creators, ps, ce, product_filter=product_filter)
    def _run_headline():
        return headline_stats(creators, cs, ce, ps, pe, product_filter=product_filter)
    def _run_top():
        return top_creators(creators, cs, ce, product_filter=product_filter)
    def _run_products():
        # When filtered to one product, the per-product table is redundant.
        return [] if product_filter else videos_by_product(creators, cs, ce)
    with ThreadPoolExecutor(max_workers=4) as pool:
        f_daily = pool.submit(_run_daily)
        f_headline = pool.submit(_run_headline)
        f_top = pool.submit(_run_top)
        f_products = pool.submit(_run_products)
        all_daily = f_daily.result()
        stats = f_headline.result()
        top = f_top.result()
        products = f_products.result()
    from datetime import date as _d
    def _to_d(s: str) -> _d:
        return _d.fromisoformat(s)
    daily_curr = [row for row in all_daily if cs <= _to_d(row["date"]) <= ce]
    daily_prev = [row for row in all_daily if ps <= _to_d(row["date"]) <= pe]
    ctx = {
        "poc_name": poc_name,
        "roster_size": len(creators),
        "curr_start": cs.isoformat(),
        "curr_end": ce.isoformat(),
        "prev_start": ps.isoformat(),
        "prev_end": pe.isoformat(),
        "span_days": span_days,
        "product_filter": product_filter,
        "stats": stats,
        "top_creators": top,
        "daily": daily_curr,
        "daily_prev": daily_prev,
        "products": products,
        "_from_cache": False,
    }
    _write_cached(cache_key, cs, ce, ctx)
    return ctx
