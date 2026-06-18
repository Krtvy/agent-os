"""Google SSO via Authlib, domain-restricted.

Only emails ending in @{ALLOWED_EMAIL_DOMAIN} (default mosaicwellness.in)
may access the portal.
"""
import os
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import redirect, session, url_for

oauth = OAuth()


def init_oauth(app):
    """Register the Google provider on the Flask app."""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def allowed_domain() -> str:
    return os.environ.get("ALLOWED_EMAIL_DOMAIN", "mosaicwellness.in").lower()


def verify_and_login(claims: dict) -> tuple[bool, str | None]:
    """Verify email domain and populate session['user']. Returns (ok, err_msg)."""
    email = (claims.get("email") or "").lower()
    domain = allowed_domain()
    if not email.endswith(f"@{domain}"):
        return False, f"Only @{domain} emails may access this portal. You tried: {email or '(no email)'}"
    session["user"] = {
        "email": email,
        "name": claims.get("name", email),
        "picture": claims.get("picture"),
    }
    return True, None


def login_required(f):
    """Decorator: redirect to /login if no session user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated
