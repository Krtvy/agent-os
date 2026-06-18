"""
Portal user store — whitelisted emails + per-user password hashes.

Storage: _private/portal_users.json (gitignored).
Schema:
    {
      "alice@mosaicwellness.in": {
        "name": "Alice",
        "password_hash": "pbkdf2_sha256$...",   # null if not yet set
        "created_at": "2026-05-27T00:10:00+05:30",
        "last_login": "2026-05-27T01:42:11+05:30"
      },
      ...
    }

Email is the identity (matches existing slug-based POC detection). Anyone
not in this file cannot log in, full stop.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Iterable

from .passwords import hash_password, verify_password

REPO_ROOT = Path(__file__).resolve().parents[2]
USERS_PATH = REPO_ROOT / "_private" / "portal_users.json"

_LOCK = Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _load() -> dict:
    if not USERS_PATH.exists():
        return {}
    try:
        with USERS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = USERS_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    tmp.replace(USERS_PATH)


def _norm(email: str | None) -> str:
    return (email or "").strip().lower()


def is_whitelisted(email: str) -> bool:
    return _norm(email) in _load()


def has_password(email: str) -> bool:
    rec = _load().get(_norm(email))
    return bool(rec and rec.get("password_hash"))


def authenticate(email: str, password: str) -> bool:
    rec = _load().get(_norm(email))
    if not rec:
        return False
    return verify_password(password, rec.get("password_hash"))


def set_password(email: str, password: str) -> bool:
    """Set/replace the password hash for a whitelisted email. Returns False
    if the email isn't whitelisted (we never auto-create accounts)."""
    key = _norm(email)
    with _LOCK:
        data = _load()
        if key not in data:
            return False
        data[key]["password_hash"] = hash_password(password)
        data[key]["password_set_at"] = _now_iso()
        _save(data)
    return True


def record_login(email: str) -> None:
    key = _norm(email)
    with _LOCK:
        data = _load()
        if key in data:
            data[key]["last_login"] = _now_iso()
            _save(data)


def get_user(email: str) -> dict | None:
    rec = _load().get(_norm(email))
    if not rec:
        return None
    return {
        "email": _norm(email),
        "name": rec.get("name") or _norm(email).split("@", 1)[0],
        "has_password": bool(rec.get("password_hash")),
        "last_login": rec.get("last_login"),
    }


def list_users() -> list[dict]:
    """Operator-facing summary — no hashes."""
    out = []
    for email, rec in sorted(_load().items()):
        out.append({
            "email": email,
            "name": rec.get("name") or email.split("@", 1)[0],
            "has_password": bool(rec.get("password_hash")),
            "created_at": rec.get("created_at"),
            "last_login": rec.get("last_login"),
        })
    return out


def seed(entries: Iterable[tuple[str, str]], overwrite: bool = False) -> dict:
    """Seed whitelisted emails. `entries` is iterable of (email, display_name).
    Existing rows are preserved unless `overwrite=True`.
    Returns {"added": [...], "skipped": [...]}.
    """
    added, skipped = [], []
    with _LOCK:
        data = _load()
        for email, name in entries:
            key = _norm(email)
            if not key or "@" not in key:
                continue
            if key in data and not overwrite:
                skipped.append(key)
                continue
            data[key] = {
                "name": name or key.split("@", 1)[0],
                "password_hash": None,
                "created_at": _now_iso(),
                "last_login": None,
            }
            added.append(key)
        _save(data)
    return {"added": added, "skipped": skipped}
