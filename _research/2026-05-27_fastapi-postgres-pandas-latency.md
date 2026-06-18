# FastAPI + Postgres + pandas Latency Cheatsheet (portal/, May 2026)

Stack: fastapi 0.115, uvicorn[standard] 0.32, psycopg[binary] 3.2.3 + psycopg-pool 3.3.1, pandas 2.2.3, jinja2 3.1.4. Supabase read-replica, single-region Fly.io. Pandas does in-memory aggregation.

Source tiers: **T1** = official docs / source. **T2** = maintainer or vendor blog. **T3** = community / Medium.

## TL;DR (highest leverage, do these first)

1. Pool sizing + `prepare_threshold=None` if you hit Supabase via the 6543 transaction pooler. Wrong settings here = silent crashes, not just slow. [T1]
2. Move pandas hot paths to DuckDB-on-DataFrame (no service, no rewrite, 5–10x on group-by/joins). [T2]
3. Add `GZipMiddleware` (1 line, ~70% bytes off for HTML/JSON). [T1]
4. `--limit-concurrency` matched to pool size — prevents the death-spiral under burst. [T1]
5. `pg_stat_statements` + `application_name=portal` to find your actual slow queries instead of guessing. [T1]
6. Bytecode-cache Jinja, `auto_reload=False` in prod. [T1]

Everything else is single-digit-ms unless your endpoint specifically hits that path.

---

## 1. FastAPI + uvicorn

### 1.1 Workers/threads for I/O-bound

**One-liner:** For I/O-bound work, scale workers, not threads — but cap so DB pool isn't oversubscribed.

```bash
# Fly 1x shared-cpu (1 core, 256MB-1GB) — start here:
uvicorn portal.app:app --host 0.0.0.0 --port 8080 \
  --workers 2 --loop uvloop --http httptools \
  --proxy-headers --forwarded-allow-ips '*' \
  --timeout-keep-alive 5 --limit-concurrency 50 --limit-max-requests 2000
```

- **Expected:** 2x throughput vs 1 worker; tail latency stays bounded under bursts. [T3]
- **Cost:** 5 min. Edit `run.sh` / `fly.toml`.
- **Caveat:** workers multiply memory (each loads pandas). On 256MB Fly, stay at 1–2 workers. `--limit-concurrency` must be ≤ (db_pool_max × workers) or you get pile-up. [T1]

### 1.2 Default JSON is already fast — skip orjson unless you have evidence

- Pydantic v2 is the default since FastAPI 0.100; serialization is Rust-backed and ~10–50× faster than v1. [T3]
- ORJSONResponse still 2–3× faster on large array payloads (>10k items), but for HTML-heavy Jinja portals this is irrelevant. [T3]
- **Do this only if** you're shipping >100KB JSON arrays; otherwise skip.

```python
from fastapi.responses import ORJSONResponse
app = FastAPI(default_response_class=ORJSONResponse)
```

- **Cost:** 5 min + `pip install orjson`. **Caveat:** Pydantic models still go through pydantic-core regardless.

### 1.3 GZipMiddleware (huge for HTML tables)

```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)
```

- **Expected:** 60–80% byte reduction on HTML/JSON, ~1–3ms CPU cost. [T1]
- **Cost:** 5 min. Brotli (`brotli-asgi`, quality=4) is ~33% faster compression and tighter — worth it only if you serve >64KB text frequently. [T3]
- **Caveat:** Don't gzip already-compressed bodies (images, parquet). Already pre-compressed assets — set `Content-Encoding` and bypass.

### 1.4 BackgroundTasks for fire-and-forget

```python
from fastapi import BackgroundTasks
@app.post("/refresh")
async def refresh(bt: BackgroundTasks):
    bt.add_task(rebuild_cache)  # returns immediately, runs after response
    return {"queued": True}
```

