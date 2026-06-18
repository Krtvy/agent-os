# NL-to-pivot — design doc (not yet implemented)

Adding natural-language data queries to the portal. POC types a question
in plain English; LLM proposes a pivot config; POC reviews and runs it
through the existing safe path.

**Status:** designed, not built. Ship when you're ready by following the
"Implementation plan" section below.

---

## Constraints / Goals

This is "very perfect" per Kartavya. That has a specific definition here:

1. **The LLM never executes SQL directly.** It outputs structured JSON
   that becomes a `PivotPlan`. The plan passes through the same
   `validate_plan()` whitelist that the click-driven path uses.
2. **POC sees and edits the proposal before Run.** Human-in-loop, every
   query. No auto-execute.
3. **Hallucinations are caught at the whitelist layer.** If LLM invents
   `tiktok_revenue_table`, validation rejects with "Unknown table." POC
   sees a clear error, not a silent wrong answer.
4. **Domain knowledge is in the prompt, not in the LLM's head.** IST
   adjust, GMV formula, content_type='Livestream', cancellation filter
   — all passed as system context from `column_warnings.py`.
5. **The generated SQL is shown on the result page.** Falsifiable.
6. **Audit trail records the question, the proposal, and the final SQL.**

### Non-goals

- Free-form SQL editing by the POC.
- Agentic loops (LLM calls tools, decides on its own what to fetch).
- Chart generation. CSV is the deliverable; charts are downstream.
- Conversational memory across questions. Each question is independent.

---

## Architecture

```
POC types "Top creators by GMV in May 2026"
         │
         │ POST /ask  {question: "..."}
         ▼
┌─────────────────────────────────────────────┐
│ portal/lib/nl_to_pivot.py                   │
│                                             │
│  build_schema_context()  ── information_schema, column_warnings,
│                              schema_labels  → ~3-5k tokens
│  propose(question, ctx) ── Anthropic SDK,
│                              Haiku 4.5 model, JSON-mode output
│  validate proposal     ── PivotPlan structure check (typed)
└─────────────────────────────────────────────┘
         │
         │ store proposal in pocs/<poc>/proposals/<id>.json
         │ 303 → /ask/review/<proposal_id>
         ▼
┌─────────────────────────────────────────────┐
│ /ask/review/<proposal_id>                   │
│                                             │
│  Renders pivot form PRE-FILLED with LLM     │
│  proposal. POC sees:                        │
│    - Original question (quoted)             │
│    - LLM explanation in plain English       │
│    - Confidence badge (high/medium/low)     │
│    - The pivot form with rows, values,      │
│      filters, columns_dim populated         │
│    - The generated SQL preview              │
│    - "Looks right? → Run pivot"             │
│      or "Not what I meant — edit below"     │
└─────────────────────────────────────────────┘
         │
         │ POST /browse/pivot/run  (existing M7-M9 route)
         ▼
┌─────────────────────────────────────────────┐
│ validate_plan(plan, valid_columns)          │
│   ↳ whitelist catches hallucinated columns/ │
│     aggs/operators                          │
│ start_async(...)  ← existing                │
│ /result/<task_id>  ← existing               │
└─────────────────────────────────────────────┘
```

The LLM's only job is intent → JSON. From that point on, every line of
code is one we already wrote, tested, and audited. Hallucinations land
as validation errors, not wrong answers.

---

## Files to create / modify

```
portal/lib/nl_to_pivot.py          ── NEW. propose() + schema-context builder
portal/lib/llm_client.py            ── NEW. Anthropic SDK wrapper, retry/cache
portal/templates/_ask_search.html   ── NEW. search bar fragment (home page)
portal/templates/ask_review.html    ── NEW. proposal review page
portal/app.py                       ── add routes:
                                       POST /ask           (submit question)
                                       GET  /ask/review/<id>  (render proposal)
                                       POST /ask/review/<id>/run  (re-validate + run)
portal/templates/home.html          ── insert _ask_search.html at top
portal/requirements.txt             ── add: anthropic==0.40.0  (or current latest)
portal/.env.example                 ── document: ANTHROPIC_API_KEY=...
pocs/<poc>/proposals/<id>.json      ── runtime storage (filesystem, gitignored)
```

No changes to runner.py, pivot.py, db.py — the existing safe path is
the execution layer. NL is purely an alternate entry point to that path.

---

## The LLM prompt (concrete sketch)

### System prompt (~2000 tokens)

