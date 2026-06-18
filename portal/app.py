"""
Rootlabs POC Portal v2 — entry point.

Architecture: POC → form → SQL → CSV. No agent, no LLM, no subprocess.
Patterns are documented in training/patterns/<slug>.md.
Executable reports live in reports/<slug>/{manifest.json, query.sql}.
The Browse Data wizard (M6+) is built into the portal, not a report.

Routes are added milestone by milestone (see portal/RUN-LOCALLY.md).
"""

from __future__ import annotations

import os
import re
import warnings as _warnings_mod
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemBytecodeCache
from starlette.middleware.sessions import SessionMiddleware

from .lib.cache import get_cached, query_hash, set_cached
from .lib.column_warnings import warnings_for_column
from .lib.creator_detail import daily_gmv_for_creator, default_range, lives_for_creator, summary_for_creator, videos_for_creator
from .lib.creators_list import build_creators_list, get_content_id_gmv, get_all_db_creators
from .lib.lives_view import build_lives_view
from .lib.dashboard import build_for_poc, sparkline_svg
from .lib.products import hero_products
from .lib.db import get_conn
from .lib.pivot import SUPPORTED_AGGS, SUPPORTED_OPS, FilterSpec, PivotPlan, PivotValidationError, ValueSpec, build_sql, pivot_wide, validate_plan
from .lib.reports import Report, discover_reports, load_report
from .lib.runner import execute_sync, start_async
from .lib.schema import list_columns, list_schemas, list_tables, sample_rows
from .lib.poc_creators import (
    add_creator,
    all_pocs,
    bulk_add_creators,
    get_creators_for_poc,
    poc_name_from_slug,
    remove_creator,
    roster_meta,
)
from .lib.products import all_products
from .lib.schema_labels import column_label, creator_column_for, schema_label, sort_columns, table_label
from .lib.session import clear, current_user, resolve_poc_email, set_user
from .lib import users as _users
from .lib.status import read_status
from .lib.storage import find_deliverable, poc_slug_from_email

VERSION = "v2.0.0-m9"

_DEV_SECRET_DEFAULT = "dev-only-not-for-production-replace-in-phase-b"
_secret_key = os.getenv("PORTAL_SECRET_KEY", _DEV_SECRET_DEFAULT)
if _secret_key == _DEV_SECRET_DEFAULT:
    _warnings_mod.warn(
        "PORTAL_SECRET_KEY not set; using dev default. Safe locally, NEVER in production.",
        stacklevel=1,
    )

app = FastAPI(
    title="Rootlabs POC Portal",
    version=VERSION,
    description="Self-serve data portal for the 8 POCs at Rootlabs.",
)
_HTTPS_ONLY = os.getenv("PORTAL_HTTPS_ONLY", "").lower() in ("1", "true", "yes", "on")

app.add_middleware(
    SessionMiddleware,
    secret_key=_secret_key,
    session_cookie="portal_session",
    same_site="lax",
    https_only=_HTTPS_ONLY,
)

# Gzip every text response > 500B. ~60-80% bandwidth reduction on the HTML
# tables (creators, lives, trackers) — biggest single perceived-speed win
# over the ngrok tunnel. compresslevel=6 is the sweet spot for HTML payloads.
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Bytecode-cache compiled Jinja templates to /tmp and disable per-render
# mtime stat() — eliminates ~50ms of template parse/compile overhead per
# page render. Trade-off: template changes need a restart, which we do
# explicitly via pilot.sh anyway.
_JINJA_CACHE_DIR = Path("/tmp/jinja-portal-cache")
_JINJA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
templates.env.bytecode_cache = FileSystemBytecodeCache(str(_JINJA_CACHE_DIR))
templates.env.auto_reload = False


# Mount /static with browser-cache headers so CSS isn't refetched on every
# page (saves 200-600ms per nav over ngrok). 1-day max-age; if we update
# CSS, POCs get the new version within a day.
class _CachedStatic(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        try:
            response.headers["Cache-Control"] = "public, max-age=86400"
        except Exception:  # noqa: BLE001
            pass
        return response


app.mount("/static", _CachedStatic(directory=STATIC_DIR), name="static")


# ────────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────────
# Cache pre-warmer
# ────────────────────────────────────────────────────────────────────
# Background thread that calls every @cached() function with the typical
# arguments routes use, every 4 minutes. Because cache TTL is 300s, the
# warmer refreshes entries before they expire — so POCs effectively never
# hit a cold cache. The warmer takes ~5-10s per cycle (8 POCs × ~5 hot
# functions, fanned out internally), runs as a daemon thread so it dies
# with the process. Failures are logged and the loop continues.
import threading as _threading
import time as _wt


def _warm_once() -> None:
    from datetime import date as _date, timedelta as _td
    from .lib.creators_list import build_creators_list as _bcl
    from .lib.operator_dashboard import build_operator_view as _bov
    from .lib.lives_view import build_lives_view as _blv
    from .lib.poc_targets import for_all_pocs as _fap, current_period as _cp
    from .lib import standup as _su

    today = _date.today()
    start_30 = today - _td(days=30)
    pocs = list(all_pocs())

    # Per-POC creators_list (default 30d window, no product filter)
    for p in pocs:
        try: _bcl(p, start_30, today, "")
        except Exception as e: print(f"[warm] creators_list({p}): {e}")
    # Operator dashboard
    try: _bov(start_30, today, "")
    except Exception as e: print(f"[warm] operator_view: {e}")
    # Coordinator targets per product, current period
    for prod in ("hgr", "magashwa"):
        try: _fap(prod, _cp())
        except Exception as e: print(f"[warm] for_all_pocs({prod}): {e}")
    # Standup per POC
    for p in pocs:
        try: _su.build(p, today)
        except Exception as e: print(f"[warm] standup({p}): {e}")
    # Lives — operator-wide + per POC
    try: _blv(None, start_30, today)
    except Exception as e: print(f"[warm] lives(all): {e}")
    for p in pocs:
        try: _blv(p, start_30, today)
        except Exception as e: print(f"[warm] lives({p}): {e}")


def _warmer_loop() -> None:
    # Wait a few seconds after process start so the pool + imports settle
    # before the first warm-up cycle.
    _wt.sleep(8)
    while True:
        t0 = _wt.time()
        try:
            _warm_once()
            print(f"[warm] cycle ok in {_wt.time() - t0:.1f}s")
        except Exception as e:  # noqa: BLE001
            print(f"[warm] cycle failed: {e}")
        _wt.sleep(240)


@app.on_event("startup")
def _start_warmer() -> None:
    if os.getenv("PORTAL_DISABLE_WARMER", "").lower() in ("1", "true", "yes"):
        print("[warm] recurring warmer disabled via PORTAL_DISABLE_WARMER")
    else:
        t = _threading.Thread(target=_warmer_loop, name="cache-warmer", daemon=True)
        t.start()
        print("[warm] background thread started (4-min cycle)")

    # NOTE: the one-shot pre-warm experiment was removed — it competed
    # with real traffic and saturated Supabase's role connection cap on
    # cold start. The 30-min TTL on /dashboard + /coordinator caches is
    # sufficient: first real visit pays the cold cost once per half hour.


# Supabase read-replica recovery-conflict handler
# ────────────────────────────────────────────────────────────────────
# Supabase serves our SELECTs from a read replica. When the primary
# vacuums or commits a change that conflicts with our in-flight query,
# the replica kills the query with `SerializationFailure: canceling
# statement due to conflict with recovery`. It's transient — retrying
# the same request almost always succeeds. Instead of showing a scary
# 500, render a tiny auto-refreshing page that re-runs the request.
import psycopg as _psycopg


def _retry_html(path_with_qs: str, msg: str = "Re-running query…", delay_s: int = 1) -> str:
    safe = path_with_qs.replace("\"", "&quot;")
    return f"""<!doctype html><html><head>
    <meta charset="utf-8"><title>Loading…</title>
    <meta http-equiv="refresh" content="{delay_s}; url={safe}">
    <link rel="stylesheet" href="/static/design-tokens.css">
    <link rel="stylesheet" href="/static/design-app.css">
    </head><body style="display:grid;place-items:center;height:100vh;font-family:var(--f-sans);background:var(--c-bg);">
    <div style="text-align:center;max-width:480px;padding:var(--s-6);">
      <div style="width:36px;height:36px;border:3px solid var(--c-border);border-top-color:var(--c-accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto var(--s-4);"></div>
      <h2 style="margin:0 0 var(--s-2);font-weight:600;font-size:var(--t-18);color:var(--c-ink);">{msg}</h2>
      <p style="margin:0;color:var(--c-ink-3);font-size:var(--t-13);">Database had a brief hiccup — retrying automatically.</p>
      <p style="margin:var(--s-4) 0 0;color:var(--c-ink-4);font-size:var(--t-12);">If this loops, <a href="{safe}">click here</a>.</p>
    </div>
    <style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>
    </body></html>"""


# Max retries + delay schedule for the replica-conflict / connection-blip
# auto-refresh loop. Bumped from (2,1) and (1,1) — the old budgets were
# too tight; POCs hit the "give up" page on routine Supabase hiccups.
_SERIALIZATION_MAX_RETRIES = 5
_OPERATIONAL_MAX_RETRIES = 3
_RETRY_DELAYS = [1, 2, 3, 3, 4]   # seconds per attempt; clipped if longer


# ────────────────────────────────────────────────────────────────────
# Server-side retry decorator
# ────────────────────────────────────────────────────────────────────
# Wraps a route handler so that transient Supabase errors retry WITHIN
# the same HTTP request. POC sees nothing — the request just takes
# 50-200 ms longer instead of a 1-3 second spinner page. Only after
# this exhausts does the exception bubble up to the auto-refresh handlers
# above, which act as the final fallback.
import asyncio as _asyncio
import functools as _functools
import time as _time


def with_db_retry(retries: int = 3, backoff_ms: int = 50):
    """Retry the route on transient psycopg errors up to `retries` times
    before letting the exception escape.

    Includes InvalidSqlStatementName — that happens when psycopg's
    prepared-statement cache desyncs from Supabase's pooler. The retry
    forces psycopg to re-parse the query, which works."""
    transient = (
        _psycopg.errors.SerializationFailure,
        _psycopg.errors.OperationalError,
        _psycopg.errors.InvalidSqlStatementName,
    )

    def deco(fn):
        if _asyncio.iscoroutinefunction(fn):
            @_functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                last = None
                for attempt in range(retries + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except transient as e:
                        last = e
                        if attempt < retries:
                            await _asyncio.sleep(backoff_ms * (attempt + 1) / 1000)
                raise last  # type: ignore[misc]
            return async_wrapper
        else:
            @_functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                last = None
                for attempt in range(retries + 1):
                    try:
                        return fn(*args, **kwargs)
                    except transient as e:
                        last = e
                        if attempt < retries:
                            _time.sleep(backoff_ms * (attempt + 1) / 1000)
                raise last  # type: ignore[misc]
            return sync_wrapper
    return deco


@app.exception_handler(_psycopg.errors.SerializationFailure)
async def _on_serialization_failure(request: Request, exc: _psycopg.errors.SerializationFailure):
    qs = dict(request.query_params)
    attempt = int(qs.get("_retry", 0)) + 1
    if attempt > _SERIALIZATION_MAX_RETRIES:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user_email": current_user(request),
             "error": "The database kept hiccuping. Try again in a few seconds, or reload the page."},
            status_code=503,
        )
    qs["_retry"] = str(attempt)
    qs_str = "&".join(f"{k}={v}" for k, v in qs.items())
    url = f"{request.url.path}?{qs_str}"
    delay = _RETRY_DELAYS[min(attempt - 1, len(_RETRY_DELAYS) - 1)]
    return HTMLResponse(content=_retry_html(url, delay_s=delay), status_code=200)


