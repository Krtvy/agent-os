# EUKA — Definition

**Source:** Kartavya, 2026-05-13.

## What EUKA is

A **third-party platform** for creator-data enrichment. You give it a CSV list of creator usernames; it returns enriched attributes for each — most importantly:

- **Shop GMV (last 30 days)** — recent revenue from each creator's TikTok Shop activity
- **Category** — what content niche the creator operates in
- Other attributes (audience demographics, engagement metrics, etc. — TBD)

## How it's used at Rootlabs

The team uploads creator lists periodically and pulls the resulting data back into the May workbook (and presumably future trackers). The `EUKA Data 8 May` tab is one such pull — a snapshot from May 8, 2026.

**Primary use cases:**

- Shop GMV lookups when assessing a creator's monetary potential
- Category attribution for segmentation / matching to product fits

## What this means for analyses

- **EUKA tabs are dated snapshots, not live data.** Shop GMV from a May 8 pull is May 8's view of last-30-days revenue; using it on May 13 means the trailing window is now misaligned by 5 days. For freshness-sensitive analyses, re-pull.
- **The CSV-in → CSV-out model means EUKA isn't a live integration.** It's a batch enrichment service. The team submits, waits, and ingests.
- **Don't conflate EUKA Shop GMV with Rootlabs `gmv_data`.** They measure different things — EUKA is TikTok Shop platform-wide, while `gmv_data` is sales attributed to Rootlabs' products (HGR, MagAshwa, etc.). The two will rarely match for the same creator on the same day.

## Pending detail

- Cadence: how often does the team pull from EUKA? Monthly? Weekly? On-demand?
- Exact columns returned beyond Shop GMV + category — need to walk the `EUKA Data 8 May` tab to enumerate.
- Whether EUKA is reachable programmatically (API) or only via manual CSV upload to their web UI.
