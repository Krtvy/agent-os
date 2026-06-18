"""
Execute a report's query.sql against Supabase, write result.csv + audit.md.

Two entry points:
  start_async(report, params, poc_email) -> task_id
    Creates the deliverable folder, writes status.json (running), spawns a
    daemon thread that runs the query, returns the task_id immediately.
    Used by the form/result page flow — POC sees /result/<task_id> while
    the SQL is still executing.

  execute_sync(report, params, poc_email) -> RunResult
    Blocks until the query finishes. Used by curl/JSON clients that want
    the CSV inline in the response.

Parameters are passed via psycopg's named-parameter binding (%(name)s);
never string interpolation, so SQL injection from form inputs is
structurally impossible.
"""

from __future__ import annotations

import csv
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .db import get_conn
from .reports import Report
from .status import write_status
from .storage import deliverable_dir, new_task_id, now_iso, poc_slug_from_email

# Signature: (columns, rows) -> (columns, rows). Used by M9 cross-tab pivots
# to reshape the tall query output before writing the CSV.
PostProcessFn = Callable[[list[str], list[tuple]], tuple[list[str], list[tuple]]]


@dataclass(frozen=True)
class RunResult:
    task_id: str
    poc_slug: str
    csv_path: Path
    audit_path: Path
    row_count: int
    status: str  # "ok" | "error"
    error: str | None = None


def start_async(
    report: Report,
    params: dict | None,
    poc_email: str | None,
    post_process: PostProcessFn | None = None,
) -> tuple[str, str]:
    """Kick off background execution. Returns (task_id, poc_slug) immediately."""
    params = params or {}
    poc_slug = poc_slug_from_email(poc_email)
    task_id = new_task_id()
    out_dir = deliverable_dir(poc_slug, task_id)
    started_at = now_iso()

    write_status(
        out_dir,
        status="running",
        task_id=task_id,
        poc_slug=poc_slug,
        report_slug=report.slug,
        started_at=started_at,
        ended_at=None,
        row_count=None,
        error=None,
    )

    t = threading.Thread(
        target=_run_in_thread,
        args=(report, params, poc_slug, task_id, out_dir, started_at, post_process),
        daemon=True,
        name=f"report-{report.slug}-{task_id}",
    )
    t.start()
    return task_id, poc_slug


def execute_sync(
    report: Report,
    params: dict | None,
    poc_email: str | None,
    post_process: PostProcessFn | None = None,
) -> RunResult:
    """Block until the query finishes. For curl/JSON clients."""
    params = params or {}
    poc_slug = poc_slug_from_email(poc_email)
    task_id = new_task_id()
    out_dir = deliverable_dir(poc_slug, task_id)
    started_at = now_iso()
    write_status(
        out_dir,
        status="running",
        task_id=task_id,
        poc_slug=poc_slug,
        report_slug=report.slug,
        started_at=started_at,
    )
    return _do_run(report, params, poc_slug, task_id, out_dir, started_at, post_process)


def _run_in_thread(
    report: Report,
    params: dict,
    poc_slug: str,
    task_id: str,
    out_dir: Path,
    started_at: str,
    post_process: PostProcessFn | None,
) -> None:
    try:
        _do_run(report, params, poc_slug, task_id, out_dir, started_at, post_process)
    except Exception as e:  # noqa: BLE001
        write_status(
            out_dir,
            status="error",
            ended_at=now_iso(),
            error=f"{type(e).__name__}: {e}",
        )


def _do_run(
    report: Report,
    params: dict,
    poc_slug: str,
    task_id: str,
    out_dir: Path,
    started_at: str,
    post_process: PostProcessFn | None = None,
) -> RunResult:
    csv_path = out_dir / "result.csv"
    audit_path = out_dir / "audit.md"

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(report.query_sql, params)
                columns = [d.name for d in cur.description] if cur.description else []
                rows = cur.fetchall() if cur.description else []
        if post_process is not None:
            columns, rows = post_process(columns, rows)
        _write_csv(csv_path, columns, rows)
        ended_at = now_iso()
        _write_audit(
            audit_path,
            report=report,
            params=params,
            poc_slug=poc_slug,
            task_id=task_id,
            started_at=started_at,
            ended_at=ended_at,
            row_count=len(rows),
            status="ok",
            error=None,
        )
        write_status(
            out_dir,
            status="ok",
            ended_at=ended_at,
            row_count=len(rows),
        )
        return RunResult(
            task_id=task_id,
            poc_slug=poc_slug,
            csv_path=csv_path,
            audit_path=audit_path,
            row_count=len(rows),
            status="ok",
        )
    except Exception as e:  # noqa: BLE001
        ended_at = now_iso()
        err = f"{type(e).__name__}: {e}"
        _write_audit(
            audit_path,
            report=report,
            params=params,
            poc_slug=poc_slug,
            task_id=task_id,
            started_at=started_at,
            ended_at=ended_at,
            row_count=0,
            status="error",
            error=err,
        )
        write_status(out_dir, status="error", ended_at=ended_at, error=err)
        return RunResult(
            task_id=task_id,
            poc_slug=poc_slug,
            csv_path=csv_path,
            audit_path=audit_path,
            row_count=0,
            status="error",
            error=err,
        )


def _write_csv(path: Path, columns: list[str], rows: list[tuple]) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        for r in rows:
            w.writerow(r)


def _write_audit(
    path: Path,
    *,
    report: Report,
    params: dict,
    poc_slug: str,
    task_id: str,
    started_at: str,
    ended_at: str,
    row_count: int,
    status: str,
    error: str | None,
) -> None:
    lines = [
        f"# Audit — {report.slug} / {task_id}",
        "",
        f"- **POC:** `{poc_slug}`",
        f"- **Report:** `{report.slug}` — {report.title}",
        f"- **Status:** `{status}`",
        f"- **Rows:** {row_count}",
        f"- **Started:** {started_at}",
        f"- **Ended:** {ended_at}",
        "",
        "## Inputs",
        "",
    ]
    if params:
        for k, v in params.items():
            lines.append(f"- `{k}` = `{v!r}`")
    else:
        lines.append("_(none)_")
    lines += ["", "## Query", "", "```sql", report.query_sql.strip(), "```", ""]
    if error:
        lines += ["## Error", "", "```", error, "```", ""]
    path.write_text("\n".join(lines))