- **Expected:** Removes 100ms–10s from p99 for any "log this / send email / refresh cache" path. [T1]
- **Cost:** 5 min per route. **Caveat:** Runs in the same process — if it crashes, you crash. For real fan-out (>1s, retryable), use a real queue.

### 1.5 Sync DB call inside async route — DON'T

```python
# WRONG: blocks the event loop, kills concurrency
@app.get("/x")
async def x():
    return sync_query()  # psycopg sync inside async = disaster

# RIGHT option A — declare def, not async def: FastAPI auto-pools to threads
@app.get("/x")
def x():
    return sync_query()

# RIGHT option B — explicit:
from fastapi.concurrency import run_in_threadpool
@app.get("/x")
async def x():
    return await run_in_threadpool(sync_query)
```

- **Expected:** ~50% faster vs fully blocking; restores async concurrency. [T3]
- **Cost:** 5 min audit of every `async def` route.
- **Caveat:** Default threadpool is 40 threads; for many slow sync calls bump `anyio` limiter. The portal uses psycopg async pool — verify nothing in `app.py` calls a sync path from `async def`.

### 1.6 ETag + Cache-Control for stable dashboards

```python
import hashlib
from fastapi import Request, Response

@app.get("/dashboard")
async def dashboard(request: Request, response: Response):
    body = render_dashboard()
    etag = '"' + hashlib.md5(body.encode()).hexdigest() + '"'
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=30, must-revalidate"
    return Response(content=body, media_type="text/html", headers=response.headers)
```

- **Expected:** 304s short-circuit at ~5ms; saves render + DB. [T3]
- **Cost:** 30 min. **Caveat:** ETag computed AFTER render = no win for compute. For real wins, compute ETag from a cheap key (e.g. `max(updated_at)`).

---

## 2. Psycopg 3 + Postgres + Supabase

### 2.1 AsyncConnectionPool sizing (single most-impactful item)

```python
# portal/lib/db.py — at module init
from psycopg_pool import AsyncConnectionPool

pool = AsyncConnectionPool(
    conninfo=DSN + "?application_name=portal",
    min_size=2, max_size=10,         # per worker. With 2 workers -> 20 total.
    timeout=10,                      # wait-for-connection
    max_lifetime=60 * 30,            # recycle every 30 min (avoids stale on read replica)
    max_idle=60 * 5,
    open=False,                      # open in lifespan, not at import
    kwargs={"prepare_threshold": None} if PORT == 6543 else {},
)

@asynccontextmanager
async def lifespan(app):
    await pool.open(wait=True, timeout=30)
    yield
    await pool.close()
```

- **Sizing rule:** `workers × max_size ≤ Supabase pool limit`. Free-tier direct = 60 connections; via Supavisor transaction pooler = effectively unbounded client-side, capped by the platform. For app pools behind PgBouncer/Supavisor, **5–10 per instance is the right ballpark**. [T3]
- **Expected:** Removes connection-storm failures; p99 drops 50–500ms when you stop reconnecting per request.
- **Cost:** 30 min. **Caveat:** `open=False` + lifespan is the canonical pattern; pool inits at import = race + fork issues. [T1]

### 2.2 Prepared statements: the Supabase transaction-pooler trap

- psycopg 3 auto-prepares after `prepare_threshold=5` (default) executions. [T1]
- **Supabase 6543 (Supavisor transaction mode) breaks prepared statements** unless underlying PgBouncer ≥1.22. Setting `prepare_threshold=None` disables them. [T1, T2]
- **Direct connection (5432) or session-mode pooler:** keep defaults, get free 10–30% on hot queries.
- **Action:** check which port your `DATABASE_URL` uses. If 6543 → `prepare_threshold=None`. If 5432 → default is fine.

### 2.3 `application_name` for debugging

```python
DSN = "postgresql://...?application_name=portal-prod"
# or per-connection: SET application_name = 'portal-job-rebuild';
```

