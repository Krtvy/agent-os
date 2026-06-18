# Portal UX research — 2026-05-22

What POCs are doing in the portal is a **well-studied UX problem**: pick a
data source, build a query, see the result. There are mature reference
products. This doc distills which patterns to copy, which to ignore, and
what we're shipping today vs. parking.

## Reference products we should look like

| Product                                        | What to copy                                                                                                                                                                         | What NOT to copy                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| **Metabase Question Builder**                  | Single page, three stacked sections: Data → Filter → Summarize. Defaults sensibly to "table + count of rows." Each section is a focused panel, not 4 fieldsets jammed together.      | Their visual identity (heavy blue, too many drawers). Skip.        |
| **PostHog Insights → SQL**                     | "Edit" mode hides query complexity behind a clean form. "Show SQL" toggle for power users. Audit trail of past runs is right there.                                                  | Their result-area dominates the view; we don't need charts yet.    |
| **Tableau "Rows / Columns / Marks / Filters"** | Drag-and-drop semantics are second nature to data folks. Even without drag-drop, the _layout_ (Rows on top, Columns next, Values third, Filters last) maps directly to mental model. | Tableau's whole "marks/colors/shapes" cosmology — wildly overkill. |
| **Notion database table view**                 | Add/remove/reorder is friction-free. Empty states ("Add a property") are inviting, not blank.                                                                                        | Their notion of "properties" is too coupled to their data model.   |
| **Supabase Studio table editor**               | Native to our DB; familiar typography to anyone who's used the Supabase dashboard. Schema picker is a left rail, table opens to the right.                                           | The actual SQL editor — too engineer-coded for POCs.               |

## Five UX principles we should follow

1. **Progressive disclosure.** Most pivots = "count something, grouped by something." Don't show 4 fieldsets up front. Show the 2 that matter (Values, Rows). Tuck Columns, Filters into expanders that open on click. Reduces visual load by ~50%.

2. **Sensible defaults.** A new pivot form should be PRE-filled with `COUNT(*) of <something>` so clicking Run immediately yields a result. Empty forms force POCs to figure out the syntax.

3. **One primary action, visible always.** "Run" should be the only filled-green button on the page. Cancel/secondary always muted. Scroll-resistant — Run stays in view as you build.

4. **Inline help that doesn't take you elsewhere.** Tooltips ("?" icons), single-sentence hints inside legends, and warnings collapsed into ONE panel. POC never has to leave the page to understand what they're seeing.

5. **Empty states are first impressions.** "Pick a schema" is technically accurate but unfriendly. "Where do you want to look?" + a guided first-click lands better. A POC who feels lost in 5 seconds will not be back.

## What's currently messy and why

| What                                                                             | Problem                                                                                   | Root cause                |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------- |
| `/browse` detail page is long                                                    | Header + warnings + columns + preview + pivot builder = ~1500px tall, all visible at once | No progressive disclosure |
| Pivot form: 4 fieldsets visible at once                                          | Rows, Columns, Values, Filters, Limit — all unfolded                                      | Same                      |
| Empty form on first open                                                         | User has to fill agg + col before clicking Run                                            | No sensible default row   |
| `/result/<id>` doesn't link back                                                 | "← All reports" is small and muted                                                        | No breadcrumb             |
| Run button scrolls out of view in long forms                                     | When pivot has many filters added                                                         | No sticky CTA             |
| Warnings live in a yellow panel above the table, but the column rows also flag ⚠ | Same info displayed twice                                                                 | Redundancy                |

## Shipping today (Tier 1)

1. **Sensible default value row** — pivot form opens with `COUNT(*)` pre-selected in the first value spec. User can change or remove.
2. **Progressive disclosure for Columns + Filters** — Rows + Values open by default (most common); Columns (cross-tab) + Filters collapse by default behind clickable headers.
3. **Empty state on `/browse`** — hero copy "Pick a data source to start exploring" + arrows/visual hint, replacing the bare dropdown.
4. **Sticky Run button** — `position: sticky; bottom: 0` so it stays in view as the form gets long.
5. **Breadcrumb on result page** — clearer back-link with the report name, not just "All reports."
6. **Remove duplicate warning markers** — column rows lose the ⚠ since the panel above already lists them.

## Deferring (Tier 2, do if asked)

- **Two-column layout** (schemas on left rail, detail on right). Bigger refactor; not blocking.
- **`/history` page** — list of your past tasks with re-run links. Needs a small index across `pocs/<poc>/deliverables/`.
- **Inline SQL preview as form changes** — live show the SQL being generated as the POC ticks boxes. Cool but ~150 LOC of HTMX.
- **Saved queries / favorites** — "bookmark this pivot for next month" with a name. Real feature; full backend work.
- **Charts** — bar/line of result data. Out of scope; POCs export to Sheets/Excel for visuals.

## Deferring (Tier 3, do if you want to invest)

- **Drag-and-drop column placement** between Rows/Columns/Values panels. Big visual win, big code investment.
- **Keyboard shortcuts** — Cmd+Enter to submit, ⌘K to focus first field.
- **Real-time result preview** — show the first 10 rows while the POC is still tweaking filters.
- **Dark mode** — Pico supports it; we'd just need to test the custom CSS overrides.

## What to test on POCs (not us)

When you share the portal with the first POC, watch for these failure modes:

- Do they understand "Browse Data" as the way in? Or do they expect a search bar?
- Do they grasp the difference between Rows / Columns / Values? (Excel pivot mental model assumed.)
- Do they read the ⚠ warnings? Or do they ignore them and get wrong numbers?
- Do they bookmark `/result/<id>` or come back via the home page?
- Do they use the `+ add filter` button or get stuck with one?

Tracking these answers is more valuable than any UX rewrite.

---

_Living doc — update as POCs surface new friction or as we ship Tier 2/3 items._
