# Portal security review — 2026-05-25

Comprehensive sweep of every attack surface in `portal/`. Status: ✅
safe for local trial with POCs via ngrok / same-WiFi. 6 advisory findings
for Phase B (deployed) that MUST be addressed before exposing the portal
to the public internet.

---

## 1. Authentication & session

### Current state (M2)

- `/login` accepts ANY email with an `@` in it. No password. No verification.
- Session stored in a signed cookie (`SessionMiddleware` + `itsdangerous`),
  key = `PORTAL_SECRET_KEY` env var or `"dev-only-not-for-production-replace-in-phase-b"` default.
- Same-Site = `lax`. HTTPOnly = true. `https_only=False` in dev.

### Findings

|                 | Phase B requirement                                                                                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-AUTH-1** | Replace `PORTAL_SECRET_KEY` default with `python -c "import secrets; print(secrets.token_hex(32))"`. Forge-able sessions if left at default in production.      |
| 🟡 **F-AUTH-2** | Replace the dev login with Google OAuth restricted to `@mosaicwellness.in`. Currently anyone hitting the URL can type `attacker@example.com` and get a session. |
| 🟡 **F-AUTH-3** | Set `https_only=True` on `SessionMiddleware` once HTTPS is in place. Cookies should not flow over plain HTTP.                                                   |
| 🟡 **F-AUTH-4** | `?as=<email>` query-param dev escape on `/login` and `/run/<slug>`. Locks down behind a `DEV_MODE` env flag in production.                                      |

### Test

```bash
# Confirm session cookie is signed (tampering should invalidate):
curl -i -X POST -d "email=attacker@evil.com" http://localhost:8000/login
# Currently: 303 + valid session. After Phase B: 403 because not @mosaicwellness.in.
```

---

## 2. SQL injection

### Threat model

Every place where user input touches the SQL layer.

### Defenses (all confirmed in code)

#### Identifiers (schema, table, column, agg, op)

- **Regex whitelist** `_IDENT_RE = ^[a-z_][a-z0-9_]{0,62}$` enforced in `portal/app.py` for schema/table on every browse route.
- **list_columns() whitelist** in `portal/lib/pivot.py:validate_plan()` — every row/value/filter column name is matched against the live `information_schema.columns` result for that exact (schema, table). Hallucinated columns from the LLM (M11 design) or from a malicious POST are rejected before the SQL ever runs.
- **Aggregations** matched against `SUPPORTED_AGGS` tuple. **Operators** matched against `SUPPORTED_OPS` dict.
- **Identifier quoting** via `psycopg.sql.Identifier()` for sample queries and via the in-code `_quote_ident()` (double-quote with embedded-quote escape) for the pivot builder.

#### Values (filter values, dates, POC names, report params)

- **psycopg `%(name)s` named-parameter binding everywhere.** No string interpolation of values into SQL.
- POC creator lists bound via Postgres `ANY(%(name)s::text[])` — array binding, no `IN (val1, val2, ...)` text construction.
- `SET statement_timeout = N` uses `int(N)` from env, never user input.

### Probes that should be re-run before any deploy

```bash
# These all returned 400/safe responses in M0–M9:
curl "http://localhost:8000/browse/tables?schema=public';DROP%20TABLE%20users;--"
curl "http://localhost:8000/browse/detail?schema=tiktok_raw_data&table=tiktok_orders';--"
curl -X POST -d "schema=tiktok_raw_data&table=tiktok_orders&rows=order_status%3B%20DROP%20TABLE%20x&value_agg=COUNT&value_col=order_id" http://localhost:8000/browse/pivot/run
```

### Findings

|                |                                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ **F-SQL-1** | No path interpolates user input as raw SQL. Verified by code review of pivot.py, schema.py, runner.py.                                   |
| ✅ **F-SQL-2** | Read-only DB session (`SET TRANSACTION READ ONLY` + 30s/120s statement timeout). Even if injection somehow occurred, no writes possible. |

---

## 3. Per-POC isolation

### What's enforced