- **Expected:** `pg_stat_activity` and `pg_stat_statements` now filterable to portal-only traffic. Saves hours when something slow hits Supabase. [T1]
- **Cost:** 5 min. **Caveat:** none.

### 2.4 `pg_stat_statements` — find the actual slow queries

Already enabled on Supabase. Run in SQL editor:

```sql
SELECT substring(query, 1, 120) AS q,
       calls, mean_exec_time::int AS mean_ms,
       total_exec_time::int AS total_ms,
       rows
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC
LIMIT 20;
-- Reset after fixes: SELECT pg_stat_statements_reset();
```

- **Expected:** Surfaces the 3–5 queries eating 80% of DB time. [T1]
- **Cost:** 5 min. Run weekly. **Caveat:** stores only last 5,000 statements. [T1]

### 2.5 Statement timeout per connection

```python
async with pool.connection() as conn:
    await conn.execute("SET statement_timeout = '5s'")  # session-level
    # or per-tx:  SET LOCAL statement_timeout = '5s'
```

- **Free-tier Supabase role defaults:** anon=3s, authenticated=8s, postgres=2min. [T1]
- **Cannot be set via the 6543 transaction pooler.** Use 5432 or function-level timeouts. [T1]
- **Expected:** Bounded tail latency; a stuck query no longer holds a worker for minutes.
- **Cost:** 5 min. **Caveat:** Set per pool via `configure=` callback so every checkout gets it.

### 2.6 Server-side cursors for big reads

```python
async with conn.cursor(name="big_read") as cur:  # named => server-side
    await cur.execute("SELECT ...")
    async for row in cur:  # streams, doesn't buffer
        ...
```

- **Expected:** Constant memory regardless of row count. [T1]
- **Cost:** 30 min refactor where used. **Caveat:** named cursors aren't compatible with PgBouncer transaction mode either — same 5432 caveat.

### 2.7 `COPY` for bulk insert/load

```python
async with conn.cursor() as cur:
    async with cur.copy("COPY events (a,b,c) FROM STDIN") as copy:
        for row in rows:
            await copy.write_row(row)
```

- **Expected:** 10–100x faster than INSERT loops. [T1]
- **Cost:** 30 min. **Caveat:** No per-row error handling; one bad row aborts.

### 2.8 Read-replica recovery conflicts

- Symptom: `ERROR: canceling statement due to conflict with recovery`.
- Supabase read replicas are a **paid feature** (Pro+) — free tier has only the primary. If you're using one: ensure long analytics queries go to primary, or accept retries.
- **Hot-standby-feedback** is not user-tunable on Supabase free tier (no superuser).
- **Free workaround:** wrap reads in retry-on-`SerializationFailure`/`OperationalError`:

```python
for attempt in range(3):
    try: return await run_query()
    except psycopg.errors.OperationalError as e:
        if "recovery" not in str(e) or attempt == 2: raise
        await asyncio.sleep(0.2 * (2 ** attempt))
```

- **Caveat:** retry only on idempotent reads.

---

## 3. Pandas → DuckDB / Polars / PyArrow

### 3.1 DuckDB on pandas DataFrames — the easy win

```python
import duckdb
df = pd.read_sql(q, conn)  # already have a DataFrame
# instead of df.groupby(...).agg(...) — push to duckdb:
agg = duckdb.sql("""
  SELECT region, SUM(amount) total, COUNT(*) n
  FROM df GROUP BY region ORDER BY total DESC
""").df()
```

- **Expected:** 5–10x on group-by/joins vs pandas 2.2; zero-copy from pandas via Arrow. [T2]
- **Cost:** 5 min per hot aggregation. `pip install duckdb`.
- **Caveat:** Updates/in-place mutation are slower than pandas (4x). Use DuckDB for read-shaped analytics only. [T3]

### 3.2 pandas `read_sql` with PyArrow backend

```python
df = pd.read_sql(query, conn, dtype_backend="pyarrow")
```

