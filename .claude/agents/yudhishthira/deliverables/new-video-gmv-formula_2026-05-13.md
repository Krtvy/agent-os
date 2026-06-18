# New Video GMV — Formula Documentation and Validation

**Task type:** Reconciliation (value-derivation verification)
**File:** `/tmp/yudhi-sheet2.xlsx` (XLSX export of master sheet; read-only)
**Original sheet:** `https://docs.google.com/spreadsheets/d/10tGKGxnnzK4LJD_NPzx0eoYrlL1KK5ybLXgJlPdTQ2k`
**Produced:** 2026-05-13
**Analyst:** Yudhishthira

---

## Anchor-mismatch note

The user initially described the target column as "second column = live GMV." Clarified before computation: the target is **Main!D**, which is the second of the three numeric columns (Number of videos, **New Video GMV**, Overall GMV) — column D in the sheet's A-through-E layout, where column A is blank.

---

## P2 Inspect — tab shapes confirmed

| Tab         | Rows                                     | Columns                                                                                        | Note                                                                   |
| ----------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Main        | 93 raw (91 data rows, 1 blank, 1 header) | 5 (A blank, B Username, C Num Videos, D New Video GMV, E Overall GMV)                          | Matches main-thread report                                             |
| gmv_data    | 4,562                                    | 9 (date, creator, product, content_type, content_id, post_date, traffic_type, gmv, New Video?) | Matches                                                                |
| Video Count | 53,193                                   | 4 (Creator, Videos, Product, Date)                                                             | Main thread reported 53,194; off by 1 (header row counting difference) |

**gmv_data null counts:** `post_date` = 4,562 (entire column null), `New Video?` = 4,384 null / 178 "Yes". All other columns complete.

**Products in gmv_data:** `hgr` (2,489 rows), `alpha` (875), `magashwa` (756), `ppp` (193), `bb` (187), `confidence_duo` (29), `reset_trio` (14), `rl_seamoss` (12), `turmeric` (5), `glow_duo` (2).

---

## P3 Understanding

**P3.1 Question:** How is Main!D (New Video GMV) calculated from gmv_data?

**P3.2 Data available:** Main (91 creators), gmv_data (4,562 rows), Video Count (53,193 rows).

**P3.3 Data needed:** Per-creator sum of `gmv` from gmv_data, filtered to a specific product and to rows where `New Video?` = "Yes".

**P3.4 Key gap:** XLSX export carries values only, not cell formulas. The derivation is reconstructed by finding the filter combination that produces zero delta across all 91 creators.

**P3.5 Task type:** Reconciliation — verifying that a derived column in Main matches its computed value from the source tab.

---

## P4 Declared filters

For the New Video GMV validation pass:

- **Filter 1:** `gmv_data[product] == 'hgr'`
- **Filter 2:** `gmv_data['New Video?'] == 'Yes'`
- **Aggregation:** `SUM(gmv)` grouped by `creator`

For the Overall GMV validation pass:

- **Filter 1:** `gmv_data[product] == 'hgr'`
- **Aggregation:** `SUM(gmv)` grouped by `creator`

**Critical discovery:** Main!D and Main!E are both scoped to a single product — `hgr`. The gmv_data tab contains rows for 10 products total. Main does not aggregate all products; it aggregates `hgr` only. This was not obvious from column headers alone and was surfaced by the reconciliation process.

---

## P5b Compute — validation pass

### Row counts at each filter step (global)

| Step                                         | Rows  |
| -------------------------------------------- | ----- |
| gmv_data total                               | 4,562 |
| After product = 'hgr'                        | 2,489 |
| After product = 'hgr' AND New Video? = 'Yes' | 96    |

### 8-creator validation table

Creators selected to span the range: one non-zero New Video GMV creator (the only one in this dataset), three zero-NV with substantial Overall GMV, one zero-NV with small Overall GMV, and three zero-both.

**New Video GMV (Main!D)**

