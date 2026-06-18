# Rootlabs Data Portal — POC Guide

For: Trupti, Shivangi, Khushi, Vansh, Manini, Chanchal, Rachit, Sanya.

This is the one-pager. Read it once; bookmark the portal URL; you're done.

---

## What this is

A web page where you can ask data questions or get a template filled — **without going through Kartavya every time.**

Type a question like _"how much GMV did my creators do last month?"_ and you get a CSV back. Or upload a spreadsheet template with the columns you want and get it back filled with the right numbers from Supabase.

Behind the scenes, your old friend **Yudhi** (the Mahabharat-named data agent) reads the database, runs the math, audits his own work, and returns two files: the data CSV and a `.md` that explains every filter and step he took.

---

## Getting in

Open: **`https://portal.<your-domain>`** (Kartavya will share the actual URL).

Click **"Sign in with Google"** and pick your `@mosaicwellness.in` account. That's it. No new password. Non-Mosaic Google accounts are blocked.

---

## Two things you can do

### 1. "Ask a question"

Click the **"Ask a question"** card on the home page.

Type your question in plain English. Be specific:

- ✅ _"How much livestream GMV did Trupti's HGR creators do between May 1 and May 15, 2026, broken down by product?"_
- ❌ _"GMV report"_ (Yudhi will ask you to clarify which window, which product, which creators)

Click **"Send to Yudhi"**. You'll land on a result page that spins for 30-90 seconds.

When it's done you get:

- A **Download CSV** button (the data)
- A **View audit MD** button (Yudhi's explanation — every filter, every row count, what he cross-checked)

### 2. "Fill a template"

Click the **"Fill a template"** card.

**Step 1:** Upload a CSV with the column headers you want. Either leave the rows empty or include one example row Yudhi can pattern-match on. Examples:

```
creator_username, may_livestream_gmv, total_orders, top_product
trupti_creator_01, ?, ?, ?
trupti_creator_02, ?, ?, ?
```

**Step 2:** Write instructions in the text box. Be explicit about which columns you want filled and the rules.

- ✅ _"For each creator_username in column A, fill May 2026 livestream GMV (column B), total orders (column C), and the top product by GMV (column D). Use HGR creators only."_
- ❌ _"Fill it"_

Click **"Send to Yudhi"**. Wait 30-90 seconds. Get the filled CSV back.

---

## What happens while you wait

The result page shows a spinning indicator and updates every 2.5 seconds. **You can close the tab and come back to the same URL later** — bookmark it or save it. If email is set up, you'll also get an email when it's done.

Status colours:

- 🟡 **Yellow + spinner** — running, give it a minute
- 🟢 **Green** — done, both files ready
- 🟠 **Amber** — partial (Yudhi finished but only delivered one of CSV/MD; usually because he refused to fabricate something — read the audit)
- 🔴 **Red** — error or timeout (read the stderr box at the bottom)

---

## Why Yudhi sometimes says no

Yudhi is named after the dharmaraja — the king of truth. He won't:

- Compute a number he can't audit
- Apply a filter he can't name
- Silently deduplicate rows
- Make up data when the database is down

If your CSV comes back partial or empty with an audit MD explaining what blocked him, that's working as intended. Either Yudhi needs more info (re-ask with the missing detail), or there's a real data problem (Kartavya to investigate).

---

## When something goes wrong

| Symptom                                  | Try                                                                                                                  |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Login says "Access denied"               | Are you signed in with `@mosaicwellness.in`? Personal Gmail won't work.                                              |
| Result page stuck on "running" >5 min    | Reload it once. If still stuck, ping Kartavya with the task ID (visible at top of page).                             |
| Result is "error" with no useful message | Copy the task ID + the stderr box content to Kartavya.                                                               |
| The CSV is empty / wrong                 | Open the audit MD — Yudhi explains what he did. Often the fix is "your filter was ambiguous, here's what I assumed." |
| The portal is completely down            | Ping Kartavya. He'll check the VPS.                                                                                  |

---

## What Yudhi can see, and what he can't

**He CAN see:**

- Rootlabs Supabase Postgres (read-only). Tables like `tiktok_raw_data.tiktok_orders`, `gmv_data`, creator/product tables.
- Any Google Sheet you've made publicly viewable (just paste the share-link in your instructions).
- The CSV you upload.

**He CANNOT see (yet):**

- Sheets that are auth-walled (Phase 2 — provisioning his own Google account is on the roadmap).
- Slack messages, Notion pages, your local files.
- Anything outside what's in the Supabase database + your uploaded file.

If you need data from a source he can't reach, tell Kartavya — that's how new data sources get added.

---

## What gets remembered

Every request you make gets logged to `training/patterns/_candidates/` (Kartavya can see this, you don't need to think about it). Over time, common shapes of requests become **patterns** that the portal handles faster. So **using the portal a lot** literally makes it better for the whole team.

---

## Questions / it broke / something weird

Ping Kartavya. Include the **task ID** (visible on the result page) — that's how he'll find what went wrong on the back end.

He won't be mad you used it. That's the whole point.
