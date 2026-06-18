-- Provenance: _private/excel_automation/automation/reports/videos_posted.py · QUERY
-- Purpose:    Count of videos posted per creator per day, with creator + content metadata.
-- Notes:      Parameters use psycopg2 `%(name)s` form. Common params: start, end (both as 'YYYY-MM-DD HH:MM:SS' strings).
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

WITH videos AS (
    SELECT DISTINCT ON (video_id)
        video_id,
        handle,
        product,
        post_time
    FROM tiktok_raw_data.tt_video
    WHERE video_id IS NOT NULL
      AND post_time IS NOT NULL
    ORDER BY video_id, post_time DESC
)
SELECT
    DATE(v.post_time)                                                       AS date,
    v.handle                                                                AS creator,
    LOWER(REPLACE(REPLACE(rp.rootlabs_common_name, ' ', '_'), '+', '_'))    AS product,
    COUNT(DISTINCT v.video_id)                                              AS video_count
FROM videos v
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON sl.platform_product_id = v.product
   AND sl.listing_source = 'tiktok'
   AND sl.is_active = true
JOIN rootlabs_core.rootlabs_products rp
    ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
   AND rp.product_status = 'active'
WHERE v.post_time >= %(start)s
  AND v.post_time <  %(end)s
  AND rp.rootlabs_common_name IN ('HGR', 'MagAshwa', 'Alpha', 'PPP', 'BB')
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
