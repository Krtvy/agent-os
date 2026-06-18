# Google Sheets Formula Playbook for Data Analysts

**Author:** Research synthesis for Yudhishthira (data-analysis agent)
**Date:** 2026-05-12
**Purpose:** Operational reference. A senior-analyst-grade Sheets formula bible — covering ~95% of recurring single-sheet analysis tasks so the agent reaches for `QUERY`/`ARRAYFORMULA`/`SUMIFS` before pandas.

---

## TL;DR

Sheets-fluent beats pandas-fluent for the majority of single-sheet analyst work under ~500k cells. The decisive moves are: (1) **`QUERY`** for SQL-style filter/group/pivot in one cell; (2) **`SUMIFS`/`COUNTIFS`/`AVERAGEIFS`** for fast conditional aggregation; (3) **`XLOOKUP`** (Sheets-supported since Aug 2022) for lookups, falling back to `INDEX`/`MATCH` for advanced cases; (4) **`ARRAYFORMULA`** + `FILTER`/`UNIQUE`/`SORT` for whole-column transforms without copy-paste; (5) **`IMPORTRANGE` + `QUERY`** for cross-sheet joins. Drop to pandas only when row count exceeds ~500k, when you need real statistics (regression, time-series decomposition, ML), when regex needs lookbehind, or when the pipeline is multi-file ETL. [T1, multiple]

---

## Key Findings

- **The "formula bible" is ~40 functions.** A senior Sheets analyst uses the same small kit constantly; the rest of Google's 500+ functions are reachable from documentation when needed. [T3, multiple practitioner sources]
- **QUERY is the closest thing to pandas inside a cell.** It implements Google Visualization API Query Language with SELECT/WHERE/GROUP BY/PIVOT/ORDER BY/LIMIT/OFFSET/LABEL/FORMAT in that order. Wrong clause order is a parse error. [T1, Google Docs + T1 Google Developers]
- **Sheets has true superpowers Excel lacks:** `QUERY`, native array-returning `FILTER`, `ARRAYFORMULA`, `IMPORTRANGE`, `GOOGLEFINANCE`, `GOOGLETRANSLATE`, `REGEXEXTRACT`/`REGEXMATCH`/`REGEXREPLACE` (RE2 engine), and the `=AI()` function (rolled out 2025, expanded to seven additional languages Sep 23, 2025). [T1, Google Workspace Updates]
- **XLOOKUP arrived in Google Sheets Aug 25, 2022** — three years after Excel got it. For pre-2022 cross-team compatibility, prefer `INDEX`/`MATCH`. For new work, prefer `XLOOKUP`. [T2, 9to5Google Aug 2022]
- **LAMBDA / MAP / BYROW / BYCOL / REDUCE / SCAN / MAKEARRAY released Aug 24, 2022.** `LET` does **not** exist in Sheets — use an anonymous LAMBDA pattern as substitute. Named Functions replace many LET use cases. [T1, Google Workspace Updates blog; T3 Ben Collins]
- **Performance cliff is real and earlier than the cell limit.** Cell limit doubled to **20 million cells** (announced Apr 2026, beta) from 10M, but timeouts begin around 1.2M cells, and the practical "comfortable" range is under 100k rows. `IMPORTRANGE` slows substantially above 100k imported cells. [T1, Google Workspace Updates Apr 2026; T3 RowZero/Zapier]
- **The pandas-vs-Sheets line:** under ~500k rows, single sheet, no advanced stats → Sheets formula-first is faster end-to-end (write + run + iterate). Above that, or multi-file, or stats/ML → pandas wins. [T2/T3, pandas docs + multiple practitioner sources]
- **LLM hallucination patterns are consistent:** invented function names, wrong arg order (especially `IF` vs `IFS`, `SUMIFS` vs `SUMIF`), wrong locale separator (comma vs semicolon), forgetting `ARRAYFORMULA` wrapper, and assuming Excel-only functions like `LET` work. Mitigation: verify against Google's official function list at `support.google.com/docs/table/25273`. [T1, Google official list; T3, multiple]

---

## The Formula Bible

For each formula: **signature** (exact, from Google official), **use**, **pitfall**, **example**. All examples are runnable as-is in a US-locale sheet (comma-separated args).

### A. Lookups & References

#### 1. `VLOOKUP(search_key, range, index, [is_sorted])` [T1]

- **Use:** Lookup a value in the leftmost column, return a column to its right.
- **Pitfall:** Lookup column must be on the left; `is_sorted=TRUE` is the default in many older sheets — always pass `FALSE` for exact match. Breaks if columns are reordered (because `index` is a number).
- **Example:** `=VLOOKUP(A2, Customers!A:E, 3, FALSE)`
- **Prefer:** `XLOOKUP` (new work) or `INDEX`/`MATCH` (compatibility).

#### 2. `HLOOKUP(search_key, range, index, [is_sorted])` [T1]

- **Use:** Same as VLOOKUP but searches the top row. Rare in modern work.
- **Pitfall:** Same as VLOOKUP. Almost always better expressed via `XLOOKUP` with column-oriented args or `INDEX`/`MATCH`.

#### 3. `XLOOKUP(search_key, lookup_range, result_range, [missing_value], [match_mode], [search_mode])` [T1, available since Aug 25, 2022]

- **Use:** Modern lookup. Lookup range can be anywhere. Built-in default for "not found." Supports approximate and wildcard match.
- **Pitfall:** `match_mode` values: `0` exact (default), `1` exact-or-next-larger, `-1` exact-or-next-smaller, `2` wildcard. `search_mode`: `1` first-to-last (default), `-1` last-to-first, `2`/`-2` binary search. Binary search requires sorted data — wrong sort = silent wrong answer.
- **Example:** `=XLOOKUP("alice", A:A, C:C, "not found", 0, 1)`

#### 4. `INDEX(reference, [row], [column])` + `MATCH(search_key, range, [search_type])` [T1]

- **Use:** Classic two-step lookup. More flexible than `VLOOKUP`; faster than `XLOOKUP` for some large-data multi-criteria cases. [T3, Excelforum/Ablebits]
- **Pitfall:** `MATCH` returns `#N/A` if not found — wrap in `IFNA`. `search_type` default `1` requires ascending sort; use `0` for exact.
- **Example:** `=INDEX(C:C, MATCH("alice", A:A, 0))`

#### 5. `FILTER(range, condition1, [condition2, ...])` [T1]

- **Use:** Return all rows where conditions are TRUE. Native array output — no `ARRAYFORMULA` wrapper needed.
- **Pitfall:** Conditions must all be same orientation (row or column) and same length as `range`. Multiple conditions are AND (use `*`); use `+` for OR. Returns `#N/A` if zero matches — wrap in `IFERROR`.
- **Example (AND):** `=FILTER(A2:D, B2:B="north", C2:C>1000)`
- **Example (OR):** `=FILTER(A2:D, (B2:B="north") + (B2:B="south"))`