- **Expected:** Lower memory (Arrow types), better null handling, faster downstream if you stay in Arrow-land. With ADBC driver (separate install) it's "significantly faster" and zero-copy. [T1, T2]
- **Cost:** 5 min. **Caveat:** Some pandas ops are slower or buggy on Arrow dtypes (string ops especially). Test the actual hot path; don't blanket-flip.

### 3.3 Polars — yes, but selectively

- 5–10x faster than pandas 2.x on groupby/join/scan; lazy API catches redundant scans. [T3]
- **Wins:** joins (~9x), reads, group-by, large parquet.
- **Loses:** heavy string regex, `.apply`-style row logic (as of Polars 1.15, early 2026). [T3]
- **Dissent:** "not a drop-in replacement — silent behavior changes show up in prod." [T3]
- **Action:** migrate one hot path at a time. The portal's pandas-in-memory pivots are exactly Polars' sweet spot:

```python
import polars as pl
df = pl.read_database(query, connection=conn)  # via connectorx/adbc
result = (df.lazy()
            .group_by("category")
            .agg(pl.col("gmv").sum())
            .sort("gmv", descending=True)
            .collect())
```

- **Cost:** half-day for one pivot route; do not rewrite everything.

### 3.4 Vectorize — kill `.iterrows()` and `.apply`

```python
# BAD: df["x"] = df.apply(lambda r: r.a + r.b, axis=1)   # row-by-row Python
# GOOD: df["x"] = df["a"] + df["b"]                       # vectorized
```

- **Expected:** 10–1000x on the actual cell. [T1]
- **Cost:** 5 min per offender. Grep `app.py` for `.apply\|.iterrows`. **Caveat:** none — apply is almost never the right answer.

---

## 4. Caching layer (free, no Redis)

### 4.1 `functools.lru_cache` for pure functions

```python
from functools import lru_cache
@lru_cache(maxsize=256)
def parse_product_catalog(path: str) -> dict: ...
```

- **Expected:** O(1) on repeat; effectively free.
- **Cost:** 5 min. **Caveat:** not thread-safe across processes (workers each have their own); args must be hashable; no TTL.

### 4.2 `cachetools.TTLCache` for time-bounded reads

```python
from cachetools import TTLCache
import asyncio

_cache: TTLCache = TTLCache(maxsize=512, ttl=60)
_locks: dict[str, asyncio.Lock] = {}

async def cached(key: str, fetch):
    if key in _cache: return _cache[key]
    lock = _locks.setdefault(key, asyncio.Lock())
    async with lock:                       # stampede prevention
        if key in _cache: return _cache[key]
        val = await fetch()
        _cache[key] = val
        return val
```

- **Expected:** First request pays cost; rest are µs. Lock prevents N concurrent identical fetches. [T1]
- **Cost:** 30 min. **Caveat:** per-worker memory; cleared on deploy. Hot keys only.

### 4.3 `diskcache` for cross-restart persistence

```python
from diskcache import Cache
dc = Cache("/data/cache")  # single SQLite file, thread+process safe
dc.set("dashboard:may", payload, expire=300)
```

- **Expected:** Survives restarts; 10–100µs reads. [T2]
- **Cost:** 5 min. **Caveat:** Fly volume needed for persistence across redeploys; otherwise behaves like `/tmp`.

### 4.4 When does Redis actually help?

- Only when (a) multi-instance + need consistency, (b) >100MB cache, or (c) pub/sub. For a single Fly machine, **in-process LRU + diskcache is strictly faster** (no network hop). Skip Redis until you scale out.

---

## 5. Jinja2

### 5.1 Bytecode cache + no auto-reload

```python
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
env = Environment(
    loader=FileSystemLoader("portal/templates"),
    bytecode_cache=FileSystemBytecodeCache("/tmp/jinja-cache"),
    auto_reload=False,           # prod: skip mtime checks
    cache_size=400,
)
```

