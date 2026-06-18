-- Provenance: _private/daily_reporting/main.py · def sql_video_creator_mtd(d: dict)
-- Purpose:    MTD creator/video counts per product, current month vs M-1, M-2.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

WITH mtd AS (
    SELECT
        rp.rootlabs_simple_name                AS product,
        DATE_TRUNC('month', v.post_time)::date AS month_start,
        COUNT(DISTINCT v.video_id)             AS video_count,
        COUNT(DISTINCT v.handle)               AS creator_count
    FROM tiktok_raw_data.latest_tt_video v
    JOIN rootlabs_core.rootlabs_sku_listings sl
        ON sl.platform_product_id = v.product
       AND sl.listing_source = 'tiktok'
       AND sl.is_active = true
    JOIN rootlabs_core.rootlabs_products rp
        ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
       AND rp.product_status = 'active'
    WHERE v.post_time >= '{d["m2_start"]}'
      AND EXTRACT(DAY FROM v.post_time) <= {d["report_dom"]}
      AND v.product IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    product,
    COALESCE(MAX(video_count)   FILTER (WHERE month_start = '{d["m0_start"]}'), 0) AS videos_m0,
    COALESCE(MAX(creator_count) FILTER (WHERE month_start = '{d["m0_start"]}'), 0) AS creators_m0,
    COALESCE(MAX(video_count)   FILTER (WHERE month_start = '{d["m1_start"]}'), 0) AS videos_m1,
    COALESCE(MAX(creator_count) FILTER (WHERE month_start = '{d["m1_start"]}'), 0) AS creators_m1,
    COALESCE(MAX(video_count)   FILTER (WHERE month_start = '{d["m2_start"]}'), 0) AS videos_m2,
    COALESCE(MAX(creator_count) FILTER (WHERE month_start = '{d["m2_start"]}'), 0) AS creators_m2
FROM mtd
GROUP BY product
ORDER BY MAX(video_count) FILTER (WHERE month_start = '{d["m0_start"]}') DESC NULLS LAST;