| Username             | Main!D | Computed sum (hgr, NV=Yes) | Delta |
| -------------------- | ------ | -------------------------- | ----- |
| jrzjales             | 605.02 | 605.02                     | 0.00  |
| mattyyork0           | 0.00   | 0.00                       | 0.00  |
| princesstori_00      | 0.00   | 0.00                       | 0.00  |
| k2sm1th              | 0.00   | 0.00                       | 0.00  |
| chico.shop07         | 0.00   | 0.00                       | 0.00  |
| naturally.me.recipes | 0.00   | 0.00                       | 0.00  |
| jacobien233          | 0.00   | 0.00                       | 0.00  |
| stephanie_ann_05     | 0.00   | 0.00                       | 0.00  |

All 8 deltas = 0.00. Full 91-creator sweep: **0 mismatches** at tolerance 0.01.

**Overall GMV (Main!E) — bonus check**

| Username             | Main!E   | Computed sum (hgr only) | Delta |
| -------------------- | -------- | ----------------------- | ----- |
| jrzjales             | 2,761.73 | 2,761.73                | 0.00  |
| mattyyork0           | 1,694.04 | 1,694.04                | 0.00  |
| princesstori_00      | 1,424.69 | 1,424.69                | 0.00  |
| k2sm1th              | 1,651.37 | 1,651.37                | 0.00  |
| chico.shop07         | 391.46   | 391.46                  | 0.00  |
| naturally.me.recipes | 350.16   | 350.16                  | 0.00  |
| jacobien233          | 0.00     | 0.00                    | 0.00  |
| stephanie_ann_05     | 0.00     | 0.00                    | 0.00  |

All 8 deltas = 0.00. Full 91-creator sweep: **0 mismatches** at tolerance 0.01.

Note on earlier apparent mismatches: the initial naive attempt (sum all gmv per creator, no product filter) produced deltas for 13 creators (e.g. mattyyork0 appeared off by -132.28). Every one of those disappeared once the `product = 'hgr'` filter was applied. The discrepancy rows were `magashwa`, `alpha`, `bb`, `ppp`, etc. — products that appear in gmv_data but not in the Main summary.

---

## P6 Audit — cross-check via different path

**New Video GMV:**

- Path A: groupby creator, filter `product=hgr` AND `New Video?=Yes`, sum gmv per creator, then sum across creators → **5,693.47**
- Path B: global direct sum filtered on `product=hgr` AND `New Video?=Yes` → **5,693.47**
- Difference: **0.000000**

**Overall GMV:**

- Path A: groupby creator, filter `product=hgr`, sum gmv per creator, then sum → **148,425.18**
- Path B: global direct sum filtered on `product=hgr` → **148,425.18**
- Difference: **0.000000**

Both cross-checks pass. The two paths use different aggregation orders; identical results confirm no groupby artifact or floating-point accumulation issue.

---

## P7 Deliverable — verified formulas

### Main!D (New Video GMV) — three formula forms

