# Products at Rootlabs

**Source:** Kartavya, 2026-05-13.

## The roster

10 products appear in the `gmv_data` tab:

| Product (gmv_data value) | Status (per Kartavya 2026-05-13)                                                                                  | Tracked in May workbook?                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **`hgr`**                | **Hero / flagship product.** The comparatively biggest-selling line. This month's primary focus.                  | ✓ Dedicated tab + featured in `Main PoC`   |
| **`magashwa`**           | Previous month's focus (newly launched, needed market push). Still tracked this month to see momentum carry-over. | ✓ Dedicated tab (smaller scope than HGR)   |
| `alpha`                  | Not actively pushed this month                                                                                    | Not tracked beyond appearing in `gmv_data` |
| `ppp`                    | Not actively pushed this month                                                                                    | Same                                       |
| `bb`                     | Not actively pushed this month                                                                                    | Same                                       |
| `confidence_duo`         | Not actively pushed this month                                                                                    | Same                                       |
| `reset_trio`             | Not actively pushed this month                                                                                    | Same                                       |
| `rl_seamoss`             | Not actively pushed this month                                                                                    | Same                                       |
| `turmeric`               | Not actively pushed this month                                                                                    | Same                                       |
| `glow_duo`               | Not actively pushed this month                                                                                    | Same                                       |

## The "this month vs last month" pattern

Rootlabs **rotates focus** between products month-to-month based on launch timing and momentum:

- **Launch month + 1 or 2**: heavy push on the new product (last month was MagAshwa)
- **Steady state**: return to HGR as the hero
- **Trailing tracking**: keep the previously-focused product on the dashboard for a month or two to monitor momentum

This means:

- The `Main PoC` tab's `product = "hgr"` filter is **current-month-specific**, not eternal.
- Next month or in two months, when a new product launches, the same dashboard tab might have a different product filter.
- Future workbook trackers should expect this pattern of product-of-the-month focus.

## Implication for analyses

- **Don't sum all products by default.** When the user says "GMV by creator," they almost always mean the current focus product (HGR right now). Confirm scope before summing.
- **Per-creator analyses across products** are valid but rare — typically used for cross-product creators (someone driving both HGR and MagAshwa sales) where the question is "which product is their strength?"
- **Watch for the next launch.** When a new product appears in `gmv_data` with non-trivial volume, that's the signal a launch is happening — and the dashboard scope will likely shift.

## Pending detail

- What defines "hero product" formally — highest revenue, longest history, broadest creator participation, something else?
- Roadmap of upcoming launches that will rotate into focus
- Whether the "two-month tail" pattern (e.g., keep MagAshwa tracked even though HGR is the current focus) is formal policy or just current practice