@app.exception_handler(_psycopg.errors.OperationalError)
async def _on_operational_error(request: Request, exc: _psycopg.errors.OperationalError):
    qs = dict(request.query_params)
    attempt = int(qs.get("_retry", 0)) + 1
    if attempt > _OPERATIONAL_MAX_RETRIES:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user_email": current_user(request),
             "error": "Database connection kept dropping. Try again in a moment."},
            status_code=503,
        )
    qs["_retry"] = str(attempt)
    qs_str = "&".join(f"{k}={v}" for k, v in qs.items())
    url = f"{request.url.path}?{qs_str}"
    delay = _RETRY_DELAYS[min(attempt - 1, len(_RETRY_DELAYS) - 1)]
    return HTMLResponse(content=_retry_html(url, msg="Reconnecting to database…", delay_s=delay), status_code=200)


# psycopg's prepare-statement cache can desync from Supabase's pooler
# (overnight idle, session recycle). Retrying re-parses the query.
@app.exception_handler(_psycopg.errors.InvalidSqlStatementName)
async def _on_invalid_prepared_stmt(request: Request, exc: _psycopg.errors.InvalidSqlStatementName):
    qs = dict(request.query_params)
    attempt = int(qs.get("_retry", 0)) + 1
    if attempt > _OPERATIONAL_MAX_RETRIES:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "user_email": current_user(request),
             "error": "Database query cache desynced. Try again in a moment."},
            status_code=503,
        )
    qs["_retry"] = str(attempt)
    qs_str = "&".join(f"{k}={v}" for k, v in qs.items())
    url = f"{request.url.path}?{qs_str}"
    delay = _RETRY_DELAYS[min(attempt - 1, len(_RETRY_DELAYS) - 1)]
    return HTMLResponse(content=_retry_html(url, msg="Refreshing query cache…", delay_s=delay), status_code=200)

# Identifier whitelist: lowercase letters, digits, underscores. Schema/table
# names from form input must match this before being passed to schema.py.
_IDENT_RE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


def _wants_json(request: Request) -> bool:
    return "text/html" not in request.headers.get("accept", "")


def _load_report_or_404(slug: str):
    try:
        return load_report(slug)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Report manifest invalid: {e}") from e


def _duration_seconds(started_at: str | None, ended_at: str | None) -> float:
    if not started_at or not ended_at:
        return 0.0
    try:
        s = datetime.fromisoformat(started_at)
        e = datetime.fromisoformat(ended_at)
        return round((e - s).total_seconds(), 2)
    except ValueError:
        return 0.0


def _require_login(request: Request):
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/login", status_code=303)
    return user, None


# ────────────────────────────────────────────────────────────────────
# Top-level
# ────────────────────────────────────────────────────────────────────


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "version": VERSION}


@app.get("/whoami")
def whoami(request: Request) -> dict:
    user = current_user(request)
    return {"logged_in": user is not None, "user_email": user}


@app.get("/", response_model=None)
def home(request: Request):
    user = current_user(request)
    if user:
        return RedirectResponse("/standup", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/menu", response_model=None)
def menu(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    reports = discover_reports()
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_email": user,
            "poc_slug": poc_slug_from_email(user),
            "reports": reports,
        },
    )


# ────────────────────────────────────────────────────────────────────
# Auth
# ────────────────────────────────────────────────────────────────────


@app.get("/creators", response_model=None)
@with_db_retry()
def creators_list_page(request: Request):
    """Per-creator summary for the logged-in POC's roster. Date + product
    filter combo; each row has a tiny daily-video sparkline that expands
    to a larger interactive chart in a modal on click."""
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    default_start = today - _td(days=30)
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    product_q = (request.query_params.get("product") or "").strip()
    sd = default_start; ed = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try: sd = _date.fromisoformat(start_q)
        except ValueError: sd = default_start
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try: ed = _date.fromisoformat(end_q)
        except ValueError: ed = today
    ctx = build_creators_list(poc_name, sd, ed, product_filter=product_q)
    # Build per-row inline sparkline + payload for the modal expander.
    # Sparkline shows CUMULATIVE videos over the window — a steady upward
    # curve is easier to read than the daily spike pattern.
    sparks = {}
    daily_payload = {}
    for c in ctx["creators"]:
        running = 0
        cum_rows = []
        for d in c["daily_videos"]:
            running += d["count"]
            cum_rows.append({"date": d["date"], "count": running})
        sparks[c["creator"]] = sparkline_svg(
            [r["count"] for r in cum_rows], width=120, height=24, show_dots=False,
        )
        # Modal chart uses the cumulative series too, for consistency.
        daily_payload[c["creator"]] = cum_rows
    return templates.TemplateResponse(
        "creators_list.html",
        {
            "request": request,
            "user_email": user,
            "ctx": ctx,
            "hero_products": hero_products(),
            "sparklines": sparks,
            "daily_payload": daily_payload,
        },
    )


@app.get("/lives", response_model=None)
@with_db_retry()
def lives_page(request: Request):
    """Roster-wide TikTok livestream view — every live by every creator
    in the date range, with product × GMV breakdown for orders attributed
    to that live. Operators see all rosters; POCs see their own.
    """
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    known_pocs = {p.lower() for p in all_pocs()}
    is_poc = slug.lower() in known_pocs
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    default_start = today - _td(days=30)
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    sd = default_start; ed = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try: sd = _date.fromisoformat(start_q)
        except ValueError: sd = default_start
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try: ed = _date.fromisoformat(end_q)
        except ValueError: ed = today

    # POC sees own roster; operator sees the union (poc_name=None).
    scope = poc_name if is_poc else None
    if not is_poc:
        forced = (request.query_params.get("poc") or "").strip()
        if forced:
            scope = forced  # operator scoped to one POC

    ctx = build_lives_view(scope, sd, ed)

    # Build per-creator sparkline (cumulative lives) + a top-level
    # roster-wide daily-total sparkline. Same shape as /creators.
    sparks = {}
    daily_payload = {}
    for c in ctx.get("creators_summary", []):
        running = 0
        cum = []
        for d in c["daily_lives"]:
            running += d["count"]
            cum.append({"date": d["date"], "count": running})
        sparks[c["creator"]] = sparkline_svg(
            [r["count"] for r in cum], width=120, height=24, show_dots=False,
        )
        daily_payload[c["creator"]] = cum

    # Roster-wide daily total: non-cumulative for the top chart so spikes
    # are visible (which day was the live-heavy day).
    daily_total_payload = ctx.get("daily_total", [])
    daily_total_spark = sparkline_svg(
        [d["count"] for d in daily_total_payload], width=720, height=64, show_dots=True,
    ) if daily_total_payload else ""

    return templates.TemplateResponse(
        "lives.html",
        {
            "request": request,
            "user_email": user,
            "ctx": ctx,
            "is_operator": not is_poc,
            "available_pocs": sorted(all_pocs()) if not is_poc else [],
            "nav_active": "lives",
            "sparklines": sparks,
            "daily_payload": daily_payload,
            "daily_total_spark": daily_total_spark,
        },
    )


