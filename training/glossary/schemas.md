# Rootlabs Supabase — schema map

## Schemas visible to `rachit_analytics`

Discovered via `SELECT schema_name FROM information_schema.schemata` on
2026-05-15. Re-run periodically to detect new schemas.

| Schema                          | What it contains (best guess from production queries)                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| `rootlabs_core`                 | Master tables: products, SKU listings, team members, communication channels.                    |
| `tiktok_raw_data`               | Order-level facts from TikTok Shop. The hot tables: `tiktok_orders`, `tiktok_affiliate_orders`. |
| `tt_creator_relations_raw_data` | Creator profile / outreach data from TikTok Creator Relations side.                             |
| `creator_dashboard`             | Curated views for the creator-facing dashboard.                                                 |
| `acq_dashboard`                 | Acquisition-funnel dashboard tables.                                                            |
| `tejas_sync`                    | Tejas (whichever upstream service that is) sync staging.                                        |
| `wp_convo`                      | WhatsApp conversation tables (Periskope or similar).                                            |
| `public`                        | Default Postgres schema — usually empty in Supabase.                                            |

## Hot tables — `rootlabs_core`

| Table                             | Notes                                                                                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `rootlabs_products`               | One row per Rootlabs product. Keys: `rootlabs_product_id`, `rootlabs_sku_id`. Useful: `rootlabs_common_name`, `sku_name`, `product_status`. |
| `rootlabs_sku_listings`           | Maps each platform listing (TikTok / Amazon / Shopify) to a Rootlabs SKU. Keys: `platform_sku_id`, `listing_source`, `is_active`.           |
| `rootlabs_communication_channels` | Comms channels (Slack, WhatsApp groups, etc.).                                                                                              |
| `rootlabs_team_members`           | Team roster.                                                                                                                                |
| `team_member_phones`              | Phone numbers per team member.                                                                                                              |

## Hot tables — `tiktok_raw_data`

| Table                     | Notes                                                                                                                                                                                                                             |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tiktok_orders`           | One row per order line item. Hot columns: `order_id`, `sku_id`, `created_time` (UTC), `sku_unit_original_price`, `sku_subtotal_after_discount`, `sku_platform_discount`, `quantity`, `cancellation_return_type`.                  |
| `tiktok_affiliate_orders` | One row per affiliate-attributed order line. Joins to `tiktok_orders` on (`order_id`, `sku_id`). Hot columns: `creator_username`, `content_type` (video/livestream/showcase), `content_id`, `actual_shop_ads_commission_payment`. |

## Canonical join

The product-resolution chain used by every GMV / revenue query:

```sql
FROM tiktok_raw_data.tiktok_orders t
JOIN tiktok_raw_data.tiktok_affiliate_orders a
    ON t.order_id = a.order_id AND t.sku_id = a.sku_id
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id
   AND sl.listing_source = 'tiktok'
   AND sl.is_active = true
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
   AND rp.product_status = 'active'
```

Copy this exact join whenever you need "order rows enriched with creator +
Rootlabs product names." Never re-derive from scratch.

## IST date boundary

`tiktok_orders.created_time` is UTC. The Rootlabs IST day is offset −8 hours
from this column (UTC+5:30 minus the ~13.5-hour wraparound the team treats as
"a TikTok day"). Canonical form:

```sql
DATE(t.created_time - INTERVAL '8 hours') AS date
```

For range filtering:

```sql
WHERE t.created_time >= %(start)s::timestamp + INTERVAL '8 hours'
  AND t.created_time <  %(end)s::timestamp   + INTERVAL '8 hours'
```

(Pass `start` and `end` as IST-local date strings; this shifts them into the
right UTC range.)

## Discovery cheat-sheet

```bash
# Schemas
lib/yudhi-sql.sh -c "SELECT schema_name FROM information_schema.schemata
  WHERE schema_name NOT LIKE 'pg_%' AND schema_name <> 'information_schema'
  ORDER BY schema_name"

# Tables in a schema
lib/yudhi-sql.sh -c "SELECT table_name FROM information_schema.tables
  WHERE table_schema = 'rootlabs_core' ORDER BY table_name"

# Columns of a table
lib/yudhi-sql.sh -c "SELECT column_name, data_type FROM information_schema.columns
  WHERE table_schema = 'tiktok_raw_data' AND table_name = 'tiktok_orders'
  ORDER BY ordinal_position"

# Row count (capped — DO NOT remove the LIMIT trick)
lib/yudhi-sql.sh -c "SELECT count(*) FROM tiktok_raw_data.tiktok_orders
  WHERE created_time >= NOW() - INTERVAL '7 days'"
```
