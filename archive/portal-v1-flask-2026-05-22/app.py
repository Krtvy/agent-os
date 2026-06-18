"""
Rootlabs POC Self-Serve Data Portal — Flask app

POC types a question or uploads a template; portal captures the request to
training/patterns/_candidates/ (build-as-capture), spawns Yudhi in a background
thread, immediately returns a result page that polls /api/result/<task_id>.

Auth: Google SSO via Authlib, restricted to @mosaicwellness.in.
"""
import logging
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from portal.lib.auth import init_oauth, login_required, oauth, verify_and_login, allowed_domain
from portal.lib.capture import capture_request
from portal.lib.task_runner import get_task_status, run_task_in_background

load_dotenv()

# Stdout logging so Docker / gunicorn captures it.
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("portal")

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[1]))
DELIVERABLES_ROOT = Path(os.environ.get("DELIVERABLES_ROOT", REPO_ROOT / "pocs"))
CANDIDATES_DIR = Path(
    os.environ.get("CANDIDATES_DIR", REPO_ROOT / "training" / "patterns" / "_candidates")
)
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
YUDHI_TIMEOUT = int(os.environ.get("YUDHI_TIMEOUT_SECONDS", "90"))

# Local-dev escape hatch: set DEV_BYPASS_AUTH=1 to skip Google OAuth entirely.
# The fake session user comes from DEV_USER_EMAIL (default kartavya@mosaicwellness.in).
# Never enable in production — anyone hitting the portal becomes "logged in."
DEV_BYPASS_AUTH = os.environ.get("DEV_BYPASS_AUTH", "0") == "1"
DEV_USER_EMAIL = os.environ.get("DEV_USER_EMAIL", "kartavya@mosaicwellness.in")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or (
    os.urandom(32).hex() if DEV_BYPASS_AUTH else "dev-only-not-for-production"
)
if not DEV_BYPASS_AUTH:
    init_oauth(app)
else:
    log.warning("DEV_BYPASS_AUTH=1 — OAuth disabled, all requests treated as %s", DEV_USER_EMAIL)


