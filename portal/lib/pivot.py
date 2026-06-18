"""
Dynamic pivot SQL builder + filter clause.

Safety contract:
- Every column / schema / table identifier is whitelist-validated against
  the live information_schema listing BEFORE being interpolated.
- Aggregation names + filter operators are whitelist-validated against
  hardcoded sets.
- Identifiers are double-quoted with embedded-quote escape.
- Filter VALUES (user-supplied) NEVER touch the SQL string. They flow
  through psycopg's %(name)s named-parameter binding and are returned
  in a params dict that the caller hands to cur.execute().
"""

from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_AGGS = ("SUM", "COUNT", "COUNT_DISTINCT", "AVG", "MIN", "MAX")

# Filter operators — each maps to a SQL fragment template.
# `{ident}` = quoted column identifier; `{p}`, `{p2}` = placeholder names.
SUPPORTED_OPS: dict[str, dict] = {
    "=": {"template": "{ident} = %({p})s", "needs": 1, "label": "equals"},
    "!=": {"template": "{ident} != %({p})s", "needs": 1, "label": "not equal"},
    ">": {"template": "{ident} > %({p})s", "needs": 1, "label": "greater than"},
    "<": {"template": "{ident} < %({p})s", "needs": 1, "label": "less than"},
    ">=": {"template": "{ident} >= %({p})s", "needs": 1, "label": "≥"},
    "<=": {"template": "{ident} <= %({p})s", "needs": 1, "label": "≤"},
    "contains": {"template": "{ident} ILIKE %({p})s", "needs": 1, "label": "contains (case-insensitive)"},
    "between": {"template": "{ident} BETWEEN %({p})s AND %({p2})s", "needs": 2, "label": "between"},
    "is_null": {"template": "{ident} IS NULL", "needs": 0, "label": "is null"},
    "is_not_null": {"template": "{ident} IS NOT NULL", "needs": 0, "label": "is not null"},
}


@dataclass(frozen=True)
class ValueSpec:
    agg: str  # one of SUPPORTED_AGGS
    column: str  # must be a real column of (schema, table)


@dataclass(frozen=True)
class FilterSpec:
    column: str  # must be a real column of (schema, table)
    op: str  # one of SUPPORTED_OPS keys
    value: str | None
    value2: str | None  # for BETWEEN


@dataclass(frozen=True)
class PivotPlan:
    schema: str
    table: str
    rows: tuple[str, ...]
    values: tuple[ValueSpec, ...]
    filters: tuple[FilterSpec, ...]
    limit: int
    columns_dim: str | None = None  # M9: cross-tab — single col whose values become output headers
    # POC scope: when set, applied as a system WHERE clause restricting the
    # query to creators assigned to the chosen POC. Not editable by the user
    # via the regular filter UI — it's a separate "scope" mechanism.
    creator_column: str | None = None
    poc_creator_filter: tuple[str, ...] | None = None
    poc_name: str | None = None  # for audit only


class PivotValidationError(ValueError):
    pass


