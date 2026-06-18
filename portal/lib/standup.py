"""
Standup — the M2 landing page logic.

"Open at 10am, see what to do today."

Three buckets of work surfaced for a POC each morning:
  1. Underperformers      — creators in their roster with a clear drop signal
  2. Gone silent          — creators who haven't posted in N days
  3. Anomalies yesterday  — single-day GMV/order spikes that need a look

Each item links to that creator's /creator/<handle> card so the POC can
investigate + act in one click.

All read-only. No new schema. Honest heuristics, not ML — comments call
out what each threshold means so we can tune them after the first week.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

from .db import get_conn
from .memcache import cached
from .poc_creators import get_creators_for_poc


def _underperformers(creators: list[str], today: date) -> list[dict]:
    """Creators whose 7d GMV is < 50% of their prior 7d GMV AND prior was > $100.
    The $100 floor stops us flagging noise on micro-creators.
    """
    if not creators:
        return []
    cs = today - timedelta(days=6)
    pe = cs - timedelta(days=1)
    ps = pe - timedelta(days=6)
    sql = """
        SELECT a.creator_username,
               SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(ce)s
                        THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_curr,
               SUM(CASE WHEN DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(pe)s
                        THEN COALESCE(t.sku_subtotal_after_discount, 0) + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_prev
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(ps)s AND %(ce)s
          AND a.creator_username = ANY(%(c)s::text[])
        GROUP BY a.creator_username
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"cs": cs, "ce": today, "ps": ps, "pe": pe, "c": creators})
            rows = cur.fetchall()
    out = []
    for handle, gmv_curr, gmv_prev in rows:
        gc = float(gmv_curr or 0)
        gp = float(gmv_prev or 0)
        if gp >= 100 and gc < gp * 0.5:
            drop_pct = round((gc - gp) / gp * 100, 0) if gp else None
            out.append({
                "handle": handle,
                "gmv_7d": gc,
                "gmv_7d_prev": gp,
                "drop_pct": drop_pct,
                "reason": f"GMV dropped {abs(int(drop_pct or 0))}% week-over-week",
            })
    out.sort(key=lambda r: r["gmv_7d_prev"], reverse=True)
    return out[:10]


def _silent(creators: list[str], today: date, threshold_days: int = 7) -> list[dict]:
    """Creators in roster who haven't posted a video in `threshold_days`+."""
    if not creators:
        return []
    sql = """
        SELECT handle, MAX(DATE(post_time - INTERVAL '8 hours')) AS last_d
        FROM tiktok_raw_data.tt_video
        WHERE handle = ANY(%(c)s::text[]) AND post_time IS NOT NULL
        GROUP BY handle
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"c": creators})
            last_by_handle = {r[0]: r[1] for r in cur.fetchall()}
    out = []
    for h in creators:
        last = last_by_handle.get(h)
        if last is None:
            out.append({"handle": h, "days_silent": None, "reason": "no video posts on record"})
            continue
        days = (today - last).days
        if days >= threshold_days:
            out.append({
                "handle": h,
                "days_silent": days,
                "last_post": str(last),
                "reason": f"no posts in {days} days",
            })
    out.sort(key=lambda r: (r.get("days_silent") or 9999), reverse=True)
    return out[:10]


def _yesterday_anomalies(creators: list[str], today: date) -> list[dict]:
    """Creators whose yesterday's GMV was ≥ 2× their 30-day median day GMV
    (excluding zero days). Flags both positive and negative spikes — but
    we only return the *positive* ones because crashes already show up
    in underperformers.
    """
    if not creators:
        return []
    yday = today - timedelta(days=1)
    base_start = today - timedelta(days=31)
    sql = """
        WITH daily AS (
          SELECT a.creator_username AS handle,
                 DATE(t.created_time - INTERVAL '8 hours') AS d,
                 SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                   + COALESCE(t.sku_platform_discount, 0)) AS gmv
          FROM tiktok_raw_data.tiktok_orders t
          JOIN tiktok_raw_data.tiktok_affiliate_orders a ON t.order_id = a.order_id AND t.sku_id = a.sku_id
          WHERE t.cancellation_return_type IS NULL
            AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(base_start)s AND %(yday)s
            AND a.creator_username = ANY(%(c)s::text[])
          GROUP BY a.creator_username, d
        )
        SELECT handle,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gmv) FILTER (WHERE d < %(yday)s AND gmv > 0) AS med_prior,
               MAX(CASE WHEN d = %(yday)s THEN gmv ELSE NULL END) AS gmv_yesterday
        FROM daily
        GROUP BY handle
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"c": creators, "base_start": base_start, "yday": yday})
            rows = cur.fetchall()
    out = []
    for handle, med, gy in rows:
        if not gy or not med:
            continue
        gy = float(gy)
        med = float(med)
        if gy >= med * 2 and gy >= 50:  # $50 floor to skip dust
            out.append({
                "handle": handle,
                "gmv_yesterday": gy,
                "median_day": med,
                "multiple": round(gy / med, 1),
                "reason": f"yesterday {round(gy/med,1)}× their typical day",
            })
    out.sort(key=lambda r: r["gmv_yesterday"], reverse=True)
    return out[:10]