@app.get("/dashboard", response_model=None)
@with_db_retry()
def dashboard_page(request: Request):
    """Per-POC personalized landing — current vs previous 30-day window."""
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    first_name = (user or "").split("@")[0].capitalize()
    poc_name = poc_name_from_slug(slug)
    # Is the logged-in user actually a POC?
    known = {p.lower() for p in all_pocs()}
    is_poc = slug.lower() in known
    # Operator view — aggregate across all POCs
    if not is_poc:
        from .lib.operator_dashboard import build_operator_view
        start_q = request.query_params.get("start", "").strip()
        end_q = request.query_params.get("end", "").strip()
        product_q = (request.query_params.get("product") or "").strip()
        from datetime import date as _d
        sd = None; ed = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
            try: sd = _d.fromisoformat(start_q)
            except ValueError: sd = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
            try: ed = _d.fromisoformat(end_q)
            except ValueError: ed = None
        op_ctx = build_operator_view(start_date=sd, end_date=ed, product_filter=product_q)
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user_email": user,
                "first_name": first_name,
                "is_poc": False,
                "op": op_ctx,
                "hero_products": hero_products(),
            },
        )
    # Optional ?start=YYYY-MM-DD&end=YYYY-MM-DD&product=<name> for custom window + filter.
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    product_q = (request.query_params.get("product") or "").strip()
    from datetime import date as _date
    start_date = None
    end_date = None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try:
            start_date = _date.fromisoformat(start_q)
        except ValueError:
            start_date = None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try:
            end_date = _date.fromisoformat(end_q)
        except ValueError:
            end_date = None
    refresh = request.query_params.get("refresh") == "1"
    ctx = build_for_poc(
        poc_name, start_date=start_date, end_date=end_date,
        refresh=refresh, product_filter=product_q,
    )
    # Per-tile mini sparklines (no dots — too tiny to hover)
    tiles = {}
    daily = ctx["daily"]
    for key, prefix in [("videos", ""), ("lives", ""), ("orders", ""), ("gmv", "$"), ("commission", "$")]:
        tiles[key] = sparkline_svg(
            [d[key] for d in daily],
            width=200, height=30, value_prefix=prefix, show_dots=False,
        )
    # Main chart: current vs prior period overlay with hover dots
    from .lib.dashboard import sparkline_overlay_svg
    main_chart = sparkline_overlay_svg(
        curr=[d["gmv"] for d in daily],
        prev=[d["gmv"] for d in ctx["daily_prev"]],
        labels_curr=[d["date"] for d in daily],
        width=480, height=120, value_prefix="$",
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_email": user,
            "first_name": first_name,
            "is_poc": True,
            "ctx": ctx,
            "tile_sparklines": tiles,
            "main_chart": main_chart,
            "hero_products": hero_products(),
        },
    )


@app.get("/creator/{handle}/new-video-breakdown", response_model=None)
@with_db_retry()
def creator_new_video_breakdown(handle: str, request: Request):
    """JSON: per-video GMV for the 'new video' portion of a creator's GMV
    in the window. Called by the /creators page drill-down modal."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="Invalid handle")
    from .lib.creator_breakdowns import new_video_breakdown
    s = (request.query_params.get("start") or "").strip()
    e = (request.query_params.get("end") or "").strip()
    if not (re.match(r"^\d{4}-\d{2}-\d{2}$", s) and re.match(r"^\d{4}-\d{2}-\d{2}$", e)):
        raise HTTPException(status_code=400, detail="Provide start + end as YYYY-MM-DD")
    return JSONResponse({"handle": handle, "start": s, "end": e, "rows": new_video_breakdown(handle, s, e)})


@app.get("/creator/{handle}/live-breakdown", response_model=None)
@with_db_retry()
def creator_live_breakdown(handle: str, request: Request):
    """JSON: per-live GMV for a creator in the window."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="Invalid handle")
    from .lib.creator_breakdowns import live_breakdown
    s = (request.query_params.get("start") or "").strip()
    e = (request.query_params.get("end") or "").strip()
    if not (re.match(r"^\d{4}-\d{2}-\d{2}$", s) and re.match(r"^\d{4}-\d{2}-\d{2}$", e)):
        raise HTTPException(status_code=400, detail="Provide start + end as YYYY-MM-DD")
    return JSONResponse({"handle": handle, "start": s, "end": e, "rows": live_breakdown(handle, s, e)})


