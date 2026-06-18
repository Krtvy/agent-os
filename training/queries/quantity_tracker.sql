-- Provenance: _private/daily_reporting/main.py · def sql_quantity_tracker(d: dict)
-- Purpose:    Units sold per product+variation, MTD vs prior month same-range.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

SELECT
    rp.rootlabs_common_name                                              AS product,
    rp.sku_name                                                          AS variation,
    COALESCE(SUM(t.quantity * COALESCE(rp.unit_multiplier, 1))
        FILTER (WHERE DATE((t.created_time - INTERVAL '8 hours')) = DATE '{d["d_minus_2"]}'), 0)  AS day_0,
    COALESCE(SUM(t.quantity * COALESCE(rp.unit_multiplier, 1))
        FILTER (WHERE DATE((t.created_time - INTERVAL '8 hours')) = DATE '{d["d_minus_1"]}'), 0)  AS day_1,
    COALESCE(SUM(t.quantity * COALESCE(rp.unit_multiplier, 1))
        FILTER (WHERE DATE((t.created_time - INTERVAL '8 hours')) = DATE '{d["d_0"]}'), 0)        AS day_2
FROM tiktok_raw_data.tiktok_orders t
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id
   AND sl.listing_source = 'tiktok'
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
WHERE (t.created_time - INTERVAL '8 hours') >= '{d["three_day_start"]}'
  AND (t.created_time - INTERVAL '8 hours') <  '{d["day_end"]}'
  AND t.cancellation_return_type IS NULL
  AND t.sku_unit_original_price <> 0
  AND rp.product_status = 'active'
  AND sl.is_active       = true
GROUP BY rp.rootlabs_product_id, rp.rootlabs_common_name, rp.sku_name
ORDER BY LOWER(rp.rootlabs_common_name), rp.sku_name
