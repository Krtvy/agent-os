-- Provenance: _private/daily_reporting/reference/queries_final/03_content_type_split.sql
-- Purpose:    Frozen reference form (hard-coded date range). Useful as a template; for parameterized form see the matching `content_type_split.sql`.

-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

-- Content Type Split
-- Single day query. Live vs Video GMV breakdown per product.
-- Joins tiktok_orders (revenue columns) with tiktok_affiliate_orders (content_type).
-- GMV = sku_subtotal_after_discount + sku_platform_discount.
-- Only Video and Livestream content types. Products with >= $1 GMV.

SELECT
    rp.rootlabs_common_name                                                AS product,
    ROUND(COALESCE(SUM(
        COALESCE(t.sku_subtotal_after_discount, 0)
        + COALESCE(t.sku_platform_discount, 0)
    ) FILTER (WHERE a.content_type = 'Livestream'), 0)::numeric, 2)        AS live_gmv,
    ROUND(COALESCE(SUM(
        COALESCE(t.sku_subtotal_after_discount, 0)
        + COALESCE(t.sku_platform_discount, 0)
    ) FILTER (WHERE a.content_type = 'Video'), 0)::numeric, 2)            AS video_gmv
FROM tiktok_raw_data.tiktok_orders t
JOIN tiktok_raw_data.tiktok_affiliate_orders a
    ON t.order_id = a.order_id AND t.sku_id = a.sku_id
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id AND sl.listing_source = 'tiktok'
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
WHERE t.created_time >= '2026-04-15 00:00:00'
  AND t.created_time <  '2026-04-16 00:00:00'
  AND t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price <> 0
  AND rp.product_status = 'active'
  AND sl.is_active       = true
  AND a.content_type IN ('Video', 'Livestream')
GROUP BY rp.rootlabs_product_id, rp.rootlabs_common_name
HAVING SUM(COALESCE(t.sku_subtotal_after_discount, 0)
         + COALESCE(t.sku_platform_discount, 0)) >= 1
ORDER BY LOWER(rp.rootlabs_common_name);
