# Sheet Calculation Analysis — Audit Trail

**Task:** Reverse-engineer how the values in the Main tab are calculated from the `gmv_data` and `Video Count` source tabs.
**Date:** 2026-05-13
**Analyst:** Yudhishthira (Tier-0 Data Analyst)
**Source sheet (user-confirmed copy):** https://docs.google.com/spreadsheets/d/1JicU6fbUiYAFnwzp_iV8miOXdGvWihQ3coiic7sSiWM/edit?usp=sharing
**Local XLSX path (pre-fetched by main thread):** `/tmp/yudhi-workbook.xlsx`
**Engine:** openpyxl (pandas ExcelFile)

---

## P0 — Backup Guardrail

User confirmed: "I made a copy." Read-only analysis on the copy. Proceeding.

---

## P1 — Session Bootstrap

- Bhishma (constitution) loaded: `.claude/agents/_meta/conductor/bhishma.md` — confirmed readable.
- Playbook loaded: `.claude/agents/yudhishthira/playbook.md` — no existing entries for this file class; `playbook_state: bootstrap` for this task.
- Memories scanned: no relevant memories for this sheet or task type.
- Formula reference loaded: `_audit/2026-05-12_sheets-formula-playbook.md` — governs any formula discussion (anti-hallucination rules 1–10 apply throughout).
- Playbook §W5 (Cross-Sheet Join) and §G54 (IMPORTRANGE) are relevant context for diagnosing the broken source tabs — cited below.

---

## P2 — INSPECT (Profile Report)

Three tabs found in `/tmp/yudhi-workbook.xlsx`.

### Tab 1: `Main`

| Attribute     | Value                                                                                                                                                                                 |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape         | 93 raw rows × 5 cols (row 0 is blank, row 1 is the header, rows 2–93 are data = **91 data rows**)                                                                                     |
| Columns       | col A: _(blank — all null, float64)_; col B: `Username`; col C: `Number of videos`; col D: `New Video GMV`; col E: `Overall GMV`                                                      |
| dtypes        | col A: float64 (all NaN); Username: str; Number of videos: object; New Video GMV: object; Overall GMV: object                                                                         |
| Null counts   | col A: 91 nulls (100%); Username: 0 nulls; all other cols: 0 nulls                                                                                                                    |
| Unique values | Username: 91 distinct values (all different — no duplicates detected); Number of videos: 1 unique value = `0`; New Video GMV: 1 unique value = `0`; Overall GMV: 1 unique value = `0` |

**Sample rows (rows 2–4):**

| (blank) | Username        | Number of videos | New Video GMV | Overall GMV |
| ------- | --------------- | ---------------- | ------------- | ----------- |
| NaN     | jrzjales        | 0                | 0             | 0           |
| NaN     | princesstori_00 | 0                | 0             | 0           |
| NaN     | mattyyork0      | 0                | 0             | 0           |

**Finding:** Every numeric column (`Number of videos`, `New Video GMV`, `Overall GMV`) contains exactly `0` for all 91 data rows. This is uniform — not sparse zeros, not a few missing rows. Every row without exception.

---

### Tab 2: `gmv_data`

| Attribute   | Value                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| Shape       | 0 data rows × 1 col                                                                                                    |
| Columns     | `#REF!` (the column header itself is a `#REF!` error — the XLSX export serialised the error string as the column name) |
| dtypes      | object                                                                                                                 |
| Null counts | 0 nulls (empty DataFrame)                                                                                              |

**Sample:** Empty — no data rows at all.

**Finding:** The entire tab resolves to a `#REF!` error. In XLSX export, this means the formula in the source cell evaluated to `#REF!` at export time, and all dependent cells returned errors as well.

---

### Tab 3: `Video Count`

| Attribute   | Value                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| Shape       | 0 data rows × 4 cols                                                                                                      |
| Columns     | `#REF!`, `#REF!.1`, `#REF!.2`, `#REF!.3` (pandas de-duplicates repeated error-column names by appending `.1`, `.2`, `.3`) |
| dtypes      | all object                                                                                                                |
| Null counts | all 0 (empty DataFrame)                                                                                                   |

