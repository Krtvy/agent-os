# Credentials setup

How to capture and configure the API tokens, keys, and cookies the pipeline needs.

## Where credentials live

| File                       | Tracked?          | What's in it                                           |
| -------------------------- | ----------------- | ------------------------------------------------------ |
| `.credentials.example.yml` | ✅ Yes (template) | Schema with placeholders. Safe to share.               |
| `.credentials.yml`         | ❌ Gitignored     | Your real keys. **Never commit. Never paste in chat.** |

The pipeline scripts read `.credentials.yml` at runtime. If a section is missing or contains `REPLACE_ME` placeholders, scripts fall through to stub mode and log clearly.

## Apify (TikTok video discovery)

Used by `hanuman/scripts/competitor-discovery.sh`.

### Capture

1. Go to https://console.apify.com/account/integrations
2. Copy the API token shown (or create one if blank)
3. Edit `~/projects/observer-test/.credentials.yml`:

```yaml
apify:
  tokens:
    - "apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # your real token
```

4. **For multiple tokens (rotation):** uncomment additional lines and add more.

### Verify

```bash
cd ~/projects/observer-test
bash .claude/agents/hanuman/scripts/competitor-discovery.sh
```

Look for `apify_tokens_available: N` in the output. If `N > 0`, the script will try real Apify calls. If a token is bad or rate-limited, you'll see `HTTP 401/429 ... rotating` and it will try the next one.

### ToS notes

Apify's terms typically prohibit creating multiple accounts to evade per-account resource limits. **Safer alternatives:**

- **One paid Starter plan ($49/mo):** ToS-clean, no rotation gymnastics needed, easy pitch to Mayank
- **One personal free tier:** sufficient for prototyping (~$5/mo in credits); upgrade if scaling

Token rotation in the script is still useful for transient errors even with a single token.

## Gemini (video content analysis — Phase 2)

Used by `arjuna/scripts/video-analyze-batch.sh` once built.

### Capture

1. Go to https://aistudio.google.com/apikey
2. Click "Create API key" → copy
3. Edit `.credentials.yml`:

```yaml
gemini:
  keys:
    - "AIzaSy..." # your real key
```

Free tier: 60 requests per minute. For 25–50 videos/day, a single key suffices. Adding more keys handles transient errors.

### ToS notes

Google's terms allow personal use of the Gemini free tier across reasonable use. Multiple keys from one Google account = fine. Multiple keys from multiple Google accounts = gray area; same flag as Apify.

## Kalodata (creator analytics — separate scout pipeline, not competitor content)

Used by hanuman's per-creator scout procedure (P4–P9). **Not used by the competitor content pipeline.** Documenting here for completeness since you mentioned having access.

### Capture (cookie-based session)

Kalodata doesn't expose a public API at the intern access tier, so we use logged-in browser session cookies.

1. **Open a fresh Chrome incognito window.** Important: use a session that won't get logged out by your normal browsing.
2. Log in at https://www.kalodata.com with your real credentials.
3. Once logged in, navigate to any creator profile page so a real session request fires.
4. Open Chrome DevTools (F12 / Cmd+Option+I).
5. **Network tab** → reload the page → click any request to `kalodata.com`.
6. Right panel → **Headers** → **Request Headers** section.
7. Find and copy:
   - **`Cookie`** header (entire value, very long string)
   - **`User-Agent`** header
8. Paste into `.credentials.yml`:

```yaml
kalodata:
  cookie: "PASTE_FULL_COOKIE_VALUE_HERE"
  user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ..."
```

### Cookie lifetime

Kalodata sessions typically last 7–14 days. When the cookie expires, scripts will get 401 or redirect-to-login. You'll need to:

1. Re-login in a fresh browser
2. Re-capture the cookie + user-agent
3. Update `.credentials.yml`

The pipeline will flag this in the run summary ("Kalodata returned login redirect — cookie likely expired").

### Security notes

- **The cookie IS your login session.** Anyone with it can impersonate you on Kalodata for as long as it's valid.
- **`.credentials.yml` is gitignored**, but verify before each commit: `git status` should never show it.
- **Never paste the cookie value in chat with me** — write it directly into `.credentials.yml` on your machine.
- If you accidentally share the cookie anywhere (chat, screenshot, repo), **invalidate it immediately** by logging out of Kalodata in that browser session. New login forces a fresh cookie.

## What to share with me (and how)

| Item            | How                                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------------------- |
| Apify token(s)  | Paste directly into `.credentials.yml` on your machine. Don't paste into chat. Just tell me "Apify tokens added." |
| Gemini key(s)   | Same. Paste into `.credentials.yml`, tell me "Gemini keys added."                                                 |
| Kalodata cookie | Same. Paste into `.credentials.yml`, tell me "Kalodata cookie added."                                             |
| Any errors      | Paste error messages into chat (no credentials in them; the script redacts tokens to last-4).                     |

The principle: I see code, you see credentials. The credentials live on your disk in a gitignored file. I read the file at runtime via the scripts. They never enter my context.

## Verifying everything is gitignored

Before any commit, run:

```bash
cd ~/projects/observer-test
git status --short | grep -E "credentials|\.env|cookies"
```

This should return **nothing**. If it returns anything, do not commit until you've verified that file isn't supposed to contain secrets.

## Emergency: I accidentally committed a credential

1. **Revoke immediately** — at the source:
   - Apify: https://console.apify.com/account/integrations → delete the token, generate new
   - Gemini: https://aistudio.google.com/apikey → delete the key
   - Kalodata: log out everywhere, change password
2. **Then clean up git history:**

```bash
# If only in the most recent commit, not yet pushed:
git reset --soft HEAD~1
# Edit the file to remove the secret, then re-commit

# If pushed: contact me, we'll use git-filter-repo to rewrite history
```

The first step matters most. Cleaning git history doesn't help if the credential is already in the wrong hands.