- `/result/<task_id>/*` checks that the task_id exists under THE REQUESTING POC's deliverables folder before responding. Cross-POC reads return 404.
- Cache index lives at `pocs/<poc>/cache.json` — never read across POC boundaries.
- POC creator list lookup is whitelist-based; can't be coerced into reading another POC's roster.

### Test

```bash
# Already part of the M5 audit — POC trupti gets 404 on kartavvya's task_id.
```

### Findings

|                |                                                                                      |
| -------------- | ------------------------------------------------------------------------------------ |
| ✅ **F-POC-1** | Per-POC isolation enforced at the route layer + the storage layer. Two-deep defense. |

---

## 4. Filesystem access

### What writes happen

- `pocs/<poc>/deliverables/<task_id>/{result.csv, audit.md, status.json}` — runner output
- `pocs/<poc>/cache.json` — cache index
- `training/patterns/_candidates/*` (M3 design, not active)

### What reads happen

- `reports/<slug>/{manifest.json, query.sql}` — static report config
- `portal/May Sheet PoC.csv` — POC roster
- `_private/daily_reporting/.env` — DB credentials

### Findings

|               |                                                                                                                                                                                                                                                                                                                                                                       |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-FS-1** | task_id paths use `secrets.token_hex(8)` — 64 bits of entropy, unguessable. But the directory join `POCS_ROOT / poc_slug / "deliverables" / task_id` should validate `task_id` matches a hex pattern before path construction. Currently relies on the regex not being bypassed via path traversal in URL. Add a `^[a-f0-9]{16}$` validation in `find_deliverable()`. |
| ✅ **F-FS-2** | `_private/daily_reporting/.env` is gitignored; never committed.                                                                                                                                                                                                                                                                                                       |
| ✅ **F-FS-3** | No user input flows into `open(<path>)` calls. All paths are derived from session POC slug + validated task_id.                                                                                                                                                                                                                                                       |

---

## 5. Rate limiting & DoS

### Current state: NONE.

Anyone with a session can hit `/browse/pivot/run` repeatedly, queue arbitrarily many threads, exhaust the connection pool, or saturate Supabase.

### Findings

|               |                                                                                                                                                                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴 **F-RL-1** | **Critical for Phase B.** Before exposing to the open internet, add rate limiting at the reverse proxy (Caddy / nginx) — e.g. 10 pivot runs/min per IP, 60/hr per session. Threading limit per process: cap concurrent task threads (e.g. 10 max). |
| 🟡 **F-RL-2** | Add a per-POC daily cap on Anthropic API spend when NL-to-pivot ships. Track tokens in `pocs/<poc>/llm_spend.json`.                                                                                                                                |

---

## 6. CSRF (cross-site request forgery)

### Current state

- `SessionMiddleware` uses `same_site="lax"` — protects POST routes from cross-site form posts in modern browsers.
- No CSRF tokens on state-changing routes.

### Findings

|                 |                                                                                                                                                                                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-CSRF-1** | Add CSRF tokens to `POST /login`, `POST /run/<slug>`, `POST /browse/pivot/run` for Phase B. Starlette has `starlette-csrf` middleware that bolts in cleanly. Same-site `lax` mitigates most of the risk but isn't full protection on older browsers. |

---

## 7. Secrets

### Current state

- DB credentials: `_private/daily_reporting/.env` (gitignored)
- Session signing key: env var `PORTAL_SECRET_KEY` (dev default if unset)
- Future Anthropic key: env var `ANTHROPIC_API_KEY` (planned)
- `*.dmg`, `.env`, `_private/`, `.credentials.yml` all gitignored

### Findings

|                |                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| ✅ **F-SEC-1** | No secrets committed to git. `git log -p                                                                                                    | grep -i 'password\|secret\|api_key'` returns no leaks. |
| ✅ **F-SEC-2** | DB connection string never logged. Audit MDs never echo `_poc_creators` (the bound array) — they show the SQL with `%(name)s` placeholders. |

---

## 8. Dependency vulnerabilities