**Sample:** Empty — no data rows.

**Finding:** All four cells in this tab are `#REF!` errors. The `.1`/`.2`/`.3` suffixes are pandas artefacts from de-duplicating four identical `#REF!` column names — the original sheet had four cells each showing `#REF!`.

---

## P3 — UNDERSTAND

### P3.1 — The question

"How are the values in the Main tab's columns (`Number of videos`, `New Video GMV`, `Overall GMV`) calculated from the `gmv_data` and `Video Count` source tabs?"

### P3.2 — The data we have

- **Main tab:** 91 usernames, all numeric columns = 0. Five physical columns; col A is blank (possibly a row-number or formula-helper column). Header row is row 1, not row 0.
- **gmv_data tab:** Structurally empty — single cell is a `#REF!` error.
- **Video Count tab:** Structurally empty — four cells all `#REF!` errors.

### P3.3 — The data we need

To answer the question, we need one or both of:

1. **The actual formula text** in Main's cells C2, D2, E2 (and their range — do they drag down, use `ARRAYFORMULA`, etc.), AND
2. **The actual source data** behind `gmv_data` and `Video Count` — i.e., the external workbooks those tabs were pulling from.

Neither is available in the current copy. The XLSX export captures _values at export time_ and does not preserve formula text. The source tabs contain only error states.

### P3.4 — Gaps

**Gap 1 — Formulas are not visible in XLSX exports.**
CSV/XLSX export captures resolved values (or errors). Formula text lives only in the live Sheets file. To see the formula in cell C2 of Main, the user needs to open the sheet and look at the formula bar, or share the sheet with formula-read access.

**Gap 2 — Source tabs are broken.**
`gmv_data` and `Video Count` both return `#REF!`. This is the canonical symptom of an `IMPORTRANGE` that has lost its authorisation grant. When a sheet is copied, all `IMPORTRANGE` links in the copy lose their permission — the user must click "Allow access" in each broken cell to re-grant. Until they do, every formula in Main that references these tabs gets 0 (likely wrapped in `IFERROR`) or propagates the `#REF!` error.

**Gap 3 — The all-zeros in Main are not real data.**
The uniform `0` across all 91 rows is not "91 creators with zero GMV." It is the result of `IFERROR(<formula referencing broken tab>, 0)` — a common defensive wrapper. The real values are present in the source workbooks; they are simply unreachable from this copy in its current state.

**Gap 4 — "Second column = live GMV" anchor mismatch (surface for user).**
The user stated: _"the value in the second column is the live GMV."_ In the Main tab, the second column from the left is `Username` (a string of creator handles). The columns that contain GMV are `New Video GMV` (col D, the fourth column) and `Overall GMV` (col E, the fifth column). Possible explanations:

- The user is indexing from the first _data_ column (i.e., ignoring the blank col A), making "second" = `Number of videos`, not GMV — still not GMV.
- The user has a different tab or view in mind where the column order is different from what the XLSX exported.
- The user is using "second column" loosely to mean "the GMV column" — referring to the primary numeric metric rather than position.

**This discrepancy cannot be resolved from the XLSX alone.** The user should clarify which column they mean.

**Gap 5 — Blank col A origin unknown.**
Column A (all NaN, float64) may be a row-number or serial column that was empty in the original, or it may be a formula helper column whose values also evaluated to blank/zero. Cannot determine without formula access.

### P3.5 — Task type + deliverable shape

**Task type: `other` — structural / calculation-reverse-engineering task.**

This is not a compute task. There are no values to sum, filter, join, or aggregate — all numeric values in the file are either `0` or `#REF!`. The deliverable is a diagnosis of why the calculation flow cannot be observed from the current copy, and a clear set of next actions to unblock real analysis.

**Deliverable shape: `.md` only.** No `.csv` because there is no valid table to export. The all-zeros Main data and the empty source tabs would produce a misleading or useless CSV.

