# Live GMV (livestream Gross Merchandise Value)

## Plain English

Revenue from orders that were placed through a TikTok livestream (`content_type = 'livestream'`).
"GMV" here means **realized customer payment plus platform discount add-back** —
i.e. the value of the goods sold, not the cash collected after platform absorbed
its share of discounts.

## Mechanical definition

```sql
SUM(t.sku_subtotal_after_discount + t.sku_platform_discount) AS gmv
```

Grouped per the dimension you need (day · creator · product).

## Filters / exclusions

- `t.cancellation_return_type IS NULL` — exclude cancelled / returned orders
- `t.sku_unit_original_price <> 0` — exclude zero-price free orders
- `LOWER(a.content_type) = 'livestream'` — restrict to livestream traffic only
- Active products + active listings (`rp.product_status = 'active'`,
  `sl.is_active = true`)

## IST convention

`DATE(t.created_time - INTERVAL '8 hours') AS date` for day grouping.
Range filter: `t.created_time >= %(start)s::timestamp + INTERVAL '8 hours'`
(so a user-passed IST date becomes the right UTC range).

## Product family filtering

The production pipeline filters live GMV per product family using
`rp.rootlabs_common_name ILIKE %(product)s`. Pattern conventions:

- `%` → all products (Overall DoD)
- `%hgr%` → HGR family (HGR DoD)
- `%magashwa%` → MagAshwa family (MagAshwa DoD)

## Provenance

- Pivot per creator: `training/queries/live_gmv___pivot_query.sql`
- Day-level totals: `training/queries/live_gmv___date_gmv_query.sql`
- Max-window aggregate: `training/queries/live_gmv_max.sql`
- Python source: `_private/excel_automation/automation/reports/live_gmv.py`
