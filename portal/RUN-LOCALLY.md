# Run the portal locally

The portal is local-only until Phase B (deployment). For now, everything runs on `localhost:8000`.

## First-time setup

From the **repo root** (`/Users/mosaic/projects/observer-test`):

```bash
cd portal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

## Every time after that

From **anywhere** (the script CDs itself to the repo root):

```bash
./portal/run.sh
```

That's it. The script echoes the resolved command and execs uvicorn with
`--reload --port 8000`. Open http://localhost:8000/healthz in your browser:

```json
{ "ok": true, "version": "v2.0.0-m9" }
```

### Pass-through args

Anything you append goes straight to uvicorn:

```bash
./portal/run.sh --host 0.0.0.0 --port 8000   # expose on LAN (same-WiFi sharing)
./portal/run.sh --port 9000                  # different port
./portal/run.sh --log-level debug            # verbose logs
```

### If you'd rather invoke uvicorn directly

From the **repo root** (not from inside `portal/`):

```bash
portal/.venv/bin/uvicorn portal.app:app --reload --port 8000
```

The portal uses relative imports, so it has to be launched from the repo root as `portal.app:app`, not from inside `portal/` as `app:app`.

## Try the probe report (M1) + session (M2)

### Browser flow (cookies handled automatically)

1. `http://localhost:8000/login?as=Kartavvya@mosaicwellness.in` → returns `{"logged_in":true, ...}` and sets a session cookie
2. `http://localhost:8000/run/probe` → downloads a CSV; deliverable lands in `pocs/trupti/deliverables/<task_id>/`
3. `http://localhost:8000/whoami` → confirms which POC is in session
4. `http://localhost:8000/logout` → clears

### Curl flow (use a cookie jar)

```bash
JAR=/tmp/portal.cookies

# login
curl -s -c $JAR "http://localhost:8000/login?as=Kartavvya@mosaicwellness.in"

# session-driven run (no ?as= needed)
curl -s -i -b $JAR http://localhost:8000/run/probe | head -12

# inspect / clear
curl -s -b $JAR http://localhost:8000/whoami
curl -s -b $JAR -c $JAR http://localhost:8000/logout
```

The `?as=<email>` query param still works on `/run/<slug>` as a fallback when there's no session — useful for one-off curl tests without logging in.

## Session security

Sessions are signed-cookie based (Starlette `SessionMiddleware` + `itsdangerous`). The signing key is read from `PORTAL_SECRET_KEY`; if unset, a hardcoded dev default is used and a warning is printed. **For Phase B (real deployment) you must set `PORTAL_SECRET_KEY` to a random 32+ byte string.**

## What works at this milestone

| Milestone                           | Status     | What it adds                                                                   |
| ----------------------------------- | ---------- | ------------------------------------------------------------------------------ |
| M0 — Skeleton                       | ✅ shipped | `/healthz`                                                                     |
| M1 — Probe report                   | ✅ shipped | `/run/probe` queries Supabase, returns CSV                                     |
| M2 — Dev auth + session             | ✅ shipped | `/login`, `/logout`, `/whoami` + cookie session                                |
| M3 — Report registry + home menu    | ✅ shipped | `GET /` lists all reports as cards; login/logout via HTML forms                |
| M4 — Inputs, forms, result page     | ✅ shipped | Reports with `inputs[]` get a form; runs land on `/result/<task_id>`           |
| M5 — Async tasks + come-back-later  | ✅ shipped | Runs execute in background; `/result/<id>` polls status; per-POC isolation     |
| M6 — Browse Data (schema → table)   | ✅ shipped | `/browse` lets POCs pick schema → table, see columns + warnings + preview      |
| M7 — Pivot builder (group-by + agg) | ✅ shipped | Inline on browse page — pick rows + aggregations, run, async CSV               |
| M8 — Pivot filters                  | ✅ shipped | WHERE clause; 10 operators incl. IS NULL/BETWEEN/ILIKE; values parameter-bound |
| M9 — True cross-tab pivot           | ✅ shipped | Optional Columns dim, server-side pandas pivot, Excel-style wide CSV           |

## Sharing with a POC for testing (M4+)

- **Same WiFi:** `portal/.venv/bin/uvicorn portal.app:app --host 0.0.0.0 --port 8000`, then share `http://<your-mac-ip>:8000` — `ifconfig | grep "inet "` to find your IP.
- **Anywhere:** `ngrok http 8000` — public URL, tunnels to your Mac. Free tier; URL changes per session.

## A note on port 8000

We use **port 8000** (FastAPI default), not 5000. macOS Monterey+ hijacks port 5000 for AirPlay Receiver — if you ever see `Server: AirTunes/...` in a response, that's AirPlay answering, not your portal. You can disable AirPlay Receiver in System Settings → General → AirDrop & Handoff, but it's simpler to just stay on 8000.

## Stop the portal

`Ctrl+C` in the uvicorn terminal.