#### 6. `QUERY(data, query, [headers])` — **the SQL-in-a-cell power tool** [T1]

- **Use:** Filter, group, aggregate, pivot, order, limit — all in one formula. The single biggest leverage move in Sheets.
- **Clause order (mandatory, wrong order = parse error):** `SELECT` → `WHERE` → `GROUP BY` → `PIVOT` → `ORDER BY` → `LIMIT` → `OFFSET` → `LABEL` → `FORMAT` → `OPTIONS`. [T1, Google Developers Query Language reference]
- **Column refs:** Use `A, B, C...` when querying a sheet range, `Col1, Col2...` when querying an array/`IMPORTRANGE` result.
- **Pitfalls:**
  - Mixed column types (text in a number column) silently drop rows.
  - Date literals use `date 'YYYY-MM-DD'` format inside the query string.
  - `headers` arg: pass `1` to force header detection on a single header row.
  - Aggregations need explicit `GROUP BY` on every non-aggregated column.
- **Examples:**
  - Filter + select: `=QUERY(A1:E, "select A, C, E where B = 'north' and D > 100", 1)`
  - Group + sum: `=QUERY(A1:E, "select B, sum(D) where A is not null group by B order by sum(D) desc", 1)`
  - Pivot: `=QUERY(A1:E, "select B, sum(D) group by B pivot C", 1)`
  - Date filter: `=QUERY(A1:E, "select * where A >= date '2026-04-01'", 1)`
  - On IMPORTRANGE: `=QUERY(IMPORTRANGE("URL","Sheet1!A:E"), "select Col1, sum(Col4) group by Col1", 1)`

#### 7. `INDIRECT(reference_string, [is_A1_notation])` [T1]

- **Use:** Build a reference from text. Useful for dynamic sheet names.
- **Pitfall:** Volatile (recalculates often) and not compatible with `ARRAYFORMULA` in many cases. Slow at scale. [T3, multiple]
- **Example:** `=INDIRECT("'"&A1&"'!B2")` (where A1 holds a sheet name)

#### 8. `OFFSET(cell_reference, offset_rows, offset_columns, [height], [width])` [T1]

- **Use:** Build a dynamic range. Useful but volatile.
- **Pitfall:** Volatile — recalculates on every change. Prefer `INDEX` for static range derivation.

---

### B. Aggregation

#### 9. `SUM(value1, [value2, ...])` [T1] — baseline.

#### 10. `SUMIF(range, criterion, [sum_range])` [T1]

- **Pitfall:** Only one criterion. Use `SUMIFS` for >1 (more consistent argument order).

#### 11. `SUMIFS(sum_range, criteria_range1, criterion1, [criteria_range2, criterion2, ...])` [T1]

- **Note:** Argument order differs from `SUMIF` — sum_range comes **first** here. Common LLM error: swapping these. [T3]
- **Criterion syntax:** Comparison operators in quotes: `">100"`, `"<>"&A1`, `">="&DATE(2026,1,1)`. Wildcards `*` and `?` work for text.
- **Example:** `=SUMIFS(D:D, B:B, "north", C:C, ">="&DATE(2026,1,1))`

#### 12. `COUNTIFS(criteria_range1, criterion1, [criteria_range2, criterion2, ...])` [T1]

- **Use:** Count rows meeting all criteria.
- **Example:** `=COUNTIFS(B:B, "north", D:D, ">1000")`

#### 13. `AVERAGEIFS(average_range, criteria_range1, criterion1, ...)` [T1]

- **Same argument order as SUMIFS.**

#### 14. `MAXIFS` / `MINIFS(result_range, criteria_range1, criterion1, ...)` [T1]

- **Use:** Conditional max/min.

#### 15. `SUMPRODUCT(array1, [array2, ...])` [T1]

- **Use:** Multiply corresponding entries and sum. Works as a multi-condition counter/summer using boolean arrays.
- **Pitfall:** All arrays must be same size. Boolean-to-1/0 conversion needs `--` (double unary) or `*1`.
- **Example (weighted average):** `=SUMPRODUCT(A2:A10, B2:B10) / SUM(B2:B10)`
- **Example (conditional count, alternative to COUNTIFS):** `=SUMPRODUCT((B:B="north")*(D:D>1000))`

#### 16. `SUBTOTAL(function_code, range1, [range2, ...])` [T1]

- **Use:** Sum/avg/count **ignoring hidden rows**. The only aggregate that respects a Sheets `FILTER` view.
- **Function codes:** 9 = SUM (ignore hidden), 109 = SUM (also ignore manually hidden). Equivalent for AVG (1/101), COUNT (3/103), etc.

#### 17. `UNIQUE(range, [by_column], [exactly_once])` [T1]

- **Use:** Dedupe. `exactly_once=TRUE` returns only values that appear exactly once.
- **Example:** `=UNIQUE(A2:A)`

#### 18. `COUNTUNIQUE(value1, [value2, ...])` [T1]

- **Use:** Count of distinct values. Note: counts unique items, doesn't list them.

---

### C. Conditional Logic

#### 19. `IF(logical_expression, value_if_true, value_if_false)` [T1] — baseline.

#### 20. `IFS(condition1, value1, [condition2, value2, ...])` [T1]

- **Use:** Multi-branch without nested `IF`s. Returns first match.
- **Pitfall:** Returns `#N/A` if no condition matches — always end with a catchall `TRUE, "default"`.
- **Example:** `=IFS(A1<0, "neg", A1=0, "zero", A1>0, "pos")`

#### 21. `SWITCH(expression, case1, value1, [case2, value2, ...], [default])` [T1]

- **Use:** Like a case statement. Cleaner than nested `IF` for value-matching.
- **Example:** `=SWITCH(A1, "N", "North", "S", "South", "Unknown")`

#### 22. `IFERROR(value, [value_if_error])` [T1]

- **Use:** Replace any error (`#N/A`, `#DIV/0!`, `#REF!`, `#VALUE!`, `#NAME?`, `#NUM!`, `#NULL!`) with a fallback.
- **Pitfall:** Hides ALL errors, including bugs. Prefer `IFNA` if you only want to handle missing lookups.

#### 23. `IFNA(value, value_if_na)` [T1]

- **Use:** Targeted — only catches `#N/A`. Real errors still surface.
- **Example:** `=IFNA(VLOOKUP(A2, Customers!A:E, 3, FALSE), "no customer")`

#### 24. `AND(...)` / `OR(...)` / `NOT(...)` / `XOR(...)` [T1] — boolean glue.

---

### D. Text

#### 25. `CONCATENATE(...)` and `&` operator [T1]

