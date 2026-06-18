-- Provenance: _private/excel_automation/automation/reports/live_gmv.py · _PIVOT_QUERY
-- Purpose:    Two queries: per-creator GMV pivot for livestream sales, AND day-level GMV+creator count for livestream sales (both filtered to specific product family).
-- Notes:      Parameters use psycopg2 `%(name)s` form. Common params: start, end (both as 'YYYY-MM-DD HH:MM:SS' strings).
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

SELECT
  DATE(t.created_time - INTERVAL '8 hours')                                 AS date,
  a.creator_username                                                         AS creator,
  SUM(t.sku_subtotal_after_discount + t.sku_platform_discount)              AS gmv
FROM tiktok_raw_data.tiktok_orders t
JOIN tiktok_raw_data.tiktok_affiliate_orders a
  ON t.order_id = a.order_id AND t.sku_id = a.sku_id
JOIN rootlabs_core.rootlabs_sku_listings sl
  ON t.sku_id = sl.platform_sku_id
 AND sl.listing_source = 'tiktok'
 AND sl.is_active = true
JOIN rootlabs_core.rootlabs_products rp
  ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
 AND rp.product_status = 'active'
WHERE t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price <> 0
  AND LOWER(a.content_type) = 'livestream'
  AND rp.rootlabs_common_name ILIKE %(product)s
  AND t.created_time >= %(start)s::timestamp + INTERVAL '8 hours'
  AND t.created_time <  %(end)s::timestamp   + INTERVAL '8 hours'
GROUP BY 1, 2
ORDER BY 1, 2;
