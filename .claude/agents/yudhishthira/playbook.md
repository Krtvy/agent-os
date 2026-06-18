# ⚖️ Yudhishthira — Playbook

> Living procedural reference for Yudhishthira (data analyst agent). File locations, canonical schemas, metric definitions, recurring task patterns, intern conventions. Updated as patterns are learned.
>
> Hyperagent document ID: `cmp1f7kpo105407adc5ijk8r9`. This local copy mirrors the deployed Playbook so Sanjaya can observe its growth. The deployed copy on Hyperagent is the source of truth — keep this file in sync after each Playbook update.

## File locations

Canonical file paths and where to find what. Updated as we go.

- **SQL query library** — `training/queries/*.sql` (24 queries as of 2026-05-15; one `-- Purpose:` line per file for grep).
- **Metric glossary** — `training/glossary/*.md` (one file per metric: median-price, live-gmv, affiliate-gmv, str-table, mtd, schemas).
- **SQL wrapper** — `lib/yudhi-sql.sh` (read-only Supabase access; never invoke psycopg2 directly).
- **Glossary index** — `training/glossary/README.md` (master list of defined metrics).
- **Schema map** — `training/glossary/schemas.md` (Supabase schemas + canonical join chain + IST convention).
- **Source projects (gitignored)** — `_private/excel_automation/` and `_private/daily_reporting/` are the production pipelines we mined for queries. Don't run them; reference them for context.

## Canonical schemas

Column shapes for recurring tables. Source of truth: `training/glossary/schemas.md`.

- `tiktok_raw_data.tiktok_orders` — one row per order line item. Hot columns: `order_id`, `sku_id`, `created_time` (UTC), `sku_unit_original_price`, `sku_subtotal_after_discount`, `sku_platform_discount`, `quantity`, `cancellation_return_type`.
- `tiktok_raw_data.tiktok_affiliate_orders` — affiliate join. Hot columns: `creator_username`, `content_type`, `content_id`, `actual_shop_ads_commission_payment`, `est_shop_ads_commission_payment`.
- `rootlabs_core.rootlabs_products` — product master. Keys: `rootlabs_product_id`, `rootlabs_sku_id`. Useful: `rootlabs_common_name`, `sku_name`, `product_status`.
- `rootlabs_core.rootlabs_sku_listings` — platform-listing → Rootlabs-SKU map. Keys: `platform_sku_id`, `listing_source`, `is_active`.

**Canonical join chain** (copy verbatim — see `training/glossary/schemas.md`):

```sql
FROM tiktok_raw_data.tiktok_orders t
JOIN tiktok_raw_data.tiktok_affiliate_orders a
    ON t.order_id = a.order_id AND t.sku_id = a.sku_id
JOIN rootlabs_core.rootlabs_sku_listings sl
    ON t.sku_id = sl.platform_sku_id
   AND sl.listing_source = 'tiktok' AND sl.is_active = true
JOIN rootlabs_core.rootlabs_products rp
    ON sl.rootlabs_sku_id = rp.rootlabs_sku_id
   AND rp.product_status = 'active'
```

## Metric definitions

How metrics are computed in this org. Authoritative source: `training/glossary/*.md`.

| Metric                | Glossary file          | One-liner                                                                                                     |
| --------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------- |
| Live GMV              | `live-gmv.md`          | `SUM(sku_subtotal_after_discount + sku_platform_discount)` for `content_type = 'livestream'`.                 |
| Affiliate GMV         | `affiliate-gmv.md`     | Same SUM formula across all content_types; splits traffic into `shop_ads` vs `organic` via commission column. |
| Median customer price | `median-price.md`      | `PERCENTILE_CONT(0.5)` over `sku_subtotal_after_discount`, with `quantity = 1`. Cancellations NOT excluded.   |
| STR                   | `str-table.md`         | `ads_spend / GMV`. Lower is better. Normalized by max-live-GMV in the window for cross-product comparison.    |
| MTD                   | `mtd.md`               | Calendar-month-start to target day; compared like-for-like across M0/M1/M2 same day-of-month.                 |
| MoM                   | (no glossary file yet) | Trailing 30 days, NOT calendar month. Per intern policy — see memory M??? when teaching.                      |

## Recurring task patterns

### POC CSV enrichment via DB

The intern has POC creators in `pocs/<name>/` directories. A common ask: "for the POC's creators, what was their May live GMV?"

1. **Profile** the POC CSV (P2): rows, columns, sample creator names.
2. **Read** `training/glossary/live-gmv.md` for the metric definition.
3. **Pull** `training/queries/live_gmv___pivot_query.sql` and parameterize `start`, `end`, `product`. Or write a tighter ad-hoc query that filters by `creator_username IN (...)` from the CSV.
4. **Run** via `lib/yudhi-sql.sh -f <query> -p start=... -p end=... --out /tmp/live_gmv_<window>.csv`.
5. **Join** the POC CSV with the query output on `creator_username` (pandas).
6. **Audit** row counts at each filter step. Flag creators with no DB match.
7. **Deliver** the enriched CSV + audit MD per the standard P6 deliverable format.

The POC CSV is the workflow layer; the DB is the source of truth. Never edit the POC CSV's structure beyond appending columns.

### Single-number DB lookup

If the intern asks "what was total live GMV last week?":

1. Read glossary entry.
2. Grep `training/queries/` for an existing query.
3. Parameterize and run.
4. Deliver MD only (no CSV needed for a single number).
5. Include in the MD: the exact SQL run, the filters applied, the IST date range, the result, and a one-sentence audit ("Cross-checked against `live_gmv___date_gmv_query.sql` summed over the window — matches.").

## Intern conventions

- **POC directories** — under `pocs/<name>/`. Each POC has its own working dir; never spill outputs into the wrong one.
- **CSV naming** — `<task>_<YYYY-MM-DD>.csv` for deliverables; `<thing>_snapshot_<YYYY-MM-DD>.csv` for explicit moment-in-time exports.
- **$ locks in Sheets formulas** — per memory `feedback_sheets_dollar_locks`: always lock refs deliberately ($A1 / A$1 / $A$1), state in the audit MD which side is locked and why, and which way the formula fills.
- **IST timezone** — all date math is IST-local. The DB has UTC timestamps; the canonical IST shift is `created_time - INTERVAL '8 hours'`. See `training/glossary/schemas.md`.

## Open questions

- **MoM definition glossary entry** — memory says trailing 30 days, no glossary file yet. Promote to `training/glossary/mom.md` next time the topic comes up.
- **Phase 2 Sheets write-back** — still pending dedicated service account provisioning.
- **POC schema convention** — what's the standard column set for a POC creator CSV? Document once we've seen 3+ examples.

## Change log

- 2026-05-11 — bootstrap — initial empty playbook created.
- 2026-05-15 — DB access added. SQL query library at `training/queries/` (24 queries); glossary at `training/glossary/` (5 metrics + schema map); read-only wrapper at `lib/yudhi-sql.sh`. Skill file updated with hard constraints 11–13 (no destructive SQL, glossary-first, grep-queries-first). Source projects: `_private/excel_automation/` and `_private/daily_reporting/` (gitignored).
