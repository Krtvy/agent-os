# Median customer price (per product · per day)

## Plain English

For a single calendar day, what was the typical price a customer paid for one
unit of a given product? Use the median (not mean) so promos and zero-priced
free orders don't drag the number around.

## Mechanical definition

```sql
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.sku_subtotal_after_discount)
```

Grouped by `rp.rootlabs_common_name, rp.sku_name`.

## Filters / exclusions

- `quantity = 1` — single-unit orders only (multi-unit orders distort per-unit
  realized price)
- `rp.product_status = 'active' AND sl.is_active = true`
- `sku_unit_original_price <> 0` (excludes zero-price free orders)
- **Cancellations are NOT excluded** — this is intentional per the production
  query header

## IST convention

Date filter is on `t.created_time` directly (UTC range), not the
`DATE(created_time - INTERVAL '8 hours')` form. If switching to IST-day
boundaries, use the latter; the production reference query uses UTC range.

## Provenance

- Canonical (parameterized): `training/queries/median_price.sql`
- Frozen reference: `training/queries/ref_median_price.sql`
- Python source: `_private/daily_reporting/main.py · def sql_median_price(d)`
