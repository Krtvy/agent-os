-- Creator activity by date range — per-product videos, lives, orders,
-- estimated commission, GMV, and New Video GMV.
--
-- DEFINITIONS (per Kartavvya):
--   videos_total                 = distinct videos posted in range
--   hgr/alpha/magashwa/bb/ppp_videos = per-hero-product video count
--   lives_done                   = distinct livestreams in range
--   orders_from_videos           = COUNT(DISTINCT order_id) from
--                                  Video-attributed affiliate orders
--   est_commission_organic       = SUM(est_standard_commission_payment)
--                                  on Video-attributed orders
--   est_commission_shop_ads      = SUM(est_shop_ads_commission_payment)
--                                  on Video-attributed orders
--                                  (zero/NULL on most rows — shop ads
--                                  only fires when the order came
--                                  through a paid Shop Ads listing)
--   gmv                          = total revenue (all content types)
--   new_video_gmv                = GMV from videos posted in the same
--                                  month as the order
--
-- IST: all timestamps converted via - INTERVAL '8 hours'.
-- POC filter: when 'poc' empty → all creators; when set, filters via
-- %(poc_creators)s::text[] bound from May Sheet PoC.csv ↔ portal roster.

WITH params AS (
  SELECT
    %(start_date)s::date AS start_d,
    %(end_date)s::date AS end_d,
    %(poc)s::text AS poc_name
),
-- All video-derived per-creator stats in one pass through tt_video +
-- the product-name join. Per-product columns use COUNT(DISTINCT CASE..)
-- so a video that's tagged with HGR contributes to hgr_videos but not
-- the other product columns.
video_stats AS (
  SELECT
    v.handle AS creator,
    COUNT(DISTINCT v.video_id) AS videos_total,
    COUNT(DISTINCT CASE WHEN rp.rootlabs_common_name = 'HGR'      THEN v.video_id END) AS hgr_videos,
    COUNT(DISTINCT CASE WHEN rp.rootlabs_common_name = 'Alpha'    THEN v.video_id END) AS alpha_videos,
    COUNT(DISTINCT CASE WHEN rp.rootlabs_common_name = 'MagAshwa' THEN v.video_id END) AS magashwa_videos,
    COUNT(DISTINCT CASE WHEN rp.rootlabs_common_name = 'BB'       THEN v.video_id END) AS bb_videos,
    COUNT(DISTINCT CASE WHEN rp.rootlabs_common_name = 'PPP'      THEN v.video_id END) AS ppp_videos
  FROM tiktok_raw_data.tt_video v
  LEFT JOIN rootlabs_core.rootlabs_sku_listings sl
    ON sl.platform_product_id = v.product
   AND sl.listing_source = 'tiktok'
   AND sl.is_active = true
  LEFT JOIN rootlabs_core.rootlabs_products rp
    ON rp.rootlabs_sku_id = sl.rootlabs_sku_id
  WHERE v.video_id IS NOT NULL
    AND v.post_time IS NOT NULL
    AND DATE(v.post_time - INTERVAL '8 hours')
        BETWEEN (SELECT start_d FROM params) AND (SELECT end_d FROM params)
    AND (
      (SELECT poc_name FROM params) = ''
      OR v.handle = ANY(%(poc_creators)s::text[])
    )
  GROUP BY v.handle
),
lives AS (
  SELECT creator_username AS creator, COUNT(DISTINCT content_id) AS lives_done
  FROM tiktok_raw_data.tiktok_affiliate_orders
  WHERE content_type = 'Livestream'
    AND content_id IS NOT NULL
    AND time_created IS NOT NULL
    AND DATE(time_created - INTERVAL '8 hours')
        BETWEEN (SELECT start_d FROM params) AND (SELECT end_d FROM params)
    AND (
      (SELECT poc_name FROM params) = ''
      OR creator_username = ANY(%(poc_creators)s::text[])
    )
  GROUP BY creator_username
),
-- All order-derived per-creator stats in one pass through
-- tiktok_orders × tiktok_affiliate_orders. Conditional aggregates
-- split video-specific vs total.
order_stats AS (
  SELECT
    a.creator_username AS creator,
    SUM(COALESCE(t.sku_subtotal_after_discount, 0)
        + COALESCE(t.sku_platform_discount, 0)) AS gmv,
    COUNT(DISTINCT CASE WHEN a.content_type = 'Video' THEN t.order_id END) AS orders_from_videos,
    -- Commission split into organic (standard) vs shop-ads streams.
    -- "Organic" = est_standard_commission_payment.
    -- "Shop ads" = est_shop_ads_commission_payment (when the order
    -- came through a TikTok Shop Ads-promoted listing).
    SUM(
      CASE WHEN a.content_type = 'Video'
           THEN COALESCE(a.est_standard_commission_payment, 0)
           ELSE 0 END
    ) AS est_commission_organic,
    SUM(
      CASE WHEN a.content_type = 'Video'
           THEN COALESCE(a.est_shop_ads_commission_payment, 0)
           ELSE 0 END
    ) AS est_commission_shop_ads
  FROM tiktok_raw_data.tiktok_orders t
  JOIN tiktok_raw_data.tiktok_affiliate_orders a
    ON t.order_id = a.order_id AND t.sku_id = a.sku_id
  WHERE t.cancellation_return_type IS NULL
    AND t.created_time IS NOT NULL
    AND DATE(t.created_time - INTERVAL '8 hours')
        BETWEEN (SELECT start_d FROM params) AND (SELECT end_d FROM params)
    AND (
      (SELECT poc_name FROM params) = ''
      OR a.creator_username = ANY(%(poc_creators)s::text[])
    )
  GROUP BY a.creator_username
),
-- New Video GMV: GMV from orders in the same month as the video's post.
videos_unique AS (
  SELECT DISTINCT ON (video_id) video_id, post_time
  FROM tiktok_raw_data.tt_video
  WHERE video_id IS NOT NULL AND post_time IS NOT NULL
    AND post_time >= (DATE_TRUNC('month', (SELECT start_d FROM params))::timestamp + INTERVAL '8 hours')
    AND post_time <  (DATE_TRUNC('month', (SELECT end_d FROM params))::timestamp + INTERVAL '1 month' + INTERVAL '8 hours')
  ORDER BY video_id, post_time DESC
),
new_video_gmv AS (
  SELECT
    a.creator_username AS creator,
    SUM(COALESCE(t.sku_subtotal_after_discount, 0)
        + COALESCE(t.sku_platform_discount, 0)) AS new_video_gmv
  FROM tiktok_raw_data.tiktok_orders t
  JOIN tiktok_raw_data.tiktok_affiliate_orders a
    ON t.order_id = a.order_id AND t.sku_id = a.sku_id
  JOIN videos_unique v
    ON v.video_id = a.content_id
  WHERE t.cancellation_return_type IS NULL
    AND a.content_type = 'Video'
    AND t.created_time IS NOT NULL
    AND DATE(t.created_time - INTERVAL '8 hours')
        BETWEEN (SELECT start_d FROM params) AND (SELECT end_d FROM params)
    AND DATE_TRUNC('month', t.created_time - INTERVAL '8 hours')
        = DATE_TRUNC('month', v.post_time - INTERVAL '8 hours')
    AND (
      (SELECT poc_name FROM params) = ''
      OR a.creator_username = ANY(%(poc_creators)s::text[])
    )
  GROUP BY a.creator_username
)
SELECT
  COALESCE(vs.creator, l.creator, os.creator, nvg.creator) AS creator,
  COALESCE(vs.videos_total, 0)     AS videos_total,
  COALESCE(vs.hgr_videos, 0)       AS hgr_videos,
  COALESCE(vs.alpha_videos, 0)     AS alpha_videos,
  COALESCE(vs.magashwa_videos, 0)  AS magashwa_videos,
  COALESCE(vs.bb_videos, 0)        AS bb_videos,
  COALESCE(vs.ppp_videos, 0)       AS ppp_videos,
  COALESCE(l.lives_done, 0)        AS lives_done,
  COALESCE(os.orders_from_videos, 0) AS orders_from_videos,
  ROUND(COALESCE(os.est_commission_organic, 0)::numeric, 2)  AS est_commission_organic,
  ROUND(COALESCE(os.est_commission_shop_ads, 0)::numeric, 2) AS est_commission_shop_ads,
  ROUND(COALESCE(os.gmv, 0)::numeric, 2)       AS gmv,
  ROUND(COALESCE(nvg.new_video_gmv, 0)::numeric, 2) AS new_video_gmv
FROM video_stats vs
FULL OUTER JOIN lives l         USING (creator)
FULL OUTER JOIN order_stats os  USING (creator)
FULL OUTER JOIN new_video_gmv nvg USING (creator)
WHERE COALESCE(vs.creator, l.creator, os.creator, nvg.creator) IS NOT NULL
ORDER BY gmv DESC, videos_total DESC;