@app.get("/creator/{handle}", response_model=None)
def creator_detail(handle: str, request: Request):
    """Drill-down view for one creator. Default range: last 30 days."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="Invalid creator handle")
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    default_start, default_end = default_range()
    start_date = start_q if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q) else default_start
    end_date = end_q if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q) else default_end
    try:
        videos = videos_for_creator(handle, start_date, end_date)
        lives = lives_for_creator(handle, start_date, end_date)
        daily = daily_gmv_for_creator(handle, start_date, end_date)
    except Exception as e:  # noqa: BLE001
        return templates.TemplateResponse(
            "creator_detail.html",
            {
                "request": request,
                "user_email": user,
                "handle": handle,
                "start_date": start_date,
                "end_date": end_date,
                "videos": [],
                "lives": [],
                "summary": summary_for_creator([], []),
                "error": f"DB error: {e}",
            },
            status_code=500,
        )
    spark = sparkline_svg(
        [d["gmv"] for d in daily],
        labels=[d["date"] for d in daily],
        width=480, height=80, value_prefix="$",
    )
    return templates.TemplateResponse(
        "creator_detail.html",
        {
            "request": request,
            "user_email": user,
            "handle": handle,
            "start_date": start_date,
            "end_date": end_date,
            "videos": videos,
            "lives": lives,
            "summary": summary_for_creator(videos, lives),
            "sparkline": spark,
        },
    )


# ────────────────────────────────────────────────────────────────────
# COCKPIT — Standup, Creator Card, Outreach, Campaigns
# ────────────────────────────────────────────────────────────────────

from .lib import creator_card as _cc
from .lib import creator_events as _ce
from .lib import creator_notes as _cn
from .lib import outreach as _outreach
from .lib import standup as _standup
from .lib import campaigns as _campaigns


def _greeting_word(hour_local: int) -> str:
    if hour_local < 12: return "morning"
    if hour_local < 17: return "afternoon"
    return "evening"


@app.get("/standup", response_model=None)
@with_db_retry()
def standup_page(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    first_name = (user or "").split("@")[0].split(".")[0].capitalize()
    from datetime import datetime as _dt
    hour = _dt.now().hour
    # If they're the operator (not a POC), bounce them to the dashboard —
    # standup is built around a personal roster.
    known = {p.lower() for p in all_pocs()}
    if slug.lower() not in known:
        return RedirectResponse("/dashboard", status_code=303)
    # Parallel fan-out: standup buckets + per-product targets all in one pool.
    # Wall-time becomes max(standup_build, target_for_one_product) instead of
    # serial sum. Each call opens its own DB connections — safe to race.
    product_key = (request.query_params.get("product") or "hgr").lower()
    if product_key not in _poc_targets.PRODUCTS:
        product_key = "hgr"
    from concurrent.futures import ThreadPoolExecutor
    try:
        with ThreadPoolExecutor(max_workers=1 + len(_poc_targets.PRODUCTS)) as pool:
            f_standup = pool.submit(_standup.build, poc_name)
            f_targets = {
                k: pool.submit(_poc_targets.for_poc, slug, k)
                for k in _poc_targets.PRODUCTS
            }
            standup_ctx = f_standup.result()
            both = {k: fut.result() for k, fut in f_targets.items()}
            targets_ctx = both.get(product_key)
    except Exception as e:  # noqa: BLE001
        return templates.TemplateResponse(
            "standup.html",
            {
                "request": request, "user_email": user,
                "first_name": first_name, "greeting_word": _greeting_word(hour),
                "standup": {"poc_name": poc_name, "today": "", "roster_size": 0,
                            "top_three": [], "underperformers": [],
                            "silent": [], "anomalies": []},
                "targets": None, "targets_by_product": {}, "active_product": product_key,
                "error": f"standup build failed: {e}",
            },
            status_code=500,
        )
    return templates.TemplateResponse(
        "standup.html",
        {
            "request": request, "user_email": user,
            "first_name": first_name, "greeting_word": _greeting_word(hour),
            "standup": standup_ctx,
            "targets": targets_ctx,
            "targets_by_product": both,
            "active_product": product_key,
        },
    )


@app.get("/creator-card/{handle}", response_model=None)
def creator_card_page(handle: str, request: Request):
    """The M1 Creator Card. Replaces /creator/{handle} as the primary
    drill-down. The old route still exists for now as a tabular fallback.
    """
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="Invalid creator handle")
    slug = poc_slug_from_email(user)
    try:
        card = _cc.build_card(slug, handle)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"card build failed: {e}"}, status_code=500)
    # Prefill outreach draft based on current status + top product.
    top_product = card["top_products"][0]["product"] if card["top_products"] else None
    outreach_draft = _outreach.draft_outreach(handle, card["status_key"], top_product)
    return templates.TemplateResponse(
        "creator_card.html",
        {
            "request": request, "user_email": user,
            "card": card, "outreach_draft": outreach_draft,
        },
    )


# Redirect the old detail route into the new card so existing links work.
@app.get("/creator/{handle}/card", response_model=None)
def creator_card_alias(handle: str):
    return RedirectResponse(f"/creator-card/{handle}", status_code=303)


@app.post("/creator/{handle}/notes", response_model=None)
async def creator_note_add(handle: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    body = (form.get("body_md") or "").strip()
    is_shared = bool(form.get("is_shared"))
    if not body:
        return RedirectResponse(f"/creator-card/{handle}", status_code=303)
    try:
        _cn.add(slug, handle, body, is_shared=is_shared)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return RedirectResponse(f"/creator-card/{handle}#notes-panel", status_code=303)


@app.post("/creator/{handle}/notes/{note_id}/toggle-share", response_model=None)
def creator_note_toggle(handle: str, note_id: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    try:
        _cn.toggle_share(slug, handle, note_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="note not found")
    return RedirectResponse(f"/creator-card/{handle}#notes-panel", status_code=303)


@app.post("/creator/{handle}/notes/{note_id}/delete", response_model=None)
def creator_note_delete(handle: str, note_id: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    _cn.delete(slug, handle, note_id)
    return RedirectResponse(f"/creator-card/{handle}#notes-panel", status_code=303)


@app.post("/creator/{handle}/status", response_model=None)
async def creator_status_set(handle: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    new_status = (form.get("status") or "").strip()
    try:
        _ce.set_status(slug, handle, new_status)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return RedirectResponse(f"/creator-card/{handle}", status_code=303)


@app.post("/creator/{handle}/outreach", response_model=None)
async def creator_outreach_log(handle: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    body = (form.get("body") or "").strip()
    _ce.record(slug, handle, "outreach_sent", {"body": body[:1000]})
    return RedirectResponse(f"/creator-card/{handle}", status_code=303)


@app.get("/outreach", response_model=None)
def outreach_page(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    known = {p.lower() for p in all_pocs()}
    if slug.lower() not in known:
        return RedirectResponse("/dashboard", status_code=303)
    kanban = _outreach.build_kanban(poc_name, slug)
    return templates.TemplateResponse(
        "outreach.html",
        {"request": request, "user_email": user, "kanban": kanban},
    )


@app.post("/outreach/move", response_model=None)
async def outreach_move(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    handle = (form.get("handle") or "").strip()
    new_status = (form.get("status") or "").strip()
    if not handle or not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="invalid handle")
    try:
        _outreach.move_card(slug, handle, new_status)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return RedirectResponse("/outreach", status_code=303)


@app.get("/campaigns", response_model=None)
def campaigns_page(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    return templates.TemplateResponse(
        "campaigns.html",
        {
            "request": request, "user_email": user,
            "campaigns": _campaigns.list_campaigns(),
            "hero_products": hero_products(),
        },
    )


@app.post("/campaigns/new", response_model=None)
async def campaign_create(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    form = await request.form()
    try:
        _campaigns.create_campaign(
            name=(form.get("name") or "").strip(),
            product=(form.get("product") or "").strip(),
            start_date=(form.get("start_date") or "").strip(),
            end_date=(form.get("end_date") or "").strip(),
            brief_md=(form.get("brief_md") or "").strip(),
            assignments=[],
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return RedirectResponse("/campaigns", status_code=303)


# ────────────────────────────────────────────────────────────────────
# Trackers — CSV-driven per-product target tracking
# ────────────────────────────────────────────────────────────────────

from .lib import trackers as _trackers
from .lib import poc_targets as _poc_targets


@app.get("/trackers", response_model=None)
def trackers_index(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    return templates.TemplateResponse(
        "trackers_list.html",
        {
            "request": request, "user_email": user,
            "trackers": _trackers.list_trackers(),
        },
    )


@app.get("/trackers/{tracker_id}", response_model=None)
@with_db_retry()
def tracker_view(tracker_id: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise HTTPException(status_code=400, detail="Invalid tracker id")
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    # Operators (anyone not in KNOWN_POCS) see all rows by default.
    # POCs see only their own; can flip with ?view=all if they're the operator.
    known_pocs = {p.lower() for p in all_pocs()}
    is_poc = slug.lower() in known_pocs
    requested_view = (request.query_params.get("view") or "").lower()
    # Date range — auto columns recompute against [start, end].
    # Default: current half-month, mirroring Tanmita's reporting cadence.
    from datetime import date as _date
    rs_q = (request.query_params.get("start") or "").strip()
    re_q = (request.query_params.get("end") or "").strip()
    range_start = range_end = None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", rs_q):
        try: range_start = _date.fromisoformat(rs_q)
        except ValueError: pass
    if re.match(r"^\d{4}-\d{2}-\d{2}$", re_q):
        try: range_end = _date.fromisoformat(re_q)
        except ValueError: pass
    if not is_poc:
        # Operator: default to all, can scope to a specific POC via ?poc=
        scope = (request.query_params.get("poc") or "").strip() or None
        ctx = _trackers.load_editable_view(
            tracker_id, poc_name=scope, poc_slug_for_status=slug,
            range_start=range_start, range_end=range_end,
        )
        can_see_all = True
    else:
        # POC: default to their own, can request `?view=all` to see roster-wide.
        view_filter = None if requested_view == "all" else poc_name
        ctx = _trackers.load_editable_view(
            tracker_id, poc_name=view_filter, poc_slug_for_status=slug,
            range_start=range_start, range_end=range_end,
        )
        can_see_all = True  # POCs can also see all if curious — not sensitive
    if ctx.get("error"):
        return templates.TemplateResponse(
            "trackers_list.html",
            {
                "request": request, "user_email": user,
                "trackers": _trackers.list_trackers(),
                "error": ctx["error"],
            },
            status_code=404 if "Unknown" in ctx["error"] else 200,
        )
    return templates.TemplateResponse(
        "tracker_view.html",
        {
            "request": request, "user_email": user,
            "ctx": ctx, "can_see_all": can_see_all,
            "viewer_poc_name": poc_name,
        },
    )


# ── Tracker CRUD endpoints (editable spreadsheet behaviour) ──────────

from .lib import tracker_data as _tdata
from .lib.tracker_schema import manual_field_keys
from .lib import csv_export as _csv_export


@app.get("/trackers/{tracker_id}/export.csv", response_model=None)
@with_db_retry()
def tracker_export_csv(tracker_id: str, request: Request):
    """Same data as the /trackers/{tracker_id} HTML page, but as CSV.
    Respects the same query params (start, end, view, poc) so what you
    download matches what you see."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise HTTPException(status_code=400, detail="Invalid tracker id")
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    known_pocs = {p.lower() for p in all_pocs()}
    is_poc = slug.lower() in known_pocs
    requested_view = (request.query_params.get("view") or "").lower()
    from datetime import date as _date
    rs_q = (request.query_params.get("start") or "").strip()
    re_q = (request.query_params.get("end") or "").strip()
    range_start = range_end = None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", rs_q):
        try: range_start = _date.fromisoformat(rs_q)
        except ValueError: pass
    if re.match(r"^\d{4}-\d{2}-\d{2}$", re_q):
        try: range_end = _date.fromisoformat(re_q)
        except ValueError: pass
    if not is_poc:
        scope = (request.query_params.get("poc") or "").strip() or None
        ctx = _trackers.load_editable_view(
            tracker_id, poc_name=scope, poc_slug_for_status=slug,
            range_start=range_start, range_end=range_end,
        )
    else:
        view_filter = None if requested_view == "all" else poc_name
        ctx = _trackers.load_editable_view(
            tracker_id, poc_name=view_filter, poc_slug_for_status=slug,
            range_start=range_start, range_end=range_end,
        )
    if ctx.get("error"):
        raise HTTPException(status_code=404, detail=ctx["error"])

    body = _csv_export.tracker_view_to_csv(ctx)
    fname = _csv_export.csv_response_filename(
        f"tracker_{tracker_id}",
        ctx.get("range_start") and str(ctx["range_start"]),
        ctx.get("range_end") and str(ctx["range_end"]),
    )
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"content-disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/tt-export/videos.csv", response_model=None)
def tt_export_videos(request: Request):
    """Full dump of tt_video as CSV. Streams via server-side cursor +
    bumped statement timeout (same pattern as /wp-export/messages.csv).

    tt_video has duplicate rows per video_id (one per fetch_date
    snapshot) — we DISTINCT ON (video_id) and keep the most recent
    snapshot. Result: one row per unique video.

    Query params (all optional):
      ?days=30             window relative to today (default 30)
      ?start=YYYY-MM-DD    explicit start (overrides days)
      ?end=YYYY-MM-DD      explicit end (defaults to today)
      ?handle=foo          one creator only
      ?product=HGR         videos tagged with that product

    Default: ~3-5K rows for 30 days across all creators. ~1-3 MB CSV.
    """
    user, err = _require_login(request)
    if err:
        return err
    from fastapi.responses import StreamingResponse
    from datetime import date as _date, timedelta as _td
    import csv as _csv
    import io as _io

    today = _date.today()
    days_raw = (request.query_params.get("days") or "30").strip()
    try:
        days = int(days_raw)
        if days < 1: days = 30
        if days > 3650: days = 3650
    except (TypeError, ValueError):
        days = 30
    default_start = today - _td(days=days)

    s = (request.query_params.get("start") or "").strip()
    e = (request.query_params.get("end") or "").strip()
    handle = (request.query_params.get("handle") or "").strip()
    product = (request.query_params.get("product") or "").strip()

    start_date = default_start
    end_date = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        try: start_date = _date.fromisoformat(s)
        except ValueError: pass
    if re.match(r"^\d{4}-\d{2}-\d{2}$", e):
        try: end_date = _date.fromisoformat(e)
        except ValueError: pass

    where = ["post_time IS NOT NULL", "post_time >= %(s)s::date", "post_time <= %(e)s::date"]
    params: dict = {"s": start_date, "e": end_date}
    if handle and re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        where.append("handle = %(handle)s")
        params["handle"] = handle
    if product:
        where.append("product = %(product)s")
        params["product"] = product

    sql = f"""
        SELECT DISTINCT ON (video_id)
          post_time, handle, video_id, title, gmv, view_count,
          units_sold, like_count, comment_count, engagement_rate,
          ctr, roi, product, fetch_date
        FROM tiktok_raw_data.tt_video
        WHERE {" AND ".join(where)}
        ORDER BY video_id, fetch_date DESC
    """

    HEADER = [
        "post_time", "handle", "video_id", "title", "gmv", "view_count",
        "units_sold", "like_count", "comment_count", "engagement_rate",
        "ctr", "roi", "product", "fetch_date",
    ]

    def row_stream():
        import time as _time
        buf = _io.StringIO()
        w = _csv.writer(buf, lineterminator="\n")
        w.writerow(HEADER)
        yield buf.getvalue()
        buf.seek(0); buf.truncate(0)
        from .lib.db import get_conn as _get_conn

        # Retry the execute() up to 3 times on transient errors (replica
        # recovery conflicts, connection blips) BEFORE we start streaming
        # data rows. Once we start streaming rows it's too late to retry.
        last_err = None
        for attempt in range(3):
            try:
                with _get_conn() as conn:
                    with conn.cursor() as c:
                        c.execute("SET statement_timeout = 600000")
                    # Regular cursor (not server-side) — single execute,
                    # libpq buffers result, we fetchmany() locally. Less
                    # vulnerable to mid-query VACUUM conflicts.
                    with conn.cursor() as cur:
                        cur.execute(sql, params)
                        while True:
                            batch = cur.fetchmany(5000)
                            if not batch:
                                break
                            for row in batch:
                                w.writerow(row)
                            yield buf.getvalue()
                            buf.seek(0); buf.truncate(0)
                return
            except (_psycopg.errors.SerializationFailure,
                    _psycopg.errors.OperationalError) as e:
                last_err = e
                if attempt < 2:
                    _time.sleep(2 * (attempt + 1))
        # Exhausted retries — emit an inline CSV error row so the user
        # sees what happened in the downloaded file.
        w.writerow([f"# ERROR after 3 attempts: {str(last_err)[:200]}"])
        yield buf.getvalue()

    fname_bits = [f"videos_{start_date.isoformat()}_to_{end_date.isoformat()}"]
    if handle:  fname_bits.append(handle)
    if product: fname_bits.append(product.replace(" ", "_"))
    fname = "_".join(fname_bits) + ".csv"
    return StreamingResponse(
        row_stream(),
        media_type="text/csv; charset=utf-8",
        headers={"content-disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/wp-export/messages.csv", response_model=None)
def wp_export_messages(request: Request):
    """Full dump of wp_convo.messages as CSV. Streams row-by-row using
    a server-side cursor so we don't load 260K+ rows into memory, and
    bumps the statement timeout for this single request so the long
    scan doesn't get killed by Supabase's default 2-min cap.

    Optional filters via query params:
      ?start=YYYY-MM-DD&end=YYYY-MM-DD     date window on sent_at
      ?direction=outbound|inbound          one direction only
      ?performed_by=email                  one POC's outgoing messages

    With no filters: 260K rows, ~60MB CSV, ~30-60s to stream.
    """
    user, err = _require_login(request)
    if err:
        return err
    from fastapi.responses import StreamingResponse
    import csv as _csv
    import io as _io

    s = (request.query_params.get("start") or "").strip()
    e = (request.query_params.get("end") or "").strip()
    direction = (request.query_params.get("direction") or "").strip()
    performed_by = (request.query_params.get("performed_by") or "").strip()

    where = []
    params: dict = {}
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        where.append("sent_at >= %(s)s::date")
        params["s"] = s
    if re.match(r"^\d{4}-\d{2}-\d{2}$", e):
        where.append("sent_at < (%(e)s::date + INTERVAL '1 day')")
        params["e"] = e
    if direction in ("inbound", "outbound"):
        where.append("direction = %(direction)s")
        params["direction"] = direction
    if performed_by and "@" in performed_by:
        where.append("performed_by = %(performed_by)s")
        params["performed_by"] = performed_by
    where_sql = "WHERE " + " AND ".join(where) if where else ""

    sql = f"""
        SELECT sent_at, performed_by, direction, chat_id, user_phone,
               sender_phone, message_type, has_media, body
        FROM wp_convo.messages
        {where_sql}
        ORDER BY chat_id, sent_at
    """

    # Static header — order matches the SELECT above. Sent immediately
    # so ngrok sees first bytes well before its ~60s first-byte cutoff.
    WP_HEADER = [
        "sent_at", "performed_by", "direction", "chat_id", "user_phone",
        "sender_phone", "message_type", "has_media", "body",
    ]

    def row_stream():
        buf = _io.StringIO()
        w = _csv.writer(buf, lineterminator="\n")
        w.writerow(WP_HEADER)
        yield buf.getvalue()
        buf.seek(0); buf.truncate(0)
        from .lib.db import get_conn as _get_conn
        with _get_conn() as conn:
            with conn.cursor() as c:
                c.execute("SET statement_timeout = 600000")  # 10 min
            with conn.cursor(name="wp_dump") as cur:
                cur.itersize = 5000
                cur.execute(sql, params)
                for row in cur:
                    w.writerow(row)
                    if buf.tell() > 64 * 1024:
                        yield buf.getvalue()
                        buf.seek(0); buf.truncate(0)
                if buf.tell() > 0:
                    yield buf.getvalue()

    fname = "wp_messages"
    if s: fname += f"_{s}"
    if e: fname += f"_to_{e}"
    fname += ".csv"
    return StreamingResponse(
        row_stream(),
        media_type="text/csv; charset=utf-8",
        headers={"content-disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/creators/export.csv", response_model=None)
@with_db_retry()
def creators_export_csv(request: Request):
    """Same data as the /creators HTML page, but as CSV. Respects
    ?start=&end=&product= so the download matches what you see."""
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    default_start = today - _td(days=30)
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    product_q = (request.query_params.get("product") or "").strip()
    sd = default_start; ed = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try: sd = _date.fromisoformat(start_q)
        except ValueError: sd = default_start
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try: ed = _date.fromisoformat(end_q)
        except ValueError: ed = today
    data = build_creators_list(poc_name, sd, ed, product_filter=product_q)
    creators = [c["creator"] for c in data.get("creators") or []]
    cid_rows = get_content_id_gmv(creators, sd, ed, product_filter=product_q)
    body = _csv_export.creators_list_to_csv(data, content_id_rows=cid_rows)
    fname = _csv_export.csv_response_filename(
        f"creators_{slug or 'all'}", sd.isoformat(), ed.isoformat(),
    )
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"content-disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/all-creators", response_model=None)
@with_db_retry()
def all_creators_page(request: Request):
    """Operator-only view of every creator in the DB, regardless of POC roster."""
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    known_pocs = {p.lower() for p in all_pocs()}
    is_poc = slug.lower() in known_pocs
    if is_poc:
        raise HTTPException(status_code=403, detail="Operator access only")
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    default_start = today - _td(days=30)
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    product_q = (request.query_params.get("product") or "").strip()
    sd = default_start; ed = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try: sd = _date.fromisoformat(start_q)
        except ValueError: sd = default_start
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try: ed = _date.fromisoformat(end_q)
        except ValueError: ed = today
    all_db = get_all_db_creators()
    ctx = build_creators_list(None, sd, ed, product_filter=product_q, creator_list_override=all_db)
    ctx["poc_name"] = "All creators (DB)"
    sparks = {}
    daily_payload = {}
    for c in ctx["creators"]:
        running = 0
        cum_rows = []
        for d in c["daily_videos"]:
            running += d["count"]
            cum_rows.append({"date": d["date"], "count": running})
        sparks[c["creator"]] = sparkline_svg(
            [r["count"] for r in cum_rows], width=120, height=24, show_dots=False,
        )
        daily_payload[c["creator"]] = cum_rows
    return templates.TemplateResponse(
        "creators_list.html",
        {
            "request": request,
            "user_email": user,
            "ctx": ctx,
            "hero_products": hero_products(),
            "sparklines": sparks,
            "daily_payload": daily_payload,
            "nav_active": "all_creators",
            "export_url": "/all-creators/export.csv",
        },
    )


@app.get("/all-creators/export.csv", response_model=None)
@with_db_retry()
def all_creators_export_csv(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    known_pocs = {p.lower() for p in all_pocs()}
    if slug.lower() in known_pocs:
        raise HTTPException(status_code=403, detail="Operator access only")
    from datetime import date as _date, timedelta as _td
    today = _date.today()
    default_start = today - _td(days=30)
    start_q = request.query_params.get("start", "").strip()
    end_q = request.query_params.get("end", "").strip()
    product_q = (request.query_params.get("product") or "").strip()
    sd = default_start; ed = today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", start_q):
        try: sd = _date.fromisoformat(start_q)
        except ValueError: sd = default_start
    if re.match(r"^\d{4}-\d{2}-\d{2}$", end_q):
        try: ed = _date.fromisoformat(end_q)
        except ValueError: ed = today
    all_db = get_all_db_creators()
    data = build_creators_list(None, sd, ed, product_filter=product_q, creator_list_override=all_db)
    cid_rows = get_content_id_gmv(all_db, sd, ed, product_filter=product_q)
    body = _csv_export.creators_list_to_csv(data, content_id_rows=cid_rows)
    fname = _csv_export.csv_response_filename("all_creators", sd.isoformat(), ed.isoformat())
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"content-disposition": f'attachment; filename="{fname}"'},
    )


