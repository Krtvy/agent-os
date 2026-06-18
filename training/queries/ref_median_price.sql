-- Provenance: _private/daily_reporting/reference/queries_final/01_median_price.sql
-- Purpose:    Frozen reference form (hard-coded date range). Useful as a template; for parameterized form see the matching `median_price.sql`.

-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

-- Median Price Tracking
-- Single day query. Replace date range for target day.
-- Filters: quantity = 1 (single-unit orders only), active products/listings,
--          non-zero price, no cancellations excluded (intentional).

SELECT
    rp.rootlabs_common_name                                 AS product,
    rp.sku_name                                             AS variation,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY t.sku_subtotal_after_discount
        )::numeric,
        2
    )                                                       AS median_customer_price
FROM tiktok_raw_data.tiktok_orders t
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id
   AND sl.listing_source = 'tiktok'
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
WHERE t.created_time >= '2026-04-15 00:00:00'
  AND t.created_time <  '2026-04-16 00:00:00'
  AND rp.product_status = 'active'
  AND sl.is_active       = true
  AND t.sku_unit_original_price <> 0
  AND t.quantity          = 1
GROUP BY rp.rootlabs_product_id, rp.rootlabs_common_name, rp.sku_name
ORDER BY LOWER(rp.rootlabs_common_name), rp.sku_name;
