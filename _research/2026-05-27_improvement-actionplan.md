# Improvement Action Plan — 2026-05-27

Synthesis of three research efforts. All recommendations are **free** (no SaaS, no paid tier).

**Source reports:**

- [Perf + DX audit](2026-05-27_perf-audit.md) — codebase-specific findings with file:line
- [FastAPI/Postgres/pandas cheatsheet](2026-05-27_fastapi-postgres-pandas-latency.md) — techniques + code
- [Claude Code optimization playbook](2026-05-27_claude-code-optimization.md) — agent ecosystem

---

## DO TODAY (90 minutes total, biggest leverage)

### 1. Check `DATABASE_URL` port — 5 min — CRITICAL FOOTGUN

If `portal/lib/db.py` connects via **port 6543** (Supavisor transaction pooler), set `prepare_threshold=None` in psycopg kwargs. Without this, psycopg auto-prepares statements that PgBouncer silently breaks. Symptom: random query failures under load. If port is 5432, default is fine.

### 2. Add `GZipMiddleware` — 5 min — 60–80% bytes off

In `portal/app.py` after `app = FastAPI(...)`:

```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)
```

### 3. Set `application_name` on DB connection — 5 min

Append `?application_name=portal-prod` to your DSN. Lets you filter `pg_stat_activity` and `pg_stat_statements` to portal-only traffic.

### 4. Run `pg_stat_statements` query in Supabase SQL editor — 5 min

Already enabled on Supabase. Surfaces the 3–5 queries eating 80% of DB time:

```sql
SELECT substring(query, 1, 120) AS q, calls, mean_exec_time::int AS mean_ms,
       total_exec_time::int AS total_ms, rows
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC LIMIT 20;
```

This tells you where to spend the next hour.

### 5. Add missing creator-join indexes — 10 min — `−40–60%` on /creators

`portal/lib/creators_list.py:78–87` joins `tt_video → rootlabs_sku_listings → rootlabs_products`. Add:

```sql
CREATE INDEX IF NOT EXISTS idx_skul_platform_product ON rootlabs_sku_listings(platform_product_id);
CREATE INDEX IF NOT EXISTS idx_rprod_sku ON rootlabs_products(rootlabs_sku_id);
```

### 6. Add uvicorn flags in `portal/run.sh` — 10 min

```bash
uvicorn portal.app:app --host 0.0.0.0 --port 8080 \
  --workers 2 --loop uvloop --http httptools \
  --proxy-headers --forwarded-allow-ips '*' \
  --timeout-keep-alive 5 --limit-concurrency 50 --limit-max-requests 2000
```

`--limit-max-requests 2000` recycles workers — catches pandas memory leaks. `--limit-concurrency` prevents pile-up.

### 7. Install ccusage for cost monitoring — 10 min

```bash
npx ccusage@latest
```

Reads `~/.claude/projects/*.jsonl`, no upload. Until you see the bill per session you can't trim it.

### 8. Run `/fewer-permission-prompts` skill — 5 min

Auto-generates `.claude/settings.json` allowlist from your transcripts. Drops sudo/wildcard risks.

### 9. Add per-agent `model:` frontmatter — 30 min — biggest free agent win

In each `.claude/agents/*/agent.md` add `model:` line:

| Agent        | Set to     | Why                             |
| ------------ | ---------- | ------------------------------- |
| Hanuman      | haiku-4-5  | Mechanical fetching             |
| Narada       | haiku-4-5  | Drafting/messaging              |
| Nakula       | haiku-4-5  | Light job runs                  |
| Sanjaya      | haiku-4-5  | Trace summarisation             |
| Arjuna       | sonnet-4-6 | Tactical exec, needs care       |
| Sahadeva     | sonnet-4-6 | Weekly audit synthesis          |
| Yudhishthira | sonnet-4-6 | Data reasoning                  |
| Vidura       | sonnet-4-6 | Research orchestration          |
| Vyasa        | opus-4-7   | Long-form meta-synthesis — keep |

Haiku 4.5 is $1/$5 vs Opus 4.7 $5/$25 — 5x cost delta, ~1.2pt SWE-bench gap. Most of these agents don't need Opus.

### 10. Audit `lib/session-start-greeting.sh` for cache-busting strings — 5 min

Any per-turn timestamp or session ID in the SessionStart output invalidates prompt cache. Static content first, dynamic content last (or omit entirely).

---

## THIS WEEK (half-day total)

### Portal — Python/SQL

