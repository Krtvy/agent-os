# STR (Spend-to-Revenue ratio)

## Plain English

For a given product + day, how many dollars of ads spend did Rootlabs invest
per dollar of GMV produced? Lower is better. STR is the headline efficiency
metric for the ads team.

## Mechanical definition

```
STR = ads_spend / GMV
```

GMV here uses the same `sku_subtotal_after_discount + sku_platform_discount`
formula as Live GMV / Affiliate GMV. Ads spend comes from the
`cost` field in the campaigns table.

## Why "max" appears in `live_gmv_max.sql`

When normalizing STR across products in the same dashboard, the production
pipeline divides each product's STR by the **max live GMV** seen in the
window. This gives a relative-size axis so a tiny product's bad STR doesn't
visually dominate a giant product's slightly-bad STR.

## Provenance

- STR table: `training/queries/str_table.sql`
- Frozen reference: `training/queries/ref_str_table.sql`
- Live GMV max (normalization): `training/queries/live_gmv_max.sql`
- Python source: `_private/daily_reporting/main.py · def sql_str_table(d)`
  and `def sql_live_gmv_max(d)`

## Output

A grid where rows = products, columns = days. Each cell shows
spend / GMV / STR ratio in a stacked layout. Rendered to PNG by
Playwright and pushed to Slack via the daily reporting pipeline.
