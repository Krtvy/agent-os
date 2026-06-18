# Deploying the POC Portal to Fly.io

A 1-week pilot deploy for 8 POCs + ops. Follow top to bottom. ~30 min end-to-end.

## 0. Install the Fly CLI (one time)

```bash
brew install flyctl
fly auth signup        # if you don't have a Fly account
# or
fly auth login
```

A Fly account requires a credit card on file. Smallest VM + 1 GB volume + Mumbai
region runs about **$3–6 / month**. Tear-down later: `fly apps destroy <name>`.

## 1. Confirm what you'll be deploying

From the repo root:

```bash
ls portal/Dockerfile portal/fly.toml portal/.dockerignore
cat portal/fly.toml | grep -E "^app|^primary_region"
```

Should print `app = "rootlabs-portal"` and `primary_region = "bom"`. If the
app name is already taken on Fly (it's a global namespace), edit `app = "..."`
in `portal/fly.toml` to something like `mw-rootlabs-portal` before continuing.

## 2. Create the app + volume

```bash
cd portal

# Creates the app shell on Fly under the name in fly.toml.
fly apps create $(grep '^app' fly.toml | cut -d'"' -f2)

# Persistent storage for portal_users.json + trackers_data/ + poc_targets.json.
# 1 GB is way more than the pilot needs; sized for headroom.
fly volumes create portal_data --region bom --size 1
```

## 3. Set secrets (DB creds + cookie key + HTTPS flag)

Pull the same values from `_private/daily_reporting/.env`:

```bash
DB_HOST=$(grep '^DB_HOST=' ../_private/daily_reporting/.env | cut -d'=' -f2-)
DB_PORT=$(grep '^DB_PORT=' ../_private/daily_reporting/.env | cut -d'=' -f2-)
DB_NAME=$(grep '^DB_NAME=' ../_private/daily_reporting/.env | cut -d'=' -f2-)
DB_USER=$(grep '^DB_USER=' ../_private/daily_reporting/.env | cut -d'=' -f2-)
DB_PASSWORD=$(grep '^DB_PASSWORD=' ../_private/daily_reporting/.env | cut -d'=' -f2-)

fly secrets set \
  DB_HOST="$DB_HOST" \
  DB_PORT="$DB_PORT" \
  DB_NAME="$DB_NAME" \
  DB_USER="$DB_USER" \
  DB_PASSWORD="$DB_PASSWORD" \
  PORTAL_SECRET_KEY="$(openssl rand -hex 32)" \
  PORTAL_HTTPS_ONLY=1
```

Verify:

```bash
fly secrets list
```

Should list 7 names (no values shown).

## 4. Deploy

```bash
fly deploy
```

First deploy builds the image (~3-5 min). Subsequent deploys are faster.

When it finishes, `fly status` shows the app URL — e.g.
`https://rootlabs-portal.fly.dev`.

Smoke-test it:

```bash
APP_URL=$(fly status --json | python3 -c 'import json,sys; print("https://" + json.load(sys.stdin)["Hostname"])')
curl -s "$APP_URL/healthz"
```

Expect `ok`.

## 5. Seed the volume with state files

The mounted volume starts empty, so `_private/portal_users.json` (the
whitelist) and the tracker JSON files need to be copied in once.

```bash
fly ssh sftp shell -a $(grep '^app' fly.toml | cut -d'"' -f2)
```

Inside the SFTP shell:

```
put ../_private/portal_users.json /app/_private/portal_users.json
put ../_private/poc_targets.json  /app/_private/poc_targets.json
mkdir /app/_private/trackers_data
put -r ../_private/trackers_data  /app/_private/trackers_data
quit
```

Restart so the app picks up the new files:

```bash
fly apps restart $(grep '^app' fly.toml | cut -d'"' -f2)
```

Verify the whitelist landed:

```bash
fly ssh console -C 'ls -la /app/_private && head -20 /app/_private/portal_users.json'
```

## 6. Smoke-test the auth flow (from your laptop)

Open `https://<your-app>.fly.dev/login` in a fresh incognito window:

1. Enter `kartavvya@mosaicwellness.in` → should land on /signup
2. Pick a password ≥10 chars → should land on /standup with data loaded
3. /logout → log back in with email + password → /standup again
4. Try `randomperson@gmail.com` → expect "Email not authorized"

If any of those fail: `fly logs -a <app>` shows the live container output.

## 7. Share with the POCs

Message to send in the WhatsApp group:

> Hi team — the new POC portal is live at **https://<your-app>.fly.dev**.
>
> Go there → enter your **@mosaicwellness.in** email → you'll be asked to
> **set your own password** on first visit. ≥10 chars, save it somewhere
> safe (no email reset flow yet — ping me if you forget).
>
> Sessions stay open for 30 days. Any issues, screenshot + DM me.

Whitelisted emails (already seeded, just visit the URL):

```
trupti@mosaicwellness.in
khushi@mosaicwellness.in
manini@mosaicwellness.in
rachit@mosaicwellness.in
vansh@mosaicwellness.in
chanchal@mosaicwellness.in
shivangi@mosaicwellness.in
saniya@mosaicwellness.in
tanmita@mosaicwellness.in
kartavvya@mosaicwellness.in
```

## Operating it during the pilot

```bash
# Live logs:
fly logs

# Restart the app:
fly apps restart <app>

# Open a shell inside the running container:
fly ssh console

# If someone forgets their password (no reset flow yet — manually clear it):
fly ssh console -C "python3 -c 'from portal.lib import users; d=users._load(); d[\"trupti@mosaicwellness.in\"][\"password_hash\"]=None; users._save(d); print(\"reset\")'"
# Then DM them to revisit the portal and set a new password.

# Tear down at end of pilot:
fly apps destroy <app>          # removes the app
fly volumes destroy portal_data # removes the volume (irrecoverable)
```

## What to watch during the pilot

1. **Cold-start latency.** First request after idle can take 8-12 s while the
   connection pool warms. `min_machines_running = 1` in fly.toml keeps a
   machine warm so this should only happen at app startup. If POCs complain
   about slowness, check `fly logs` for "pool exhausted" or timeouts.

2. **Connection-pool saturation.** Supabase has a tenant-wide cap. With 1
   worker × pool max 10 = 10 connections. If you see "too many connections"
   errors in logs, lower `PORTAL_POOL_MAX` via `fly secrets set PORTAL_POOL_MAX=6`.

3. **Volume disk usage.** Tracker JSON grows with edits. `fly volumes show
portal_data` shows free space. 1 GB is overkill — you won't run out.

4. **Replica recovery conflicts.** Already handled — the SerializationFailure
   handler renders an auto-refresh page if Supabase hiccups. If POCs see it
   often, it's a Supabase-side thing, not the portal.