```
You are a data query intent translator for the Rootlabs POC portal.

Your job: given a POC's plain-English question, propose a JSON pivot
plan that will be executed against the Rootlabs Supabase Postgres.

You DO NOT execute SQL. You DO NOT generate SQL. You output a structured
JSON plan that the portal validates and runs through a safe whitelist.

### Schema available

[For each schema, list tables. For each table, list columns with types.
Include the friendly label from schema_labels.py and the data_type from
information_schema. Aim for ~3000 tokens of schema context.]

Example schema dump:
  tiktok_raw_data.tiktok_orders  (Orders)
    order_id            text
    sku_id              text
    order_status        text       — values: Canceled, Completed, Shipped, To ship
    created_time        timestamp  ⚠ IST: subtract INTERVAL '8 hours' for IST day boundary
    quantity            integer    ⚠ Multiply by rootlabs_products.unit_multiplier for true units
    sku_subtotal_after_discount   numeric   ⚠ For GMV add sku_platform_discount
    cancellation_return_type      text     ⚠ Filter IS NULL to exclude cancellations
    ...

  tiktok_raw_data.tt_video  (Videos)
    video_id   text
    handle     text        — TikTok creator handle
    post_time  timestamp   ⚠ IST adjust
    product    text
    ...

  tiktok_raw_data.tiktok_affiliate_orders  (Affiliate orders)
    creator_username   text
    content_id         text
    content_type       text   — values: Video, Livestream, Showcase, External Traffic Program
    time_created       timestamp  ⚠ IST adjust  (NOTE: time_created here, NOT created_time)
    ...

### Output format — JSON only, no prose outside JSON

If the question is clear and answerable:
{
  "kind": "pivot",
  "explanation": "One sentence describing what you understood. Reference the
                  domain knowledge applied — e.g. 'Counting distinct video_id
                  from tt_video, filtered to May 2026 (IST), grouped by handle.'",
  "confidence": "high" | "medium" | "low",
  "plan": {
    "schema": "tiktok_raw_data",
    "table": "tt_video",
    "rows": ["handle"],
    "values": [{"agg": "COUNT_DISTINCT", "column": "video_id"}],
    "filters": [
      {"column": "post_time", "op": ">=", "value": "2026-05-01"},
      {"column": "post_time", "op": "<",  "value": "2026-06-01"}
    ],
    "columns_dim": null,
    "limit": 100
  }
}

If the question is ambiguous, ask ONE clarifying question:
{
  "kind": "clarification",
  "question": "By 'top creators' do you mean by GMV (revenue), by number of
               videos posted, or by number of livestreams?",
  "context": "I see three possible interpretations; pick one and re-ask."
}

If the question cannot be answered with the available data:
{
  "kind": "cannot_answer",
  "reason": "The data needed is not in any table I have access to. Specifically:
             you asked for X, but no column matches that concept."
}

### Rules

- ONLY use columns that exist in the schema dump above. Never invent.
- ONLY use aggregations in {SUM, COUNT, COUNT_DISTINCT, AVG, MIN, MAX}.
- ONLY use filter ops in {=, !=, >, <, >=, <=, contains, between, is_null, is_not_null}.
- For date filters, prefer >= start AND < end_of_next_period rather than equality.
- Apply ALL relevant ⚠ warnings to your plan (IST adjust, GMV formula, content_type literal).
- If the question mentions GMV or revenue: COUNT/SUM is not enough.
  Currently the pivot builder does not support computed expressions like
  `sku_subtotal_after_discount + sku_platform_discount`. If GMV is asked,
  return a "cannot_answer" with reason "GMV needs a computed-column feature
  not yet in the pivot builder; ask in Browse Data with a pre-built report."
- If a creator name is mentioned, use the literal handle if you recognize it,
  otherwise include a filter on the creator field with the user's text and
  note in the explanation that you matched it literally.
- Always set a sane limit. Default 100. Cap at 10000.
- The explanation MUST mention any domain assumption made (IST, exclusion of
  cancellations, etc.) so the POC can verify.
```

### Example interactions

**User:** "How many videos did `swugshop` post in May 2026?"

**LLM proposal:**

```json
{
  "kind": "pivot",
  "explanation": "Counting distinct video_id in tt_video where handle='swugshop' and post_time falls in May 2026 (IST day boundary applied).",
  "confidence": "high",
  "plan": {
    "schema": "tiktok_raw_data",
    "table": "tt_video",
    "rows": [],
    "values": [{ "agg": "COUNT_DISTINCT", "column": "video_id" }],
    "filters": [
      { "column": "handle", "op": "=", "value": "swugshop" },
      { "column": "post_time", "op": ">=", "value": "2026-05-01 00:00:00" },
      { "column": "post_time", "op": "<", "value": "2026-06-01 00:00:00" }
    ],
    "columns_dim": null,
    "limit": 100
  }
}
```

**User:** "Top livestreamers"

**LLM clarification:**

