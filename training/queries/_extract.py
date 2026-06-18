"""Extract canonical SQL queries from the two zip projects into training/queries/.

Run from repo root:
    .venv/bin/python training/queries/_extract.py

Sources:
  - _private/daily_reporting/main.py — sql_* functions
  - _private/daily_reporting/reference/queries_final/*.sql — frozen snapshots
  - _private/excel_automation/automation/reports/*.py — QUERY constants

This script is reproducible: rerun after the source projects change to refresh
the library. Each output file has a header that names its provenance.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "training" / "queries"
OUT.mkdir(parents=True, exist_ok=True)


def header(provenance: str, purpose: str, notes: str = "") -> str:
    body = textwrap.dedent(f"""\
        -- Provenance: {provenance}
        -- Purpose:    {purpose}
        {f'-- Notes:      {notes}' if notes else ''}
        -- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
        --   to align with Rootlabs-team's IST day boundary.
        -- Read-only: this library is meant for read-only execution via
        --   lib/yudhi-sql.sh. Never edit or DROP from these tables.
        -- ────────────────────────────────────────────────────────────────────

        """)
    return body


def write_query(slug: str, header_text: str, sql: str) -> None:
    sql_clean = textwrap.dedent(sql).strip() + "\n"
    target = OUT / f"{slug}.sql"
    target.write_text(header_text + sql_clean)
    print(f"  wrote {target.relative_to(ROOT)}")


# ─── A. sql_* functions in daily_reporting/main.py ────────────────────────

def extract_main_py_functions():
    text = (ROOT / "_private" / "daily_reporting" / "main.py").read_text()
    rx = re.compile(
        r"def\s+(sql_[a-z_]+)\(d:\s*dict\)\s*->\s*str:\s*\n"
        r"(?:[ ]+\"\"\"[\s\S]*?\"\"\"\s*\n)?"
        r"[ ]+return\s+(?:rf?|fr?|f|r)?\"\"\"([\s\S]*?)\"\"\"",
        re.MULTILINE)
    purposes = {
        "sql_median_price":      "Median customer price per product+variation for a single day. Filters: quantity=1, active products, active listings, non-zero price.",
        "sql_quantity_tracker":  "Units sold per product+variation, MTD vs prior month same-range.",
        "sql_content_split":     "GMV split by content_type (video / livestream / showcase / etc.) per product.",
        "sql_video_lives_trend": "Per-day count of videos and livestreams that produced orders, last N days.",
        "sql_creator_stats":     "Per-creator stats for the last reporting day: GMV, orders, videos, lives.",
        "sql_top_lives":         "Top livestreams by GMV for a window — creator, livestream count, GMV.",
        "sql_str_table":         "Spend-to-revenue table (STR) — ads cost vs GMV per product/day.",
        "sql_live_gmv_max":      "Single-cell aggregate: max live GMV for a window. Used for STR table normalization.",
        "sql_video_creator_mtd": "MTD creator/video counts per product, current month vs M-1, M-2.",
        "sql_samples":           "Samples shipped last 3 days — creator-level shipping events.",
    }
    for m in rx.finditer(text):
        name = m.group(1)
        sql = m.group(2)
        # Strip f-string Python interpolation hints — replace `{d['x']}` with `:x`
        # so Yudhishthira sees a clean parameterized template.
        sql_clean = re.sub(r"\{d\['([^']+)'\]\}", r":\1", sql)
        slug = name.replace("sql_", "")
        h = header(
            provenance=f"_private/daily_reporting/main.py · def {name}(d: dict)",
            purpose=purposes.get(name, "(no description recorded)"),
            notes=("Parameters are :name placeholders — substitute via psycopg2 "
                   "`%(name)s` or pass via lib/yudhi-sql.sh -p name=value."))
        write_query(slug, h, sql_clean)


# ─── B. Reference SQL files (canonical frozen snapshots) ──────────────────

def copy_reference_sql():
    ref = ROOT / "_private" / "daily_reporting" / "reference" / "queries_final"
    for sql_path in sorted(ref.glob("*.sql")):
        # Files are named like 01_median_price.sql — keep the descriptive slug
        # but prefix with "ref_" so they don't collide with extracted dynamic
        # forms.
        slug = "ref_" + re.sub(r"^\d+_", "", sql_path.stem)
        body = sql_path.read_text()
        h = header(
            provenance=f"_private/daily_reporting/reference/queries_final/{sql_path.name}",
            purpose=("Frozen reference form (hard-coded date range). Useful as "
                     "a template; for parameterized form see the matching "
                     f"`{slug.replace('ref_', '')}.sql`."))
        write_query(slug, h, body)


# ─── C. excel_automation report modules (QUERY constants) ─────────────────

def extract_excel_automation_queries():
    reports_dir = ROOT / "_private" / "excel_automation" / "automation" / "reports"
    purposes = {
        "affiliate_gmv": "Per-day, per-creator, per-product, per-content-type GMV for TikTok affiliate orders. Splits traffic into 'shop_ads' vs 'organic'.",
        "hgr_free_orders": "Free orders for HGR product (samples / promo / zero-price), per day per creator.",
        "flagged_commission_rates": "Creators whose commission rate exceeded normal threshold — for flagging in the ops sheet.",
        "live_gmv": "Two queries: per-creator GMV pivot for livestream sales, AND day-level GMV+creator count for livestream sales (both filtered to specific product family).",
        "videos_posted": "Count of videos posted per creator per day, with creator + content metadata.",
    }
    for py in sorted(reports_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        text = py.read_text()
        # All QUERY-style constants (some files have multiple)
        for m in re.finditer(
            r'^(_?[A-Z_]*QUERY[A-Z_]*)\s*=\s*"""([\s\S]*?)"""',
            text, re.MULTILINE):
            query_name = m.group(1)
            sql = m.group(2)
            stem = py.stem
            slug = stem if query_name in ("QUERY",) else f"{stem}__{query_name.lower()}"
            h = header(
                provenance=f"_private/excel_automation/automation/reports/{py.name} · {query_name}",
                purpose=purposes.get(stem, "(no description recorded)"),
                notes=("Parameters use psycopg2 `%(name)s` form. Common params: "
                       "start, end (both as 'YYYY-MM-DD HH:MM:SS' strings)."))
            write_query(slug, h, sql)


def write_readme():
    readme = OUT / "README.md"
    queries = sorted(p.name for p in OUT.glob("*.sql"))
    body = textwrap.dedent(f"""\
        # Canonical SQL query library

        Extracted from the two production projects (`excel_automation` + `daily_reporting`)
        that already run against the Rootlabs Supabase. These are the team's
        actual proven queries — copy, parameterize, run.

        ## Run via the read-only wrapper

        ```bash
        lib/yudhi-sql.sh -f training/queries/median_price.sql -p target_day=2026-05-14
        ```

        See `lib/yudhi-sql.sh --help` for full options.

        ## Conventions used everywhere

        - **IST day boundary**: `DATE(t.created_time - INTERVAL '8 hours')`
          (DB stores UTC; Rootlabs reporting is IST).
        - **Active-products filter**: `rp.product_status = 'active' AND sl.is_active = true`.
        - **Cancellation filter**: `t.cancellation_return_type IS NULL`.
        - **Price filter**: `t.sku_unit_original_price <> 0` (excludes promos / free orders).
        - **Parameters**: `%(name)s` placeholders for psycopg2; substitute via
          `lib/yudhi-sql.sh -p name=value`.

        ## Query inventory

        Total queries: {len(queries)}.

        Each file has a `-- Provenance:` and `-- Purpose:` header line so you
        can grep for capability before opening files:

        ```bash
        grep -l "median" training/queries/*.sql
        grep "Purpose:" training/queries/*.sql | head
        ```

        ## Refresh

        Regenerate from the source projects whenever they change:

        ```bash
        .venv/bin/python training/queries/_extract.py
        ```

        Output is deterministic from the source.
        """)
    readme.write_text(body)
    print(f"  wrote {readme.relative_to(ROOT)}")


def main():
    extract_main_py_functions()
    copy_reference_sql()
    extract_excel_automation_queries()
    write_readme()


if __name__ == "__main__":
    main()