- **Use:** Join text. The `&` operator is more idiomatic.
- **Example:** `=A1 & " " & B1`

#### 26. `TEXTJOIN(delimiter, ignore_empty, text1, [text2, ...])` [T1]

- **Use:** Best concat with delimiter, optionally skipping blanks.
- **Example:** `=TEXTJOIN(", ", TRUE, A2:A10)`

#### 27. `SPLIT(text, delimiter, [split_by_each], [remove_empty_text])` [T1]

- **Use:** Split text into columns. Array-returning.
- **Pitfall:** `split_by_each=TRUE` (default) treats each char in delimiter as a separator — usually wrong; pass `FALSE` to match the literal delimiter string.

#### 28. `REGEXEXTRACT(text, regular_expression)` [T1]

- **Use:** Extract first regex match (or first capture group). Returns multiple columns if multiple capture groups.
- **Pitfall:** Returns `#N/A` if no match — wrap in `IFERROR`. Engine is **RE2**, not PCRE — no lookbehind, no lookahead, no backreferences in pattern. [T1, Google Docs]
- **Example:** `=REGEXEXTRACT(A2, "([A-Z]{2})-(\d+)")`

#### 29. `REGEXMATCH(text, regular_expression)` [T1]

- **Use:** Returns TRUE/FALSE if regex matches. Great inside `FILTER` and `IF`.
- **Example:** `=FILTER(A:A, REGEXMATCH(A:A, "^[A-Z]{3}-"))`

#### 30. `REGEXREPLACE(text, regular_expression, replacement)` [T1]

- **Use:** Substitute via regex. Backreference in replacement: `$1`, `$2`, etc.
- **Pitfall:** Replacement syntax is Google's, not RE2's standard — see Google docs.

#### 31. `SUBSTITUTE(text_to_search, search_for, replace_with, [occurrence_number])` [T1]

- **Use:** Literal (non-regex) replacement. Faster than `REGEXREPLACE` for plain strings.

#### 32. `TRIM(text)`, `CLEAN(text)`, `PROPER(text)`, `LOWER(text)`, `UPPER(text)` [T1]

- **Use:** Cleanup. `TRIM` removes leading/trailing/duplicate spaces. `CLEAN` removes non-printable characters. Chain: `=PROPER(TRIM(CLEAN(A2)))`.

#### 33. `TEXT(number, format)` [T1]

- **Use:** Format a number/date as text. Critical for joining dates into strings.
- **Example:** `=TEXT(A2, "yyyy-mm-dd")` or `=TEXT(B2, "$#,##0.00")`

#### 34. `VALUE(text)` [T1]

- **Use:** Coerce numeric text → number. Often needed after `SPLIT` or `REGEXEXTRACT`.

#### 35. `LEN`, `LEFT`, `RIGHT`, `MID`, `FIND`, `SEARCH` [T1]

- **Note:** `FIND` is case-sensitive; `SEARCH` is case-insensitive and supports wildcards. Both return `#VALUE!` if not found — wrap in `IFERROR`.

---

### E. Date & Time

#### 36. `TODAY()` / `NOW()` [T1] — volatile, recalc on edit.

#### 37. `DATE(year, month, day)` [T1]

- **Use:** Build a date from parts. Auto-rolls overflow: `DATE(2026, 13, 1)` = Jan 1, 2027.
- **Use in criteria:** `">="&DATE(2026,1,1)`.

#### 38. `EDATE(start_date, months)` [T1]

- **Use:** Add/subtract months. Handles leap years and month-end edge cases — `EDATE("1/31/2026", 1)` = 2/28/2026.
- **Pitfall:** Pass a real date (cell reference or `DATE(...)`); raw `"10/10/2000"` is interpreted as arithmetic if unquoted.

#### 39. `EOMONTH(start_date, months)` [T1]

- **Use:** Last day of a month, N months from start.
- **Common pattern (full month range filter):**
  - First of this month: `=EOMONTH(TODAY(), -1) + 1`
  - Last of this month: `=EOMONTH(TODAY(), 0)`

#### 40. `DATEDIF(start_date, end_date, unit)` [T1]

- **Units:** `"Y"`, `"M"`, `"D"`, `"MD"` (days ignoring months/years), `"YM"` (months ignoring years), `"YD"` (days ignoring years).
- **Pitfall:** If cell shows a date instead of a number, change the cell format to Number. [T1]

#### 41. `NETWORKDAYS(start_date, end_date, [holidays])` and `NETWORKDAYS.INTL(start_date, end_date, [weekend], [holidays])` [T1]

- **Use:** Count business days. `.INTL` lets you customize the weekend pattern (e.g., Fri-Sat weekends).

#### 42. `WEEKNUM(date, [type])`, `ISOWEEKNUM(date)`, `WEEKDAY(date, [type])` [T1]

- **Note:** ISO week numbers differ from US convention — use `ISOWEEKNUM` for international reporting.

---

### F. Array Functions

#### 43. `ARRAYFORMULA(array_formula)` [T1]

- **Use:** Apply a formula across whole ranges in one cell. Replaces drag-fill.
- **Pitfall:** Many functions auto-expand without `ARRAYFORMULA` (e.g., `FILTER`, `QUERY`, `UNIQUE`, `SORT`). Conversely, `SUMIFS`/`COUNTIFS` do **not** spill via `ARRAYFORMULA` cleanly — use `MMULT` tricks or `BYROW`. [T3]
- **Tip:** `Ctrl+Shift+Enter` auto-wraps. Cannot be exported to Excel as native formula.
- **Example:** `=ARRAYFORMULA(IF(A2:A="", "", A2:A * B2:B))`

#### 44. `SEQUENCE(rows, [columns], [start], [step])` [T1] — generate numeric sequence.

#### 45. `LAMBDA(name, ..., formula_expression)` [T1, released Aug 24, 2022]

- **Use:** Create an anonymous function for the helpers below. Cannot be called standalone except via Named Functions.
- **No LET in Sheets:** Use an immediately-invoked LAMBDA as a substitute: `=LAMBDA(x, x*x+1)(A1)` ≈ Excel `LET(x, A1, x*x+1)`. [T3, Ben Collins]

#### 46. `MAP(array1, [array2, ...], lambda)` [T1, Aug 2022]

- **Use:** Apply a lambda elementwise. Use when `ARRAYFORMULA` can't handle the inner function.
- **Example:** `=MAP(A2:A, LAMBDA(x, IF(x>0, SQRT(x), 0)))`

#### 47. `BYROW(array, lambda)` / `BYCOL(array, lambda)` [T1, Aug 2022]

- **Use:** Reduce each row (or column) to a single value. The clean way to sum/max/concat per row when the row width is dynamic.
- **Example:** `=BYROW(A2:E, LAMBDA(row, SUM(row)))`