```json
{
  "kind": "clarification",
  "question": "Top by what — total livestream count, total GMV from lives, or distinct products sold?",
  "context": "I see three reasonable rankings and the answer differs."
}
```

---

## Cost model

- **Haiku 4.5:** ~$0.80 / million input tokens, ~$4 / million output.
- **Per question:** ~4000 tokens in (schema context + question), ~500 tokens out.
- **Per question cost:** ~$0.005 (half a cent).
- **8 POCs × 10 queries/day × 22 working days = 1,760 queries/month.**
- **Monthly LLM bill: ~$9.** Negligible.
- Cache: hash of (question + schema_context_hash) → cached proposal. Many
  POCs ask "give me the same answer for next month" — cache hits eliminate
  re-calls when only the date changes (need parameter detection — see
  Open Questions).

---

## UX flow (with the search bar)

### Home page

```
┌─────────────────────────────────────────────────────────────┐
│ Rootlabs Portal               kartavvya@... · log out       │
├─────────────────────────────────────────────────────────────┤
│ What do you want to do?                                     │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💬 Ask in plain English                                  │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ how many videos did swugshop post in May 2026?      │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ Try: "top creators by GMV last month" · "lives done by   │ │
│ │ X this week"                                             │ │
│ │                                            [Ask →]       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔍 Browse Data — click through schemas and tables       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Saved reports                                               │
│  • Creator activity by month                                │
│  • Database probe                                           │
│  • ...                                                      │
└─────────────────────────────────────────────────────────────┘
```

### Review page (`/ask/review/<id>`)

```
Reports › Ask › Review

Your question: "how many videos did swugshop post in May 2026?"

╭──────────────────────────────────────────────────────────╮
│ ● High confidence                                         │
│ I understood this as: Counting distinct video_id in       │
│ tt_video where handle='swugshop' and post_time falls in   │
│ May 2026 (IST day boundary applied).                      │
╰──────────────────────────────────────────────────────────╯

[Pivot form, pre-filled. POC can edit any field.]

Values: COUNT DISTINCT  video_id
Rows:   (none — single summary row)
Filters:
  handle = swugshop
  post_time ≥ 2026-05-01 00:00:00
  post_time <  2026-06-01 00:00:00

[Show SQL ▾]
SELECT COUNT(DISTINCT "video_id") AS "count_distinct_video_id"
FROM "tiktok_raw_data"."tt_video"
WHERE "handle" = 'swugshop'
  AND "post_time" >= '2026-05-01 00:00:00'
  AND "post_time" <  '2026-06-01 00:00:00'
LIMIT 100;

[Run pivot] [Edit fields] [Ask different question]
```

### Clarification page

If LLM returns `kind: "clarification"`, show:

```
Your question was ambiguous.

I see three ways to interpret "top livestreamers" and the answer differs.
Could you re-ask with one of these?

  • Top by total livestream count   [use this]
  • Top by GMV from lives           [use this]
  • Top by distinct products sold   [use this]
```

Each "use this" button re-submits the question with the disambiguation
appended, e.g. `top livestreamers by total livestream count`.

---

## Validation layer (catches hallucination)

The LLM might propose a column that doesn't exist. The portal MUST catch
this before running, with a clear error to the POC.

```python
# portal/lib/nl_to_pivot.py
def validate_proposal(proposal: dict, schema: str, table: str) -> PivotPlan:
    valid_cols = {c.name for c in list_columns(schema, table)}
    plan = PivotPlan(
        schema=schema,
        table=table,
        rows=tuple(proposal["plan"]["rows"]),
        values=tuple(ValueSpec(**v) for v in proposal["plan"]["values"]),
        filters=tuple(FilterSpec(**f) for f in proposal["plan"]["filters"]),
        columns_dim=proposal["plan"].get("columns_dim"),
        limit=proposal["plan"].get("limit", 100),
    )
    validate_plan(plan, valid_cols)  # M7 whitelist — same one click users hit
    return plan
```

If `validate_plan` raises `PivotValidationError`, the review page shows
a clear "The model proposed something that doesn't exist. Edit fields
below or try rephrasing." We never silently execute a hallucination.

---

## Failure modes + mitigations

