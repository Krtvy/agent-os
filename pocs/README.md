# `pocs/` — Per-POC Workspaces

Per-POC (Point of Contact) workspaces for Yudhishthira's data work. Each POC owns a slice of creators / campaigns / sample-deliveries and has their own data sources. When a task comes in, the POC name determines which folder Yudhishthira reads from and where deliverables land.

## Current POCs

| POC      | Folder                   | Register                                       |
| -------- | ------------------------ | ---------------------------------------------- |
| Trupti   | [`trupti/`](trupti/)     | [`trupti/register.md`](trupti/register.md)     |
| Shivangi | [`shivangi/`](shivangi/) | [`shivangi/register.md`](shivangi/register.md) |
| Khushi   | [`khushi/`](khushi/)     | [`khushi/register.md`](khushi/register.md)     |
| Vansh    | [`vansh/`](vansh/)       | [`vansh/register.md`](vansh/register.md)       |
| Manini   | [`manini/`](manini/)     | [`manini/register.md`](manini/register.md)     |
| Chanchal | [`chanchal/`](chanchal/) | [`chanchal/register.md`](chanchal/register.md) |
| Rachit   | [`rachit/`](rachit/)     | [`rachit/register.md`](rachit/register.md)     |
| Sanya    | [`sanya/`](sanya/)       | [`sanya/register.md`](sanya/register.md)       |

## Each POC folder follows the same shape

```
<poc-name>/
├── register.md       ← who they are, what tasks they own, what data sources they have
├── sheets/           ← fetched Google Sheets (XLSX/CSV exports from `lib/yudhi-fetch.sh`)
├── raw/              ← raw data files the user pastes in (CSV, JSON, etc.)
├── exports/          ← exports from external systems (EUKA, Cruva, Kalodata, etc.)
├── deliverables/     ← Yudhishthira's outputs for this POC (final .csv + .md per task)
└── tasks/            ← active task descriptions / briefs from the POC
```

## How Yudhishthira uses these folders

**Today (Phase 1 — informal):**

- When a task names a POC ("here's a task for Vansh"), Yudhishthira reads from `pocs/vansh/` and writes deliverables to `pocs/vansh/deliverables/`.
- The discipline is documented but **not yet enforced** by Yudhishthira's `agent.md` `write_scope` — that's a constitutional change pending Sahadeva endorsement (proposal at `_audit/2026-05-13_proposed-poc-workspace.md`).
- For now: Yudhishthira is asked-to-do-this by the human dispatching the task, not blocked from violating it by the runtime hook.

**Future (Phase 2 — after constitutional formalisation):**

- Yudhishthira's `write_scope` extends to `pocs/<poc>/deliverables/` per-POC.
- A P0 step routes Yudhishthira to the named POC's register before any work.
- `lib/bhishma-check.sh` blocks writes to any POC folder Yudhishthira wasn't dispatched for.
- Cross-POC analysis becomes an explicit, declared task type with its own access scope.

## The "always-copy" rule still applies

Anything in `<poc>/sheets/` is treated as a local copy of a live Google Sheet. The live original on Google Drive is **never** modified by Yudhishthira. If a task requires writing back to the live sheet, that's still Phase 2 work pending dedicated-account provisioning (per `.claude/agents/yudhishthira/skill.md` § Phase 2 readiness).

## Cross-POC training and shared knowledge

Shared training material — past good deliverables, terminology, reusable task patterns — lives outside this directory in [`training/`](../training/). Yudhishthira reads `training/` regardless of which POC he's serving.

## DB enrichment (added 2026-05-15)

POC CSVs can now be enriched with database lookups. The Supabase Postgres has been made accessible read-only via [`lib/yudhi-sql.sh`](../lib/yudhi-sql.sh) (statement_timeout = 30s; destructive verbs hard-rejected). The canonical query library is at [`training/queries/`](../training/queries/) (24 queries) and the metric glossary is at [`training/glossary/`](../training/glossary/).

**Common POC enrichment flow:**

```bash
# 1. List the creators the POC cares about
csvcut -c creator_username pocs/<name>/raw/<file>.csv | tail -n +2 > /tmp/creators.txt

# 2. Run a canonical query parameterized for that window
lib/yudhi-sql.sh -f training/queries/live_gmv___date_gmv_query.sql \
  -p start='2026-05-01 00:00:00' \
  -p end='2026-05-15 00:00:00' \
  --out /tmp/live_gmv_may.csv

# 3. Join in pandas and write to the POC's deliverables/
lib/yudhi-py.sh -c "
import pandas as pd
poc = pd.read_csv('pocs/<name>/raw/<file>.csv')
db  = pd.read_csv('/tmp/live_gmv_may.csv')
out = poc.merge(db, on='creator_username', how='left')
out.to_csv('pocs/<name>/deliverables/<task>_2026-05-15.csv', index=False)
"
```

The POC CSV is the workflow layer; the DB is the source of truth. Yudhishthira never edits a POC's input CSV — only appends columns and writes to `pocs/<name>/deliverables/`.

## Adding a new POC

1. `mkdir -p pocs/<name>/{sheets,raw,exports,deliverables,tasks}` + `.gitkeep` in each.
2. Copy a register.md from an existing POC, edit for the new POC's scope.
3. Update this README's table.
4. Update `.claude/agents/yudhishthira/agent.md` `read_scope` to include the new POC folder (constitutional change — should go through proposal flow).