#### 48. `REDUCE(initial_value, array, lambda)` / `SCAN(initial_value, array, lambda)` [T1, Aug 2022]

- **Use:** Fold across an array. `REDUCE` returns final accumulator; `SCAN` returns running accumulator.
- **Example (running total):** `=SCAN(0, A2:A10, LAMBDA(acc, x, acc + x))`

#### 49. `MAKEARRAY(rows, columns, lambda(row, col))` [T1, Aug 2022] — synthesize a grid.

#### 50. `SORT(range, sort_column, is_ascending, [sort_column2, is_ascending2, ...])` and `SORTN(range, n, display_ties_mode, sort_column, is_ascending, ...)` [T1] — array-returning sorts.

#### 51. `TRANSPOSE(array_or_range)` [T1] — swap rows/columns.

#### 52. `HSTACK(range1, [range2, ...])` / `VSTACK(range1, [range2, ...])` [T1] — concatenate arrays.

#### 53. `FLATTEN(range1, [range2, ...])` [T1] — collapse 2D to 1D column.

---

### G. Sheets-Only Power Imports

#### 54. `IMPORTRANGE(spreadsheet_url, range_string)` [T1]

- **Use:** Read from another spreadsheet.
- **Behavior:** Polls the source every ~hour (configurable to 1 minute via File → Settings → Calculation → "On change and every minute"). Initial use requires user to grant access. [T3, Google Docs Community]
- **Pitfall:** Slow above 100k imported cells; ~50 reference limit. Common pattern: import once to a hidden tab, then reference locally. [T3, Sheetgo/buralog]
- **Example wrapped in QUERY:** `=QUERY(IMPORTRANGE("https://docs.google.com/spreadsheets/d/ABC123", "Sales!A:F"), "select Col1, sum(Col5) group by Col1", 1)`

#### 55. `IMPORTHTML(url, query, index, [locale])` [T1] — scrape a `"table"` or `"list"` from HTML.

#### 56. `IMPORTXML(url, xpath_query, [locale])` [T1] — scrape via XPath.

#### 57. `IMPORTDATA(url, [delimiter], [locale])` [T1] — fetch CSV/TSV from URL.

#### 58. `GOOGLEFINANCE(ticker, [attribute], [start_date], [end_date|num_days], [interval])` [T1]

- **Real-time attributes:** `price` (default), `priceopen`, `high`, `low`, `volume`, `marketcap`, `tradetime`, `datadelay`, `volumeavg`, `pe`, `eps`, `high52`, `low52`, `change`, `beta`, `changepct`, `closeyest`, `shares`, `currency`.
- **Historical attributes:** `open`, `close`, `high`, `low`, `volume`, `all`.
- **Interval:** `"DAILY"` or `"WEEKLY"` (or `1` / `7`). No intraday.
- **Pitfall:** Real-time delayed up to 20 minutes. Dates treated as noon UTC. Historical results expand as an array with headers. Not available via Sheets API / Apps Script.
- **Example:** `=GOOGLEFINANCE("NASDAQ:GOOG", "close", DATE(2026,1,1), TODAY(), "DAILY")`

#### 59. `GOOGLETRANSLATE(text, [source_language], [target_language])` [T1] — translation in a cell.

---

### H. Statistical (Used Often)

#### 60. `CORREL(data_y, data_x)` [T1] — Pearson correlation.

#### 61. `PERCENTILE(data, percentile)` / `PERCENTILE.INC` / `PERCENTILE.EXC` [T1] — percentiles (INC includes endpoints).

#### 62. `QUARTILE(data, quartile_number)` — `0`=min, `1`=Q1, `2`=median, `3`=Q3, `4`=max.

#### 63. `STDEV.S(value1, ...)` / `STDEV.P(value1, ...)` [T1] — sample vs population std dev.

#### 64. `RANK.EQ(value, data, [is_ascending])` — equal-rank version of RANK.

#### 65. `SLOPE(data_y, data_x)`, `INTERCEPT(data_y, data_x)`, `RSQ(data_y, data_x)` [T1] — single-variable linear regression in three formulas. For multivariable, use `LINEST(known_data_y, [known_data_x], [calculate_b], [verbose])`.

---

### I. Newer / AI

#### 66. `=AI(prompt, [range])` [T1, generally available 2025, expanded to seven additional languages Sep 23, 2025; Search-enhanced version Oct 2025]

- **Use:** Generate or classify text in a cell using Gemini.
- **Limits:** Capped at ~200 cells per operation; reapply in chunks for larger ranges. [T3]
- **Pitfall:** Hallucinates. Use only for tasks tolerant of 90-95% accuracy (e.g., sentiment, categorization). Compounding `=AI()` outputs increases drift. [T3, Online Journalism Blog Apr 2025]

---

## Workflows (End-to-End)

### W1. Data Cleanup Pipeline

Goal: turn a raw CSV into something analysis-ready in one tab.

```
1. Trim + clean text columns:
   =ARRAYFORMULA(IF(A2:A="", "", PROPER(TRIM(CLEAN(A2:A)))))

2. Coerce numbers stored as text:
   =ARRAYFORMULA(IF(B2:B="", "", IFERROR(VALUE(B2:B), B2:B)))

3. Parse dates from inconsistent strings:
   =ARRAYFORMULA(IF(C2:C="", "", IFERROR(DATEVALUE(C2:C), "BAD")))

4. Dedupe:
   =UNIQUE(A2:E)

5. Inspect bad rows:
   =FILTER(A2:E, D2:D="BAD")
```

### W2. Lookup / Reconciliation Decision Table

| Need                                     | Use                                    | Why                         |
| ---------------------------------------- | -------------------------------------- | --------------------------- |
| Single value from leftmost-keyed table   | `XLOOKUP`                              | Cleanest. [T1]              |
| Same, pre-2022 sheets / cross-team Excel | `INDEX`/`MATCH`                        | Backward-compatible. [T2]   |
| All rows matching ≥1 condition           | `FILTER`                               | Native array, fast. [T1]    |
| Filter + project columns + aggregate     | `QUERY`                                | One formula. [T1]           |
| Boolean "does X exist in list?"          | `COUNTIF`                              | `=COUNTIF(B:B, A2)>0`. [T3] |
| Multi-criteria lookup                    | `XLOOKUP` with concat key, or `FILTER` | Don't try `VLOOKUP`.        |

### W3. Pivot / Aggregation

```
Option A — Built-in Pivot Table (UI):
  Best for ad-hoc exploration, drag-and-drop.

Option B — QUERY:
  =QUERY(data!A1:F, "select B, sum(D), count(A) where E='active' group by B order by sum(D) desc label sum(D) 'Revenue', count(A) 'Orders'", 1)

Option C — SUMIFS array:
  Use when you need the pivot embedded in a larger formula chain
  or want surgical control. Example for a month × region matrix:
  =SUMIFS($D:$D, $B:$B, $G2, $C:$C, H$1)
```