- **Expected:** Eliminates parse+compile (~ms/template); auto_reload off saves a stat() per render. [T1]
- **Cost:** 5 min. **Caveat:** Must redeploy to see template changes — that's the point. Bytecode cache invalidates by source checksum, so it's safe across deploys. [T1]

### 5.2 Streaming big tables

```python
from fastapi.responses import StreamingResponse
template = env.get_template("big_table.html")
return StreamingResponse(template.stream(rows=row_iter), media_type="text/html")
```

- **Expected:** TTFB drops to first chunk (~10ms) instead of full render (~500ms+ for 10k rows). [T1]
- **Cost:** 30 min. **Caveat:** Mid-render exceptions = broken HTML to client; no rollback.

---

## 6. Static + frontend

### 6.1 `Cache-Control: immutable` for hashed assets

```python
from fastapi.staticfiles import StaticFiles
class ImmutableStatic(StaticFiles):
    def file_response(self, *a, **kw):
        r = super().file_response(*a, **kw)
        r.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return r
app.mount("/static", ImmutableStatic(directory="portal/static"), name="static")
```

- **Expected:** Browser never re-requests hashed assets. [T3]
- **Cost:** 5 min. **Caveat:** Filenames MUST be content-hashed (`app.abc123.js`). If not hashed, you'll ship stale.

### 6.2 Server-Timing for client-side debugging

```python
import time
@app.middleware("http")
async def timing(request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    resp.headers["Server-Timing"] = f"app;dur={(time.perf_counter()-t0)*1000:.1f}"
    return resp
```

- **Expected:** Chrome DevTools "Timing" tab shows your server breakdown — zero infra. [T3]
- **Cost:** 5 min. **Caveat:** Don't leak internals to public users; gate by env or IP.

### 6.3 HTTP keep-alive (already on)

- uvicorn defaults to keep-alive; `--timeout-keep-alive 5` is the tune knob. Fly proxy holds keep-alive too. Nothing to do. [T1]
- **HTTP/2:** uvicorn does NOT speak h2 natively. Fly's edge terminates HTTP/2 to clients and speaks h1 to your app — you already get the client-side benefit. [T2]

### 6.4 `<link rel="preload">` hints

```html
<link rel="preload" href="/static/app.abc123.css" as="style" />
<link rel="preload" href="/static/data.json" as="fetch" crossorigin />
```

- **Expected:** ~100–300ms perceived on cold cache. [T3]
- **Cost:** 5 min. **Caveat:** Preload only what's used >90% of the time; otherwise wastes bandwidth.

---

## 7. Profiling (free)

### 7.1 py-spy — attach to running process, no code change

```bash
pip install py-spy
py-spy top --pid $(pgrep -f 'uvicorn portal' | head -1)
py-spy record -o flame.svg --pid $PID --duration 30
```

- **Expected:** Finds the actual hot function in 60s. Sampling at 100Hz, near-zero overhead. [T1]
- **Cost:** 5 min. **Caveat:** Needs to run as same user (or root) as the python process. On Fly: `fly ssh console` → install and attach.

### 7.2 Scalene — CPU + memory + GPU, line-level

```bash
pip install scalene
scalene --html --outfile profile.html portal/app.py
```

- **Expected:** Separates Python time from native (pandas C) time; line-by-line. [T2]
- **Cost:** 30 min (run locally on representative load). **Caveat:** higher overhead than py-spy; use in dev, not prod.

### 7.3 Austin — TUI flamegraph

```bash
brew install austin
austin -i 1ms -o austin.out python -m uvicorn portal.app:app
austin-tui austin.out
```

- **Expected:** Real-time live flamegraph; similar to py-spy. [T3]
- **Cost:** 5 min.

---

## 8. Tracing / observability (free, self-host)

### 8.1 OpenTelemetry → Grafana Tempo/Prometheus

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp \
  opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-psycopg
