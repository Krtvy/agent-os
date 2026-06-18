-- Provenance: _private/excel_automation/automation/reports/hgr_free_orders.py · QUERY
-- Purpose:    Free orders for HGR product (samples / promo / zero-price), per day per creator.
-- Notes:      Parameters use psycopg2 `%(name)s` form. Common params: start, end (both as 'YYYY-MM-DD HH:MM:SS' strings).
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

SELECT
    t.order_id,
    t.sku_id,
    t.buyer_username,
    DATE(t.created_time   - INTERVAL '8 hours')   AS ordered_date,
    DATE(t.delivered_time - INTERVAL '8 hours')   AS delivery_date
FROM tiktok_raw_data.tiktok_orders t
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id
   AND sl.listing_source = 'tiktok'
   AND sl.is_active = true
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
   AND rp.product_status = 'active'
WHERE t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price = 0
  AND t.quantity = 1
  AND LOWER(REPLACE(REPLACE(rp.rootlabs_common_name, ' ', '_'), '+', '_')) LIKE '%%hgr%%'
  AND t.created_time >= %(start)s::timestamp + INTERVAL '8 hours'
  AND t.created_time <  %(end)s::timestamp   + INTERVAL '8 hours'
ORDER BY t.created_time, t.order_id, t.sku_id;