---

## P3a — Path Decision

**N/A.** No compute path applies. This is a structural-analysis task. Neither the formula path (P5a) nor the pandas path (P5b) produces meaningful output when all values are `0` or `#REF!`. P4, P5, P6 are skipped with explanation.

---

## P4 — DECLARE FILTERS

Skipped — no compute step. Reason: source data is fully unresolvable in the copy's current state.

---

## P5 — COMPUTE

Skipped — same reason. Computing over all-zero data would be audit theater.

---

## P6 — AUDIT

Skipped — no primary number was computed, so no cross-check applies. The honest audit position is stated in P3.4: the data is not there.

---

## P7 — DELIVER

### The diagnosis in plain language

The sheet is a three-tab workbook: a **Main** display tab that shows 91 creator usernames with three calculated columns (`Number of videos`, `New Video GMV`, `Overall GMV`), and two **source tabs** (`gmv_data`, `Video Count`) that are supposed to hold the raw data those columns pull from.

In the live original sheet (before the copy was made), the calculation flow almost certainly looks like this:

1. `gmv_data` and `Video Count` each contain one or more `IMPORTRANGE(external_sheet_url, range)` formulas that pull live data from external workbooks (per Playbook §G54 — `IMPORTRANGE` is Sheets' mechanism for reading from a different spreadsheet entirely). These external workbooks are the real source of truth for GMV and video count data.

2. The Main tab's formula cells (`Number of videos`, `New Video GMV`, `Overall GMV`) then reference these source tabs — likely via `VLOOKUP`, `XLOOKUP`, `QUERY`, or `INDEX/MATCH` on `Username` as the join key — to fetch each creator's values from the imported data.

3. These lookup formulas are almost certainly wrapped in `IFERROR(..., 0)` (per Playbook §C22 — `IFERROR` replaces any error, including `#REF!`, with a fallback). That is why Main shows uniform `0` rather than `#REF!` — the defensive wrapper catches the broken reference and substitutes zero silently.

**Why the copy is broken:** Google Sheets requires explicit authorisation for each `IMPORTRANGE` link. When a sheet is copied, those authorisations do not transfer to the copy — the copy's `IMPORTRANGE` cells immediately show `#REF!` until the user clicks "Allow access" in the broken cell. Because `gmv_data` and `Video Count` are both `#REF!`, every downstream formula in Main that depends on them also fails — or silently returns 0 via `IFERROR`.

**Evidence for this hypothesis:**

| Evidence                                                          | Interpretation                                                                                                                      |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `gmv_data` tab: 0 data rows, column name = `#REF!`                | The root cell of the IMPORTRANGE chain is broken — the error propagated to every cell in the tab, including the header              |
| `Video Count` tab: 0 data rows, 4 columns all `#REF!`             | Same — likely 4 IMPORTRANGE-derived columns, all broken; pandas de-duplicated them as `#REF!`, `#REF!.1`, `#REF!.2`, `#REF!.3`      |
| Main tab: all 91 rows show exactly `0` across all numeric columns | Uniform zeros indicate `IFERROR(..., 0)` wrapping — not genuinely zero values, but silenced errors                                  |
| Username column has 91 unique values, 0 nulls                     | The username list in Main is hardcoded or self-contained — it does not depend on IMPORTRANGE and therefore survived the copy intact |
| Col A in Main is all null                                         | Likely a row-number/helper column whose formula also depended on the source tabs and similarly went blank                           |

**What this means:** The calculation logic exists; it is simply not visible from this copy in its current state. The source external workbooks contain real GMV and video count data. Until the copy's `IMPORTRANGE` links are re-authorised, neither Yudhishthira nor the user can see actual values.

---

### Anchor mismatch — action required from user

**User statement:** "the value in the second column is the live GMV."

**What the export shows:** Column 2 (0-indexed col 1) of Main is `Username`. The GMV columns are `New Video GMV` (col D / position 4) and `Overall GMV` (col E / position 5).

**Request:** Please clarify which column you mean when you say "second column." Options:

- Are you counting from the first non-blank column (ignoring blank col A)? If so, "second" = `Number of videos`, which is still not GMV.
- Are you referring to the live/primary GMV number in the context of a different tab or view?
- Do you mean `Overall GMV` specifically (the last column), and "second" is shorthand for "the main metric"?

The answer matters for any future analysis or formula the user writes against this sheet.

---

### Next actions — how to unblock real analysis

The user has three paths, in order of effort:

**Option A — Re-authorise IMPORTRANGEs in the copy (fastest for live analysis)**

1. Open the copy in Google Sheets.
2. Navigate to the `gmv_data` tab. Click on the cell showing `#REF!`. A tooltip will appear: "You need to connect these sheets." Click "Allow access."
3. Do the same for the `Video Count` tab (four cells, but typically one "Allow access" covers the whole IMPORTRANGE URL).
4. If the external source workbooks are still accessible and public-view-with-link (or shared with the user's account), the data will populate within seconds.
5. Once both source tabs are live, Main's calculated columns will resolve from zero to real values.
6. After the data loads: screenshot or export the live Main tab, and share the formula text from cells C2, D2, E2 (copy the formula bar text, not the value) — Yudhishthira can then document the exact calculation logic.

**Option B — Share the formula text directly (fastest for Yudhishthira to document logic)**

Without opening the copy and re-authorising anything:

1. Open the original (pre-copy) sheet you made this copy from.
2. Click on cell C2 (the first data row under `Number of videos`).
3. Copy the formula bar text. Repeat for D2 (`New Video GMV`) and E2 (`Overall GMV`).
4. Paste those three formula strings into this chat.

With the formula text, Yudhishthira can explain exactly what each column computes, what join key it uses, what external workbook URL it points to, and what the full calculation chain looks like — without needing the data to resolve.

**Option C — Share the source workbooks (if the intern has access)**

If you have access to the external workbooks that `gmv_data` and `Video Count` were importing from:

1. Make them public-view-with-link (or download as CSV/XLSX).
2. Share the URL(s) or upload the files.

Yudhishthira can then ingest the raw source data directly and replicate the calculation logic from scratch in pandas — independent of the formula layer entirely.

---

## Confidence

**Low.** The calculation flow cannot be derived empirically from the current XLSX. All findings in this document are structural (what the data looks like) and inferential (what likely caused the broken state). The IMPORTRANGE hypothesis is high-confidence as a diagnosis — this is the canonical failure mode for Sheets copies, and the evidence (uniform `#REF!` in source tabs, uniform `0` in Main) is consistent with it. But no formula text has been seen, and no actual GMV or video count values have been observed. This audit documents the obstacle, not the answer.

---

## Caveats

1. The XLSX export does not preserve formula text. Structural findings from the XLSX are reliable; formula-level findings are impossible without direct Sheets access.
2. The "second column = live GMV" discrepancy is unresolved — it may reflect a different view, a different indexing convention, or a misstatement. Do not proceed with any downstream analysis until the user clarifies which column holds live GMV.
3. Phase 1 (read-only, no write-back): Yudhishthira cannot modify the sheet, add formulas, or re-authorise IMPORTRANGEs on the user's behalf. All remediation steps above require the user to act in the sheet directly.
4. If the source external workbooks referenced by the IMPORTRANGEs are private or the user's account has lost access to them, Option A above will not resolve the `#REF!` errors even after clicking "Allow access." The user would need to verify that the source workbooks are still accessible.

---

## Files

| File                                                                         | Purpose                                               |
| ---------------------------------------------------------------------------- | ----------------------------------------------------- |
| `/tmp/yudhi-workbook.xlsx`                                                   | XLSX of the full workbook, pre-fetched by main thread |
| `.claude/agents/yudhishthira/deliverables/sheet-calc-analysis_2026-05-13.md` | This document                                         |

No `.csv` deliverable — task type is `other` (structural diagnosis); there is no valid table to export.