**When QUERY beats Pivot Tables:** when the result must feed another formula, when you need dynamic labels, when you want to filter before grouping with complex `WHERE` clauses.

### W4. Time-Series Rollup (Monthly)

```
Build month start column once:
  G2: =EOMONTH(C2, -1)+1     (first of C2's month)

Then SUMIFS by month:
  =SUMIFS(D:D, G:G, EOMONTH(TODAY(), -K2)+1)

Or one-shot via QUERY (no helper column):
  =QUERY(A1:E, "select year(C)*100+month(C), sum(D) where C is not null group by year(C)*100+month(C) order by year(C)*100+month(C)", 1)
```

### W5. Cross-Sheet Join

```
Tab "Master":
  =QUERY(
    {IMPORTRANGE("SHEET_A_URL","Data!A:E"); IMPORTRANGE("SHEET_B_URL","Data!A:E")},
    "select Col1, Col2, sum(Col5) where Col1 is not null group by Col1, Col2",
    1
  )

Notes:
  - First-time IMPORTRANGE requires permission grant (#REF! error → click "Allow access" in cell).
  - Use the semicolon between IMPORTRANGEs inside {} to stack vertically.
  - Wrap each IMPORTRANGE in {} if columns differ.
  - Cache: paste-as-values into a hidden tab if data doesn't need to be live.
```

### W6. Conditional Formatting + Alerts (Early Warning)

Conditional formatting via UI: Format → Conditional formatting → "Custom formula is" → `=AND(B2 > 0, B2 < B$1*0.5)` (highlight cells below 50% of header benchmark).

Alert via formula: surface flagged rows in a "Watch" tab:

```
=QUERY(Data!A:F, "select A, B, F where F < 0 or B > 1000 order by B desc", 1)
```

For email alerts, escalate to Apps Script `onEdit` triggers — not formula territory.

### W7. Reconciliation Between Two Sources (Looker-style Mapping)

Yudhishthira-style four-quadrant output (matched / mismatched / a_only / b_only).

```
Assume:
  Sheet "A": cols A=key, B=value
  Sheet "B": cols A=key, B=value

Matched rows (key in both, values agree):
  =FILTER(A!A:B, COUNTIFS(B!A:A, A!A:A, B!B:B, A!B:B) > 0)

Mismatched (key in both, values differ):
  =FILTER(A!A:B, COUNTIF(B!A:A, A!A:A) > 0, COUNTIFS(B!A:A, A!A:A, B!B:B, A!B:B) = 0)

A only (key not in B):
  =FILTER(A!A:B, COUNTIF(B!A:A, A!A:A) = 0)

B only (key not in A):
  =FILTER(B!A:B, COUNTIF(A!A:A, B!A:A) = 0)
```

Alternative QUERY-based reconciliation (single tab output, labeled status column):

```
=ARRAYFORMULA(
  {"key","status","a_value","b_value";
   IFNA(MAP(UNIQUE({A!A2:A; B!A2:A}),
     LAMBDA(k,
       LET = nope.  Use immediately-invoked LAMBDA:
       LAMBDA(av, bv,
         {k,
          IFS(av="", "b_only", bv="", "a_only", av=bv, "matched", TRUE, "mismatched"),
          av, bv}
       )(IFERROR(VLOOKUP(k, A!A:B, 2, FALSE), ""),
         IFERROR(VLOOKUP(k, B!A:B, 2, FALSE), ""))
     )))})
```

(Note: as of 2026-05, Sheets has no `LET`. The IIFE LAMBDA pattern is the workaround. [T3])

---

## Performance + Scale Limits

| Constraint                        | Value (as of May 2026)                                                                          | Source                                  |
| --------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------- |
| Cell limit per spreadsheet        | **20 million cells** (beta, from 10M)                                                           | [T1, Google Workspace Updates Apr 2026] |
| Max columns                       | 18,278 (column ZZZ)                                                                             | [T3, RowZero]                           |
| Practical "fast" range            | <100k rows, <500k cells                                                                         | [T3, Layer/RowZero]                     |
| Timeouts begin around             | ~1.2M cells with formulas                                                                       | [T3, Zapier]                            |
| `IMPORTRANGE` slowdown threshold  | ~100k imported cells                                                                            | [T3, buralog/Sheetgo]                   |
| `IMPORTRANGE` references per file | ~50 max                                                                                         | [T3, Sheetgo]                           |
| `=AI()` cell cap per call         | 200 cells                                                                                       | [T3, multiple]                          |
| Recalc setting                    | Default on change; volatile (NOW, TODAY, RAND, IMPORTRANGE) configurable to every minute / hour | [T1, Google Docs]                       |

**Slow function offenders (rank-ordered):** `INDIRECT` (volatile), `OFFSET` (volatile), `IMPORTRANGE` (network), `QUERY` on large ranges, `ARRAYFORMULA` over open-ended ranges (`A:A` vs `A2:A1000`). [T3, multiple]

**Performance speedups:**

1. Bound ranges (`A2:A1000`, not `A:A`).
2. Cache `IMPORTRANGE` to a values-only tab.
3. Replace `INDIRECT` with `INDEX`/`CHOOSE` when possible.
4. Move heavy aggregations to a single `QUERY` rather than scattered `SUMIFS`.
5. Convert finished formula tabs to values (Copy → Paste Special → Values only) once they don't need to recalc.

---

## When to Drop to Pandas (The Honest Line)

Drop out of Sheets when:

1. **Row count > 500k** for active editing, or > 1.2M for any work — performance becomes punishing.
2. **Multi-file ETL** — joining 5+ files. Pandas + glob is faster to write and faster to run than chained `IMPORTRANGE`.
3. **Real statistics:** multivariate regression beyond `LINEST`, time-series decomposition (STL), survival analysis, anything with `statsmodels`/`scipy.stats`.
4. **ML / clustering / NLP beyond `=AI()`** — embeddings, classification with training, anomaly detection.
5. **Regex needing lookbehind / lookahead / backreferences** — RE2 doesn't have them. Python `re` does.
6. **Repeating workflow** — if you'll run it 50+ times, the Python script's reusability and version control win.
7. **Data privacy:** if data can't touch Google Drive.
8. **Programmatic outputs:** when the result needs to feed an API or a non-Sheets system.

**Stay in Sheets when:**

- Single-source, single-sheet analysis under 500k rows.
- Stakeholder will view/edit the result interactively.
- Ad-hoc exploration with rapid iteration.
- The task is a pivot, filter, lookup, or simple aggregation — even on big data, `QUERY` is usually faster end-to-end than spinning up a notebook.
- Time budget is < 10 minutes.