opentelemetry-bootstrap -a install
```

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
FastAPIInstrumentor.instrument_app(app)
PsycopgInstrumentor().instrument(enable_commenter=True)
```

Run an OTel Collector + Tempo + Prometheus + Grafana stack via docker-compose (the `blueswen/fastapi-observability` repo is a working template). [T2]

- **Expected:** Per-request trace with DB span breakdown; aggregated p50/p95/p99 metrics.
- **Cost:** half-day to stand up first time. **Caveat:** Self-hosting needs a VM (cheap Fly machine OK). For one-off perf work, py-spy is faster.

### 8.2 psycopg logging

```python
import logging
logging.getLogger("psycopg").setLevel(logging.INFO)
# enable query commenter for query-level attribution:
PsycopgInstrumentor().instrument(enable_commenter=True, commenter_options={"db_driver": True})
```

- Adds `/* application='portal',route='/dashboard' */` to every query — shows up in `pg_stat_statements`. [T2]

---

## 9. Async/concurrency wins

### 9.1 `asyncio.gather` parallel independent queries

```python
async def dashboard_data():
    async with pool.connection() as c1, pool.connection() as c2, pool.connection() as c3:
        a, b, c = await asyncio.gather(
            c1.execute("SELECT ..."),
            c2.execute("SELECT ..."),
            c3.execute("SELECT ..."),
        )
    return a, b, c
```

- **Expected:** Wall time = max(queries) instead of sum. 3 queries × 100ms each → 100ms. [T1]
- **Cost:** 30 min. **Caveat:** Cursors on the **same** connection serialize — you must check out separate connections for true parallelism. [T1] Don't blow your pool: 3 parallel × 50 concurrent requests = 150 connections.

### 9.2 `anyio.to_thread.run_sync` for sync libs

Same as `run_in_threadpool` — interchangeable in FastAPI. Use whichever your code already uses.

---

## 10. uvloop / httptools

`uvicorn[standard]` already pulls in `uvloop` and `httptools`. Confirm they're active:

```bash
uvicorn portal.app:app --loop uvloop --http httptools
```

- **Expected:** ~2x event-loop perf vs default asyncio; ~3x HTTP parsing vs h11. [T1]
- **Cost:** 5 min. **Caveat:** On macOS dev, uvloop is fine; on Windows, fall back to asyncio (Fly is Linux, not an issue).

---

## 11. One-liner uvicorn flags

```bash
uvicorn portal.app:app \
  --workers 2 --loop uvloop --http httptools \
  --proxy-headers --forwarded-allow-ips '*' \
  --timeout-keep-alive 5 \
  --timeout-graceful-shutdown 20 \
  --limit-concurrency 50 \
  --limit-max-requests 2000 \
  --backlog 2048
```

- `--proxy-headers --forwarded-allow-ips '*'`: trust Fly's `X-Forwarded-*` so client IPs/scheme are right. [T1]
- `--limit-concurrency 50`: 503 instead of OOM under burst. [T1]
- `--limit-max-requests 2000`: recycle worker every 2k reqs — catches slow memory leaks (pandas is leak-prone). [T1]
- `--timeout-keep-alive 5`: short, since Fly handles client keep-alive. [T1]
- `--backlog 2048`: kernel queue depth — helps cold-start bursts. [T1]
- **Caveat:** `--workers` is incompatible with `--reload`. Don't ship `--reload` to prod (you're not).

---

## Confidence assessment

- **Strong (T1 official + multiple confirmations):** psycopg pool sizing, prepare_threshold-on-6543 trap, uvicorn flags, GZipMiddleware, run_in_threadpool, Jinja bytecode cache, pg_stat_statements availability on Supabase.
- **Convergent (T2/T3 agree):** DuckDB-on-pandas wins on aggregation, Polars 5–10x on group-by, py-spy is the right first profiler.
- **Contested:** orjson vs default Pydantic v2 — both fast; small payloads make orjson irrelevant. Polars-vs-pandas drop-in claim — explicitly disputed.
- **Single source:** Supabase free-tier role timeout defaults (3s/8s/2min) — only seen in Supabase docs, but that's T1.

