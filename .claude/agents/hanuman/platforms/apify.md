# Apify — Platform Knowledge for Hanuman

> Last refreshed: 2026-05-13 from `apify.com` (public marketing pages + docs links).

## What this platform is

**One-liner:** Full-stack web scraping and data extraction platform — serverless, anti-blocking, with a marketplace of pre-built scrapers for popular sites.

**Three-liner:** Apify lets you run "Actors" (serverless scripts) that scrape web data at scale. The Apify Store has ~29,000 pre-built Actors for TikTok, Instagram, Google Maps, Amazon, Facebook, and most other major sites. You can also write your own. Apify handles proxies, anti-blocking, scheduling, and data export.

## What KIND of creator data lives here

Apify is **not a creator-data source** itself. It's the **plumbing that pulls creator data FROM other platforms** (TikTok, Instagram, etc.) on demand. Use Apify when:

- You need TikTok creator-profile data that isn't on the TikTok-Shop side (so Kalodata can't help)
- You need Instagram / cross-platform creator data (which Kalodata and probably Cruva don't cover)
- You need bulk pulls (1,000+ creators) where manual lookup is impractical
- You need data freshness on demand rather than waiting for a monthly EUKA pull

## Coverage / scope

| Platform Apify can scrape | Actor name (high-traffic)               | Use case                                                             |
| ------------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| TikTok                    | TikTok Scraper (176K runs, 4.7★)        | Public profile metrics, posts, video metadata                        |
| Instagram                 | Instagram Scraper (260K runs, 4.7★)     | Profile metrics, posts, follower counts                              |
| Google Maps               | Google Maps Scraper (403K runs, 4.7★)   | Local business data — useful if matching creators to physical brands |
| Amazon                    | Amazon Scraper (12K runs, 4.9★)         | Product / listing data                                               |
| Facebook                  | Facebook Posts Scraper (69K runs, 4.5★) | Public posts                                                         |
| (29,000+ others)          | Browse `apify.com/store`                | Most major sites have a community-built Actor                        |

Freshness: **as fresh as the scrape run.** Run it now, get data from now. Run it weekly, get weekly snapshots.

## Inputs accepted

Per-Actor. Most TikTok / Instagram Actors take:

- Profile URL (`https://www.tiktok.com/@username`) — most reliable
- Username (`@username` or `username`) — usually works
- Search term — for discovery rather than known-creator lookup

Hanuman should default to **profile URL** when given just a handle, to avoid ambiguity.

## Outputs available

Per-Actor; typical TikTok Scraper output includes:

- Profile metrics: follower count, following count, video count, total likes
- Per-video data: video URL, content_id, post date, view count, like/comment/share counts, caption text, hashtags
- Audio data per video (TikTok-specific)
- Optionally: full transcripts if the Actor supports it

Exports: CSV, JSON, Excel, optionally markdown for LLM ingestion.

## Comparative: when to prefer Apify over the others

- **Over Kalodata:** when you need data from TikTok proper (creator side) rather than TikTok Shop (commerce side). Or for non-TikTok platforms (Instagram, etc.).
- **Over EUKA:** when you need on-demand pulls instead of waiting for batch enrichment cycles. Or when you need fields EUKA doesn't return.
- **Over Cruva:** when you need raw platform data instead of CRM-curated views.

**When to NOT use Apify:** when the data you want lives on a logged-in / paywalled page (Apify scrapes public surface area). For example, TikTok Shop's seller-side analytics → not Apify, that's Kalodata.

## Direct extraction (what Hanuman can do alone)

**API access:** Yes — RESTful API at `https://api.apify.com/v2/`. Docs at `https://docs.apify.com/api`.

**SDK access:** Yes — Python and JavaScript SDKs. Docs at `https://docs.apify.com/sdk/`.

**MCP integration:** ✓ — Apify has an MCP server. `https://docs.apify.com/platform/integrations/mcp`. **This is the most relevant integration for Hanuman.** If wired in, Hanuman can call Actors via natural-language MCP rather than constructing HTTP requests.

**Auth:** API token. Each user gets one in the console.

**Free tier:** "$500 free platform credits" for new accounts per Apify's homepage.

**Pricing tiers:** Public homepage doesn't enumerate. Linked from `apify.com/pricing` (not yet fetched). To check before scaling.

## Manual playbook (the "tell Kartavya the steps" mode)

When Hanuman can't or shouldn't extract directly (e.g., he's not wired to the Apify MCP yet, or you specifically want to do the run yourself):

### Task: Get TikTok creator profile + recent posts for a known handle

1. Navigate to: `https://console.apify.com/actors`
2. Search Store for: "TikTok Scraper" (top result is `clockworks/free-tiktok-scraper` or `apify/tiktok-scraper` — pick whichever has higher run count + ★)
3. Click **Try for free** (or **Run** if already saved)
4. In the input form, paste: profile URL `https://www.tiktok.com/@<handle>`
5. Set `resultsPerPage` to the number of recent videos you want (default 30 is fine for most tasks)
6. Click **Start**
7. Wait for run to complete (~30 sec to 2 min for a single profile)
8. Click **Storage → Dataset → Export** → choose CSV or JSON
9. Save to: `pocs/<poc>/raw/apify_tiktok_<handle>_<YYYY-MM-DD>.csv`

### Task: Bulk pull for many handles (50+)

1. Same Actor (TikTok Scraper)
2. In input form, use the `startUrls` field — paste all profile URLs as a JSON array `[{"url": "..."}, {"url": "..."}, ...]`
3. Increase `maxConcurrency` to 5–10 (be polite — don't get rate-limited)
4. Run, export, save

### Task: Schedule a recurring pull

1. After running an Actor once and confirming output, go to: Actor page → **Schedules** tab
2. **+ Create schedule** → cron expression (e.g., `0 2 * * *` for daily 02:00 UTC)
3. Tie the schedule to a specific input set
4. Outputs persist to Datasets, queryable later

## Failure modes

- **Anti-bot blocks.** If a target site is aggressive (e.g., Cloudflare-protected), some Actors fail. Switch to a different Actor for the same platform, or one that uses paid proxies.
- **Stale Actors.** Community-built Actors decay when target sites change their HTML. Check the Actor's "last successful run" date before relying on it for production.
- **Rate limits.** TikTok and Instagram both rate-limit aggressively. Bulk pulls of 1,000+ creators in one run will often fail mid-way; chunk into batches of 50–100.
- **Cost surprise.** Long-running scrapes consume credits. Set max-cost or max-runtime limits on every run.

## Pricing / quota

Free tier: $500 in platform credits. Beyond that, pay-as-you-go (compute units + proxy bandwidth + dataset storage). Pricing page not yet fetched. **Recommend: check current pricing before any task that pulls >1,000 records.**

## Login URL

- Sign up: `https://console.apify.com/sign-up`
- Log in: `https://console.apify.com/sign-in`
- Console (post-login): `https://console.apify.com/`
- Docs (no login needed): `https://docs.apify.com/`
- Store (no login needed for browsing): `https://apify.com/store`

## What I still don't know about Apify

- Pricing tiers and per-Actor costs (need to walk `apify.com/pricing`)
- Whether Rootlabs has an existing Apify account + which user owns it
- Whether the Apify MCP is wired into Hanuman's runtime yet (per agent.md frontmatter, `mcps: [kalodata, cruva]` — Apify is NOT listed)
- Specific Actor recommendations for our use cases (need a few real runs to identify the best ones)

## Adding Apify to Hanuman's MCP list (constitutional change pending)

The current `hanuman/agent.md` frontmatter declares `mcps: [kalodata, cruva]`. Adding Apify is a constitutional change per Bhishma R23 (touches `mcps`). Should go through proposal flow: write proposal at `_meta/observer/proposals/`, Sahadeva endorses Sunday 2026-05-17, Kartavya commits.

## Source

This file built from public WebFetch of `apify.com` on 2026-05-13. Marketing pages only — the actual product UI is auth-walled. Refresh this file when:

- Pricing changes
- A specific Actor proves load-bearing for a recurring task (add to the comparative table)
- The Apify MCP is wired into Hanuman (update the "Direct extraction" section)
- A creator-data Actor we use frequently has a known quirk (add to Failure modes)
