# May New-Video GMV — Content ID Breakdown

**Task:** Identify every `content_id` that contributed to New Video GMV in May 2026, with per-content_id totals.
**Date:** 2026-05-13
**Analyst:** Yudhishthira (Tier-0 Data Analyst) — authored in-thread by main session after two 529 server overloads on the subagent dispatch. Procedural rigor preserved.
**Source workbook (user-confirmed read-only):** `1NbMW0OTuOr4I6vzNCaFgUcnRn15VPNWAPNxC5uYMBkA` — fetched as XLSX at `/tmp/yudhi-sheet3.xlsx`. **No writes to either Google Sheet.**

---

## P0 — Backup guardrail

User confirmed read-only intent on the source workbook. No writes. Data was accessed via Google's public XLSX export endpoint, which is one-way: it pulls a snapshot to local disk; nothing returns to the live sheet.

## P1 — Session bootstrap

- Bhishma loaded (R1–R23 govern this run).
- Playbook §W3 (Pivot/Aggregation) and §B11 (SUMIFS) apply to the conceptual logic; pandas is used for the actual compute (anti-hallucination rule 1 — pandas-path means the formula playbook governs only the **language we describe** the result in, not the compute itself).
- Memories scanned: `yudhishthira_local_setup.md` confirms `lib/yudhi-py.sh` is the right Python wrapper. Used throughout.

## P2 — INSPECT

| Tab          | Shape     | Relevant columns                                                                                   |
| ------------ | --------- | -------------------------------------------------------------------------------------------------- |
| `gmv_data`   | 4,562 × 9 | date · creator · product · content_type · content_id · post_date · traffic_type · gmv · New Video? |
| `Video Data` | 2,852 × 2 | Video link · Content ID                                                                            |

**Date range:** 2026-05-01 to 2026-05-11 (all rows are May 2026; no extra date filter needed).

## P3 — UNDERSTAND

- **P3.1 — Question:** "Which content_ids contributed to New Video GMV in May, and how much each?"
- **P3.2 — Data we have:** `gmv_data` (sale events) and `Video Data` (registry of new-video content_ids). Already verified that `gmv_data["New Video?"] == "Yes"` rows match exactly the rows whose content_id appears in `Video Data` (178 rows, $9,414.67 either way).
- **P3.3 — Data we need:** Per-content_id aggregation (sum of gmv, event count, dates, traffic types) within the filtered set, plus a join to `Video Data` to attach the TikTok URL for each content_id.
- **P3.4 — Gaps:** None blocking. Two scope options exist (hgr-only vs all-products) because the user's reference document (Main tab) is hgr-only but the broader business view may want all products — both scopes are produced.
- **P3.5 — Task type:** `breakdown` (per-content_id table). Deliverable shape: 2 × CSV + this MD.

## P3a — Path

**Pandas.** Two scopes, multi-column aggregation with creator-integrity check and a left-join to `Video Data`. Comfortably in pandas territory. Formula path would require live Sheets access and isn't needed here.

## P4 — Declared filters

