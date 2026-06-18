-- Provenance: _private/daily_reporting/reference/queries_final/07_str_table.sql
-- Purpose:    Frozen reference form (hard-coded date range). Useful as a template; for parameterized form see the matching `str_table.sql`.

-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

-- STR Table (Spend-to-Revenue)
-- Single day query. 3 CTEs: revenue, commissions, gmv_max + separate live_gmv_max query.
-- Revenue from tiktok_orders. Commissions from affiliate_orders joined to orders.
-- GMV MAX from product_campaign_performance (uses report_date, not created_time).
-- Live GMV MAX from live_campaign_performance (aggregate, no product breakdown).
-- Commissions: actual → estimated fallback. Cancelled orders excluded.

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
    WHERE t.created_time >= '2026-04-15 00:00:00'
      AND t.created_time <  '2026-04-16 00:00:00'
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
    WHERE t.created_time >= '2026-04-15 00:00:00'
      AND t.created_time <  '2026-04-16 00:00:00'
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
    WHERE pc.report_date = DATE '2026-04-15'
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
ORDER BY r.revenue + r.platform_discounts + r.shipping_revenue DESC;


-- Live GMV Max (separate query, aggregate only, no product breakdown)
-- Added as a standalone row before Totals in the report.
-- Included in Totals row's GMV MAX and Total Spend.

SELECT COALESCE(SUM(COALESCE(cost, 0)), 0)::int AS live_gmv_max
FROM tiktok_raw_data.live_campaign_performance
WHERE report_date = DATE '2026-04-15';
