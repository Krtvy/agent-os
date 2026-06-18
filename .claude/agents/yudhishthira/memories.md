# Yudhishthira — Memories

> Atomic facts (the _what_, not the _how_). One entry per fact. Read at the start of every session alongside the playbook.
>
> **Rules:**
>
> 1. Entries are added only when the intern explicitly says "remember this" (or equivalent). Yudhishthira never sneaks facts into this file.
> 2. Entries are one line of fact + one line of context. Concise.
> 3. Append-only with respect to entries. Superseded facts get a `[SUPERSEDED YYYY-MM-DD — see entry N]` annotation; the new entry is added below.
> 4. Procedures and patterns belong in `playbook.md`, not here. If a fact is more than one line of detail, it's probably a procedure.

---

## Format

Each entry has:

```
### M<NNN>. <one-line fact>
- Added: YYYY-MM-DD
- Scope: <when this applies — e.g., "always", "only for GMV tasks", "this project only">
- Source: <intern phrase that established the fact, paraphrased>
```

---

## Entries

### M001. Read-only Supabase Postgres access exists at `lib/yudhi-sql.sh`

- Added: 2026-05-15
- Scope: always — whenever a task could benefit from a DB lookup, this is the only sanctioned access path.
- Source: Kartavya, "the intern has access to the database now; the agent is empowered with the database, so he can work on the CSV and also he can add data from the database to the CSV."

### M002. Canonical SQL query library lives at `training/queries/*.sql`

- Added: 2026-05-15
- Scope: always — grep here before writing any fresh SQL. 24 queries extracted from production pipelines.
- Source: derived from `_private/daily_reporting/main.py` (sql\__ functions) and `\_private/excel_automation/automation/reports/_.py`.

### M003. Metric definitions live at `training/glossary/*.md`

- Added: 2026-05-15
- Scope: always — read the glossary entry BEFORE computing any defined metric (Live GMV, Affiliate GMV, Median Price, STR, MTD).
- Source: extracted from production pipelines on 2026-05-15.

### M004. IST day boundary = `DATE(created_time - INTERVAL '8 hours')`

- Added: 2026-05-15
- Scope: always for any query on `tiktok_raw_data.tiktok_orders`. Column is UTC; Rootlabs reports in IST-local days.
- Source: production code in `_private/daily_reporting/main.py` and `_private/excel_automation/automation/reports/live_gmv.py`.

### M005. Canonical join chain: orders → affiliate_orders → sku_listings → products

- Added: 2026-05-15
- Scope: any query that needs creator + Rootlabs product name. Copy verbatim from `training/glossary/schemas.md`; never re-derive.
- Source: identical chain appears in every revenue/GMV query across both production projects.

### M006. Active-products filter is mandatory for production parity

- Added: 2026-05-15
- Scope: GMV / revenue queries. Always include `rp.product_status = 'active' AND sl.is_active = true`.
- Source: every production GMV query includes these filters.

### M007. Cancellation filter for GMV: `t.cancellation_return_type IS NULL`

- Added: 2026-05-15
- Scope: GMV / revenue queries. EXCEPTION: the median-price query intentionally does NOT exclude cancellations (see `training/glossary/median-price.md`).
- Source: production pipeline pattern.

### M008. Database user is `rachit_analytics`; database is `postgres` on Supabase pooler

- Added: 2026-05-15
- Scope: useful for debugging connection issues only. NEVER echo credentials. The wrapper handles auth.
- Source: `lib/yudhi-sql.sh --probe` output 2026-05-15 02:51 IST.

### M009. Destructive SQL is hard-rejected by `lib/yudhi-sql.sh`

- Added: 2026-05-15
- Scope: always. INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER/GRANT/REVOKE/CREATE/COMMENT/REINDEX/CLUSTER/VACUUM/COPY/MERGE/REPLACE all rejected pre-flight. Do NOT construct workarounds. Escalate to Kartavya if a write is genuinely needed.
- Source: skill.md hard constraint #11.

### M010. POC enrichment flow: profile CSV → glossary → grep queries → run → join → audit → deliver

- Added: 2026-05-15
- Scope: any task that takes a POC CSV and asks for DB-derived numbers. Procedure detailed in `playbook.md` § Recurring task patterns.
- Source: Kartavya, 2026-05-15 — POCs need to enrich their CSVs with DB data.

---

(Append M011, M012, … as the intern teaches atomic facts.)

Example shape:

```
### M001. Canonical GMV table is gmv_data.csv at ~/projects/observer-test/data/
- Added: 2026-05-11
- Scope: always — any GMV question defaults to this file unless intern says otherwise.
- Source: intern, "the canonical GMV table is gmv_data.csv, remember that."

### M002. MoM means trailing 30 days, not calendar month
- Added: 2026-05-11
- Scope: always — applies to GMV, orders, active-creator metrics.
- Source: intern, "remember MoM is trailing 30 days for us."

### M003. status='pending' is excluded from GMV totals by default
- Added: 2026-05-11
- Scope: gmv_data.csv only.
- Source: intern, "remember pending rows aren't counted in GMV."
```

---

## Change log

- 2026-05-11 — bootstrap — initial empty memories file created.