## Gaps

- No measured latency for the _actual_ portal/ routes — none of these have ground truth until you run py-spy + pg_stat_statements against the live app.
- ADBC driver for Supabase Postgres: install path on Fly's Debian image not verified here.
- Brotli-asgi compatibility with FastAPI 0.115 + Starlette current — assumed working from the README; verify in a branch.

## Suggested next steps

1. Today (1 hour): add `application_name`, query `pg_stat_statements`, identify top 3 slow queries.
2. This week (half day): run py-spy against prod, snapshot flame graph; add GZipMiddleware + Jinja bytecode cache + `--limit-concurrency`.
3. Next sprint: port the single hottest pandas aggregation to DuckDB; add ETag on the dashboard route using `max(updated_at)` as the key.

## Sources

- [T1] Psycopg pool docs — https://www.psycopg.org/psycopg3/docs/advanced/pool.html
- [T1] Psycopg prepared statements — https://www.psycopg.org/psycopg3/docs/advanced/prepare.html
- [T1] Psycopg async concurrency — https://www.psycopg.org/psycopg3/docs/advanced/async.html
- [T1] FastAPI concurrency — https://fastapi.tiangolo.com/async/
- [T1] FastAPI advanced middleware — https://fastapi.tiangolo.com/advanced/middleware/
- [T1] FastAPI custom response — https://fastapi.tiangolo.com/advanced/custom-response/
- [T1] uvicorn settings — https://uvicorn.dev/settings/ (also https://www.uvicorn.org/settings/)
- [T1] Supabase timeouts — https://supabase.com/docs/guides/database/postgres/timeouts
- [T1] Supabase pg_stat_statements — https://supabase.com/docs/guides/database/extensions/pg_stat_statements
- [T1] Supabase read replicas — https://supabase.com/docs/guides/platform/read-replicas
- [T1] Jinja API / bytecode cache — https://jinja.palletsprojects.com/en/stable/api/
- [T1] py-spy — https://github.com/benfred/py-spy
- [T1] pandas 2.2 whatsnew — https://pandas.pydata.org/docs/whatsnew/v2.2.0.html
- [T2] DuckDB on pandas — https://duckdb.org/2021/05/14/sql-on-pandas
- [T2] Patrick Hoefler — pandas 2.2 — https://phofl.github.io/pandas-whatsnew-22.html
- [T2] Will Ayd — ADBC driver — https://willayd.com/leveraging-the-adbc-driver-in-analytics-workflows.html
- [T2] PgBouncer prepared statements (Supabase) — https://supabase.com/blog/supabase-pgbouncer
- [T2] fastapi-observability template — https://github.com/blueswen/fastapi-observability
- [T2] Databricks: Polars vs Pandas — https://www.databricks.com/blog/polars-vs-pandas
- [T3] Polars vs Pandas 2026 benchmarks — https://tildalice.io/polars-vs-pandas-2026-benchmarks/
- [T3] uvicorn/gunicorn tuning — https://medium.com/@connect.hashblock/8-uvicorn-gunicorn-tweaks-that-make-fastapi-fly-c34bd1c187c5
- [T3] brotli-asgi — https://github.com/fullonic/brotli-asgi
- [T3] fastapi-etag — https://github.com/steinitzu/fastapi-etag
- [T3] cachetools docs — https://cachetools.readthedocs.io/
- [T3] Supabase + psycopg3 scaling — https://medium.com/@papansarkar101/supabase-connection-scaling-the-essential-guide-for-fastapi-developers-2dc5c428b638
- [T3] Pydantic v2 vs orjson — https://medium.com/@bhagyarana80/fastapi-ultra-tuning-uvicorn-uvloop-pydantic-v2-fafffc921097
