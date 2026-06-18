-- Provenance: _private/daily_reporting/reference/queries_final/08_samples_shipped.sql
-- Purpose:    Frozen reference form (hard-coded date range). Useful as a template; for parameterized form see the matching `samples_shipped.sql`.

-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

-- Samples Shipped Last 3 Days
-- 3-day query. Counts orders where sku_unit_original_price = 0 (free/sample).
-- quantity = 1 filter. Per product, per day counts.

SELECT
    rp.rootlabs_common_name                                                AS product,
    COUNT(*) FILTER (WHERE DATE(t.created_time) = DATE '2026-04-13')       AS apr_13,
    COUNT(*) FILTER (WHERE DATE(t.created_time) = DATE '2026-04-14')       AS apr_14,
    COUNT(*) FILTER (WHERE DATE(t.created_time) = DATE '2026-04-15')       AS apr_15,
    COUNT(*)                                                               AS grand_total
FROM tiktok_raw_data.tiktok_orders t
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id AND sl.listing_source = 'tiktok'
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
WHERE t.created_time >= '2026-04-13 00:00:00'
  AND t.created_time <  '2026-04-16 00:00:00'
  AND t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price = 0
  AND t.quantity = 1
  AND rp.product_status = 'active'
  AND sl.is_active = true
GROUP BY rp.rootlabs_product_id, rp.rootlabs_common_name
ORDER BY COUNT(*) DESC;