### Current pinned set

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
psycopg[binary]==3.2.3
python-dotenv==1.0.1
itsdangerous==2.2.0
jinja2==3.1.4
python-multipart==0.0.12
pandas==2.2.3
```

### Findings

|                |                                                                                                                                                     |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-DEP-1** | Run `pip-audit -r portal/requirements.txt` monthly. Pinned versions are all current as of 2026-05-25 but vulnerabilities are discovered constantly. |
| 🟡 **F-DEP-2** | Set up Dependabot or Renovate on the repo to surface PRs when pins go stale.                                                                        |

---

## 9. Audit trail

### What's logged

- Every report run → `pocs/<poc>/deliverables/<task_id>/audit.md` (POC, report slug, params, status, query SQL, timings, errors)
- Cache index logs `cached_at` per query hash
- Server logs (uvicorn stdout) capture HTTP status per request

### What's NOT logged

- ❌ Login events (success/failure)
- ❌ Cache hits vs misses
- ❌ Cross-POC 404 attempts (potential probe activity)

### Findings

|                |                                                                                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-LOG-1** | Add a `portal.log` written by the FastAPI middleware that captures login, failed logins, cross-POC 404s, and rate-limit hits. Append-only; rotate weekly. |
| ✅ **F-LOG-2** | Audit MD is on disk per task — survives restarts, queryable via filesystem.                                                                               |

---

## 10. Data exposure

### What's in the response

- CSV downloads contain whatever the SQL returned. Currently this is all public TikTok handles, public order metadata, public sales totals.
- No PII fields in scope (no customer names, emails, addresses in any of the queries we've built).

### Findings

|                 |                                                                                                                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 **F-DATA-1** | If a future report queries `customer_*` fields (e.g. for Yadu's retention request M0/M1/M2/M3), confirm whether customer_id is PII. If yes, scope it down or hash it before returning. |
| ✅ **F-DATA-2** | No SSN, no card numbers, no auth tokens have ever been queried.                                                                                                                        |

---

## Summary scorecard

| Category                | Status                  | Critical for Phase B?  |
| ----------------------- | ----------------------- | ---------------------- |
| SQL injection           | ✅ Safe by construction | —                      |
| Identifier injection    | ✅ Whitelist + quoting  | —                      |
| Cross-POC isolation     | ✅ Two-deep defense     | —                      |
| Secrets management      | ✅ gitignored           | —                      |
| Audit trail (data)      | ✅ on disk              | —                      |
| Authentication          | 🟡 Dev mode only        | **F-AUTH-1, F-AUTH-2** |
| Session signing         | 🟡 Default key in dev   | **F-AUTH-1**           |
| HTTPS                   | ❌ Localhost only       | **F-AUTH-3**           |
| Rate limiting           | ❌ None                 | **F-RL-1**             |
| CSRF tokens             | 🟡 SameSite-lax only    | **F-CSRF-1**           |
| Dependency audit        | 🟡 Manual               | F-DEP-1                |
| Audit logging           | 🟡 Data-side only       | F-LOG-1                |
| task_id path validation | 🟡 Implicit             | **F-FS-1**             |

## Phase B pre-deploy checklist (when you're ready to go live)

In order of must-do first:

1. ☐ **F-AUTH-1**: Set `PORTAL_SECRET_KEY` to a real 32-byte secret on the host.
2. ☐ **F-AUTH-2**: Replace `/login` form with Google OAuth limited to `@mosaicwellness.in`.
3. ☐ **F-AUTH-3**: `https_only=True` on SessionMiddleware once Caddy is in place.
4. ☐ **F-AUTH-4**: Gate `?as=` dev escape behind `DEV_MODE=0`.
5. ☐ **F-RL-1**: Add rate limit at Caddy (10 req/min) + cap in-process thread count.
6. ☐ **F-CSRF-1**: Install `starlette-csrf`; add to all POST routes.
7. ☐ **F-FS-1**: Add `^[a-f0-9]{16}$` validator on every `task_id` route param.
8. ☐ **F-LOG-1**: Wire structured logging for auth events + cross-POC probes.
9. ☐ **F-DEP-1**: Run `pip-audit`; address any high/critical CVEs.

When all 9 are checked, the portal is safe to deploy to a public URL.

---

_Living doc — update after each Phase B step and re-run probes after every
non-trivial pivot/builder change._