def _coasting(creators: list[str], today: date) -> list[dict]:
    """Creators earning GMV (>= $100 in last 30d) where every dollar comes
    from videos posted MORE than 30 days ago — i.e. zero "new" attribution.
    These creators are coasting on their back catalog and need a nudge
    to post fresh content before the tail decays.

    Heuristic: 100% tail in last 30d AND no posts in the last 14 days
    (so we don't flag someone who posted 20 days ago whose video is just
    too new to qualify yet — wait, that's wrong logic; 30-day-new wouldn't
    decay yet. So we require >14d silent + >0 tail-only GMV).
    """
    if not creators:
        return []
    cs = today - timedelta(days=29)
    sql = """
        WITH video_lookup AS (
          SELECT DISTINCT ON (video_id) handle, video_id, post_time
          FROM tiktok_raw_data.tt_video
          WHERE handle = ANY(%(c)s::text[]) AND post_time IS NOT NULL
          ORDER BY video_id, post_time DESC
        ),
        last_post AS (
          SELECT handle, MAX(DATE(post_time - INTERVAL '8 hours')) AS last_d
          FROM tiktok_raw_data.tt_video
          WHERE handle = ANY(%(c)s::text[]) AND post_time IS NOT NULL
          GROUP BY handle
        )
        SELECT a.creator_username,
               SUM(CASE WHEN a.content_type = 'Video'
                          AND vl.post_time IS NOT NULL
                          AND t.created_time - vl.post_time <= make_interval(days => 30)
                        THEN COALESCE(t.sku_subtotal_after_discount, 0)
                           + COALESCE(t.sku_platform_discount, 0)
                        ELSE 0 END) AS gmv_new,
               SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                 + COALESCE(t.sku_platform_discount, 0)) AS gmv_total,
               MAX(lp.last_d) AS last_post
        FROM tiktok_raw_data.tiktok_orders t
        JOIN tiktok_raw_data.tiktok_affiliate_orders a
          ON t.order_id = a.order_id AND t.sku_id = a.sku_id
        LEFT JOIN video_lookup vl ON a.content_type = 'Video' AND vl.video_id = a.content_id
        LEFT JOIN last_post lp ON lp.handle = a.creator_username
        WHERE t.cancellation_return_type IS NULL
          AND DATE(t.created_time - INTERVAL '8 hours') BETWEEN %(cs)s AND %(today)s
          AND a.creator_username = ANY(%(c)s::text[])
        GROUP BY a.creator_username
        HAVING SUM(COALESCE(t.sku_subtotal_after_discount, 0)
                 + COALESCE(t.sku_platform_discount, 0)) >= 100
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"c": creators, "cs": cs, "today": today})
            rows = cur.fetchall()
    out = []
    for handle, gmv_new, gmv_total, last_post in rows:
        g_total = float(gmv_total or 0)
        g_new = float(gmv_new or 0)
        if g_total < 100:
            continue
        if g_new > 0:
            continue  # has SOME new contribution — not pure coasting
        days_silent = (today - last_post).days if last_post else None
        if days_silent is not None and days_silent < 14:
            continue  # silent gap not long enough yet
        out.append({
            "handle": handle,
            "gmv_tail_30d": g_total,
            "days_silent": days_silent,
            "last_post": str(last_post) if last_post else None,
            "reason": (f"earning ${g_total:,.0f} but no new posts in "
                       f"{days_silent or '?'} days — back catalog only"),
        })
    out.sort(key=lambda r: r["gmv_tail_30d"], reverse=True)
    return out[:10]


@cached(ttl_seconds=300)
def build(poc_name: str, today: date | None = None) -> dict:
    """Compose the standup view for one POC."""
    if today is None:
        today = date.today()
    creators = get_creators_for_poc(poc_name)
    with ThreadPoolExecutor(max_workers=4) as pool:
        f_under = pool.submit(_underperformers, creators, today)
        f_silent = pool.submit(_silent, creators, today)
        f_anom = pool.submit(_yesterday_anomalies, creators, today)
        f_coast = pool.submit(_coasting, creators, today)
        underperformers = f_under.result()
        silent = f_silent.result()
        anomalies = f_anom.result()
        coasting = f_coast.result()
    # "Today's 3 things" — surface the highest-leverage single item from each
    # bucket. Coasting takes priority over Silent because coasting creators are
    # still earning (revenue at risk) while pure silent creators may be lost
    # already. Cap to 3 items total — keep the page scannable.
    top_three: list[dict] = []
    if underperformers:
        top = underperformers[0]
        top_three.append({
            "kind": "underperformer",
            "headline": f"@{top['handle']} dropped {abs(int(top.get('drop_pct') or 0))}% WoW",
            "subline": f"7d GMV ${top['gmv_7d']:,.0f} vs prior ${top['gmv_7d_prev']:,.0f}",
            "handle": top["handle"],
            "action_label": "Investigate",
        })
    if anomalies:
        top = anomalies[0]
        top_three.append({
            "kind": "anomaly",
            "headline": f"@{top['handle']} spiked {top['multiple']}× yesterday",
            "subline": f"yesterday ${top['gmv_yesterday']:,.0f} vs typical ${top['median_day']:,.0f}",
            "handle": top["handle"],
            "action_label": "Celebrate / replicate",
        })
    if coasting and len(top_three) < 3:
        top = coasting[0]
        days = top.get("days_silent")
        top_three.append({
            "kind": "coasting",
            "headline": f"@{top['handle']} coasting on back catalog",
            "subline": (f"${top['gmv_tail_30d']:,.0f} in 30d, all from old posts · "
                        f"silent {days}d" if days else
                        f"${top['gmv_tail_30d']:,.0f} in 30d, all from old posts"),
            "handle": top["handle"],
            "action_label": "Ask for new content",
        })
    if silent and len(top_three) < 3:
        top = silent[0]
        days = top.get("days_silent")
        head = f"@{top['handle']} silent " + (f"for {days} days" if days else "(no posts on record)")
        top_three.append({
            "kind": "silent",
            "headline": head,
            "subline": f"last post: {top.get('last_post', 'never')}",
            "handle": top["handle"],
            "action_label": "Reach out",
        })
    return {
        "poc_name": poc_name,
        "today": today.isoformat(),
        "roster_size": len(creators),
        "top_three": top_three,
        "underperformers": underperformers,
        "silent": silent,
        "anomalies": anomalies,
        "coasting": coasting,
    }
