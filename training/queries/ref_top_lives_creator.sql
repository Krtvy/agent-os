-- Provenance: _private/daily_reporting/reference/queries_final/06_top_lives_creator.sql
-- Purpose:    Frozen reference form (hard-coded date range). Useful as a template; for parameterized form see the matching `top_lives_creator.sql`.

-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

-- Top Lives Creator
-- Single day query. Livestream-only creators ranked by GMV.
-- GMV = sku_subtotal_after_discount + sku_platform_discount.
-- Quantity = quantity * unit_multiplier.
-- Lives count = COUNT(DISTINCT content_id).

SELECT
    a.creator_username,
    COUNT(DISTINCT a.content_id)                                   AS lives_count,
    SUM(t.quantity * COALESCE(rp.unit_multiplier, 1))              AS quantity,
    ROUND(SUM(
        COALESCE(t.sku_subtotal_after_discount, 0)
        + COALESCE(t.sku_platform_discount, 0)
    )::numeric, 0)                                                 AS gmv
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
  AND a.content_type = 'Livestream'
GROUP BY a.creator_username
ORDER BY gmv DESC
LIMIT 20;
