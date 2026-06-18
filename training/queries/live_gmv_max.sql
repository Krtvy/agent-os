-- Provenance: _private/daily_reporting/main.py · def sql_live_gmv_max(d: dict)
-- Purpose:    Single-cell aggregate: max live GMV for a window. Used for STR table normalization.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

SELECT COALESCE(SUM(COALESCE(cost, 0)), 0)::int AS live_gmv_max
FROM tiktok_raw_data.live_campaign_performance
WHERE report_date = DATE '{d["report_date"]}'
