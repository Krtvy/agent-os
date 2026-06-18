"""CSV export helpers.

Each public function takes one of the existing view-builder result dicts
(from `trackers.load_editable_view` or `creators_list.build_creators_list`)
and returns a CSV string. Routes wrap that in a `Response` with the right
Content-Disposition.

Goal: what POCs see in the HTML table is what they get in the CSV — same
rows, same columns, in the same order.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime


def _fmt(value, field_format: str | None = None) -> str:
    """Stringify a cell value for CSV. Booleans become Yes/No, dates
    become ISO, money/int formats are clean, None -> empty string."""
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if field_format == "money":
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return str(value)
    if field_format == "int":
        try:
            return str(int(value))
        except (TypeError, ValueError):
            return str(value)
    if field_format == "days":
        try:
            return str(int(value))
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def tracker_view_to_csv(view: dict) -> str:
    """Build a CSV string for a tracker view (result of
    `trackers.load_editable_view`).

    Columns: handle, poc, then every auto column in order, then every
    manual column in order.
    """
    auto_cols = view.get("columns_auto") or []
    manual_cols = view.get("columns_manual") or []
    rows = view.get("rows") or []

    header = ["handle", "poc"]
    for c in auto_cols:
        header.append(c.get("label", c.get("key", "")))
    for c in manual_cols:
        header.append(c.get("label", c.get("key", "")))

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)

    for r in rows:
        out: list[str] = [_fmt(r.get("handle")), _fmt(r.get("poc"))]
        auto = r.get("auto") or {}
        for c in auto_cols:
            out.append(_fmt(auto.get(c.get("key")), c.get("format")))
        manual = r.get("manual") or {}
        for c in manual_cols:
            ftype = c.get("type")
            # Number fields render as money on the page; keep CSV plain.
            fmt = "money" if ftype == "number" else None
            out.append(_fmt(manual.get(c.get("key")), fmt))
        w.writerow(out)

    return buf.getvalue()


def creators_list_to_csv(data: dict, content_id_rows: list[dict] | None = None) -> str:
    """Build a CSV string for a /creators page result (from
    `creators_list.build_creators_list`).

    If `content_id_rows` is provided (from `get_content_id_gmv`), a second
    section is appended after a blank row with per-content-id GMV breakdown.
    """
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow([
        "handle",
        "videos",
        "lives",
        "orders",
        "gmv_total",
        "gmv_new_video",
        "new_video_content_ids",
        "gmv_tail",
        "commission",
    ])
    for c in data.get("creators") or []:
        ids = c.get("new_video_content_ids") or []
        w.writerow([
            _fmt(c.get("creator")),
            _fmt(c.get("videos"), "int"),
            _fmt(c.get("lives"), "int"),
            _fmt(c.get("orders"), "int"),
            _fmt(c.get("gmv"), "money"),
            _fmt(c.get("gmv_new"), "money"),
            ";".join(str(v) for v in ids),
            _fmt(c.get("gmv_tail"), "money"),
            _fmt(c.get("commission"), "money"),
        ])

    if content_id_rows:
        w.writerow([])  # blank separator
        w.writerow(["handle", "content_id", "content_type", "gmv_type", "gmv"])
        for row in content_id_rows:
            w.writerow([
                _fmt(row.get("creator")),
                _fmt(row.get("content_id")),
                _fmt(row.get("content_type")),
                _fmt(row.get("gmv_type")),
                _fmt(row.get("gmv"), "money"),
            ])

    return buf.getvalue()


def csv_response_filename(slug: str, start: str | None, end: str | None) -> str:
    """Build a sensible filename for the download attachment."""
    parts = [slug]
    if start:
        parts.append(start)
    if end and end != start:
        parts.append(end)
    return "_".join(parts) + ".csv"
