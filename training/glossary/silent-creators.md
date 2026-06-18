# Silent creators

**Source:** Kartavya, 2026-05-13.

## Definition

**Silent creators** are creators Rootlabs is **in contact with but not actively working with right now** — they're known to the team but not currently producing content or generating revenue.

Distinct from:

- **Acquisition prospects** — cold leads we've never worked with, currently being pursued
- **Active (Push content)** — currently producing, being pushed for more
- **Existing Creators** — the broader base population
- **Reactivation targets** — the subset of Silent creators we're actively trying to bring back

A creator becomes Silent by **stopping production**, not by leaving Rootlabs. The relationship persists; the output doesn't.

## Why this distinction matters

Silent creators are the **primary candidate pool for Reactivation operations**. The funnel is:

```
Acquisition (cold)  →  Active (producing)  →  Silent (paused)  →  Reactivation (winning back)
                                                  ↑                        │
                                                  └────────────────────────┘
                                                  (if reactivation fails,
                                                   creator stays Silent)
```

## What's not yet defined

**The precise threshold** for "silent" — how many days of no posts? Zero GMV this month? Some other heuristic? Pending confirmation. For now, treat Silent membership as **whatever criterion the tab's owner uses** rather than re-deriving it from data.

## Implication for analyses

- Don't infer Silent membership from gmv_data alone (a creator with $0 GMV in May might still be Active and producing for a delayed campaign).
- When a task asks for "silent creators," read from the `Silent` tab rather than computing membership.
- A creator's segment can change month-to-month — Silent in May doesn't mean Silent in June.
