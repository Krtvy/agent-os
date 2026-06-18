-- Provenance: _private/excel_automation/automation/reports/flagged_commission_rates.py · QUERY
-- Purpose:    Creators whose commission rate exceeded normal threshold — for flagging in the ops sheet.
-- Notes:      Parameters use psycopg2 `%(name)s` form. Common params: start, end (both as 'YYYY-MM-DD HH:MM:SS' strings).
-- IST convention: all date math uses `created_time - INTERVAL '8 hours'`
--   to align with Rootlabs-team's IST day boundary.
-- Read-only: this library is meant for read-only execution via
--   lib/yudhi-sql.sh. Never edit or DROP from these tables.
-- ────────────────────────────────────────────────────────────────────

WITH adjusted AS (
  SELECT
    creator_username,
    standard_commission_rate,
    shop_ads_commission_rate,
    (time_created - INTERVAL '12.5 hours') AS adj_time
  FROM tiktok_raw_data.tiktok_affiliate_orders
  WHERE product_name ILIKE '%%magnesium%%'
    AND (time_created - INTERVAL '12.5 hours') >= %(start)s::date
    AND (time_created - INTERVAL '12.5 hours') <  %(end)s::date
),
latest_std AS (
  SELECT DISTINCT ON (creator_username)
    creator_username,
    standard_commission_rate AS std_rate
  FROM adjusted
  WHERE standard_commission_rate IS NOT NULL
  ORDER BY creator_username, adj_time DESC
),
latest_shop AS (
  SELECT DISTINCT ON (creator_username)
    creator_username,
    shop_ads_commission_rate AS shop_rate
  FROM adjusted
  WHERE shop_ads_commission_rate IS NOT NULL
  ORDER BY creator_username, adj_time DESC
)
SELECT
  COALESCE(s.creator_username, sa.creator_username) AS creator,
  CASE
    WHEN s.std_rate = 80 AND sa.shop_rate >= 40 THEN 'both'
    WHEN s.std_rate = 80                         THEN 'organic'
    ELSE                                              'shop_ads'
  END AS type
FROM latest_std s
FULL OUTER JOIN latest_shop sa USING (creator_username)
WHERE s.std_rate = 80 OR sa.shop_rate >= 40
ORDER BY 1;
