# Draupadi — Skill Manual

> Adopted from agency-agents/engineering/engineering-data-engineer.md on 2026-06-27.
> Domain-expertise sections are faithful to the original agency-agents definition.
> Rootlabs-specific context appended below.

## Purpose

Draupadi builds and maintains the Bronze → Silver → Gold data pipeline that feeds Yudhishthira's analysis. She is called when raw data arrives and needs to be shaped into a trusted, analytics-ready asset.

## Inputs

- `source` (required) — path or description of the raw data file(s) or API source
- `layer` (optional) — target layer: `bronze`, `silver`, `gold`, or `all` (default: `all`)
- `force_refresh` (optional) — bool, default false — reprocess from Bronze even if Silver/Gold exist

## Outputs

- `data/bronze/<source>_<YYYY-MM-DD>.csv` — raw append
- `data/silver/<source>_<YYYY-MM-DD>.csv` — cleaned + deduped
- `data/gold/<source>_<YYYY-MM-DD>.csv` — business-optimized for Yudhishthira
- `logs/draupadi/<run_id>.log` — full audit log with row counts at every step

## Procedures

### P0. Session start
1. Read `bhishma.md` if present (R19 UTC, R20 run_id format).
2. Read this `skill.md`.
3. Read `yudhishthira/memories.md` — canonical metric definitions shape Gold layer design.

### P1. Backup guardrail
Before touching any source file that exists only in one place:
> "Is this file already backed up or can it be re-fetched from source? I'll wait before proceeding."

### P2. Bronze ingestion
1. Load the raw file with pandas (no type coercion, no column drops).
2. Print: shape, columns, dtypes, null counts, first 3 + last 3 rows.
3. Append to `data/bronze/<source>_<YYYY-MM-DD>.csv` (always append — never overwrite Bronze).
4. Log row count.

### P3. Silver cleaning
1. Declare every cleaning operation in plain language BEFORE running it:
   - "I will parse `date_col` as ISO8601."
   - "I will dedup on `creator_id`, keeping latest by `updated_at`."
   - "I will drop rows where `gmv` is null — these are pre-campaign entries."
2. Apply operations via pandas in Bash. Show code and row-count delta at each step.
3. Write to `data/silver/<source>_<YYYY-MM-DD>.csv`.
4. If any cleaning step drops >20% of rows: pause, explain, ask if expected.

### P4. Gold construction
1. Check `yudhishthira/memories.md` for canonical field names and metric definitions.
2. Join, aggregate, and reshape to the Gold schema the downstream consumer expects.
3. Add `ingested_at` (UTC ISO8601) and `source_file` columns to every Gold record.
4. Write to `data/gold/<source>_<YYYY-MM-DD>.csv`.

### P5. Schema validation
After every layer write:
- Confirm column names match declared schema (no drift).
- Confirm dtypes match expectations.
- Report any null columns that were declared non-null.

### P6. Logging (Sanjaya contract)
Append structured log entries at start and end of every task. See agent.md for format.

## Rootlabs-Specific Context

### Known sources
| Source | Format | Cadence | Nakula job |
|--------|--------|---------|-----------|
| Kalodata | CSV export | Daily | `kalodata-daily-sync` |
| Cruva | JSON API | Weekly | `cruva-weekly-rollup` |
| Google Sheets (POC trackers) | XLSX / CSV export | On-demand | Manual |

### Canonical join keys
- Creator data: `creator_id`
- Campaign data: `campaign_id`
- GMV records: `order_id` (unique) + `creator_id` (FK)

### Gold layer schemas (current)
- `gold/creators_<date>.csv` — one row per active creator. Columns: `creator_id`, `platform`, `follower_count`, `gmv_30d`, `gmv_ytd`, `last_updated_at`.
- `gold/campaigns_<date>.csv` — one row per campaign. Columns: `campaign_id`, `poc_name`, `creator_id`, `status`, `target_gmv`, `actual_gmv`, `last_updated_at`.

_(Add new schemas here as Draupadi builds them.)_

## Heuristics

_(Populated via Kartavya's "remember this" instructions.)_

## Change Log

- 2026-06-27 — bootstrap — adopted from agency-agents, Rootlabs context added.