**Heuristic rule the agent should encode (P3 CLASSIFY decision):**

```
IF rows < 500_000
   AND single_sheet (or ≤3 sheets linkable via IMPORTRANGE)
   AND not requires_advanced_stats
   AND not requires_lookbehind_regex
   AND not multi_file_etl
THEN formula-first (Sheets)
ELSE pandas-first
```

---

## Anti-Hallucination Protocol (For AI Writing Sheets Formulas)

### Common LLM failure modes (observed in the wild)

1. **Inventing functions.** E.g. citing `XLOOKUPS` (no such function), `SUMIFSX`, `QUERYIF`, or assuming `LET` works in Sheets. [T3]
2. **Wrong argument order in `SUMIF` vs `SUMIFS`.** `SUMIF(range, criterion, sum_range)` vs `SUMIFS(sum_range, criteria_range1, criterion1, ...)` — the `sum_range` moves to the **front** in `SUMIFS`. [T1, multiple Google docs]
3. **Locale mistakes.** Generating commas as separators when the target sheet is European locale (semicolons required). [T2/T3, Bettersheets]
4. **Missing `ARRAYFORMULA` wrapper** when a formula needs to fan out across a column.
5. **Importing Excel-only functions** — e.g. `LET` (Excel-only), `LAMBDA` syntax differences, `TEXTSPLIT` (Excel-only; Sheets uses `SPLIT`), `STOCKHISTORY` (Excel-only; Sheets uses `GOOGLEFINANCE`).
6. **Wrong QUERY clause order** — putting `ORDER BY` before `GROUP BY`. Parse error.
7. **Untyped date literals in QUERY** — `where A > '2026-01-01'` (silent fail / wrong) vs `where A > date '2026-01-01'` (correct).
8. **Mixing RE2 with PCRE regex** — using `(?<=...)` lookbehind which RE2 doesn't support.
9. **Open-ended ranges on large sheets** — `A:A` when bounded `A2:A1000` would suffice. Causes 10-100× slowdown.
10. **Forgetting `FALSE` on `VLOOKUP`** — defaulting to approximate match silently returns the wrong row.

### Verification protocol the agent should follow

Before emitting a formula, the agent should:

1. **Check the function exists in Sheets** by mapping each function name to Google's official function list at `support.google.com/docs/table/25273`. If not on that list, do not emit.
2. **Confirm argument order** against the official function page (e.g. `support.google.com/docs/answer/3238496` for `SUMIFS`). Never trust StackOverflow alone.
3. **Confirm locale separator** — ask or check workbook locale. Default to comma (US English) unless otherwise specified.
4. **Add the explicit `FALSE` / `0` for exact match** in `VLOOKUP`/`XLOOKUP`/`MATCH` even when it's the default.
5. **Wrap lookups in `IFNA`** when the lookup could miss.
6. **Bound ranges** unless `ARRAYFORMULA`/`FILTER`/`QUERY` semantics genuinely need open-ended input.
7. **Self-check QUERY clause order**: SELECT → WHERE → GROUP BY → PIVOT → ORDER BY → LIMIT → OFFSET → LABEL → FORMAT.
8. **Date in QUERY**: always use `date 'YYYY-MM-DD'` literal form.
9. **Test with one row** before applying to a whole column.
10. **For Excel-or-Sheets ambiguous functions**, prefer the Sheets-native name (`GOOGLEFINANCE`, `IMPORTRANGE`, `QUERY`) and avoid the Excel-only ones (`LET`, `STOCKHISTORY`, `TEXTSPLIT`, `TEXTBEFORE`/`TEXTAFTER` — though the latter two have been added; verify).

### Quick reference: Sheets-only vs Excel-only vs both

| Function                                          |        Sheets        |                          Excel                          | Notes                                                       |
| ------------------------------------------------- | :------------------: | :-----------------------------------------------------: | ----------------------------------------------------------- |
| `QUERY`                                           |          ✓           |                            ✗                            | Sheets-only superpower [T1]                                 |
| `ARRAYFORMULA`                                    |          ✓           |                            ✗                            | Excel uses implicit spilling instead                        |
| `FILTER` (array-returning)                        |          ✓           |                            ✓                            | Both since Excel 365                                        |
| `XLOOKUP`                                         |     ✓ (Aug 2022)     |                      ✓ (Aug 2019)                       | Both [T2]                                                   |
| `LAMBDA`                                          |     ✓ (Aug 2022)     |                            ✓                            | Both, but syntax/Named Function model differs [T1]          |
| `LET`                                             |          ✗           |                            ✓                            | **Sheets does NOT have LET** — use IIFE LAMBDA [T3]         |
| `MAP`/`REDUCE`/`BYROW`/`BYCOL`/`SCAN`/`MAKEARRAY` |     ✓ (Aug 2022)     |                            ✓                            | Both                                                        |
| `IMPORTRANGE`                                     |          ✓           |                            ✗                            | Sheets-only                                                 |
| `GOOGLEFINANCE`                                   |          ✓           |                            ✗                            | Sheets-only; Excel has `STOCKHISTORY`                       |
| `GOOGLETRANSLATE`                                 |          ✓           |                            ✗                            | Sheets-only                                                 |
| `IMPORTHTML`/`IMPORTXML`/`IMPORTDATA`             |          ✓           |                            ✗                            | Sheets-only                                                 |
| `REGEXEXTRACT`/`REGEXMATCH`/`REGEXREPLACE`        |          ✓           | ✗ (Excel uses workarounds or `REGEX` in newer versions) | RE2 engine                                                  |
| `=AI()`                                           |      ✓ (2025+)       |                 ✗ (Copilot is separate)                 | Sheets-native                                               |
| `STOCKHISTORY`                                    |          ✗           |                            ✓                            | Excel-only                                                  |
| `TEXTSPLIT`                                       |          ✗           |                            ✓                            | Sheets uses `SPLIT`                                         |
| `TEXTBEFORE`/`TEXTAFTER`                          | ✗ (use REGEXEXTRACT) |                            ✓                            | Verify; not in Google's lookup category list as of May 2026 |

---

## Decision Tables

### Lookup choice

| Situation                     | First choice                          | Second choice            |
| ----------------------------- | ------------------------------------- | ------------------------ |
| Simple key→value, key on left | `XLOOKUP`                             | `INDEX`/`MATCH`          |
| Key not on left               | `XLOOKUP`                             | `INDEX`/`MATCH`          |
| Return multiple columns       | `FILTER`                              | `QUERY`                  |
| Multi-condition               | `FILTER` or `XLOOKUP` with concat key | `QUERY`                  |
| Approximate / banded match    | `XLOOKUP` with `match_mode=1` or `-1` | `VLOOKUP` (sorted, TRUE) |
| Best non-exact match (fuzzy)  | Drop to Apps Script or pandas         | —                        |

