# Rootlabs POC Self-Serve Data Portal

Phase 1 of the VISION.md self-serve portal. 8 POCs at Rootlabs (on `@mosaicwellness.in`) log in via Google SSO and either upload a template CSV to be filled or ask a data question in plain English. Behind the portal: Yudhishthira (Claude Code agent, runs locally) hits Supabase + Google Sheets and returns a CSV + audit `.md`.

## Stack

- **Web:** Flask + Authlib (Google OAuth, restricted to `@mosaicwellness.in`)
- **Brain:** Yudhishthira invoked headlessly via `claude --print --agent yudhishthira --allowedTools "..."`
- **Storage:** filesystem — deliverables under `pocs/<poc-slug>/deliverables/<task_id>/`
- **Pattern capture:** auto-logged to `training/patterns/_candidates/` (build-as-capture)
- **UX:** sync spinner + polling fallback + optional email when done
- **Prod:** Docker Compose (Flask + Caddy) on a self-hosted VPS

---

## Run locally (dev)

```bash
# From observer-test root
cd portal
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill values (FLASK_SECRET_KEY, GOOGLE_OAUTH_*, etc.)
cd ..
FLASK_SECRET_KEY=dev portal/.venv/bin/python -m flask --app portal.app run --port 5000
# open http://localhost:5000
```

`/healthz` is unauthenticated; everything else redirects to `/login`.

---

## Deploy to a VPS (Phase 1C)

### Prerequisites you set up once

1. **Rent a VPS.** Hetzner CX22 (~€4.51/mo, EU) or DigitalOcean Basic ($6/mo) is plenty. Ubuntu 22.04+. Install Docker + Docker Compose.
2. **Buy/use a domain.** Pick the portal subdomain — `portal.rootlabs.co` if you own `rootlabs.co`, otherwise `portal.<whatever-you-own>`. Point an A record at the VPS IP.
3. **Google OAuth app.** In [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
   - Create a project, enable "Google+ API" + "OAuth 2.0".
   - OAuth consent screen: External, scope `email profile openid`, **restrict to your Workspace domain** (`mosaicwellness.in`) on the Domains tab so non-Mosaic users can't even see the consent screen.
   - Credentials → OAuth client ID → Web application → Authorized redirect URI: `https://<your-portal-domain>/auth/callback`
   - Save the `client_id` and `client_secret`.
4. **Anthropic API key.** Generate at console.anthropic.com (Yudhi's brain).
5. **Supabase creds.** Your existing `.env` at `_private/daily_reporting/.env` (or wherever) — the wrapper reads from there.

### Files you set up on the VPS once (NOT rsynced)

```bash
# As VPS_USER on the VPS, after first deploy:
sudo mkdir -p /opt/observer-test/portal
sudo chown -R deploy:deploy /opt/observer-test

# Copy .env to /opt/observer-test/portal/.env (from .env.example, filled in)
# Copy _private/ to /opt/observer-test/_private/  (Supabase creds)
```

### Deploy

```bash
# From observer-test repo root, locally:
VPS_HOST=<vps-ip-or-hostname> VPS_USER=deploy ./portal/deploy.sh
```

The script: rsyncs the repo (excluding heavy/sensitive dirs), restarts Docker Compose, polls `/healthz`.

### What's running on the VPS

- **`flask`** container: gunicorn → Flask on port 5000 (internal only)
- **`caddy`** container: ports 80/443 → reverse proxy + Let's Encrypt auto-SSL → flask:5000
- Bind-mount `/repo` → host's `/opt/observer-test/` so Yudhi can read `.claude/agents/`, `lib/`, `training/` and write to `pocs/`, `training/patterns/_candidates/`.

### Verify

```bash
curl https://<your-portal-domain>/healthz
# → {"ok":true,"candidates_dir_exists":true,"deliverables_root_exists":true}
```

Open `https://<your-portal-domain>` in a browser, log in with a `@mosaicwellness.in` Google account. Should land on home. Try `/ask` with a trivial question — expect a result page that polls and resolves in 30-90s.

---

## How a request flows

```
POC browser
  │ POST /ask {question}
  ▼
Flask /ask handler
  ├── generate task_id (uuid)
  ├── capture_request() → training/patterns/_candidates/<date>-<poc>-<slug>-<id8>.md  (pending)
  ├── run_task_in_background() → spawns daemon thread
  └── redirect → /result/<task_id>

Daemon thread:
  ├── status.json: running
  ├── invoke_yudhi() → subprocess `claude --print --agent yudhishthira --allowedTools "..."`
  ├── Yudhi runs his loop: INSPECT → CLASSIFY → DECLARE FILTERS → COMPUTE → AUDIT → DELIVER
  ├── Yudhi writes result.csv + audit.md to pocs/<poc>/deliverables/<task_id>/
  ├── status.json: success | partial | error | timeout
  ├── capture_outcome() → appends to candidate .md
  └── send_completion_email() → optional, skips if no SMTP

Browser polls GET /api/result/<task_id> every 2.5s until done.
On success → download CSV / view audit MD inline.
```

---

## Status

- [x] **Phase 1A** — Yudhi flipped from Hyperagent to local
- [x] **Phase 1B** — Flask app, lib (capture / invoker / auth / task_runner / email), 5 templates, 13 routes
- [x] **Phase 1B verification** — boot, routes, /healthz, /login, capture isolation, live end-to-end Yudhi-via-portal (real Supabase: `1,postgres,rachit_analytics,2026-05-20T00:08:30.870001`)
- [x] **Phase 1C code** — Dockerfile, docker-compose.yml, Caddyfile, deploy.sh, this README
- [ ] **Phase 1C verification** — needs VPS + DNS + Google OAuth (manual setup; see Prerequisites above)
- [ ] **Phase 1D** — POC onboarding + weekly `_candidates/` promotion review

Full plan: `~/.claude/plans/ma-am-the-thing-is-abstract-shore.md`

---

## Troubleshooting

| Symptom                                                                  | Likely cause                                             | Fix                                                                      |
| ------------------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| `/auth/callback` returns "Access denied"                                 | Email not on `@mosaicwellness.in`                        | Confirm the Google account used; check `ALLOWED_EMAIL_DOMAIN` env        |
| Yudhi tasks always return `status: error` with stderr "claude not found" | `claude` CLI not in PATH inside container                | Rebuild image; `Dockerfile` installs `@anthropic-ai/claude-code` via npm |
| Yudhi tasks time out                                                     | Task is genuinely slow, OR Anthropic API is rate-limited | Bump `YUDHI_TIMEOUT_SECONDS` in `.env`; check Anthropic status           |
| `/healthz` returns `candidates_dir_exists: false`                        | Wrong `CANDIDATES_DIR` or volume mount                   | Confirm `REPO_ROOT=/repo` and `/repo` mount exists in container          |
| Tasks succeed but no email                                               | SMTP not configured (intentional default)                | Set `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` in `.env`     |
| Caddy can't get SSL cert                                                 | DNS doesn't resolve to VPS, or port 80/443 blocked       | Check `dig <portal-domain>`, firewall, security group                    |
