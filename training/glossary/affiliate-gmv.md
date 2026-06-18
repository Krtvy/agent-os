# Affiliate GMV

## Plain English

Revenue from TikTok affiliate orders, broken down by creator, product, content
type, and **traffic type** (organic vs shop-ads).

## Mechanical definition

```sql
SUM(t.sku_subtotal_after_discount + t.sku_platform_discount) AS gmv
```

With a derived `traffic_type`:

```sql
CASE WHEN COALESCE(a.actual_shop_ads_commission_payment,
                   a.est_shop_ads_commission_payment, 0) > 0
     THEN 'shop_ads' ELSE 'organic' END
```

Grouped by `date, creator, product, content_type, content_id, post_date, traffic_type`.

## Filters / exclusions

- `t.cancellation_return_type IS NULL`
- `t.sku_unit_original_price <> 0`
- Active products + active listings

## Naming normalization

The pipeline normalizes product + content_type for sheet-friendliness:

```sql
LOWER(REPLACE(REPLACE(rp.rootlabs_common_name, ' ', '_'), '+', '_')) AS product
LOWER(REPLACE(a.content_type, ' ', '_'))                            AS content_type
```

## Output mode

Upserted into a Google Sheet tab keyed on
`(date, creator, product, content_type, content_id, traffic_type)`, with a
7-day lookback window so late-arriving rows are caught.

## Provenance

- Canonical: `training/queries/affiliate_gmv.sql`
- Python source: `_private/excel_automation/automation/reports/affiliate_gmv.py`