**Scope A (hgr only — matches Main's logic):**

1. `New Video? == "Yes"`
2. `product == "hgr"`
3. Group by `content_id`; aggregate.
4. Sort by `total_gmv` descending.

**Scope B (all products — broader business view):**

1. `New Video? == "Yes"`
2. Group by `content_id`; aggregate.
3. Sort by `total_gmv` descending.

## P5b — Compute

| Step                                | Scope A                     | Scope B        |
| ----------------------------------- | --------------------------- | -------------- |
| `gmv_data` start                    | 4,562 rows                  | 4,562 rows     |
| After `New Video? == "Yes"`         | 178 rows                    | 178 rows       |
| After `product == "hgr"`            | **96 rows**                 | (no filter)    |
| Group by `content_id`               | **59 unique**               | **124 unique** |
| `total_gmv` sum                     | **$5,693.47**               | **$9,414.67**  |
| content_ids with >1 creator         | 0 (clean)                   | 0 (clean)      |
| content_ids missing from Video Data | 0 (every one is registered) | 0              |

Per-content_id columns: `content_id`, `creator`, `product`, `content_type`, `total_gmv`, `sale_event_count`, `first_seen_date`, `last_seen_date`, `traffic_types` (semicolon-joined distinct values), `video_link` (joined from Video Data).

## P6 — Audit (reconciliation)

Three cross-checks, all passed exact:

| Check                                          | Expected                                         | Got                     | Delta   |
| ---------------------------------------------- | ------------------------------------------------ | ----------------------- | ------- |
| Scope A total_gmv sum                          | $5,693.47 (Main!New Video GMV column total)      | **$5,693.47**           | $0.00 ✓ |
| Scope B total_gmv sum                          | $9,414.67 (global gmv_data where New Video?=Yes) | **$9,414.67**           | $0.00 ✓ |
| Scope A distinct content_ids                   | 59                                               | **59**                  | ✓       |
| Scope B distinct content_ids                   | 124                                              | **124**                 | ✓       |
| Creator integrity (one creator per content_id) | 100%                                             | **100%** (0 violations) | ✓       |
| All content_ids registered in Video Data       | 100%                                             | **100%** (0 orphans)    | ✓       |

**Spot-check on top-1 content_id (Scope A):**

- `content_id = 7635465832193183006`, creator = `thehuntervance`
- Claimed total_gmv: $1,319.49
- Manual recomputation: filtered raw rows = 5, raw sum = $1,319.49 ✓
- Delta: $0.00

The reconciliation is exact across every check. Confidence is **high**.

## P7 — Deliver

Two CSVs + this MD:

| File                                                    | Purpose                           | Rows |
| ------------------------------------------------------- | --------------------------------- | ---- |
| `may-new-video-content-ids-hgr_2026-05-13.csv`          | Scope A — hgr-only (matches Main) | 59   |
| `may-new-video-content-ids-all-products_2026-05-13.csv` | Scope B — all products            | 124  |
| `may-new-video-content-ids_2026-05-13.md`               | This audit                        | —    |

### Top 10 — Scope A (hgr only)

| rank | content_id          | creator               | total_gmv | sale_event_count |
| ---: | ------------------- | --------------------- | --------: | ---------------: |
|    1 | 7635465832193183006 | thehuntervance        | $1,319.49 |                5 |
|    2 | 7635481561395105055 | kokep_7               |   $841.92 |                9 |
|    3 | 7638123063879552286 | jrzjales              |   $314.57 |                3 |
|    4 | 7635838416797601037 | trevor.top.picks      |   $226.44 |                2 |
|    5 | 7636967707325386015 | iamvictoriadoss       |   $222.93 |                3 |
|    6 | 7636981078313520398 | everyonesuddenlyvoice |   $161.18 |                1 |
|    7 | 7635811080672906526 | ayejerr\_             |   $159.40 |                5 |
|    8 | 7635728444143258911 | antoninalgriffin      |   $102.56 |                3 |
|    9 | 7636839397572349198 | iamhae                |   $101.21 |                3 |
|   10 | 7635806092223663391 | jrzjales              |    $97.16 |                2 |

**Concentration note.** The top content_id (`thehuntervance`'s video) alone drove **23%** of all hgr new-video GMV in May. The top 3 drove **43%**. The other 56 content_ids split the remaining 57%.

### Top 10 — Scope B (all products)

| rank | content_id          | creator          | product  | total_gmv |
| ---: | ------------------- | ---------------- | -------- | --------: |
|    1 | 7635465832193183006 | thehuntervance   | hgr      | $1,319.49 |
|    2 | 7635481561395105055 | kokep_7          | hgr      |   $841.92 |
|    3 | 7638123063879552286 | jrzjales         | hgr      |   $314.57 |
|    4 | 7638359763654315277 | 100anxietytips   | magashwa |   $255.92 |
|    5 | 7636195016808877343 | joshuazitting    | magashwa |   $237.95 |
|    6 | 7635838416797601037 | trevor.top.picks | hgr      |   $226.44 |
|    7 | 7636967707325386015 | iamvictoriadoss  | hgr      |   $222.93 |
|    8 | 7635811080672906526 | ayejerr\_        | hgr      |   $204.43 |
|    9 | 7636921826211319054 | mommavibes1975   | magashwa |   $173.96 |
|   10 | 7635392637721201934 | jamison904       | magashwa |   $173.17 |

**Product mix in Scope B's 124 content_ids:** hgr dominates the top tier, with magashwa being the second-most-common product. Other products (alpha, ppp, bb, confidence_duo, reset_trio, rl_seamoss, turmeric, glow_duo) contribute smaller amounts.

## Confidence

**High.** Every reconciliation total matches to the cent. The cross-validation that `gmv_data[New Video?=Yes]` rows == `gmv_data[content_id IN Video Data]` rows is exact (same 178 rows, same $9,414.67). Creator integrity is clean (each content_id has exactly one creator). All content_ids are registered in `Video Data` (no orphans). The formula logic from the user (`MAP+LAMBDA+VLOOKUP`) is verified end-to-end against the data.

## Caveats

1. **All May data through May 11 only.** `gmv_data` doesn't yet contain May 12 onward. For a "full May" answer at month-end, re-run this analysis on a refreshed `gmv_data` export.
2. **"New Video?" flag is the cached result of a formula.** If `Video Data` changes between the formula's last evaluation and the export, the cached `New Video?` column may be stale. The cross-validation we ran (which agrees exactly with the live `Video Data` registry as of this export) suggests the formula was up-to-date at export time.
3. **No multi-creator content_ids detected** in this dataset. If a future dataset has a content_id appearing under two creators, the `creator` column in these CSVs would silently take the first one — re-check `creator_uniq` before trusting in that case.
4. **`video_link` is from `Video Data`'s `Video link` column.** For Scope A, every content_id has a TikTok URL attached. For Scope B too. None are missing.
5. **Locale note.** If you re-implement this as a Sheets formula in your own working copy, US locale uses `,` as argument separator; EU locale uses `;`.

## How to re-run for future months

When more May data lands (or when June data arrives):

1. Re-fetch the workbook XLSX from the same URL.
2. Run `lib/yudhi-py.sh /tmp/yudhi-may-content-ids.py` (script at `/tmp/yudhi-may-content-ids.py`).
3. The reconciliation anchors in the script will need updating if the cached `Main!D` total moves. The structural logic (filter → group → aggregate → join) does not change.

## Provenance

Author: Claude Code session (claude-opus-4-7), main-thread in-line execution after two consecutive 529 server overloads on Yudhishthira subagent dispatch (agentIds `a5ca87cc9cbd32063`, `af2f1f61979757180`). Procedural rigor (P0–P7) preserved. Anti-hallucination rules from `_audit/2026-05-12_sheets-formula-playbook.md` applied to the formula descriptions. No formulas were typed into either source sheet.
