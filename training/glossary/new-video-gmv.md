# New Video GMV — Definition

**Source:** Kartavya, 2026-05-13 02:57 IST.

## The business definition

> **New Video GMV is the money a video earned in the same month it was posted.**

It's the slice of total GMV that comes from videos posted **within the current reporting month**. Sales from older videos (posted in prior months, still generating revenue) don't count — those land in `Overall GMV` only.

## The mechanical implementation

The current implementation lives in `gmv_data.New Video?` + `Main!D` of the May workbook. Four layers stacked:

1. **`Video Data` sheet** — the monthly cohort. Contains the `content_id`s of every video posted in the current reporting month. ~2,852 entries for May 2026. Two columns: `Video link` (TikTok URL), `Content ID`.
2. **`gmv_data.New Video?` column** — computed in-sheet via:
   ```
   =MAP(E2:E, LAMBDA(row_val,
     IF(row_val="", "",
       IF(ISNA(VLOOKUP(row_val, 'Video Data'!B:B, 1, 0)), "", "Yes")
     )
   ))
   ```
   For each sale row, checks if its `content_id` appears in `Video Data!B`. If yes → "Yes". If not → blank.
3. **`Main!D (New Video GMV)` formula** — per creator:
   ```
   =SUMIFS( gmv_data!H:H,
            gmv_data!B:B,  <Username>,
            gmv_data!C:C,  "hgr",
            gmv_data!I:I,  "Yes" )
   ```
   Sums the gmv of all sales by this creator where product = hgr AND the video was posted this month.
4. **Empirical verification** — zero-delta reconciliation across all 91 creators. Scope A (hgr only): 59 unique content_ids, $5,693.47 total. Scope B (all products): 124 unique content_ids, $9,414.67 total.

## What this means in practice

- **A creator can have $0 New Video GMV but $1,000 Overall GMV** — they're still earning, but not from new content. (Most creators in May had this pattern — 89 of 91.)
- **A creator can have New Video GMV ≈ Overall GMV** — they're driven mostly by new content (only `jrzjales` had this pattern in May at $605.02 / $2,761.73 = 22%).
- **New Video GMV ≤ Overall GMV always** — it's a strict subset.

## Implication for future months

The `Video Data` registry is a **monthly cohort**, not a permanent list:

- In May → Video Data contains May-posted content_ids
- In June → Video Data should contain June-posted content_ids
- A video that was "new" in May becomes "not new" in June

This means **the registry must be refreshed each month** for the calculation to remain meaningful. How that refresh happens (manual? automated from a video-tracking system? IMPORTRANGE from elsewhere?) isn't visible from the workbook export — verify with the sheet owner.

## Why two product scopes matter

`Main!D` filters to `product = "hgr"` only. The same business logic applied across all products gives a broader view:

| Scope                  | Filter                       | May totals                  |
| ---------------------- | ---------------------------- | --------------------------- |
| Scope A (matches Main) | product=hgr · New Video?=Yes | 59 content_ids · $5,693.47  |
| Scope B (all products) | New Video?=Yes only          | 124 content_ids · $9,414.67 |

If a future task says "new video GMV," default to **Scope A** (matches Main) unless explicitly told otherwise.

## Anti-hallucination discipline

When citing this definition in a deliverable:

- ✓ Cite this glossary entry: "per `training/glossary/new-video-gmv.md`"
- ✓ Cite the formula playbook entry for SUMIFS: `_audit/2026-05-12_sheets-formula-playbook.md` § SUMIFS
- ✓ Reconciliation numbers ($5,693.47 / $9,414.67) are anchors — re-derive don't reuse if the data refreshes
- ✗ Don't extrapolate "new video" to mean something else (e.g., "first video by a new creator" or "video tagged manually as new"). The definition is strictly: **posted in the current reporting month, earning in that same month**.

## Provenance

- Definition stated by Kartavya: 2026-05-13 02:57 IST
- Mechanical implementation reverse-engineered + verified empirically: `_audit/2026-05-12_yudhishthira-sheets-fluency.md` and follow-up deliverables
- Cross-validation that gmv_data[New Video?=Yes] rows == gmv_data[content_id IN Video Data] rows: confirmed identical (178 rows, $9,414.67 either way)
