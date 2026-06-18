"""
Supabase Postgres connection for the portal — pooled.

Why pooled: every page that fans out per-POC queries (Coordinator,
Standup, Trackers, Dashboard) was opening fresh connections per call.
With 8 POCs × multiple queries × multiple concurrent requests, we
saturated the database role's connection cap and started getting
"too many connections" errors. A bounded pool of ~10 reused
connections handles every realistic load pattern with room to spare.

Safety guards (preserved from the un-pooled version):
- Read-only session enforced once per checkout via `configure`
- Statement timeout set on each pool connection
- Credentials loaded from `_private/daily_reporting/.env`, never logged
"""

from __future__ import annotations

import atexit
import os
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Iterator

import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / "_private" / "daily_reporting" / ".env"

_POOL: ConnectionPool | None = None
_POOL_LOCK = Lock()


def _load_env() -> dict[str, str]:
    """Resolve DB_* credentials. Order of precedence:
       1. Process env vars (set by Fly secrets in prod, by shell in dev)
       2. _private/daily_reporting/.env (local dev convenience)
    If after both sources any required var is missing, raise.
    """
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    if all(os.getenv(k) for k in required):
        return {k: os.getenv(k, "") for k in required}
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=False)
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing DB env vars: {missing}. "
            f"Set them in the process env (Fly secrets) or in {ENV_PATH}."
        )
    return {k: os.getenv(k, "") for k in required}


def _configure_conn(conn: psycopg.Connection) -> None:
    """Run once per connection when the pool checks one out the first time.
    Sets read-only + statement timeout + DISABLES auto-prepared-statements.

    The prepare_threshold=None bit is critical: psycopg3 auto-prepares
    queries after 5 reuses, but Supabase's pooler can recycle the
    server-side session out from under us (overnight idle, replica
    failover, etc.) — leaving our local cache thinking a prepared
    statement exists when it doesn't. Result: `InvalidSqlStatementName:
    prepared statement "_pg3_0" does not exist` on every query until
    the pool restarts. Disabling prepares trades a tiny bit of parse
    overhead per query for cache-coherence with the pooler."""
    timeout_ms = int(os.getenv("PORTAL_SQL_TIMEOUT_MS", "120000"))
    conn.prepare_threshold = None  # disable auto-prepare for pooler compatibility
    with conn.cursor() as cur:
        cur.execute(f"SET statement_timeout = {int(timeout_ms)}")
        cur.execute("SET default_transaction_read_only = on")
    conn.commit()


def _build_pool() -> ConnectionPool:
    cfg = _load_env()
    # application_name lets us filter pg_stat_activity and pg_stat_statements
    # to portal-only traffic when debugging Supabase slowness.
    conninfo = (
        f"host={cfg['DB_HOST']} port={cfg['DB_PORT']} dbname={cfg['DB_NAME']} "
        f"user={cfg['DB_USER']} password={cfg['DB_PASSWORD']} "
        f"connect_timeout=10 application_name=portal-pilot"
    )
    min_size = int(os.getenv("PORTAL_POOL_MIN", "2"))
    max_size = int(os.getenv("PORTAL_POOL_MAX", "10"))
    pool = ConnectionPool(
        conninfo=conninfo,
        min_size=min_size,
        max_size=max_size,
        kwargs={"autocommit": False},
        configure=_configure_conn,
        timeout=30,           # wait up to 30s for a free conn under load
        max_lifetime=30 * 60, # recycle conns every 30 min
        name="portal_pool",
        open=False,            # we open it explicitly below to control timing
    )
    pool.open(wait=False)
    return pool


def _get_pool() -> ConnectionPool:
    global _POOL
    if _POOL is None:
        with _POOL_LOCK:
            if _POOL is None:
                _POOL = _build_pool()
    return _POOL


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    """Yield a connection from the pool. Returned (not closed) when the
    context exits. Read-only and statement_timeout are pre-set by configure().
    """
    pool = _get_pool()
    with pool.connection() as conn:
        yield conn
        # Pool returns it automatically when the `with` exits.


def probe() -> dict:
    """Health check — returns {ok: True, server_time, pool_stats}."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok, NOW() AS server_time")
            row = cur.fetchone()
    stats = _get_pool().get_stats()
    return {
        "ok": bool(row and row[0] == 1),
        "server_time": str(row[1]) if row else None,
        "pool": {
            "size": stats.get("pool_size"),
            "available": stats.get("pool_available"),
            "requests_waiting": stats.get("requests_waiting"),
        },
    }


def _shutdown_pool() -> None:
    """Close the pool cleanly on interpreter exit so we don't leak conns."""
    global _POOL
    if _POOL is not None:
        try:
            _POOL.close()
        except Exception:  # noqa: BLE001
            pass
        _POOL = None


atexit.register(_shutdown_pool)
