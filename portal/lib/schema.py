"""
Live Supabase schema introspection — powers the Browse Data wizard.

All identifier interpolation goes through psycopg.sql.Identifier so the
schema/table names supplied by the form are quoted+escaped properly.
Text-comparison filters (WHERE table_schema = %(schema)s) use named
parameter binding — no string interpolation surface.
"""

from __future__ import annotations

from dataclasses import dataclass

from psycopg import sql

from .db import get_conn

# Postgres internal schemas we always hide from POCs.
_HIDDEN_SCHEMAS = {
    "pg_catalog",
    "information_schema",
    "pg_toast",
}


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    data_type: str
    is_nullable: bool


@dataclass(frozen=True)
class TableInfo:
    schema: str
    name: str
    table_type: str  # "BASE TABLE" | "VIEW"


def list_schemas() -> list[str]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT LIKE 'pg_%'
                ORDER BY schema_name
                """
            )
            return [
                r[0]
                for r in cur.fetchall()
                if r[0] not in _HIDDEN_SCHEMAS
            ]


def list_tables(schema: str) -> list[TableInfo]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = %(schema)s
                ORDER BY table_type, table_name
                """,
                {"schema": schema},
            )
            return [TableInfo(schema=r[0], name=r[1], table_type=r[2]) for r in cur.fetchall()]


def list_columns(schema: str, table: str) -> list[ColumnInfo]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %(schema)s AND table_name = %(table)s
                ORDER BY ordinal_position
                """,
                {"schema": schema, "table": table},
            )
            return [
                ColumnInfo(name=r[0], data_type=r[1], is_nullable=(r[2] == "YES"))
                for r in cur.fetchall()
            ]


def sample_rows(schema: str, table: str, limit: int = 50) -> tuple[list[str], list[tuple]]:
    """Return (column_names, rows) for the first `limit` rows of the table."""
    limit = max(1, min(int(limit), 500))  # clamp
    query = sql.SQL("SELECT * FROM {sch}.{tbl} LIMIT {lim}").format(
        sch=sql.Identifier(schema),
        tbl=sql.Identifier(table),
        lim=sql.Literal(limit),
    )
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = cur.fetchall() if cur.description else []
            return cols, rows
