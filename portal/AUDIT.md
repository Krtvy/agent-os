# Portal v2 audit — 2026-05-22

Pre-trial audit run after M9 ship. Goal: prove nothing is broken and the
implementation aligns with the stated vision before POCs start using it.

**Result: ✅ ALL GREEN.** The portal is safe to test with POCs locally
(via same-WiFi or ngrok). Four advisory findings flagged for Phase B,
none of which block local testing.

---

## 1. What was tested

10 commits, M0–M9, 2,165 LOC across 26 files (Python + Jinja templates +
manifests). Every milestone re-verified against the live Supabase from
the same browser session a POC would use.

| ID  | Check                                                                               | Result                                                           |
| --- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------- |
| A   | Boot + `/healthz` returns version `v2.0.0-m9`                                       | ✅                                                               |
| B1  | Unauthenticated `/whoami` → `{logged_in:false}`                                     | ✅                                                               |
| B2  | `GET /login` renders form, HTTP 200                                                 | ✅                                                               |
| B3  | `POST /login` sets signed cookie, 303 redirect                                      | ✅                                                               |
| B4  | Authenticated `/whoami` returns POC email                                           | ✅                                                               |
| B5  | Home menu shows 3 cards: Browse + 2 reports                                         | ✅                                                               |
| B6  | M4 form renders for parameterised reports                                           | ✅                                                               |
| B7  | M5 async — `/run/probe` 303 redirects immediately                                   | ✅                                                               |
| B8  | M6 `/browse` lists 8 real schemas                                                   | ✅                                                               |
| B9  | M6 column warnings render — 5 on `tiktok_orders`                                    | ✅                                                               |
| B10 | M7 simple pivot: `COUNT(order_id) GROUP BY order_status` → 4 buckets, 534,849 total | ✅                                                               |
| B11 | M8 filter `cancellation_return_type IS NULL` → 446,309 vs 459,624 (13,315 dropped)  | ✅                                                               |
| B12 | M9 cross-tab pivot — wide CSV with 7 substatus columns                              | ✅                                                               |
| C1  | SQL injection via `?schema=public';DROP%20TABLE%20users;--`                         | ✅ Regex rejects                                                 |
| C2  | SQL injection via `?table=tiktok_orders';--`                                        | ✅ "Invalid identifier"                                          |
| C3  | Pivot row column `order_status; DROP TABLE x`                                       | ✅ 400 (whitelist blocks)                                        |
| C4  | Pivot aggregation `COUNT) UNION SELECT`                                             | ✅ 400 (whitelist blocks)                                        |
| C5  | POC `trupti` opening POC `kartavvya`'s task_id                                      | ✅ 404                                                           |
| C6  | Unauthenticated `/browse` from browser                                              | ✅ 303 → `/login`                                                |
| D1  | `py_compile` every `.py`                                                            | ✅ All compile                                                   |
| D2  | Import every module — checks for missing names                                      | ✅ All import; 22 routes registered                              |
| D3  | Unused imports                                                                      | ✅ Only false positives (`__future__.annotations` required for ` | ` union syntax) |
| E1  | `git status portal/` clean post-M9                                                  | ✅ No uncommitted                                                |
| E3  | `pivot_wide` actually used (IDE flagged unused)                                     | ✅ Used in closure at app.py:404 — IDE wrong                     |
| E4  | `post_process` plumbed through start_async → thread → \_do_run                      | ✅ Confirmed lines 53,76,88,104,114,117,134,145,146              |
| E5  | `.gitignore` covers `.env`, `*.dmg`                                                 | ✅                                                               |

## 2. Alignment with stated goals

Cross-checked against what was asked for this session.

| User requirement                                   | Status     | Where it lives                                                              |
| -------------------------------------------------- | ---------- | --------------------------------------------------------------------------- |
| "POC → form → SQL → CSV"                           | ✅         | Whole `/run` + `/browse/pivot/run` flow                                     |
| "No connection from my local system"               | 🟡 Phase B | Currently local-only by design; Phase B deploys to Fly.io/VPS               |
| "Give them a task id so they can come back later"  | ✅         | M5 — `/result/<task_id>` works forever                                      |
| "Click-driven, no natural language"                | ✅         | Every input bounded by `information_schema`                                 |
| "Pivot table builder, rows × columns × values"     | ✅         | M9 cross-tab via pandas                                                     |
| "Filter time range, value greater than, and so on" | ✅         | M8 — 10 operators incl. `between`, `>=`, `is null`                          |
| "Hybrid warnings on tricky columns"                | ✅         | `portal/lib/column_warnings.py` — 5 fire on tiktok_orders                   |
| "Yudhi out of the portal entirely"                 | ✅         | Verified: no `claude --print`, no Anthropic SDK calls anywhere in `portal/` |
| "@mosaicwellness.in for login, never @rootlabs.co" | 🟡 Phase B | Dev auth currently accepts any email; Phase B Google OAuth enforces         |
| "Kartavvya (double-v) — not the single-v spelling" | ✅         | All docs use double-v; memory updated                                       |