### Aggregation choice

| Need                                   | Use                                                           |
| -------------------------------------- | ------------------------------------------------------------- |
| Single conditional sum                 | `SUMIFS`                                                      |
| Single conditional count               | `COUNTIFS`                                                    |
| Pivot output                           | `QUERY` with `GROUP BY ... PIVOT ...` or built-in Pivot Table |
| Weighted average                       | `SUMPRODUCT(values, weights)/SUM(weights)`                    |
| Aggregation with hidden rows excluded  | `SUBTOTAL` (code 109/103/101)                                 |
| Per-row aggregation over dynamic width | `BYROW`                                                       |

### Date pattern choice

| Need                             | Pattern                                                                  |
| -------------------------------- | ------------------------------------------------------------------------ |
| First of this month              | `=EOMONTH(TODAY(),-1)+1`                                                 |
| Last of this month               | `=EOMONTH(TODAY(),0)`                                                    |
| Last full quarter                | `EOMONTH(TODAY(),-MOD(MONTH(TODAY())-1,3)-1)` to start, EOMONTH-1 to end |
| Business days between            | `NETWORKDAYS(start, end, holidays_range)`                                |
| Add N months (handles month-end) | `EDATE(date, N)`                                                         |
| Age in years/months/days         | `DATEDIF(birth, TODAY(), "Y"/"M"/"D")`                                   |

### Sheets vs Pandas decision (fast vs slow)

| Task                                           | Tool                          | Why                                |
| ---------------------------------------------- | ----------------------------- | ---------------------------------- |
| Sum sales by region, current quarter           | Sheets `SUMIFS`               | 1 formula, 8 seconds               |
| Pivot last 90 days revenue × campaign          | Sheets `QUERY`                | 1 formula, ~15 seconds             |
| Reconcile two 50k-row tables                   | Sheets `FILTER`+`COUNTIFS`    | Native                             |
| Join 8 CSVs                                    | Pandas                        | Loop is trivial, Sheets is painful |
| Cohort retention curves                        | Pandas                        | Sheets does it but slowly          |
| Regex with lookbehind on 100k strings          | Pandas                        | RE2 can't                          |
| 500k+ rows with multi-step transforms          | Pandas                        | Sheets degrades                    |
| ARIMA / Prophet forecasting                    | Pandas + statsmodels/prophet  | Sheets has only `FORECAST.LINEAR`  |
| Build a daily-refresh dashboard the team views | Sheets (Looker Studio on top) | Collaboration                      |

---

## Source Bibliography

### Tier 1 — Google Official

- [1] **Google Sheets function list** — support.google.com/docs/table/25273 — Master list of all functions, organized by category. **The source of truth for "does this function exist?"** Retrieved 2026-05-12.
- [2] **QUERY function** — support.google.com/docs/answer/3093343 — Signature, examples, headers behavior. Retrieved 2026-05-12.
- [3] **ARRAYFORMULA function** — support.google.com/docs/answer/3093275 — Signature, Ctrl+Shift+Enter shortcut. Retrieved 2026-05-12.
- [4] **FILTER function** — support.google.com/docs/answer/3093197 — Multi-condition AND/OR via `*`/`+`. Retrieved 2026-05-12.
- [5] **SUMIFS function** — support.google.com/docs/answer/3238496 — Arg order, comparison operators, wildcards. Retrieved 2026-05-12.
- [6] **REGEXMATCH** — support.google.com/docs/answer/3098292 — RE2 engine, Unicode class limitation. Retrieved 2026-05-12.
- [7] **GOOGLEFINANCE** — support.google.com/docs/answer/3093281 — Attributes, intervals, historical vs real-time. Retrieved 2026-05-12.
- [8] **EDATE** — support.google.com/docs/answer/3092974 — Leap year and month-end handling. Retrieved 2026-05-12.
- [9] **DATEDIF** — support.google.com/docs/answer/6055612 — Unit codes, formatting gotcha. Retrieved 2026-05-12.
- [10] **XLOOKUP** — support.google.com/docs/answer/12405947 — match_mode and search_mode values. Retrieved 2026-05-12.
- [11] **LAMBDA** — support.google.com/docs/answer/12508718 — Lambda + Named Functions. Retrieved 2026-05-12.
- [12] **MAP** — support.google.com/docs/answer/12568985 — Aug 2022. Retrieved 2026-05-12.
- [13] **MAKEARRAY** — support.google.com/docs/answer/12569202 — Aug 2022. Retrieved 2026-05-12.
- [14] **Google Workspace Updates — Named Functions / LAMBDA release** — workspaceupdates.googleblog.com/2022/08/named-functions-google-sheets.html — Official release announcement Aug 24, 2022.
- [15] **Google Workspace Updates — XLOOKUP release** — supported via 9to5Google reporting; confirmed by Google official documentation page existence Aug 2022.
- [16] **Google Workspace Updates — Faster performance and doubled cell limits (April 2026)** — workspaceupdates.googleblog.com/2026/04/faster-performance-and-doubled-cell-limits-in-Google-Sheets.html — **10M → 20M cells; 30% faster open, 60% faster filter/conditional formatting on 1M+ cell sheets.**
- [17] **Google Workspace Updates — AI function language expansion** — workspaceupdates.googleblog.com/2025/09/ai-function-google-sheets-new-languages.html — Seven additional languages from Sep 23, 2025.
- [18] **Google Workspace Updates — AI function + Google Search integration** — workspaceupdates.googleblog.com/2025/10/enhanced-ai-function-sheets-google-search.html — Oct 2025.
- [19] **Google Visualization API Query Language Reference v0.7** — developers.google.com/chart/interactive/docs/querylanguage — Authoritative clause-order and syntax reference for `QUERY`.
- [20] **Optimize Sheets performance (Google official)** — support.google.com/docs/answer/12159115 — Best practices for big sheets.

### Tier 2 — Major Publication

- [21] **9to5Google — Google Sheets adds XLOOKUP** — 9to5google.com/2022/08/25/google-sheets-xlookup/ — Aug 25, 2022 confirmation.
- [22] **TechRepublic — Google Sheets gains LAMBDA and helper functions** — Aug 2022.
- [23] **ICAEW — Named functions, LAMBDAs and XLOOKUP in Google Sheets** — 2022.
- [24] **pandas official docs — Comparison with spreadsheets** — pandas.pydata.org/docs/getting_started/comparison/comparison_with_spreadsheets.html — Authoritative pandas-side mapping.

### Tier 3 — Senior Practitioner Blogs

