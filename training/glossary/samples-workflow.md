# Samples workflow

**Source:** Kartavya, 2026-05-13.

## The "sample before video" pattern

**Before a creator can make a video for a Rootlabs product, they need the actual physical product** to use, taste, demonstrate, and assess. So the funnel for any product-driven content has a mandatory upstream step:

```
Identify creator → Send sample → Creator receives + tries product → Creator makes video → Video drives GMV
                       ↑
                       │
                  this step is the
                  "samples workflow"
```

A creator who doesn't get a sample will not produce video content for that product. Samples are the **content-production unlock.**

## Why it matters operationally

- **Sample delivery is gating.** Even a high-intent creator can't perform without inventory.
- **Sample logistics are real costs** — physical shipment, inventory tracking, address management.
- **A missed sample shipment is a missed creator-month.** If a creator gets their sample on May 25, the May reporting period is already mostly gone for them.

## The two tabs that track this

| Tab                        | Role                                                                                                                                                        |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`HGR Sample Delivered`** | The **delivery confirmation log.** Which creators have actually received their HGR samples? Source of truth for "is this creator unlocked for HGR content?" |
| **`hgr_samples`**          | The **working queue / staging table.** Where the team manages the operational flow — sample requests, pending shipments, etc.                               |

These are paired: `hgr_samples` is the verb (managing the process), `HGR Sample Delivered` is the noun (the resulting state).

## Implication for analyses

- **A creator with $0 HGR GMV in May might not be silent or under-performing** — they might simply not have received their sample yet. Always check `HGR Sample Delivered` before judging a creator's HGR performance.
- **Sample velocity is a leading indicator** of next month's GMV. More samples delivered in May = more potential content (and revenue) in June.
- **Cross-reference**: when a POC asks "why isn't Creator X producing?", check sample delivery first. If they haven't received the product, the question changes from "why aren't they posting?" to "where is their sample?"

## Per-product applicability

The samples workflow described here is **HGR-specific** in the May workbook (because HGR is the focus product). The same pattern presumably exists for MagAshwa (and would apply to any new launch), but no equivalent tabs are present in this workbook for MagAshwa. Worth confirming whether MagAshwa samples are tracked elsewhere or simply not currently being shipped.

## Pending detail

- Cadence of `HGR Sample Delivered` updates (when is a delivery marked as confirmed?)
- Whether the tab tracks just the fact of delivery or also the sample SKU, shipment date, address, etc.
- The full schema of `hgr_samples` — how the working queue is structured
