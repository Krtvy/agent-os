# MTD (Month-to-Date)

## Plain English

Cumulative count or sum from the **start of the current calendar month** to a
target day. Used heavily for video / creator / GMV counts.

## Same-day-range comparison convention

When showing MTD in the dashboard, the pipeline shows three numbers for the
**same calendar-day range**:

- **M0**: current month, day 1 through target day
- **M1**: previous month, day 1 through the same day-of-month (or last day if
  month is shorter)
- **M2**: two months back, same day range

This is a like-for-like comparison: "How are we doing this month vs the same
window in the previous two months?"

## Date math

Implemented in `_private/daily_reporting/main.py · def compute_mtd_dates`.
The logic handles:

- February (28 / 29 days)
- Months with fewer days than the target day-of-month (e.g. day 31 target →
  M1 ends day 30)
- IST timezone — `target` is an IST-local date

## Provenance

- Per-product MTD video + creator counts:
  `training/queries/video_creator_mtd.sql`
- Python source: `_private/daily_reporting/main.py · def sql_video_creator_mtd(d)`
  and `def compute_mtd_dates(target)`

## NOT to be confused with MoM

MoM in Rootlabs context = trailing 30 days, not calendar month. See
`feedback_yudhishthira` memories for MoM rules.