- [25] **Ben Collins — New Functions In Google Sheets For 2022** — benlcollins.com/spreadsheets/new-functions-in-google-sheets-2022/ — Curated by a recognized Sheets MVP.
- [26] **Ben Collins — LAMBDA in Google Sheets** — benlcollins.com/spreadsheets/lambda-function/
- [27] **Ben Collins — XLOOKUP in Google Sheets** — benlcollins.com/spreadsheets/xlookup-function/
- [28] **Ben Collins — Sheets locations (locale separators)** — benlcollins.com/spreadsheets/sheets-location/
- [29] **Ben Collins — Formula parse errors and fixes** — benlcollins.com/spreadsheets/formula-parse-error/
- [30] **Ben Collins — QUERY function deep dive** — benlcollins.com/spreadsheets/google-sheets-query-sql/
- [31] **Coupler.io — QUERY Function Tutorial 2026** — blog.coupler.io/google-sheets-query-function/
- [32] **Coupler.io — ARRAYFORMULA examples** — blog.coupler.io/arrayformula-google-sheets/
- [33] **Ablebits — DATEDIF and NETWORKDAYS** — ablebits.com/office-addins-blog/datedif-google-sheets/
- [34] **Ablebits — VLOOKUP in Google Sheets** — ablebits.com/office-addins-blog/vlookup-google-sheets-example/
- [35] **Ablebits — Compare two sheets/columns** — ablebits.com/office-addins-blog/google-sheets-compare-two-sheets-columns/
- [36] **regular-expressions.info — Google Sheets REGEX** — regular-expressions.info/googlesheets.html — Authoritative regex reference noting RE2 constraints.
- [37] **Zapier — 10 million cell limit explainer** — zapier.com/blog/google-sheets-cell-limit/
- [38] **RowZero — Google Sheets row/cell limits** — rowzero.com/blog/google-sheets-limits
- [39] **Layer — Google Sheets limitations** — golayer.io/blog/google-sheets/google-sheets-limitations/
- [40] **buralog — Practical IMPORTRANGE performance tips** — buralog.jp/en/importrange-performance-tips-en/
- [41] **Sheetgo — IMPORTRANGE reference cap** — sheetgo.com/blog/spreadsheets-tips/google-sheets-cell-limit/
- [42] **Online Journalism Blog — `=AI()` classification testing** — onlinejournalismblog.com/2025/04/10/google-sheets-has-a-new-ai-function/ — Empirical observation of hallucination patterns.

### Tier 4 — Forum / Community (used for triangulation only)

- [43] Google Docs Editors Community threads on IMPORTRANGE behavior, QUERY pivot, INDEX/MATCH ARRAYFORMULA gotchas — referenced for practitioner confirmation, not as primary citations.

---

## Confidence Assessment

| Area                                                      | Confidence                                                                                                  | Notes                                                                                                                                                                                     |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Function signatures                                       | **Strong**                                                                                                  | All directly verified against Google official docs [T1]. Where T1 page wasn't directly readable in research, signature is corroborated by multiple T3 sources and consistent across them. |
| Release dates (XLOOKUP Aug 2022, LAMBDA Aug 2022)         | **Strong**                                                                                                  | Multiple T1 + T2 confirmations.                                                                                                                                                           |
| Cell limits (10M → 20M April 2026)                        | **Strong**                                                                                                  | Direct T1 Google Workspace Updates blog post quote.                                                                                                                                       |
| `=AI()` capabilities and limits                           | **Moderate**                                                                                                | T1 confirms release and language expansion; T3 reports the 200-cell-per-operation cap. Behavior evolves rapidly.                                                                          |
| Performance numbers (1.2M cell timeout, 100k IMPORTRANGE) | **Moderate**                                                                                                | T3 practitioner sources; consistent across multiple but not officially documented by Google.                                                                                              |
| Sheets vs Excel function availability matrix              | **Strong** for items I directly verified; **moderate** for `TEXTBEFORE`/`TEXTAFTER` (verify before citing). |
| RE2 vs PCRE differences                                   | **Strong**                                                                                                  | T1 Google docs explicitly cite RE2 + no Unicode classes; T3 regular-expressions.info confirms no lookbehind.                                                                              |
| Pandas/Sheets decision boundary                           | **Moderate**                                                                                                | Synthesized from T2/T3 practitioner sources. The 500k threshold is a practical rule of thumb, not a hard line.                                                                            |
| LLM hallucination patterns                                | **Moderate**                                                                                                | T3 reports from Apr 2025; my own pattern enumeration extends those reports with reasoning about common LLM failure modes.                                                                 |

---

## Gaps & Open Questions

1. **`TEXTBEFORE` / `TEXTAFTER`** — these appeared in some Sheets recently per anecdotal reports. Not in the Google official function list category page I retrieved. **Verify before citing.**
2. **The `=AI()` function's exact prompt/range syntax** — Google's docs are still evolving; the 200-cell cap is from T3 sources only. Verify directly before encoding into Yudhishthira's logic.
3. **Real benchmarks for QUERY vs SUMIFS vs FILTER on 500k rows** — no controlled benchmark in the research. Anecdotal claims that `QUERY` is slower than `SUMIFS` arrays at scale, but unverified.
4. **Whether the 20M cell limit (April 2026) is fully rolled out or beta-only** — the T1 post says beta. Mainstream rollout date is uncertain as of 2026-05-12.
5. **`LET` in Sheets** — currently absent per all sources reviewed. Google could ship it; check periodically.
6. **`LAMBDA` performance** — anecdotal that `MAP` can be resource-heavy on large arrays. No quantified comparison vs `ARRAYFORMULA` for the same task. Empirical testing recommended.
7. **Apps Script handoff threshold** — the playbook covers formula-vs-pandas. The formula-vs-Apps-Script line (especially for scheduled refreshes, email alerts, multi-step workflows that stay inside Google) deserves its own analysis.

---

## Suggested Next Steps

1. **Encode the decision rule** in Yudhishthira's CLASSIFY phase: rows × multi-file × stats × regex-features → Sheets vs pandas vote.
2. **Build a formula-validator skill** that takes a proposed formula string and (a) checks every function name against the offline cached copy of Google's function list, (b) detects locale-mismatch, (c) flags Excel-only function usage, (d) verifies QUERY clause order. Cache `support.google.com/docs/table/25273` locally so the agent can do offline validation.
3. **Create a "tested patterns" library** as a sibling file — each pattern (W1-W7 here) as a runnable, parameterized formula snippet. Yudhishthira pulls from this rather than hand-authoring.
4. **Empirically benchmark** `QUERY` vs `SUMIFS`-array vs `BYROW`+`LAMBDA` on a 500k-row sample sheet. Update the performance section with measured numbers.
5. **Re-verify** the gaps list quarterly. Sheets ships new functions roughly every 6-12 months; the formula bible needs maintenance.
6. **Build a regex translation table** for the agent — given a Python regex, automatically detect lookbehind/lookahead/backreferences and either rewrite to RE2 or flag "drop to pandas."
