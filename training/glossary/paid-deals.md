# Paid Deals

**Source:** Kartavya, 2026-05-13.

## Definition

**Paid Deals** are **quid-pro-quo agreements** between Rootlabs and a creator: "you make X videos, we pay you $Y."

Fixed number of deliverables for a fixed payment. Different from organic creator economics where creators earn commission on sales — paid deals are flat-fee contracts on top of (or instead of) commission.

## Structure (inferred from the term + Kartavya's description)

A typical paid deal involves:

- **A creator** (named by username)
- **A deliverable count** — "this many videos"
- **A payment amount** — "you will pay this much"
- Implicitly: a **deadline** and a **product** the videos must feature

## Why they exist

Some creators won't post about a product on organic terms alone — they need guaranteed pay to commit production time. Paid deals are the lever Rootlabs uses to:

- Get top-tier creators (whose attention is expensive) to produce content
- Guarantee a content volume for a launch or campaign push
- Convert a Silent or Reactivation-target creator back to Active when commission incentives aren't enough

## Implication for analyses

- **`Paid Deals` tab tracks the contract layer**, not the resulting revenue. To see whether a paid deal actually produced GMV, you join `Paid Deals` → `Video Count` (did they post?) → `gmv_data` (did the videos sell?).
- **A paid deal can show "delivered" in the tracker but the videos can still flop on GMV.** That's a real outcome, not a bug — flat-fee pay decouples Rootlabs' cost from the creator's performance.
- **For ROI analysis on paid deals**, you'd compute: total GMV attributable to deal-funded videos vs total payment made. This is a clean reconciliation task pattern.

## Pending detail

- The exact schema of the `Paid Deals` tab — column names, what data is captured
- How a paid-deal video is tagged in `gmv_data` (does it get a flag, or is attribution purely via content_id matching the deal's deliverables?)
- Whether commissions stack on top of flat-fee paid deals or replace them
