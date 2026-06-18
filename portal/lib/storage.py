"""
Filesystem layout for portal runs.

pocs/<poc-slug>/deliverables/<task_id>/
├── result.csv         # the data
└── audit.md           # what was asked, what was run, when, by whom

`_dev` is the POC slug used until M2 (auth) lands.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
POCS_ROOT = REPO_ROOT / "pocs"


def new_task_id() -> str:
    """16-char hex, ~64 bits of entropy — collision-free for the foreseeable future."""
    return secrets.token_hex(8)


# Email-to-slug overrides — handles first-name collisions between
# whitelisted users. Rachit Singh (POC) and Rachit Gupta (senior/operator)
# both have first name "rachit"; the override pushes the senior's slug to
# something unique so he gets an operator-style empty/aggregate roster
# instead of accidentally inheriting the POC's data.
_SLUG_OVERRIDES = {
    "rachit.gupta@mosaicwellness.in": "rachit_gupta",
}


def poc_slug_from_email(email: str | None) -> str:
    """Derive a POC slug from an email. POC data folders are indexed by
    first name (`pocs/trupti/`, `pocs/khushi/`, etc.), so we strip
    everything after the first dot in the local part — `trupti.k@...`
    collapses to `trupti`, `khushi.shah@...` collapses to `khushi`.

    `_SLUG_OVERRIDES` handles cases where two whitelisted users share a
    first name (e.g. Rachit Singh / Rachit Gupta)."""
    if not email:
        return "_dev"
    email_lower = email.strip().lower()
    if email_lower in _SLUG_OVERRIDES:
        return _SLUG_OVERRIDES[email_lower]
    local = email_lower.split("@", 1)[0]
    return local.split(".", 1)[0]


def deliverable_dir(poc_slug: str, task_id: str) -> Path:
    d = POCS_ROOT / poc_slug / "deliverables" / task_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_deliverable(poc_slug: str, task_id: str) -> Path | None:
    """Return the deliverable folder if it exists for this POC, else None.

    Scoped to the requesting POC so one POC can't view another POC's task_id.
    """
    d = POCS_ROOT / poc_slug / "deliverables" / task_id
    return d if d.is_dir() else None


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
