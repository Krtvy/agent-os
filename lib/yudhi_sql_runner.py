"""Python runner for lib/yudhi-sql.sh.

Reads SQL from stdin. Connects via psycopg2 with read-only + statement_timeout
hard set BEFORE the query. Emits CSV (default) or JSON to stdout or a file.

The .env path comes from $YUDHI_ENV_FILE. Credentials never leave this process.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path

import psycopg2
import psycopg2.extras


def _load_env(env_path: Path) -> None:
    """Load KEY=VALUE pairs from a .env into os.environ. Tolerant of quoting."""
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        os.environ.setdefault(key, val)


def _connect():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "6543")),
        dbname=os.environ.get("DB_NAME", "postgres"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def _parse_params() -> dict:
    """Parse YUDHI_PARAMS env var: 'key=value\x1fkey=value\x1f...' → dict."""
    raw = os.environ.get("YUDHI_PARAMS", "")
    out: dict[str, str] = {}
    for pair in raw.split("\x1f"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            out[k.strip()] = v
    return out


def _coerce(value):
    """Make a value JSON/CSV-friendly."""
    if isinstance(value, (Decimal,)):
        # Decimal → float if whole, else string
        try:
            f = float(value)
            return f
        except Exception:
            return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _emit_csv(rows: list[dict], stream) -> None:
    if not rows:
        stream.write("")
        return
    fields = list(rows[0].keys())
    w = csv.writer(stream)
    w.writerow(fields)
    for r in rows:
        w.writerow([_coerce(r.get(f)) for f in fields])


def _emit_json(rows: list[dict], stream) -> None:
    stream.write(json.dumps(
        [{k: _coerce(v) for k, v in r.items()} for r in rows],
        ensure_ascii=False, indent=2))
    stream.write("\n")


def main() -> int:
    sql = sys.stdin.read()
    if not sql.strip():
        print("yudhi-sql-runner: empty SQL on stdin", file=sys.stderr)
        return 64

    env_path = Path(os.environ.get(
        "YUDHI_ENV_FILE",
        Path(__file__).resolve().parent.parent
        / "_private" / "daily_reporting" / ".env"))
    if not env_path.is_file():
        print(f"yudhi-sql-runner: env file not found: {env_path}",
              file=sys.stderr)
        return 1
    _load_env(env_path)

    timeout_ms = int(os.environ.get("YUDHI_TIMEOUT_MS", "30000"))
    params = _parse_params()
    out_file = os.environ.get("YUDHI_OUT_FILE", "")
    fmt = os.environ.get("YUDHI_FORMAT", "csv").lower()

    try:
        conn = _connect()
    except Exception as e:
        # Sanitize: don't leak host/user/password in error text
        msg = str(e)
        for var in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"):
            v = os.environ.get(var, "")
            if v:
                msg = msg.replace(v, f"<{var}>")
        print(f"yudhi-sql-runner: connect failed — {msg}", file=sys.stderr)
        return 1

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = {timeout_ms}")
                cur.execute("SET default_transaction_read_only = on")
                cur.execute("SET idle_in_transaction_session_timeout = '10s'")
                cur.execute(sql, params or None)
                if cur.description is None:
                    # No result set (would only happen on rejected DDL/DML;
                    # destructive pre-flight already caught the verbs)
                    rows: list[dict] = []
                else:
                    rows = cur.fetchall()
    except Exception as e:
        msg = str(e)
        for var in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"):
            v = os.environ.get(var, "")
            if v:
                msg = msg.replace(v, f"<{var}>")
        print(f"yudhi-sql-runner: query failed — {msg}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    if out_file:
        with open(out_file, "w", newline="") as f:
            (_emit_csv if fmt == "csv" else _emit_json)(rows, f)
        print(f"yudhi-sql-runner: wrote {len(rows)} rows → {out_file}",
              file=sys.stderr)
    else:
        (_emit_csv if fmt == "csv" else _emit_json)(rows, sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
