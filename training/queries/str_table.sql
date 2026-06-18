-- Provenance: _private/daily_reporting/main.py · def sql_str_table(d: dict)
-- Purpose:    Spend-to-revenue table (STR) — ads cost vs GMV per product/day.
-- Notes:      Parameters are :name placeholders — substitute via psycopg2 `%(name)s` or pass via lib/yudhi-sql.sh -p name=value.
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

WITH revenue AS (
    SELECT
        rp.rootlabs_product_id,
        rp.rootlabs_common_name                                            AS product,
        ROUND(SUM(COALESCE(t.sku_subtotal_after_discount, 0))::numeric, 0) AS revenue,
        ROUND(SUM(COALESCE(t.sku_platform_discount, 0))::numeric, 0)       AS platform_discounts,
        ROUND(SUM(COALESCE(t.shipping_fee_after_discount, 0))::numeric, 0) AS shipping_revenue
    FROM tiktok_raw_data.tiktok_orders t
    JOIN rootlabs_core.rootlabs_sku_listings sl
        ON t.sku_id = sl.platform_sku_id AND sl.listing_source = 'tiktok'
    JOIN rootlabs_core.rootlabs_products rp
        ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
    WHERE (t.created_time - INTERVAL '8 hours') >= '{d["day_start"]}'
      AND (t.created_time - INTERVAL '8 hours') <  '{d["day_end"]}'
      AND t.cancellation_return_type IS NULL
      AND t.sku_unit_original_price <> 0
      AND rp.product_status = 'active'
      AND sl.is_active = true
    GROUP BY rp.rootlabs_product_id, rp.rootlabs_common_name
),
commissions AS (
    SELECT
        pm.rootlabs_product_id,
        ROUND(SUM(COALESCE(a.actual_commission_payment,
                           a.est_standard_commission_payment, 0))::numeric, 0)     AS affiliate_commission,
        ROUND(SUM(COALESCE(a.actual_shop_ads_commission_payment,
                           a.est_shop_ads_commission_payment, 0))::numeric, 0)     AS shop_ads_commission,
        ROUND(SUM(
            COALESCE(t.sku_subtotal_after_discount, 0)
            + COALESCE(t.sku_platform_discount, 0)
        )::numeric, 0)                                                              AS affiliate_revenue
    FROM tiktok_raw_data.tiktok_affiliate_orders a
    JOIN tiktok_raw_data.tiktok_orders t
        ON a.order_id = t.order_id AND a.sku_id = t.sku_id
    JOIN (
        SELECT DISTINCT sl.platform_product_id,
               rp.rootlabs_product_id
        FROM rootlabs_core.rootlabs_sku_listings sl
        JOIN rootlabs_core.rootlabs_products rp
            ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
        WHERE rp.product_status = 'active'
          AND sl.listing_source = 'tiktok'
          AND sl.platform_product_id IS NOT NULL
    ) pm ON a.product_id = pm.platform_product_id
    WHERE (t.created_time - INTERVAL '8 hours') >= '{d["day_start"]}'
      AND (t.created_time - INTERVAL '8 hours') <  '{d["day_end"]}'
      AND t.cancellation_return_type IS NULL
    GROUP BY pm.rootlabs_product_id
),
gmv_max AS (
    SELECT
        rp.rootlabs_product_id,
        ROUND(SUM(COALESCE(pc.cost, 0))::numeric, 0)                      AS gmv_max
    FROM tiktok_raw_data.product_campaign_performance pc
    JOIN (
        SELECT DISTINCT rootlabs_product_id, associated_campaign_id
        FROM rootlabs_core.rootlabs_products
        WHERE associated_campaign_id IS NOT NULL
          AND product_status = 'active'
    ) rp ON pc.campaign_id = rp.associated_campaign_id
    WHERE pc.report_date = DATE '{d["report_date"]}'
    GROUP BY rp.rootlabs_product_id
)
SELECT
    r.product,
    COALESCE(c.affiliate_commission, 0)   AS affiliate_commission,
    COALESCE(c.shop_ads_commission, 0)    AS shop_ads_commission,
    COALESCE(g.gmv_max, 0)               AS gmv_max,
    COALESCE(c.affiliate_commission, 0)
        + COALESCE(c.shop_ads_commission, 0)
        + COALESCE(g.gmv_max, 0)          AS total_spends,
    COALESCE(c.affiliate_revenue, 0)      AS affiliate_revenue,
    r.revenue,
    r.platform_discounts,
    r.shipping_revenue,
    r.revenue + r.platform_discounts
        + r.shipping_revenue              AS total_revenue
FROM revenue r
LEFT JOIN commissions c ON r.rootlabs_product_id = c.rootlabs_product_id
LEFT JOIN gmv_max g     ON r.rootlabs_product_id = g.rootlabs_product_id
ORDER BY r.revenue + r.platform_discounts + r.shipping_revenue DESC
