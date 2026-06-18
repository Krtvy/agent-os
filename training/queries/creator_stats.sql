-- Provenance: _private/daily_reporting/main.py · def sql_creator_stats(d: dict)
-- Purpose:    Per-creator stats for the last reporting day: GMV, orders, videos, lives.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

WITH base AS (
    SELECT
        a.creator_username,
        a.content_type,
        rp.rootlabs_common_name                        AS product,
        t.quantity * COALESCE(rp.unit_multiplier, 1)   AS units
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
),
per_creator AS (
    SELECT
        creator_username,
        COALESCE(SUM(units) FILTER (WHERE content_type = 'Video'), 0)                    AS video,
        COALESCE(SUM(units) FILTER (WHERE content_type = 'Livestream'), 0)                AS livestream,
        COALESCE(SUM(units) FILTER (WHERE content_type = 'Showcase'), 0)                  AS showcase,
        COALESCE(SUM(units) FILTER (WHERE content_type = 'External Traffic Program'), 0)  AS external_traffic,
        SUM(units)                                                                        AS grand_total
    FROM base
    GROUP BY creator_username
),
top_product AS (
    SELECT DISTINCT ON (creator_username)
        creator_username,
        product AS top_product
    FROM (
        SELECT creator_username, product, SUM(units) AS product_units
        FROM base
        GROUP BY creator_username, product
    ) sub
    ORDER BY creator_username, product_units DESC
)
SELECT
    c.creator_username,
    c.video,
    c.livestream,
    c.showcase,
    c.external_traffic,
    c.grand_total,
    tp.top_product
FROM per_creator c
JOIN top_product tp ON c.creator_username = tp.creator_username
ORDER BY c.grand_total DESC
LIMIT 20
