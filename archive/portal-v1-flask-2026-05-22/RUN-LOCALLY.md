# Run the portal locally — zero-cost path

For: you, on this Mac, to test the portal without VPS, OAuth, domains, or any spend.

Already verified working end-to-end on 2026-05-20 (task `87306bdb03784f69` returned real Supabase data in 28.8s).

---

## What you need (all free, all already on this Mac)

| Thing                                                        | Status                                                                                        |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Python 3.12                                                  | ✅ have it                                                                                    |
| `portal/.venv/` (Flask, Authlib, gunicorn, dotenv, requests) | ✅ already installed                                                                          |
| `claude` CLI                                                 | ✅ verified — at `/Users/mosaic/.nvm/versions/node/v24.14.0/bin/claude`                       |
| Anthropic auth (for `claude --print` subprocess)             | ✅ working — your current Claude Code session can spawn `claude --print` and it inherits auth |
| Supabase creds at `_private/daily_reporting/.env`            | ✅ verified — probe returned live timestamp                                                   |
| `portal/.env` for local dev                                  | ✅ written for you with `DEV_BYPASS_AUTH=1`                                                   |

You need **nothing else**. No credit card, no Google Cloud, no domain.

---

## The three commands

From the observer-test repo root:

```bash
# 1. Activate the venv (one time per shell)
source portal/.venv/bin/activate

# 2. Start the portal
flask --app portal.app run --port 5000
```

```bash
# 3. In another terminal — open the portal in your browser
open http://localhost:5000
```

You'll land directly on the home page. No login screen. The OAuth bypass is on (`DEV_BYPASS_AUTH=1` in `portal/.env`).

---

## What you can do once it's running

### Test "ask a question" yourself

1. Click **"Ask a question"**
2. Type a real question: _"Run lib/yudhi-sql.sh --probe and report the result as a single-row CSV."_
3. Click **"Send to Yudhi"**
4. Wait ~30s. The result page polls and shows when done.
5. Download the CSV / view the audit MD.

### Test as a specific POC

Append `?as=<their-email>` to any URL — the bypass uses that as the session user:

```
http://localhost:5000/?as=trupti@mosaicwellness.in
http://localhost:5000/ask?as=shivangi@mosaicwellness.in
```

Deliverables land in `pocs/<their-localpart>/deliverables/`. Pattern candidates get tagged with their email.

### Test "fill a template"

1. Make a tiny CSV with just headers (or a single row) — e.g.:

   ```csv
   creator_username,may_livestream_gmv,top_product
   trupti_creator_01,?,?
   ```

2. Click **"Fill a template"**, upload that CSV.
3. Instructions: _"For each creator_username in column A, fill column B with May 2026 livestream GMV (HGR only) and column C with top product by GMV."_
4. Send to Yudhi. Wait.
5. The filled CSV downloads from the result page.

### Have one POC try it (without putting it on the internet)

Two zero-cost options:

- **Same network:** Run `flask --host 0.0.0.0 --port 5000`. Find your Mac's IP (`ifconfig | grep inet`). Share `http://<your-ip>:5000` — works if you and the POC are on the same WiFi.
- **Tunnel to the internet:** `ngrok http 5000` (free tier — random URL, expires when you stop ngrok). Share the ngrok URL with one POC for a real test.

---

## What's running where

```
http://localhost:5000  →  Flask (portal/.venv gunicorn-replacement)
                            │
                            └─ subprocess: claude --print --agent yudhishthira --allowedTools "..."
                                  │
                                  ├─ lib/yudhi-sql.sh   → live Supabase
                                  ├─ lib/yudhi-fetch.sh → Google Sheets (public)
                                  └─ writes deliverables to:
                                        pocs/<poc>/deliverables/<task_id>/result.csv
                                        pocs/<poc>/deliverables/<task_id>/audit.md

Pattern capture: training/patterns/_candidates/<date>-<poc>-<slug>-<id8>.md
```

---

## What this costs

- **Setup:** $0
- **Each Yudhi task:** $0.01-0.50 in Anthropic API tokens (you're already paying these)
- **Idle:** $0 (just disk + tiny RAM)

---

## When you're ready to put it on a real server

Switch to the production path documented in `portal/README.md` § Deploy to a VPS. The code is the same; you just:

1. Set `DEV_BYPASS_AUTH=0` in `.env` on the VPS
2. Add real `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET`
3. Run `./portal/deploy.sh`

Local dev keeps working — the bypass only activates when `DEV_BYPASS_AUTH=1`.

---

## Troubleshooting

| Symptom                                      | Fix                                                                                                                                                                                                      |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `flask: command not found`                   | Did you activate the venv? `source portal/.venv/bin/activate`                                                                                                                                            |
| Browser shows login screen, not home         | `DEV_BYPASS_AUTH=1` isn't being read. Check `portal/.env` exists and isn't empty. Verify with `grep DEV_BYPASS portal/.env`.                                                                             |
| Task stuck on "running" forever              | Open Flask terminal — look at log lines starting with `portal.task_runner`. If you see `task_start` but never `task_done`, the subprocess is hung; check `~/.claude/projects/*/transcripts/` for errors. |
| Task returns "error" with "claude not found" | `claude` CLI not on PATH. Run `which claude` to verify.                                                                                                                                                  |
| Yudhi refuses tasks ("shell approval gate")  | You're running an older portal/lib/yudhi_invoker.py without `--allowedTools`. Pull the latest version.                                                                                                   |
| Supabase probe fails                         | Check `_private/daily_reporting/.env` exists and has correct DB_HOST/DB_USER/DB_PASSWORD. Run `lib/yudhi-sql.sh --probe` directly to verify outside the portal.                                          |

---

## Stop the portal

Ctrl+C in the flask terminal. Or:

```bash
pkill -f "flask --app portal.app"
```

That's it. Nothing else to clean up. Your `pocs/<poc>/deliverables/` and `training/patterns/_candidates/` keep their files — those are part of the build-as-capture mechanism.
