"""
Session shape — cookie-stored, signed, no DB.

Identity contract:
- request.session["user_email"] is the canonical identity, set by /login or
  /signup after password verification.
- The `?as=<email>` query param is a DEV-ONLY escape hatch, locked behind
  the PORTAL_DEV_MODE=1 env flag. Off in production / the pilot deploy.
"""

from __future__ import annotations

import os

from fastapi import Request

SESSION_USER_KEY = "user_email"


def _dev_mode() -> bool:
    return os.getenv("PORTAL_DEV_MODE", "").lower() in ("1", "true", "yes", "on")


def current_user(request: Request) -> str | None:
    return request.session.get(SESSION_USER_KEY)


def set_user(request: Request, email: str) -> None:
    request.session[SESSION_USER_KEY] = email


def clear(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)


def resolve_poc_email(request: Request) -> str | None:
    """Session first. In DEV_MODE only, falls back to ?as= for curl convenience."""
    user = current_user(request)
    if user:
        return user
    if _dev_mode():
        return request.query_params.get("as")
    return None