def _quote_ident(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


def validate_plan(plan: PivotPlan, valid_columns: set[str]) -> None:
    if not plan.values:
        raise PivotValidationError("Pick at least one value column + aggregation.")
    if len(plan.values) > 8:
        raise PivotValidationError("Maximum 8 value columns.")
    if len(plan.rows) > 6:
        raise PivotValidationError("Maximum 6 row dimensions.")
    if len(plan.filters) > 10:
        raise PivotValidationError("Maximum 10 filters.")
    if plan.limit < 1 or plan.limit > 100_000:
        raise PivotValidationError("Limit must be between 1 and 100000.")

    for r in plan.rows:
        if r not in valid_columns:
            raise PivotValidationError(f"Unknown row column: {r!r}")
    for v in plan.values:
        if v.agg.upper() not in SUPPORTED_AGGS:
            raise PivotValidationError(f"Unsupported aggregation: {v.agg!r}")
        if v.column not in valid_columns:
            raise PivotValidationError(f"Unknown value column: {v.column!r}")
    for f in plan.filters:
        if f.op not in SUPPORTED_OPS:
            raise PivotValidationError(f"Unsupported filter operator: {f.op!r}")
        if f.column not in valid_columns:
            raise PivotValidationError(f"Unknown filter column: {f.column!r}")
        needs = SUPPORTED_OPS[f.op]["needs"]
        if needs >= 1 and (f.value is None or f.value == ""):
            raise PivotValidationError(f"Filter {f.column} {f.op} needs a value")
        if needs >= 2 and (f.value2 is None or f.value2 == ""):
            raise PivotValidationError(f"Filter {f.column} {f.op} needs a second value")
    if plan.columns_dim is not None:
        if plan.columns_dim not in valid_columns:
            raise PivotValidationError(f"Unknown columns dimension: {plan.columns_dim!r}")
        if plan.columns_dim in plan.rows:
            raise PivotValidationError(
                f"{plan.columns_dim!r} can't be both a Row and the Columns dimension"
            )
        for v in plan.values:
            if v.column == plan.columns_dim:
                raise PivotValidationError(
                    f"{plan.columns_dim!r} can't be both the Columns dimension and a Value column"
                )
    if plan.poc_creator_filter:
        if not plan.creator_column:
            raise PivotValidationError("poc_creator_filter requires creator_column to be set")
        if plan.creator_column not in valid_columns:
            raise PivotValidationError(f"Unknown creator column for POC filter: {plan.creator_column!r}")
        if len(plan.poc_creator_filter) > 5000:
            raise PivotValidationError("Too many creators in POC scope (max 5000)")


def build_sql(plan: PivotPlan) -> tuple[str, dict[str, str]]:
    """Return (sql_string, params_dict). Caller passes both to cur.execute().

    For cross-tab (M9), columns_dim is included alongside rows in SELECT +
    GROUP BY — query returns tall data; pivot_wide() reshapes it to wide.
    """
    # When columns_dim is set, treat it as an extra row dimension for the SQL
    # (it's a group-by column from the DB's perspective; we'll pivot in pandas).
    effective_rows: tuple[str, ...] = plan.rows
    if plan.columns_dim is not None:
        effective_rows = plan.rows + (plan.columns_dim,)

    select_parts: list[str] = []
    for r in effective_rows:
        select_parts.append(_quote_ident(r))
    for v in plan.values:
        agg = v.agg.upper()
        alias = f"{agg.lower()}_{v.column}"
        if agg == "COUNT_DISTINCT":
            # Postgres syntax: COUNT(DISTINCT col)
            select_parts.append(
                f"COUNT(DISTINCT {_quote_ident(v.column)}) AS {_quote_ident(alias)}"
            )
        else:
            select_parts.append(
                f"{agg}({_quote_ident(v.column)}) AS {_quote_ident(alias)}"
            )

    sql_parts: list[str] = []
    sql_parts.append("SELECT " + ", ".join(select_parts))
    sql_parts.append(f"FROM {_quote_ident(plan.schema)}.{_quote_ident(plan.table)}")

    params: dict = {}
    where_clauses: list[str] = []

    # POC scope filter — applied as a system WHERE before any user filters.
    # Uses Postgres ANY(array) syntax for a bound list of creators.
    if plan.poc_creator_filter and plan.creator_column:
        ident = _quote_ident(plan.creator_column)
        where_clauses.append(f"{ident} = ANY(%(_poc_creators)s)")
        params["_poc_creators"] = list(plan.poc_creator_filter)

    if plan.filters:
        for i, f in enumerate(plan.filters):
            spec = SUPPORTED_OPS[f.op]
            ident = _quote_ident(f.column)
            p_name = f"f{i}_v"
            p2_name = f"f{i}_v2"
            clause = spec["template"].format(ident=ident, p=p_name, p2=p2_name)
            where_clauses.append(clause)
            if spec["needs"] >= 1:
                val = f.value or ""
                if f.op == "contains":
                    val = f"%{val}%"
                params[p_name] = val
            if spec["needs"] >= 2:
                params[p2_name] = f.value2 or ""
    if where_clauses:
        sql_parts.append("WHERE " + " AND ".join(where_clauses))

    if effective_rows:
        gb = ", ".join(_quote_ident(r) for r in effective_rows)
        sql_parts.append("GROUP BY " + gb)
        sql_parts.append("ORDER BY " + gb)
    sql_parts.append(f"LIMIT {int(plan.limit)}")
    return "\n".join(sql_parts) + ";", params


def pivot_wide(
    tall_columns: list[str],
    tall_rows: list[tuple],
    plan: PivotPlan,
) -> tuple[list[str], list[tuple]]:
    """Reshape tall query output into wide cross-tab via pandas.

    Only called when plan.columns_dim is set. For plans without columns_dim,
    skip this — the tall format IS the desired output.

    Output column layout:
      [row1, row2, ..., "<value_alias>=<col_value>", "<value_alias>=<col_value>", ...]
    e.g. a plan with rows=[creator], columns_dim=product, values=[SUM(gmv)] yields:
      [creator, sum_gmv=iPhone, sum_gmv=Android, ...]
    """
    if plan.columns_dim is None:
        return tall_columns, tall_rows

    import pandas as pd

    df = pd.DataFrame(tall_rows, columns=tall_columns)
    index_cols = list(plan.rows) if plan.rows else None
    cols_dim = plan.columns_dim
    value_cols = [f"{v.agg.lower()}_{v.column}" for v in plan.values]

    # If no row dims, we still need an index for pivot_table — synthesize one.
    if not index_cols:
        df["_all_"] = "(all)"
        index_cols = ["_all_"]

    wide = df.pivot_table(
        index=index_cols,
        columns=cols_dim,
        values=value_cols,
        aggfunc="first",  # SQL already aggregated per (rows + cols_dim) bucket
    )
    # Flatten multi-level columns: ('sum_gmv', 'iPhone') → 'sum_gmv=iPhone'
    if isinstance(wide.columns, pd.MultiIndex):
        wide.columns = [f"{val_col}={col_val}" for val_col, col_val in wide.columns]
    wide = wide.reset_index()
    if "_all_" in wide.columns:
        wide = wide.drop(columns=["_all_"])
    # Replace NaN cells with None so csv.writer renders them as empty rather
    # than the literal string "nan".
    wide = wide.astype(object).where(wide.notna(), None)
    out_columns = [str(c) for c in wide.columns]
    out_rows = [tuple(r) for r in wide.itertuples(index=False, name=None)]
    return out_columns, out_rows
