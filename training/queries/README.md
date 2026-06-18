# Canonical SQL query library

Extracted from the two production projects (`excel_automation` + `daily_reporting`)
that already run against the Rootlabs Supabase. These are the team's
actual proven queries — copy, parameterize, run.

## Run via the read-only wrapper

```bash
lib/yudhi-sql.sh -f training/queries/median_price.sql -p target_day=2026-05-14
```

See `lib/yudhi-sql.sh --help` for full options.

## Conventions used everywhere

- **IST day boundary**: `DATE(t.created_time - INTERVAL '8 hours')`
  (DB stores UTC; Rootlabs reporting is IST).
- **Active-products filter**: `rp.product_status = 'active' AND sl.is_active = true`.
- **Cancellation filter**: `t.cancellation_return_type IS NULL`.
- **Price filter**: `t.sku_unit_original_price <> 0` (excludes promos / free orders).
- **Parameters**: `%(name)s` placeholders for psycopg2; substitute via
  `lib/yudhi-sql.sh -p name=value`.

## Query inventory

Total queries: 24.

Each file has a `-- Provenance:` and `-- Purpose:` header line so you
can grep for capability before opening files:

```bash
grep -l "median" training/queries/*.sql
grep "Purpose:" training/queries/*.sql | head
```

## Refresh

Regenerate from the source projects whenever they change:

```bash
.venv/bin/python training/queries/_extract.py
```

Output is deterministic from the source.