@app.post("/trackers/{tracker_id}/creators", response_model=None)
async def tracker_add_creator(tracker_id: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise HTTPException(status_code=400, detail="Invalid tracker id")
    slug = poc_slug_from_email(user)
    form = await request.form()
    handle = (form.get("handle") or "").strip().lstrip("@")
    poc = (form.get("poc") or poc_name_from_slug(slug) or "").strip()
    if not handle:
        return RedirectResponse(f"/trackers/{tracker_id}?error=missing_handle", status_code=303)
    try:
        _tdata.add_row(tracker_id, handle, poc, manual=None, author_slug=slug)
    except ValueError as e:
        return RedirectResponse(f"/trackers/{tracker_id}?error={str(e)[:80]}", status_code=303)
    return RedirectResponse(f"/trackers/{tracker_id}#row-{handle}", status_code=303)


@app.post("/trackers/{tracker_id}/creators/{handle}/field", response_model=None)
async def tracker_update_field(tracker_id: str, handle: str, request: Request):
    """Save a single cell edit. Designed for HTMX hx-post on blur."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise HTTPException(status_code=400, detail="Invalid tracker id")
    if not re.match(r"^[A-Za-z0-9._-]{1,64}$", handle):
        raise HTTPException(status_code=400, detail="Invalid handle")
    slug = poc_slug_from_email(user)
    form = await request.form()
    field = (form.get("field") or "").strip()
    raw_value = form.get("value")
    # `poc` field is special — handled separately (it's identity, not manual)
    if field == "poc":
        try:
            _tdata.update_poc(tracker_id, handle, str(raw_value or ""), author_slug=slug)
        except (ValueError, KeyError) as e:
            return JSONResponse({"error": str(e)}, status_code=400)
        return JSONResponse({"ok": True, "field": "poc", "value": raw_value})
    if field not in manual_field_keys(tracker_id):
        return JSONResponse({"error": f"unknown field: {field}"}, status_code=400)
    try:
        _tdata.update_field(tracker_id, handle, field, raw_value, author_slug=slug)
    except (ValueError, KeyError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return JSONResponse({"ok": True, "field": field, "value": raw_value})


@app.post("/trackers/{tracker_id}/creators/{handle}/remove", response_model=None)
def tracker_remove_creator(tracker_id: str, handle: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    try:
        _tdata.remove_row(tracker_id, handle, author_slug=slug)
    except KeyError:
        raise HTTPException(status_code=404, detail="Creator not in tracker")
    return RedirectResponse(f"/trackers/{tracker_id}", status_code=303)


@app.post("/trackers/{tracker_id}/creators/{handle}/restore", response_model=None)
def tracker_restore_creator(tracker_id: str, handle: str, request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    try:
        _tdata.restore_row(tracker_id, handle, author_slug=slug)
    except KeyError:
        raise HTTPException(status_code=404, detail="Creator not in tracker")
    return RedirectResponse(f"/trackers/{tracker_id}?show_removed=1#row-{handle}", status_code=303)


@app.get("/trackers/{tracker_id}/removed", response_model=None)
def tracker_removed_view(tracker_id: str, request: Request):
    """Trash bin — soft-removed rows with a Restore button each."""
    user, err = _require_login(request)
    if err:
        return err
    if not re.match(r"^[a-z0-9_-]{1,32}$", tracker_id):
        raise HTTPException(status_code=400, detail="Invalid tracker id")
    all_rows = _tdata.list_rows(tracker_id, include_removed=True)
    removed = [r for r in all_rows if r.get("removed")]
    meta = _trackers.get_tracker(tracker_id)
    return templates.TemplateResponse(
        "tracker_removed.html",
        {
            "request": request, "user_email": user,
            "tracker": meta, "rows": removed,
        },
    )


# ────────────────────────────────────────────────────────────────────
# Coordinator scorecard (Tanmita's view — POC × product targets)
# ────────────────────────────────────────────────────────────────────


@app.get("/coordinator", response_model=None)
@with_db_retry()
def coordinator_page(request: Request):
    """All POCs × focus product, targets vs achievement for one half-month."""
    user, err = _require_login(request)
    if err:
        return err
    # Default product = HGR (current focus); fall back to magashwa if asked.
    product_key = (request.query_params.get("product") or "hgr").lower()
    if product_key not in _poc_targets.PRODUCTS:
        product_key = "hgr"
    period_q = (request.query_params.get("period") or "").strip()
    if not re.match(r"^\d{4}-\d{2}-H[12]$", period_q):
        period_q = _poc_targets.current_period()
    try:
        ctx = _poc_targets.for_all_pocs(product_key, period_q)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return templates.TemplateResponse(
        "coordinator.html",
        {
            "request": request, "user_email": user,
            "ctx": ctx,
            "periods": _poc_targets.list_periods(months_back=6),
        },
    )


@app.get("/products", response_model=None)
def products_page(request: Request):
    """Product catalog view — read from portal/products.csv + live SKU counts."""
    user, err = _require_login(request)
    if err:
        return err
    products = all_products()
    # Live SKU counts from the DB
    sku_counts: dict[str, int] = {}
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT rootlabs_common_name, COUNT(*) "
                    "FROM rootlabs_core.rootlabs_products GROUP BY rootlabs_common_name"
                )
                for name, n in cur.fetchall():
                    if name:
                        sku_counts[name] = n
    except Exception as e:  # noqa: BLE001
        print(f"[products] SKU count query failed: {e}")
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "user_email": user,
            "products": products,
            "sku_counts": sku_counts,
            "all_count": len(products),
            "hero_count": sum(1 for p in products if p.category == "hero"),
            "bundle_count": sum(1 for p in products if p.category == "bundle"),
            "extra_count": sum(1 for p in products if p.category == "extra"),
        },
    )


@app.get("/roster", response_model=None)
def roster_page(request: Request):
    """Per-POC creator list management. The session POC owns this view."""
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    poc_name = poc_name_from_slug(slug)
    meta = roster_meta(slug)
    return templates.TemplateResponse(
        "roster.html",
        {
            "request": request,
            "user_email": user,
            "poc_slug": slug,
            "poc_name": poc_name,
            "creators": meta.get("creators", []),
            "updated_at": meta.get("updated_at"),
            "flash": request.query_params.get("flash"),
        },
    )


@app.post("/roster/add", response_model=None)
async def roster_add(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    handle = (form.get("handle") or "").strip()
    if handle:
        add_creator(slug, handle)
    return RedirectResponse(f"/roster?flash=Added+{handle}", status_code=303)


@app.post("/roster/bulk", response_model=None)
async def roster_bulk(request: Request):
    """Bulk-add creators from a pasted text block and/or an uploaded CSV.
    First-column CSV; auto-skips a header row named creator/handle/username.
    """
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    collected: list[str] = []

    pasted = (form.get("handles") or "").strip()
    if pasted:
        # Accept newline OR comma-separated.
        for chunk in pasted.replace(",", "\n").split("\n"):
            chunk = chunk.strip()
            if chunk:
                collected.append(chunk)

    csv_file = form.get("csv_file")
    if csv_file and hasattr(csv_file, "read"):
        try:
            content = (await csv_file.read()).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            content = ""
        if content:
            import csv as _csv
            import io as _io
            reader = _csv.reader(_io.StringIO(content))
            for i, row in enumerate(reader):
                if not row:
                    continue
                first = (row[0] or "").strip()
                if i == 0 and first.lower() in ("creator", "handle", "name", "username", "tiktok"):
                    continue
                if first:
                    collected.append(first)

    if not collected:
        return RedirectResponse("/roster?flash=Nothing+to+add", status_code=303)

    result = bulk_add_creators(slug, collected)
    msg = (
        f"Added+{result['added']}+new"
        f"+(skipped+{result['skipped_existing']}+existing"
        f"+{result['invalid']}+invalid)"
        f"+→+total+{result['total_after']}"
    )
    return RedirectResponse(f"/roster?flash={msg}", status_code=303)


@app.post("/roster/remove", response_model=None)
async def roster_remove(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    slug = poc_slug_from_email(user)
    form = await request.form()
    handle = (form.get("handle") or "").strip()
    if handle:
        remove_creator(slug, handle)
    return RedirectResponse(f"/roster?flash=Removed+{handle}", status_code=303)


_DEV_MODE = os.getenv("PORTAL_DEV_MODE", "").lower() in ("1", "true", "yes", "on")


def _landing_stats() -> dict:
    """Live counts shown on the login / signup hero. Safe under failure —
    falls back to a static set if any helper raises."""
    try:
        from .lib.poc_creators import all_pocs as _all_pocs, get_creators_for_poc as _gcfp
        pocs = list(_all_pocs())
        creator_count = sum(len(_gcfp(p)) for p in pocs)
        poc_count = len(pocs)
    except Exception:  # noqa: BLE001
        poc_count = 8
        creator_count = 0
    try:
        sku_count = len(all_products())
    except Exception:  # noqa: BLE001
        sku_count = 0
    return {
        "poc_count": poc_count,
        "creator_count": creator_count,
        "sku_count": sku_count,
    }


def _render_login(request: Request, *, stage: str, email: str | None = None,
                   error: str | None = None, status_code: int = 200):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "user_email": None,
            "stage": stage,
            "pending_email": email,
            "error": error,
            **_landing_stats(),
        },
        status_code=status_code,
    )


@app.get("/login", response_model=None)
def login_get(request: Request):
    # DEV-ONLY: ?as=<email> shortcut for local curl/testing. Locked behind
    # PORTAL_DEV_MODE=1 so it cannot be used in the deployed pilot.
    if _DEV_MODE:
        bypass = request.query_params.get("as")
        if bypass:
            if "@" not in bypass:
                if _wants_json(request):
                    raise HTTPException(status_code=400, detail="Provide ?as=<email>")
                return _render_login(request, stage="email", error="Invalid email", status_code=400)
            set_user(request, bypass.strip().lower())
            if _wants_json(request):
                return JSONResponse({"logged_in": True, "user_email": current_user(request)})
            return RedirectResponse("/standup", status_code=303)

    if request.query_params.get("reset"):
        request.session.pop("pending_email", None)
        return RedirectResponse("/login", status_code=303)

    pending = request.session.get("pending_email")
    if pending and _users.is_whitelisted(pending) and _users.has_password(pending):
        return _render_login(request, stage="password", email=pending)
    if pending:
        # State got out of sync (e.g. user record changed). Restart.
        request.session.pop("pending_email", None)
    return _render_login(request, stage="email")


@app.post("/login", response_model=None)
async def login_post(request: Request):
    """Stage 1: user enters email. We check the whitelist and route them."""
    form = await request.form()
    email = (form.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return _render_login(request, stage="email", error="Provide a valid email", status_code=400)
    if not _users.is_whitelisted(email):
        return _render_login(
            request,
            stage="email",
            error="That email isn't authorized for the portal. Ping Kartavvya if you think it should be.",
            status_code=403,
        )
    request.session["pending_email"] = email
    if not _users.has_password(email):
        return RedirectResponse("/signup", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.post("/login/password", response_model=None)
async def login_password_post(request: Request):
    """Stage 2: user enters password for the pending email."""
    pending = request.session.get("pending_email")
    if not pending or not _users.is_whitelisted(pending):
        request.session.pop("pending_email", None)
        return RedirectResponse("/login", status_code=303)
    form = await request.form()
    password = form.get("password") or ""
    if not _users.has_password(pending):
        return RedirectResponse("/signup", status_code=303)
    if not _users.authenticate(pending, password):
        return _render_login(
            request, stage="password", email=pending,
            error="Wrong password. Try again, or use the link below to start over.",
            status_code=401,
        )
    request.session.pop("pending_email", None)
    set_user(request, pending)
    _users.record_login(pending)
    return RedirectResponse("/standup", status_code=303)


@app.get("/signup", response_model=None)
def signup_get(request: Request):
    pending = request.session.get("pending_email")
    if not pending or not _users.is_whitelisted(pending):
        return RedirectResponse("/login", status_code=303)
    if _users.has_password(pending):
        # Already has a password — they shouldn't be here.
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "user_email": None, "pending_email": pending, "error": None,
         **_landing_stats()},
    )


@app.post("/signup", response_model=None)
async def signup_post(request: Request):
    pending = request.session.get("pending_email")
    if not pending or not _users.is_whitelisted(pending):
        return RedirectResponse("/login", status_code=303)
    if _users.has_password(pending):
        return RedirectResponse("/login", status_code=303)

    form = await request.form()
    new_pwd = (form.get("password") or "").strip()
    confirm = (form.get("confirm") or "").strip()

    def _err(msg: str, code: int = 400):
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "user_email": None, "pending_email": pending, "error": msg,
             **_landing_stats()},
            status_code=code,
        )

    if len(new_pwd) < 10:
        return _err("Password must be at least 10 characters.")
    if new_pwd != confirm:
        return _err("Passwords don't match. Re-type both fields.")

    if not _users.set_password(pending, new_pwd):
        return _err("Couldn't save password — your email may have been removed from the whitelist. Ping Kartavvya.", 403)

    request.session.pop("pending_email", None)
    set_user(request, pending)
    _users.record_login(pending)
    return RedirectResponse("/standup", status_code=303)


@app.get("/logout", response_model=None)
def logout(request: Request):
    clear(request)
    request.session.pop("pending_email", None)
    if _wants_json(request):
        return JSONResponse({"logged_in": False})
    return RedirectResponse("/login", status_code=303)


# ────────────────────────────────────────────────────────────────────
# Browse Data wizard (M6)
# ────────────────────────────────────────────────────────────────────


@app.get("/browse", response_model=None)
def browse_page(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    try:
        raw_schemas = list_schemas()
    except Exception as e:  # noqa: BLE001
        raw_schemas = []
        print(f"[browse] list_schemas failed: {e}")
    schemas = [{"name": s, "label": schema_label(s)} for s in raw_schemas]
    return templates.TemplateResponse(
        "browse.html",
        {"request": request, "user_email": user, "schemas": schemas},
    )


@app.get("/browse/tables", response_model=None)
def browse_tables(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    schema = (request.query_params.get("schema") or "").strip()
    if not schema or not _IDENT_RE.match(schema):
        return templates.TemplateResponse(
            "_browse_tables.html", {"request": request, "tables": []}
        )
    try:
        raw = list_tables(schema)
    except Exception as e:  # noqa: BLE001
        print(f"[browse] list_tables({schema!r}) failed: {e}")
        raw = []
    tables = [
        {
            "name": t.name,
            "label": table_label(schema, t.name),
            "table_type": t.table_type,
        }
        for t in raw
    ]
    return templates.TemplateResponse(
        "_browse_tables.html", {"request": request, "tables": tables}
    )


@app.get("/browse/detail", response_model=None)
def browse_detail(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    schema = (request.query_params.get("schema") or "").strip()
    table = (request.query_params.get("table") or "").strip()
    if not schema or not table:
        return templates.TemplateResponse(
            "_browse_detail.html",
            {"request": request, "error": "Pick a schema and table"},
        )
    if not _IDENT_RE.match(schema) or not _IDENT_RE.match(table):
        return templates.TemplateResponse(
            "_browse_detail.html",
            {"request": request, "error": "Invalid identifier"},
        )

    try:
        cols = list_columns(schema, table)
        preview_cols, preview_rows = sample_rows(schema, table, limit=50)
    except Exception as e:  # noqa: BLE001
        return templates.TemplateResponse(
            "_browse_detail.html",
            {"request": request, "error": f"DB error: {type(e).__name__}: {e}"},
        )

    # Sort columns by POC-priority before passing to the template — important
    # business columns appear first in dropdowns and reference list.
    cols = sort_columns(schema, table, cols)

    # Attach warnings and a friendly label to each column for the template
    columns_view = [
        {
            "name": c.name,
            "label": column_label(schema, table, c.name),
            "data_type": c.data_type,
            "is_nullable": c.is_nullable,
            "warnings": warnings_for_column(schema, table, c.name),
        }
        for c in cols
    ]

    creator_col = creator_column_for(schema, table)
    return templates.TemplateResponse(
        "_browse_detail.html",
        {
            "request": request,
            "schema": schema,
            "schema_label": schema_label(schema),
            "table": table,
            "table_label": table_label(schema, table),
            "columns": columns_view,
            "preview_cols": preview_cols,
            "preview_rows": preview_rows,
            "row_count": len(preview_rows),
            "supported_aggs": SUPPORTED_AGGS,
            "creator_column": creator_col,
            "poc_options": all_pocs() if creator_col else [],
        },
    )


@app.get("/browse/pivot/value-row", response_model=None)
def browse_pivot_value_row(request: Request):
    """HTMX endpoint — returns one additional value-spec row for the pivot form."""
    user, err = _require_login(request)
    if err:
        return err
    schema = (request.query_params.get("schema") or "").strip()
    table = (request.query_params.get("table") or "").strip()
    if not _IDENT_RE.match(schema) or not _IDENT_RE.match(table):
        raise HTTPException(status_code=400, detail="Invalid identifier")
    try:
        cols = list_columns(schema, table)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"DB error: {e}") from e
    cols = sort_columns(schema, table, cols)
    return templates.TemplateResponse(
        "_pivot_value_row.html",
        {
            "request": request,
            "columns": [
                {"name": c.name, "label": column_label(schema, table, c.name), "data_type": c.data_type}
                for c in cols
            ],
            "supported_aggs": SUPPORTED_AGGS,
        },
    )


@app.get("/browse/pivot/row-pick", response_model=None)
def browse_pivot_row_pick(request: Request):
    """HTMX endpoint — returns one additional row-spec dropdown for the pivot form."""
    user, err = _require_login(request)
    if err:
        return err
    schema = (request.query_params.get("schema") or "").strip()
    table = (request.query_params.get("table") or "").strip()
    if not _IDENT_RE.match(schema) or not _IDENT_RE.match(table):
        raise HTTPException(status_code=400, detail="Invalid identifier")
    try:
        cols = list_columns(schema, table)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"DB error: {e}") from e
    cols = sort_columns(schema, table, cols)
    return templates.TemplateResponse(
        "_pivot_row_pick.html",
        {
            "request": request,
            "columns": [
                {"name": c.name, "label": column_label(schema, table, c.name), "data_type": c.data_type}
                for c in cols
            ],
        },
    )


@app.get("/browse/pivot/filter-row", response_model=None)
def browse_pivot_filter_row(request: Request):
    """HTMX endpoint — returns one additional filter-spec row for the pivot form."""
    user, err = _require_login(request)
    if err:
        return err
    schema = (request.query_params.get("schema") or "").strip()
    table = (request.query_params.get("table") or "").strip()
    if not _IDENT_RE.match(schema) or not _IDENT_RE.match(table):
        raise HTTPException(status_code=400, detail="Invalid identifier")
    try:
        cols = list_columns(schema, table)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"DB error: {e}") from e
    cols = sort_columns(schema, table, cols)
    return templates.TemplateResponse(
        "_pivot_filter_row.html",
        {
            "request": request,
            "columns": [
                {"name": c.name, "label": column_label(schema, table, c.name), "data_type": c.data_type}
                for c in cols
            ],
            "supported_ops": SUPPORTED_OPS,
        },
    )


@app.post("/browse/pivot/run", response_model=None)
async def browse_pivot_run(request: Request):
    user, err = _require_login(request)
    if err:
        return err
    form = await request.form()
    schema = (form.get("schema") or "").strip()
    table = (form.get("table") or "").strip()
    if not _IDENT_RE.match(schema) or not _IDENT_RE.match(table):
        raise HTTPException(status_code=400, detail="Invalid identifier")

    rows = [r for r in form.getlist("rows") if r]
    aggs = form.getlist("value_agg")
    cols = form.getlist("value_col")
    values = tuple(
        ValueSpec(agg=a, column=c)
        for a, c in zip(aggs, cols)
        if a and c
    )

    # Filters: each row contributes (filter_col, filter_op, filter_v, filter_v2)
    # Skip rows where col or op is empty (POC clicked "+ add filter" then didn't fill it).
    f_cols = form.getlist("filter_col")
    f_ops = form.getlist("filter_op")
    f_vs = form.getlist("filter_v")
    f_v2s = form.getlist("filter_v2")
    filters_list: list[FilterSpec] = []
    for i in range(len(f_cols)):
        col_i = (f_cols[i] or "").strip()
        op_i = (f_ops[i] or "").strip()
        if not col_i or not op_i:
            continue
        filters_list.append(
            FilterSpec(
                column=col_i,
                op=op_i,
                value=(f_vs[i] if i < len(f_vs) else None) or None,
                value2=(f_v2s[i] if i < len(f_v2s) else None) or None,
            )
        )

    try:
        limit = int(form.get("limit") or "1000")
    except ValueError:
        limit = 1000

    try:
        valid_cols = {c.name for c in list_columns(schema, table)}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"DB error: {e}") from e

    columns_dim_raw = (form.get("columns_dim") or "").strip() or None

    # POC scope filter — if a POC is picked AND this table has a creator column,
    # we apply a system-level WHERE that restricts to creators owned by that POC.
    poc_filter_raw = (form.get("poc_filter") or "").strip() or None
    creator_col = creator_column_for(schema, table)
    poc_creators: tuple[str, ...] | None = None
    if poc_filter_raw and creator_col:
        poc_creators = tuple(get_creators_for_poc(poc_filter_raw))
        if not poc_creators:
            raise HTTPException(status_code=400, detail=f"No creators found for POC {poc_filter_raw!r}")

    plan = PivotPlan(
        schema=schema,
        table=table,
        rows=tuple(rows),
        values=values,
        filters=tuple(filters_list),
        limit=limit,
        columns_dim=columns_dim_raw,
        creator_column=creator_col if poc_creators else None,
        poc_creator_filter=poc_creators,
        poc_name=poc_filter_raw if poc_creators else None,
    )
    try:
        validate_plan(plan, valid_cols)
    except PivotValidationError as e:
        # Re-render the detail page with the error message
        # (Simpler M7 path: just return a small error page.)
        raise HTTPException(status_code=400, detail=str(e)) from e

    sql_str, sql_params = build_sql(plan)
    filter_desc = ", ".join(
        f"{f.column} {f.op}" + (f" {f.value}" if f.value else "") + (f"..{f.value2}" if f.value2 else "")
        for f in plan.filters
    ) or "(none)"
    columns_desc = plan.columns_dim or "(none — tall)"
    poc_desc = f"POC scope={plan.poc_name} ({len(plan.poc_creator_filter or ())} creators)" if plan.poc_creator_filter else "POC scope=ALL"
    synthetic = Report(
        slug="browse-pivot",
        title=f"Pivot: {schema}.{table}" + (f" · {plan.poc_name}" if plan.poc_name else ""),
        description=f"Dynamic pivot — {poc_desc}, rows=[{', '.join(rows) or '(none)'}], cols=[{columns_desc}], values=[{', '.join(f'{v.agg}({v.column})' for v in values)}], filters=[{filter_desc}], limit={limit}",
        inputs=[],
        owner_poc=[],
        query_sql=sql_str,
    )
    poc_email = resolve_poc_email(request)
    post_process = None
    if plan.columns_dim:
        # Closure captures plan; pivot_wide returns (cols, rows).
        def post_process(cols, rows, _plan=plan):
            return pivot_wide(cols, rows, _plan)
    poc_slug_for_cache = poc_slug_from_email(poc_email)
    cache_params = {
        "schema": schema, "table": table,
        "rows": list(rows),
        "values": [(v.agg, v.column) for v in values],
        "filters": [(f.column, f.op, f.value, f.value2) for f in plan.filters],
        "columns_dim": plan.columns_dim, "limit": limit,
        "poc": plan.poc_name or "",
    }
    q = query_hash("pivot", f"{schema}.{table}", cache_params)
    if request.query_params.get("refresh") != "1":
        cached = get_cached(poc_slug_for_cache, q)
        if cached:
            return RedirectResponse(f"/result/{cached}?from_cache=1", status_code=303)

    task_id, _ = start_async(synthetic, params=sql_params, poc_email=poc_email, post_process=post_process)
    set_cached(poc_slug_for_cache, q, task_id, summary=synthetic.description[:200])
    return RedirectResponse(f"/result/{task_id}", status_code=303)


# ────────────────────────────────────────────────────────────────────
# Reports
# ────────────────────────────────────────────────────────────────────


@app.get("/run/{slug}", response_model=None)
def run_get(slug: str, request: Request):
    report = _load_report_or_404(slug)
    if report.inputs:
        # If any input has type=poc, pass the POC option list to the template.
        needs_poc_options = any(inp.get("type") == "poc" for inp in report.inputs)
        return templates.TemplateResponse(
            "run_form.html",
            {
                "request": request,
                "user_email": current_user(request),
                "report": report,
                "submitted": None,
                "poc_options": all_pocs() if needs_poc_options else [],
            },
        )
    return _kick_off(report, params={}, request=request)


@app.post("/run/{slug}", response_model=None)
async def run_post(slug: str, request: Request):
    report = _load_report_or_404(slug)
    form = await request.form()
    params = {inp["name"]: (form.get(inp["name"]) or inp.get("default", "")) for inp in report.inputs}
    missing = [inp["label"] for inp in report.inputs if inp.get("required") and not params.get(inp["name"])]
    if missing:
        needs_poc_options = any(inp.get("type") == "poc" for inp in report.inputs)
        return templates.TemplateResponse(
            "run_form.html",
            {
                "request": request,
                "user_email": current_user(request),
                "report": report,
                "submitted": params,
                "error": f"Missing required: {', '.join(missing)}",
                "poc_options": all_pocs() if needs_poc_options else [],
            },
            status_code=400,
        )
    # POC-type inputs expand into a second bound param `<name>_creators` —
    # a list of creator handles looked up from May Sheet PoC.csv. The
    # report's SQL is expected to use ANY(%(<name>_creators)s) guarded by
    # an empty-poc OR check.
    for inp in report.inputs:
        if inp.get("type") == "poc":
            poc_name = (params.get(inp["name"]) or "").strip()
            params[inp["name"]] = poc_name  # normalise
            params[f"{inp['name']}_creators"] = (
                get_creators_for_poc(poc_name) if poc_name else []
            )

    # Cache lookup — same query within TTL → redirect to existing task.
    # ?refresh=1 bypasses cache. Skipped for curl/JSON callers since they
    # expect inline CSV (M1 contract).
    if not _wants_json(request) and request.query_params.get("refresh") != "1":
        poc_email = resolve_poc_email(request)
        poc_slug = poc_slug_from_email(poc_email)
        q = query_hash("report", slug, params)
        cached = get_cached(poc_slug, q)
        if cached:
            return RedirectResponse(f"/result/{cached}?from_cache=1", status_code=303)
    return _kick_off(report, params=params, request=request)


def _kick_off(report, params: dict, request: Request):
    poc_email = resolve_poc_email(request)
    poc_slug = poc_slug_from_email(poc_email)

    if _wants_json(request):
        result = execute_sync(report, params=params, poc_email=poc_email)
        if result.status != "ok":
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "task_id": result.task_id,
                    "error": result.error,
                    "audit_md": str(result.audit_path),
                    "result_url": f"/result/{result.task_id}",
                },
            )
        return FileResponse(
            path=result.csv_path,
            media_type="text/csv",
            filename=f"{report.slug}_{result.task_id}.csv",
            headers={
                "X-Task-Id": result.task_id,
                "X-Row-Count": str(result.row_count),
                "X-Audit-Path": str(result.audit_path),
                "X-Poc-Slug": result.poc_slug,
                "X-Result-Url": f"/result/{result.task_id}",
            },
        )

    task_id, _ = start_async(report, params=params, poc_email=poc_email)
    # Cache: store the just-kicked-off task_id so a duplicate submission
    # within TTL redirects here instead of starting another worker.
    q = query_hash("report", report.slug, params)
    set_cached(poc_slug, q, task_id, summary=f"{report.slug} {params}"[:200])
    return RedirectResponse(f"/result/{task_id}", status_code=303)


# ────────────────────────────────────────────────────────────────────
# Result pages (async task)
# ────────────────────────────────────────────────────────────────────


def _resolve_task_or_404(task_id: str, request: Request):
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/login", status_code=303)
    poc_slug = poc_slug_from_email(user)
    deliv = find_deliverable(poc_slug, task_id)
    if deliv is None:
        return None, JSONResponse(status_code=404, content={"error": "task not found"})
    return (user, poc_slug, deliv), None


def _load_csv_preview(csv_path: Path, max_rows: int = 200) -> tuple[list[str], list[list[str]], int]:
    """Return (columns, rows, total_rows). Truncates display to max_rows."""
    if not csv_path.exists():
        return [], [], 0
    import csv as _csv
    with csv_path.open() as f:
        reader = _csv.reader(f)
        try:
            cols = next(reader)
        except StopIteration:
            return [], [], 0
        rows: list[list[str]] = []
        total = 0
        for row in reader:
            total += 1
            if len(rows) < max_rows:
                rows.append(row)
        return cols, rows, total


@app.get("/result/{task_id}", response_model=None)
def result_page(task_id: str, request: Request):
    ctx, err = _resolve_task_or_404(task_id, request)
    if err:
        return err
    user, poc_slug, deliv = ctx

    status_doc = read_status(deliv) or {}
    audit_path = deliv / "audit.md"
    audit_md = audit_path.read_text() if audit_path.exists() else ""
    csv_path = deliv / "result.csv"
    preview_cols, preview_rows, total_rows = _load_csv_preview(csv_path)

    title = "Report"
    for line in audit_md.splitlines()[:8] if audit_md else []:
        if line.startswith("- **Report:**"):
            try:
                title = line.split("—", 1)[1].strip()
            except IndexError:
                pass
            break
    if not audit_md and status_doc.get("report_slug"):
        try:
            r = load_report(status_doc["report_slug"])
            title = r.title
        except Exception:  # noqa: BLE001
            title = status_doc["report_slug"]

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user_email": user,
            "task_id": task_id,
            "status": status_doc.get("status", "running"),
            "row_count": status_doc.get("row_count") or 0,
            "started_at": status_doc.get("started_at", ""),
            "ended_at": status_doc.get("ended_at", ""),
            "duration_s": _duration_seconds(status_doc.get("started_at"), status_doc.get("ended_at")),
            "error": status_doc.get("error"),
            "audit_md": audit_md,
            "report": {"title": title, "slug": status_doc.get("report_slug", "")},
            "preview_cols": preview_cols,
            "preview_rows": preview_rows,
            "total_rows": total_rows,
            "from_cache": request.query_params.get("from_cache") == "1",
        },
    )


@app.get("/result/{task_id}/fragment", response_model=None)
def result_fragment(task_id: str, request: Request):
    ctx, err = _resolve_task_or_404(task_id, request)
    if err:
        return err
    _, _, deliv = ctx
    status_doc = read_status(deliv) or {}
    status = status_doc.get("status", "running")
    response = templates.TemplateResponse(
        "_status_fragment.html",
        {
            "request": request,
            "task_id": task_id,
            "status": status,
            "row_count": status_doc.get("row_count") or 0,
            "started_at": status_doc.get("started_at", ""),
            "duration_s": _duration_seconds(status_doc.get("started_at"), status_doc.get("ended_at")),
            "error": status_doc.get("error"),
        },
    )
    # When the task transitions out of "running", force HTMX to reload the
    # full page so the inline data preview + audit MD sections render. The
    # fragment by itself only carries the status panel, not the data table.
    if status in ("ok", "error"):
        response.headers["HX-Refresh"] = "true"
    return response


@app.get("/result/{task_id}/status", response_model=None)
def result_status(task_id: str, request: Request):
    ctx, err = _resolve_task_or_404(task_id, request)
    if err:
        return err
    _, _, deliv = ctx
    status_doc = read_status(deliv) or {"status": "running"}
    return JSONResponse(status_doc)


@app.get("/result/{task_id}/csv", response_model=None)
def result_csv(task_id: str, request: Request):
    ctx, err = _resolve_task_or_404(task_id, request)
    if err:
        return err
    _, _, deliv = ctx
    csv_path = deliv / "result.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="CSV not ready yet (task may still be running)")
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=f"{task_id}.csv",
    )
