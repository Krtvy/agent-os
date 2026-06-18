"""
Known-tricky columns the POC should NOT use naively.

Each entry is matched against a column's `(schema, table, column)` triple.
A None for schema/table is a wildcard match.

Source of truth for these warnings: `training/glossary/` + `training/queries/`
already-vetted SQL. When a new pattern emerges, document it here so the
Browse Data UI flags it on hover.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Warning:
    schema: str | None  # None = match any schema
    table: str | None  # None = match any table
    column: str
    message: str


WARNINGS: list[Warning] = [
    # Date-time columns: must adjust for IST when computing day boundaries.
    Warning(
        schema=None,
        table=None,
        column="created_time",
        message="Use `created_time - INTERVAL '8 hours'` for IST day boundary — raw value is in UTC.",
    ),
    Warning(
        schema=None,
        table=None,
        column="post_time",
        message="Use `post_time - INTERVAL '8 hours'` for IST day boundary — raw value is in UTC.",
    ),
    # Revenue-related columns — naive use produces wrong GMV.
    Warning(
        schema=None,
        table="tiktok_orders",
        column="sku_subtotal_after_discount",
        message="For GMV add `sku_platform_discount` too: GMV = sku_subtotal_after_discount + sku_platform_discount.",
    ),
    Warning(
        schema=None,
        table="tiktok_orders",
        column="quantity",
        message="Multiply by `rootlabs_products.unit_multiplier` (via JOIN) to get true units sold.",
    ),
    Warning(
        schema=None,
        table="tiktok_orders",
        column="cancellation_return_type",
        message="Filter `IS NULL` to exclude cancellations/returns from GMV calculations.",
    ),
    Warning(
        schema=None,
        table=None,
        column="is_active",
        message="Always filter `is_active = true` when joining listings — inactive rows leak stale SKUs.",
    ),
    Warning(
        schema="tiktok_raw_data",
        table="tiktok_affiliate_orders",
        column="content_type",
        message="Case-sensitive. Valid values: 'Video', 'Livestream', 'Showcase', 'External Traffic Program'. NOT 'LIVE'.",
    ),
]


def warnings_for_column(schema: str, table: str, column: str) -> list[str]:
    """Return all warning messages that match this column."""
    out: list[str] = []
    for w in WARNINGS:
        if w.column != column:
            continue
        if w.schema is not None and w.schema != schema:
            continue
        if w.table is not None and w.table != table:
            continue
        out.append(w.message)
    return out