**Parallelize sequential queries** — [dashboard.py:148–154](portal/lib/dashboard.py#L148-L154), [creators_list.py:158–175](portal/lib/creators_list.py#L158-L175)
Three back-to-back `.execute()` calls. Bundle as multi-CTE OR `asyncio.gather()` on separate connections. **−30–50%** latency on dashboard + /creators.

**Replace `cache.py` file-I/O with `lru_cache`** — [portal/lib/cache.py:74–106](portal/lib/cache.py#L74-L106)
Currently reads+writes JSON file on every miss. Switch to `functools.lru_cache(maxsize=8)` or `cachetools.TTLCache`. **−10–30ms** per cache miss.

**Fix `SELECT *` in schema sampling** — [portal/lib/schema.py:94](portal/lib/schema.py#L94)
Fetch column list from `information_schema.columns` first, then SELECT explicit columns. **−10–20%** on Browse Data wizard.

**Add ETag + Cache-Control** to stable dashboard routes. Use `max(updated_at)` as cheap ETag key (don't md5 the rendered body — that defeats the savings).

**Stop sync inside async** — grep `portal/` for `async def` routes that call sync psycopg. Either change `async def` → `def` (FastAPI auto-pools to threads) or wrap with `run_in_threadpool`.

**Jinja2 bytecode cache** — [portal/app.py:79–81](portal/app.py#L79-L81):

```python
from jinja2 import FileSystemBytecodeCache
templates.env.bytecode_cache = FileSystemBytecodeCache("/tmp/jinja-cache")
templates.env.auto_reload = False
```

### Pandas hot paths

**DuckDB-on-DataFrame for aggregations** — 5–10x on group-by:

```python
import duckdb
agg = duckdb.sql("SELECT region, SUM(amount) FROM df GROUP BY region").df()
```

Grep `portal/lib/` for `.groupby(` and pick the slowest aggregation. Convert one as a test.

**Vectorize** — grep portal codebase for `.iterrows()` and `.apply(`. Each one is a 10–1000x miss.

### Agents/hooks

**Cap hook latency under 200ms** — profile `lib/bhishma-pretool-hook.sh` and `lib/post-tool-hook.sh` with `time` on a real session. Short-circuit on `BHISHMA_AGENT=""`.

**Run post-tool trace writes async** — `lib/trace-writer.sh` should end with `&` + `disown` so the next turn doesn't block on disk write.

**Trim Yudhishthira prompt** — [yudhishthira/agent.md](.claude/agents/yudhishthira/agent.md) is 276 lines. Move schema docs + phase notes to a `PLAYBOOK.md` the agent reads on demand. Target ~100 lines. **−15–20% tokens per invocation.**

**Add hook-stats one-liner** to each hook for regression detection:

```bash
printf '%s\t%s\t%d\n' "$(date -u +%s)" "$HOOK_NAME" "$ELAPSED_MS" >> .claude/_meta/hook-stats.tsv
```

### MCP / settings.json

**Defer-load rarely-used MCPs** — Higgsfield, blueprint, Vibe Prospecting, Apollo, Clay, Klaviyo are project-specific. If not used in 80%+ of sessions, defer them in `settings.json` and re-enable per session. Each one adds setup cost to every turn.

---

## THIS SPORT (1–2 weeks)

**Sahadeva → Message Batches API** — weekly audit is non-interactive. 50% discount, stacks with caching → up to 95% off. Anthropic's `/v1/messages/batches` endpoint.

**Adaptive thinking** on Vyasa + Sahadeva:

```json
"thinking": {"type": "adaptive"}
```

Replaces deprecated `budget_tokens`. Reported 40–60% cost reduction because Claude skips reasoning on easy sub-tasks.

**Loop-detector hash-and-count** in `bhishma-pretool-hook.sh`:

> hash last N tool calls (name + args); flag if any hash appears 3+ times.

**Server-side cursor** for any portal query that returns >10k rows (currently you load all into memory).

**Move pandas hot path to Polars** for one route (probably standup or dashboard pivot). Half-day spike to validate gains before broader adoption. **Caveat:** not a drop-in, behavior shifts in string-heavy ops.

**OpenTelemetry self-hosted** — `opentelemetry-instrumentation-fastapi` + Grafana Tempo via docker-compose. Per-request trace with DB span breakdown. Half-day stand-up, free forever.

**Server-Timing middleware** for Chrome DevTools breakdown:

```python
@app.middleware("http")
async def timing(request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    resp.headers["Server-Timing"] = f"app;dur={(time.perf_counter()-t0)*1000:.1f}"
    return resp
```

---

## Verification needed (don't ship blind)

1. **Run `EXPLAIN ANALYZE`** on the creators_list joins before adding indexes — confirm seq-scan suspicion.
2. **Profile portal with `py-spy`** in prod: `py-spy top --pid $(pgrep -f 'uvicorn portal')`. Tells you the actual hot path in 60 sec.
3. **Measure cache.py hit rate** before refactoring — if >80% hit, file I/O isn't the bottleneck.
4. **Check `DATABASE_URL` port** — informs the prepare_threshold question.
5. **Time the bhishma hooks** with `time bash lib/bhishma-pretool-hook.sh` on a representative input.

---

## Patterns to avoid repo-wide

- Sequential `.execute()` in same connection (use multi-CTE or gather across connections)
- Dynamic strings (timestamps, IDs) at the START of agent prompts — kills prompt cache for the whole turn
- Spawning subagents for tasks under 5 tool calls — 20K-token overhead, net loss
- `.iterrows()` / `.apply(axis=1)` in pandas — almost always wrong
- `SELECT *` in production paths
- Hardcoded thread pool sizes that don't match worker count
- Sync I/O inside `async def` routes
- Hooks that spawn multiple subprocesses on every event

---

## Expected combined impact (rough order-of-magnitude)

| Layer            | Latency win                                 | Token/$ win                           | Effort |
| ---------------- | ------------------------------------------- | ------------------------------------- | ------ |
| Today's 10 items | −30–50% portal p50, immediate footgun fix   | ~30–50% agent cost via model demotion | 90 min |
| Week's items     | −15–25% additional, cleaner cache semantics | −15–20% more on prompts               | ~6 hr  |
| Sprint items     | Tail latency bounded, hot-path 5–10x        | Up to 95% off Sahadeva-class jobs     | 1–2 wk |
