"""
Outreach pipeline (M3) — kanban view over a POC's roster.

Columns are the status taxonomy from creator_events.STATUSES. Each creator
in the POC's roster sits in exactly one column based on the most recent
status_change event. Creators with no recorded status default to
"discovered" — the entry column.

Moving a card between columns writes a status_change event. No deletes —
the event log is append-only by design so we can audit how a creator
moved over time.

Also drafts an outreach DM in narada-style voice that the POC can copy.
"""

from __future__ import annotations

from datetime import date, timedelta

from .creator_events import STATUSES, STATUS_EMOJI, STATUS_LABEL, all_creator_statuses_for_poc, set_status
from .poc_creators import get_creators_for_poc


def build_kanban(poc_name: str, poc_slug: str) -> dict:
    """Bucket roster into status columns."""
    creators = get_creators_for_poc(poc_name)
    statuses = all_creator_statuses_for_poc(poc_slug, creators)
    columns: dict[str, list[str]] = {s: [] for s in STATUSES}
    for h in creators:
        s = statuses.get(h, "discovered")
        columns.setdefault(s, []).append(h)
    # Keep columns sorted by handle for stable rendering.
    for s in columns:
        columns[s].sort()
    return {
        "poc_name": poc_name,
        "poc_slug": poc_slug,
        "columns": [
            {
                "key": s,
                "label": STATUS_LABEL[s],
                "emoji": STATUS_EMOJI[s],
                "count": len(columns[s]),
                "handles": columns[s],
            }
            for s in STATUSES
        ],
        "statuses": STATUSES,
    }


def move_card(poc_slug: str, handle: str, new_status: str) -> dict:
    """Record the move. Returns the new event."""
    return set_status(poc_slug, handle, new_status)


# ─── Outreach DM drafting ─────────────────────────────────────────────
# A pragmatic, narada-voice template. POC clicks "draft outreach" → we
# fill in handle + most-relevant product + soft pitch. They copy-paste
# (or later, we wire it directly to Periskope/Cruva).

_DM_TEMPLATES = {
    "discovered": (
        "hey @{handle} — saw your content, vibes match what we're building "
        "with {brand}. mind a quick chat about a paid creator partnership? "
        "(short — promise.)"
    ),
    "outreach_sent": (
        "hey @{handle}, following up on my earlier DM about the {product} "
        "partnership — happy to share more if you're curious."
    ),
    "cooling_off": (
        "hey @{handle}, noticed you've been quiet on {product} lately — "
        "everything ok on your end? lmk if there's anything blocking you "
        "from posting or if the brief needs tweaking."
    ),
    "active": (
        "hey @{handle}, nice run lately — would you be open to bumping "
        "your cadence on {product}? we can supply more product samples + "
        "a few new hooks."
    ),
    "top_performer": (
        "hey @{handle}, your {product} content is killing it — wanna "
        "talk about an exclusive partnership / higher-tier campaign?"
    ),
}


def draft_outreach(handle: str, status: str, top_product: str | None = None,
                   brand: str = "Rootlabs") -> str:
    tpl = _DM_TEMPLATES.get(status, _DM_TEMPLATES["discovered"])
    product = top_product or "our hero product"
    return tpl.format(handle=handle, brand=brand, product=product)
