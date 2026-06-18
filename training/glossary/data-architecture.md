# Data architecture — Supabase → Sheets

**Source:** Kartavya, 2026-05-13.

## How data flows

```
   ┌──────────────────────────┐
   │  Rootlabs internal data  │
   │  (Shopify, TikTok Shop,  │
   │   creator platforms…)    │
   └────────────┬─────────────┘
                │
                ▼
       ┌────────────────┐
       │   Supabase     │  ← backend Postgres database
       │   (canonical   │
       │    store)      │
       └────────┬───────┘
                │
                │  append / sync
                ▼
   ┌──────────────────────────┐
   │   Google Sheets workbook │
   │   (the May tracker)      │
   │                          │
   │   gmv_data, Video Data,  │
   │   Video Count, etc.      │
   └────────────┬─────────────┘
                │
                │  IMPORTRANGE / direct read
                ▼
   ┌──────────────────────────┐
   │  Tabs that POCs consume  │
   │  (Main PoC, HGR, DoD,    │
   │   segment tabs, etc.)    │
   └──────────────────────────┘
```

## Why this matters for Yudhishthira

- **The Sheet is a downstream view, not the source of truth.** Supabase is the source of truth. If a value looks wrong in the Sheet, check Supabase before assuming the Sheet has a calculation bug — the upstream data may simply have been wrong at sync time.
- **Sync cadence matters.** A Sheet read at 10:00 captures whatever Supabase had at the last sync time. The sync mechanism + frequency is currently undocumented (pending).
- **`gmv_data`, `Video Data`, `Video Count`** all come from Supabase. The user explicitly named gmv_data + "others." Treat the source-tier tabs in the workbook as Supabase appends.
- **EUKA tabs are different** — those come from CSV exchanges with the external EUKA platform, not from Supabase. See `euka.md` for details.

## Implication for the eventual portal

The portal (per VISION.md Phase 2) should ultimately read from Supabase directly — not from the Sheet. The Sheet is a human-readable middle layer; the portal can skip it. That said, in Phase 1 the Sheet is still the working surface POCs use, so Yudhishthira works from the Sheet today.

## Pending detail

- **Sync cadence** between Supabase and the Sheet. Daily? Hourly? Real-time? Manual?
- **Which tabs are Supabase-fed vs hand-maintained.** Likely Supabase: `gmv_data`, `Video Data`, `Video Count`. Likely hand-maintained: `Creators Tagging`, `Acquisition`, `Reactivation`, `Paid Deals`, `HGR Sample Delivered`. The segment tabs (`Active`, `Silent`, `Existing`, etc.) — TBD.
- **Schema documentation** in Supabase. If we can read the Supabase schema directly, we'd have the canonical names for every column — useful when the Sheet's column names get fuzzy.
