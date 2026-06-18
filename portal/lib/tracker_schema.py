"""
Tracker column schemas — one source of truth for which fields are
POC-editable (manual) vs computed from the live DB (auto).

Adding a new column for a tracker = one edit here. The data store, the
template, and the seed migration all consume this.

Field types:
  - "text"    free text input
  - "number"  numeric input (USD or count)
  - "bool"    checkbox (yes/no)
  - "select"  dropdown from a fixed option list

Per tracker, MANUAL_FIELDS is an ordered list — that order is the column
order the template renders.
"""

from __future__ import annotations

# Identity columns — every tracker has these.
IDENTITY_FIELDS = ("handle", "poc")

# Auto (read-only, live from DB) columns shown in every tracker.
# Values are computed against the date range the user picks on the page.
AUTO_FIELDS = (
    {"key": "status",         "label": "status"},
    {"key": "videos_in_range","label": "videos in range",    "format": "int"},
    {"key": "gmv_in_range",   "label": "GMV in range",        "format": "money"},
    {"key": "nv_gmv_in_range","label": "NV GMV in range",     "format": "money"},
    {"key": "last_post",      "label": "last post",           "format": "date"},
    {"key": "days_silent",    "label": "silent",              "format": "days"},
)

# Manual (POC-editable) columns per tracker. Order = column order in UI.
MANUAL_FIELDS = {
    "magashwa": [
        {"key": "flag",             "label": "Flag",              "type": "text"},
        {"key": "retainer_usd",     "label": "Retainer ($/mo)",   "type": "number"},
        {"key": "target_gmv_h1",    "label": "Target GMV (H1)",   "type": "number"},
        {"key": "target_videos_h1", "label": "Target videos (H1)","type": "number"},
        {"key": "target_gmv_h2",    "label": "Target GMV (H2)",   "type": "number"},
        {"key": "target_videos_h2", "label": "Target videos (H2)","type": "number"},
        {"key": "why_target",       "label": "Why this target",   "type": "text"},
        {"key": "comment",          "label": "Comment",           "type": "text"},
        {"key": "sample_sent",      "label": "Sample sent?",      "type": "bool"},
        {"key": "deal_closed",      "label": "Deal closed?",      "type": "bool"},
        {"key": "videos_locked",    "label": "Videos locked?",    "type": "bool"},
    ],
    "hgr": [
        {"key": "flag",             "label": "Flag",              "type": "text"},
        {"key": "retainer_usd",     "label": "Retainer ($/mo)",   "type": "number"},
        {"key": "target_gmv_h1",    "label": "Target GMV (H1)",   "type": "number"},
        {"key": "target_videos_h1", "label": "Target videos (H1)","type": "number"},
        {"key": "target_gmv_h2",    "label": "Target GMV (H2)",   "type": "number"},
        {"key": "target_videos_h2", "label": "Target videos (H2)","type": "number"},
        {"key": "why_target",       "label": "Why this target",   "type": "text"},
        {"key": "comment",          "label": "Comment",           "type": "text"},
        {"key": "sample_sent",      "label": "Sample sent?",      "type": "bool"},
        {"key": "deal_closed",      "label": "Deal closed?",      "type": "bool"},
        {"key": "videos_locked",    "label": "Videos locked?",    "type": "bool"},
    ],
}


def manual_field_keys(tracker_id: str) -> set[str]:
    return {f["key"] for f in MANUAL_FIELDS.get(tracker_id, [])}


def manual_field_type(tracker_id: str, field_key: str) -> str | None:
    for f in MANUAL_FIELDS.get(tracker_id, []):
        if f["key"] == field_key:
            return f["type"]
    return None


def empty_manual(tracker_id: str) -> dict:
    """Return a fresh manual-field dict with type-appropriate defaults."""
    out: dict = {}
    for f in MANUAL_FIELDS.get(tracker_id, []):
        if f["type"] == "bool":
            out[f["key"]] = False
        elif f["type"] == "number":
            out[f["key"]] = 0
        else:
            out[f["key"]] = ""
    return out


def coerce_value(field_type: str, raw: str) -> object:
    """Convert an HTML form string value into the right Python type."""
    raw = (raw or "").strip() if isinstance(raw, str) else raw
    if field_type == "bool":
        return str(raw).lower() in ("1", "true", "yes", "on", "y")
    if field_type == "number":
        try:
            return float(raw) if raw not in ("", None) else 0
        except (TypeError, ValueError):
            return 0
    return str(raw) if raw is not None else ""