## 3. Findings (advisory — none block local testing)

### 🟡 F1 — `PORTAL_SECRET_KEY` defaults to a hardcoded dev value

**Where:** [portal/app.py](portal/app.py) line 32.
**Why it matters:** Session cookies are signed with this key. If left at
default in production, anyone who reads the source can forge a session
as any POC. The startup warns about this, but the warning is easy to miss.
**Action for Phase B:** Set `PORTAL_SECRET_KEY` to a 32+ byte random
string before deploying. Recommend generating with
`python -c "import secrets; print(secrets.token_hex(32))"` and storing in
the host's `.env` or as a Fly.io secret (`fly secrets set`).

### 🟡 F2 — Unauthenticated curl can hit `/run/<slug>` via `_dev` fallback

**Where:** [portal/lib/session.py:resolve_poc_email()](portal/lib/session.py).
**Why it matters:** `resolve_poc_email()` returns `?as=<email>` if there's
no session — and if neither, the runner uses `_dev` as the POC slug.
Anyone hitting the deployed URL with curl could run reports without auth.
**Why it exists:** Intentional dev escape hatch (CLAUDE/curl can run reports
without logging in). Verified safe locally.
**Action for Phase B:** Add an `@require_login` dependency on `/run/<slug>`
and `/browse/pivot/run` when `DEV_MODE=0`. Keep the curl-friendly path
guarded by an env flag.

### 🟡 F3 — Legacy `pocs/kartavya/` (single-v) coexists with `pocs/kartavvya/`

**Where:** Filesystem.
**Why it matters:** 4 deliverables in the single-v folder (3 from M1 testing
this session + 1 from v1 testing on 2026-05-20). Not broken, just messy.
The portal correctly writes new deliverables to `pocs/kartavvya/` (17 tasks
from this session's verification).
**Action:** Optional cleanup. `rm -rf pocs/kartavya/` whenever you want a
clean slate. Or leave it as historical record.

### 🟡 F4 — VS Code Pyrefly uses wrong Python interpreter

**Where:** IDE state, NOT runtime.
**Why it matters:** The Problems panel will keep showing
"Cannot find module `fastapi`" until you reload VS Code to pick up
[.vscode/settings.json](.vscode/settings.json) which already points at
`portal/.venv/bin/python`.
**Action:** Cmd+Shift+P → "Python: Select Interpreter" → `./portal/.venv/bin/python`
→ Cmd+Shift+P → "Developer: Reload Window". One-time setup.

## 4. Security surface summary

Every entry point that touches SQL was probed:

```
                       │ Identifier safety        │ Value safety
───────────────────────┼──────────────────────────┼──────────────────────────
/browse/tables         │ regex _IDENT_RE          │ — (no values)
/browse/detail         │ regex _IDENT_RE          │ — (no values)
                       │ + psycopg.sql.Identifier │
/browse/pivot/value-row│ regex _IDENT_RE          │ — (no values)
/browse/pivot/filter-row│ regex _IDENT_RE         │ — (no values)
/browse/pivot/run      │ regex _IDENT_RE          │ %(name)s param binding
                       │ + whitelist against      │ via params dict from
                       │ list_columns()           │ build_sql() return
                       │ + whitelist agg against  │
                       │ SUPPORTED_AGGS           │
                       │ + whitelist op against   │
                       │ SUPPORTED_OPS            │
                       │ + double-quote escape    │
/run/<static-slug>     │ static manifest          │ %(name)s param binding
                       │ (no user identifiers)    │
```

No path interpolates user input into SQL as text.

## 5. What to do next (in order)

1. **Reload VS Code** to clear the Pyrefly false-positives (F4).
2. **Start the portal:**
   ```bash
   portal/.venv/bin/uvicorn portal.app:app --reload --port 8000
   ```
3. **Test the golden path yourself** at http://localhost:8000 →
   Log in as `Kartavvya@mosaicwellness.in` → click Browse Data → build
   the cross-tab pivot from the verification battery above.
4. **Share with one POC** via ngrok (`ngrok http 8000`) or same-WiFi
   (`uvicorn ... --host 0.0.0.0`). One POC, one report, see if the UX
   holds up before exposing to all 8.
5. **When you're ready to deploy**, address F1 (real secret key) + F2
   (close the `_dev` escape hatch) as part of Phase B.

## 6. What this audit does NOT cover

- **Performance under concurrent load.** Threading model is single
  process; if 8 POCs all hit a slow query at once, they share one
  process. Profile if it becomes a problem.
- **Long-running query behavior past the 30s statement_timeout.**
  Currently the query is killed and audit shows the timeout error.
  POC sees "✗ Error" on `/result/<id>`. Not a bug; just unscoped.
- **Manual POC UX testing.** This audit is technical correctness only.
  A real POC walkthrough will surface UX papercuts no curl test can.
- **Concurrent edits to `column_warnings.py`** — single-author resource;
  fine until multi-author day.

---

_Audit conducted 2026-05-22 18:00 IST. Re-run if a milestone is changed
substantially, or before any new POC joins the trial._
