"""
Natural-language → PivotPlan proposal pipeline.

Flow:
  1. propose(question, poc_email) → calls LLM client (mock or real),
     stores proposal JSON to pocs/<poc>/proposals/<id>.json, returns id.
  2. Later, load_proposal(poc_slug, id) reads it back for the review page.

The LLM proposal is NEVER executed directly. The review-page form POSTs
to the existing /browse/pivot/run path (or /run/<slug> for report matches),
where validate_plan() catches any hallucination.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

from .db import get_conn
from .llm_client import get_llm_client
from .schema_labels import column_label, schema_label, table_label
from .storage import POCS_ROOT, now_iso, poc_slug_from_email


def new_proposal_id() -> str:
    return secrets.token_hex(8)


def proposal_dir(poc_slug: str) -> Path:
    d = POCS_ROOT / poc_slug / "proposals"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_proposal(poc_slug: str, proposal_id: str, payload: dict) -> Path:
    path = proposal_dir(poc_slug) / f"{proposal_id}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    return path


def load_proposal(poc_slug: str, proposal_id: str) -> dict | None:
    path = proposal_dir(poc_slug) / f"{proposal_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def build_schema_context() -> str:
    """Return a compact text representation of all tables + columns in
    the data schemas, with friendly labels and ⚠ warnings inline.

    Used as the system prompt for the real LLM. The mock ignores this.
    """
    from .column_warnings import warnings_for_column
    from .schema import list_schemas, list_tables, list_columns

    target_schemas = {"tiktok_raw_data", "rootlabs_core"}  # widen later
    out: list[str] = [
        "You translate plain-English data questions into a structured JSON",
        "pivot plan. You DO NOT execute SQL. Output JSON only.",
        "",
        "Available schemas/tables:",
    ]
    try:
        for s in list_schemas():
            if s not in target_schemas:
                continue
            out.append(f"\n## {schema_label(s)} (schema: {s})")
            for t in list_tables(s):
                cols = list_columns(s, t.name)
                out.append(f"\n### {table_label(s, t.name)} (table: {t.name})")
                for c in cols:
                    warnings = warnings_for_column(s, t.name, c.name)
                    warn_txt = f"  ⚠ {'  ⚠ '.join(warnings)}" if warnings else ""
                    out.append(
                        f"  - {c.name} ({c.data_type}) — {column_label(s, t.name, c.name)}{warn_txt}"
                    )
    except Exception as e:  # noqa: BLE001
        out.append(f"\n(schema introspection failed: {e})")

    out += [
        "",
        "Output one of three JSON shapes:",
        "",
        '1. {"kind":"pivot","explanation":"...","confidence":"high|medium|low","plan":{...}}',
        '   plan = {schema, table, rows[], values[{agg,column}], filters[{column,op,value,value2}], columns_dim, limit}',
        '   aggs: SUM, COUNT, COUNT_DISTINCT, AVG, MIN, MAX',
        '   ops:  =, !=, >, <, >=, <=, contains, between, is_null, is_not_null',
        "",
        '2. {"kind":"report","report_slug":"...","params":{...},"explanation":"...","confidence":"..."}',
        '   Available pre-built reports: probe, table-info, creator-content-counts',
        "",
        '3. {"kind":"cannot_answer","reason":"..."}',
        '   or {"kind":"clarification","question":"...","context":"..."}',
        "",
        "Rules:",
        "- Only use columns that exist in the schemas above. Never invent.",
        "- Apply ⚠ warnings: IST date adjust, content_type='Livestream', etc.",
        "- For date filters use >= start AND < next_period_start, not equality.",
        "- Always set a sane limit (default 100, max 10000).",
        "- Explanation must mention any domain assumption made.",
    ]
    return "\n".join(out)


def propose(question: str, poc_email: str | None) -> dict:
    """Run the question through the LLM, save the proposal, return the
    saved record (including a new proposal_id)."""
    client = get_llm_client()
    raw = client.propose(question, schema_context=build_schema_context())

    poc_slug = poc_slug_from_email(poc_email)
    pid = new_proposal_id()
    payload: dict[str, Any] = {
        "id": pid,
        "question": question,
        "poc_slug": poc_slug,
        "asked_at": now_iso(),
        "client": client.name,
        "proposal": raw,
    }
    save_proposal(poc_slug, pid, payload)
    return payload