| Failure                                          | Mitigation                                                                                                                         |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| LLM hallucinates a column name                   | Whitelist validation rejects                                                                                                       |
| LLM picks the wrong table                        | POC sees the table on review page, can change                                                                                      |
| LLM forgets IST adjustment                       | Domain warnings in system prompt; POC sees filter values and can sanity-check                                                      |
| LLM produces ambiguous interpretation            | Clarification path explicitly supported                                                                                            |
| API key missing / network down                   | Search bar shows "AI assist is offline; use Browse Data" — graceful fallback to the click-driven path                              |
| API rate limit                                   | Backoff + retry; cache hits eliminate most calls                                                                                   |
| POC trusts a wrong answer                        | Confidence badge + explanation + visible SQL on result page                                                                        |
| Cost spike                                       | Per-POC monthly budget; hard cap at e.g. $50/month                                                                                 |
| Schema context too large                         | Trim to schemas the POC actually queries (track per-POC)                                                                           |
| Question that needs JOINs                        | Currently the pivot builder is single-table; LLM should return cannot_answer with "this needs a multi-table report — ask Kartavya" |
| Question that needs computed columns (GMV = a+b) | Same — cannot_answer until we add computed columns to PivotPlan                                                                    |

---

## Phased rollout

**Phase A — Plumbing only (~3 hours)**

- Build `lib/llm_client.py` with Anthropic SDK + retry
- Build `lib/nl_to_pivot.py` with schema-context builder + propose()
- Build POST `/ask` route that returns the JSON proposal (no UI yet)
- Test with 10 hand-picked questions, measure proposal correctness

**Phase B — Review UI (~3 hours)**

- Add `_ask_search.html` to home page
- Add `ask_review.html` (the pre-filled pivot form + explanation)
- Add POST `/ask/review/<id>/run` that re-validates and kicks off the
  existing async task

**Phase C — Hardening (~2 hours)**

- Wire up cache (in-memory dict keyed by question hash for now)
- Wire up clarification path
- Add cost tracking (log per-call token counts + price to a per-POC file)
- Add "AI assist is offline" graceful fallback

**Phase D — POC test (1 day, asynchronous)**

- Ship to one POC (recommend: Trupti or Rachit — they ask the most varied
  questions in your training queries)
- Track: of N questions, how many get correct answer in one pass vs
  needing edits vs needing clarification vs cannot_answer
- If accuracy <80% on common patterns, do prompt iteration before
  expanding to all 8 POCs

**Phase E — Expand**

- Add computed columns (`gmv_after_discount = sku_subtotal_after_discount + sku_platform_discount`)
- Add multi-table proposals (LLM picks JOIN keys from a whitelist of
  known relationships)
- Add saved-question feature ("re-run last month's question for this month")

---

## Open questions (to revisit before / during build)

1. **Schema-context size vs. accuracy.** Send all 8 schemas + 100+
   columns, or only `tiktok_raw_data` (the highest-traffic one)? Token
   budget vs. coverage. Start with `tiktok_raw_data` + `rootlabs_core`,
   expand if POCs ask cross-schema questions.

2. **How to detect parameters for caching.** "Videos in May 2026" vs.
   "videos in June 2026" — same shape, different params. Cache the
   shape, not the literal answer. Needs LLM to emit a "shape hash" or
   parameter-extraction step.

3. **Multi-table JOIN support.** Most real questions (creator GMV)
   need joins. The current pivot builder is single-table. Options:
   (a) wait, return cannot_answer for now;
   (b) add JOIN support to PivotPlan with a whitelist of known JOIN
   keys (`tiktok_orders.order_id = tiktok_affiliate_orders.order_id`,
   etc.);
   (c) generate the SQL directly and skip pivot — but that breaks the
   safety property.

4. **POC trust calibration.** First couple of weeks, show the explanation
   prominently. Later, can we hide it for high-confidence proposals?
   Or always show? Lean: always show.

5. **Model selection.** Haiku 4.5 for speed/cost. Opus 4.7 for complex
   queries. Could auto-route: if question is short and matches a common
   pattern → Haiku; if long or complex → Opus. Track accuracy per model.

6. **Prompt iteration loop.** Need a way to capture "POC asked X, LLM
   got it wrong, here's the right plan." Use those as few-shot examples
   in the system prompt. Build a tiny labeling UI? Or just maintain a
   `prompts/few_shots.jsonl` file Kartavya edits by hand.

7. **What about reports we already have?** When POC asks "creator
   activity for May," should the LLM route to the existing
   `creator-content-counts` report instead of building a pivot? Probably
   yes — add report manifests to the system prompt as "if user asks
   this, use this report instead of a pivot." Saves tokens + gives
   tested SQL.

---

## When you're ready to ship

1. Get an Anthropic API key from console.anthropic.com (~5 min).
2. Drop it into `portal/.env` as `ANTHROPIC_API_KEY=sk-ant-...`.
3. Tell me "ship NL." I implement Phase A → Phase C in one session,
   then we Phase D with one real POC.

Total LOC estimate: ~600 across the new files + minor edits. ~8 hours
of focused build time including the UI polish.

_Living design — update as decisions are made and as POCs surface
patterns that change the shape._