@app.before_request
def _inject_dev_user():
    """When DEV_BYPASS_AUTH is on, populate session['user'] for every request
    so login_required passes without redirecting. Allows ?as=<email> override
    to test per-POC behavior (e.g. ?as=trupti@mosaicwellness.in)."""
    if not DEV_BYPASS_AUTH:
        return
    requested_email = request.args.get("as", "").strip().lower()
    effective_email = requested_email if requested_email else DEV_USER_EMAIL
    session["user"] = {
        "email": effective_email,
        "name": effective_email.split("@")[0],
        "picture": None,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _poc_slug(email: str) -> str:
    """Extract POC dir slug from email (local-part of @mosaicwellness.in)."""
    return (email or "").split("@")[0].lower() or "unknown"


def _deliverable_dir(poc_email: str, task_id: str) -> Path:
    return DELIVERABLES_ROOT / _poc_slug(poc_email) / "deliverables" / task_id


def _start_task(*, kind: str, intent: str, template_path: Path | None, template_filename: str | None):
    """Common path for /upload and /ask: capture + spawn background task."""
    user = session["user"]
    poc_email = user["email"]
    task_id = uuid.uuid4().hex[:16]

    deliverable_dir = _deliverable_dir(poc_email, task_id)
    deliverable_dir.mkdir(parents=True, exist_ok=True)

    cand_path = capture_request(
        candidates_dir=CANDIDATES_DIR,
        task_id=task_id,
        poc_email=poc_email,
        kind=kind,
        intent=intent,
        template_filename=template_filename,
    )

    result_url = url_for("result", task_id=task_id, _external=True)
    run_task_in_background(
        task_id=task_id,
        poc_email=poc_email,
        kind=kind,
        intent=intent,
        template_path=template_path,
        deliverable_dir=deliverable_dir,
        candidate_path=cand_path,
        result_url=result_url,
        timeout=YUDHI_TIMEOUT,
        claude_bin=CLAUDE_BIN,
    )
    return task_id


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------


@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", user=session["user"])


@app.route("/login")
def login():
    if DEV_BYPASS_AUTH:
        return redirect(url_for("home"))
    return render_template("login.html", allowed_domain=allowed_domain())


@app.route("/auth/google")
def auth_google():
    redirect_uri = url_for("auth_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/callback")
def auth_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        log.warning("oauth_callback_error error=%s", e)
        return f"OAuth error: {e}", 400
    user_info = token.get("userinfo") or oauth.google.parse_id_token(token, None)
    ok, err = verify_and_login(user_info)
    if not ok:
        log.warning("oauth_callback_denied email=%s reason=%s",
                    (user_info or {}).get("email", "?"), err)
        session.clear()
        return f"Access denied: {err}", 403
    log.info("oauth_login_success email=%s", session["user"]["email"])
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload.html", user=session["user"])

    f = request.files.get("template")
    instructions = (request.form.get("instructions") or "").strip()
    if not f or not f.filename or not instructions:
        return "Both a template file and instructions are required.", 400

    user = session["user"]
    task_id = uuid.uuid4().hex[:16]
    deliverable_dir = _deliverable_dir(user["email"], task_id)
    deliverable_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "template" + Path(f.filename).suffix.lower()
    template_path = deliverable_dir / safe_name
    f.save(str(template_path))
    log.info("upload_received task_id=%s poc=%s file=%s size=%d",
             task_id, user["email"], f.filename, template_path.stat().st_size)

    cand_path = capture_request(
        candidates_dir=CANDIDATES_DIR,
        task_id=task_id,
        poc_email=user["email"],
        kind="upload",
        intent=instructions,
        template_filename=f.filename,
    )
    result_url = url_for("result", task_id=task_id, _external=True)
    run_task_in_background(
        task_id=task_id,
        poc_email=user["email"],
        kind="upload",
        intent=instructions,
        template_path=template_path,
        deliverable_dir=deliverable_dir,
        candidate_path=cand_path,
        result_url=result_url,
        timeout=YUDHI_TIMEOUT,
        claude_bin=CLAUDE_BIN,
    )
    return redirect(url_for("result", task_id=task_id))


@app.route("/ask", methods=["GET", "POST"])
@login_required
def ask():
    if request.method == "GET":
        return render_template("ask.html", user=session["user"])

    question = (request.form.get("question") or "").strip()
    if not question:
        return "Question cannot be empty.", 400

    task_id = _start_task(
        kind="ask",
        intent=question,
        template_path=None,
        template_filename=None,
    )
    log.info("ask_received task_id=%s poc=%s q_len=%d",
             task_id, session["user"]["email"], len(question))
    return redirect(url_for("result", task_id=task_id))


@app.route("/result/<task_id>")
@login_required
def result(task_id):
    return render_template(
        "result.html",
        task_id=task_id,
        user=session["user"],
    )


# ---------------------------------------------------------------------------
# Routes — JSON API (for polling) + downloads
# ---------------------------------------------------------------------------


@app.route("/api/result/<task_id>")
@login_required
def api_result(task_id):
    deliverable_dir = _deliverable_dir(session["user"]["email"], task_id)
    status = get_task_status(deliverable_dir)
    return jsonify(status)


@app.route("/api/result/<task_id>/csv")
@login_required
def download_csv(task_id):
    deliverable_dir = _deliverable_dir(session["user"]["email"], task_id)
    p = deliverable_dir / "result.csv"
    if not p.exists():
        abort(404)
    return send_file(str(p), as_attachment=True, download_name=f"{task_id[:8]}-result.csv")


@app.route("/api/result/<task_id>/md")
@login_required
def view_md(task_id):
    deliverable_dir = _deliverable_dir(session["user"]["email"], task_id)
    p = deliverable_dir / "audit.md"
    if not p.exists():
        abort(404)
    return p.read_text(), 200, {"Content-Type": "text/markdown; charset=utf-8"}


@app.route("/healthz")
def healthz():
    return {
        "ok": True,
        "candidates_dir_exists": CANDIDATES_DIR.is_dir(),
        "deliverables_root_exists": DELIVERABLES_ROOT.is_dir(),
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
