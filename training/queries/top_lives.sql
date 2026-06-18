-- Provenance: _private/daily_reporting/main.py · def sql_top_lives(d: dict)
-- Purpose:    Top livestreams by GMV for a window — creator, livestream count, GMV.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

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
WHERE (t.created_time - INTERVAL '8 hours') >= '{d["day_start"]}'
  AND (t.created_time - INTERVAL '8 hours') <  '{d["day_end"]}'
  AND t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price <> 0
  AND rp.product_status = 'active'
  AND sl.is_active       = true
  AND a.content_type = 'Livestream'
GROUP BY a.creator_username
ORDER BY gmv DESC
LIMIT 20