**Plain English:**
Sum the `gmv` column in the gmv_data tab for all rows where `product` = "hgr" AND `New Video?` = "Yes" AND `creator` = [this row's username].

**SUMIFS form** (Playbook §B.11 — SUMIFS):

```
=SUMIFS(gmv_data!H:H, gmv_data!B:B, B2, gmv_data!C:C, "hgr", gmv_data!I:I, "Yes")
```

- `H:H` = gmv column (column 8 in gmv_data)
- `B:B` = creator column (column 2)
- `C:C` = product column (column 3)
- `I:I` = New Video? column (column 9)
- `B2` = the username cell in the Main row being computed

Locale note: the formula above uses US-locale comma separators. If the sheet is set to a European locale (Settings → General → Locale), replace every `,` with `;`.

**QUERY form** (Playbook §A.6 — QUERY):

```
=IFERROR(
  QUERY(gmv_data!A:I,
    "select sum(H) where B = '"&B2&"' and C = 'hgr' and I = 'Yes' label sum(H) ''",
    1),
  0)
```

QUERY clause order per Playbook §A.6: SELECT → WHERE (no GROUP BY needed for a single-creator sum). The `IFERROR(..., 0)` handles creators with no matching rows (QUERY returns an empty result, not 0).

**Verification status:** SUMIFS form preferred for single-cell use. Both forms produce identical results to the values in Main!D. Validated across all 91 creators, zero deltas.

---

### Main!E (Overall GMV) — three formula forms

**Plain English:**
Sum the `gmv` column in gmv_data for all rows where `product` = "hgr" AND `creator` = [this row's username]. No New Video filter.

**SUMIFS form:**

```
=SUMIFS(gmv_data!H:H, gmv_data!B:B, B2, gmv_data!C:C, "hgr")
```

**QUERY form:**

```
=IFERROR(
  QUERY(gmv_data!A:I,
    "select sum(H) where B = '"&B2&"' and C = 'hgr' label sum(H) ''",
    1),
  0)
```

**Verification status:** Perfect match (0 mismatches across 91 creators).

---

### Main!C (Number of videos) — status: unresolved, flag for follow-up

The Video Count tab (Creator, Videos, Product, Date) was tested as the likely source. Several hypotheses were systematically tested:

| Hypothesis                                              | Match rate (91 creators) |
| ------------------------------------------------------- | ------------------------ |
| SUM(Videos) WHERE Product='HGR' AND Date in May 2–9     | 87/91 = 95.6%            |
| COUNTUNIQUE(content_id) WHERE product='hgr' in gmv_data | 71/91 = 78.0%            |
| SUM(Videos) WHERE Product='HGR' all dates               | 71/91 = 78.0%            |

The best-fitting hypothesis is a SUM of daily video counts from the Video Count tab, filtered to `Product = 'HGR'` (note: capitalized in that tab) and restricted to a recent date window (empirically, the 8-day window May 2–9 inclusive yields 95.6% match). The 4 remaining mismatches (mattyyork0, imjennyfromtheshop, thedadperspective, thefarmers91) each have 1–2 off-by-small discrepancies. This suggests the date window is slightly different from what was tested, or Main!C is sourced from a system external to these three tabs.

**Confidence for Main!C: low.** Cannot produce a zero-mismatch formula from the available data. This is flagged, not guessed. The formula should not be used in production without owner confirmation of the source logic.

---

## Confidence summary

| Column                    | Confidence | Basis                                                                                                                   |
| ------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| Main!D (New Video GMV)    | High       | 0 mismatches across all 91 creators; cross-check via two paths agrees to 0.000000                                       |
| Main!E (Overall GMV)      | High       | 0 mismatches across all 91 creators; cross-check via two paths agrees to 0.000000                                       |
| Main!C (Number of videos) | Low        | Best hypothesis = 95.6% match; 4 creators still unexplained; source logic not fully recoverable from the available tabs |

---

## Caveats

1. **Formula text vs value reconstruction.** Without formula bar access (XLSX export carries values only), these formulas are reconstructed by finding the filter combination that produces zero delta across all 91 creators. The original cell formulas may use `QUERY` instead of `SUMIFS`, or may reference named ranges — the result is the same but the syntax differs.

2. **Product scope.** Main summarizes `hgr` product rows only. This is non-obvious from the column headers. Any future update to Main that changes the product scope will break these formulas silently.

3. **New Video? column sparsity.** 4,384 of 4,562 rows in gmv_data have `New Video? = NaN`. Only 178 rows have "Yes". Of those, 96 are for `product = hgr`. The flag is categorical and binary — the formula checks for equality with the string "Yes", not for non-null.

4. **Locale.** SUMIFS formulas above use US-locale comma separators. Verify sheet locale before installing.

5. **Column positions are by name, not number.** The formulas reference named columns (H = gmv, B = creator, etc.). If columns are reordered, update the column references.

6. **Main!C remains unresolved.** Do not deploy a Number of Videos formula without owner confirmation.

---

## Totals (audit anchors)

| Metric                                     | Value        |
| ------------------------------------------ | ------------ |
| Total New Video GMV (hgr, NV=Yes)          | 5,693.47     |
| Total Overall GMV (hgr)                    | 148,425.18   |
| gmv_data rows where NV=Yes AND product=hgr | 96           |
| Creators with non-zero New Video GMV       | 1 (jrzjales) |
| Creators validated (New Video GMV)         | 91/91        |
| Creators validated (Overall GMV)           | 91/91        |
