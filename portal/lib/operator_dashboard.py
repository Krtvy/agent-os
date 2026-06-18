"""
Operator (Kartavvya) dashboard — aggregate view across ALL POCs.

Different shape from per-POC dashboard:
  - No personal greeting / "your roster"
  - Per-POC row: their roster size + key metrics + commission earned
  - Grand totals at top
  - One stat per POC so the operator sees who's driving volume
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .dashboard import _periods, headline_stats
from .memcache import cached
from .poc_creators import KNOWN_POCS, get_creators_for_poc


@cached(ttl_seconds=1800)  # 30 min — operator overview, freshness not critical
def build_operator_view(
    start_date: date | None = None,
    end_date: date | None = None,
    product_filter: str = "",
) -> dict:
    """Aggregate dashboard across all POCs.

    Returns context with:
      curr_start, curr_end, prev_start, prev_end
      pocs: [{name, roster_size, videos, lives, orders, gmv, commission}, ...]
      totals: same fields summed across all POCs
    """
    if start_date and end_date:
        from datetime import timedelta
        cs, ce = start_date, end_date
        span_days = (ce - cs).days + 1
        pe = cs - timedelta(days=1)
        ps = pe - timedelta(days=span_days - 1)
    else:
        span_days = 30
        cs, ce, ps, pe = _periods(end_date, span_days)

    def _row_for(poc: str) -> dict:
        creators = get_creators_for_poc(poc)
        if not creators:
            return {
                "name": poc, "roster_size": 0,
                "videos": 0, "lives": 0, "orders": 0, "gmv": 0.0, "commission": 0.0,
            }
        s = headline_stats(creators, cs, ce, ps, pe, product_filter=product_filter)
        return {
            "name": poc,
            "roster_size": len(creators),
            "videos": s["videos"]["curr"],
            "lives": s["lives"]["curr"],
            "orders": s["orders"]["curr"],
            "gmv": s["gmv"]["curr"],
            "commission": s["commission"]["curr"],
        }

    totals = {"videos": 0, "lives": 0, "orders": 0, "gmv": 0.0, "commission": 0.0, "roster": 0}
    with ThreadPoolExecutor(max_workers=len(KNOWN_POCS)) as pool:
        per_poc: list[dict] = list(pool.map(_row_for, KNOWN_POCS))
    for row in per_poc:
        totals["videos"] += row["videos"]
        totals["lives"] += row["lives"]
        totals["orders"] += row["orders"]
        totals["gmv"] += row["gmv"]
        totals["commission"] += row["commission"]
        totals["roster"] += row["roster_size"]
    per_poc.sort(key=lambda r: r["gmv"], reverse=True)
    return {
        "curr_start": cs.isoformat(),
        "curr_end": ce.isoformat(),
        "prev_start": ps.isoformat(),
        "prev_end": pe.isoformat(),
        "span_days": span_days,
        "product_filter": product_filter,
        "pocs": per_poc,
        "totals": totals,
    }
