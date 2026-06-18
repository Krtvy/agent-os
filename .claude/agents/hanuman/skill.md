# hanuman — Skill Manual

> Last updated: 2026-05-10 by bootstrap

## Purpose

Hanuman scouts a creator (or a batch of creators) and produces a markdown report with tier-tagged sources, a fit assessment, and risk flags. Read-only on all external systems. Heavy use of a local cache to avoid hammering APIs.

## Inputs

- `targets` (required) — handle, URL, or list.
- `depth` (optional, default `shallow`) — `shallow` or `full`.
- `sources` (optional) — restricted source list.
- `cache` (optional, default `respect`) — `respect` or `bypass`.
- `purpose` (optional) — context for the fit-assessment section.

## Outputs

A markdown file per target at `research/creators/<handle>-<YYYYMMDD>.md`. Format defined in `agent.md` § "Your outputs."

## Procedures

### P1. Bhishma load

- Read `bhishma.md`. Stop on missing file.

### P2. Input normalization and dedup

- For each target: strip `@`, lowercase, resolve URL → handle.
- Deduplicate the resulting list.
- Emit one report per unique handle.

### P3. Handle resolution

- Per `agent.md` § "Handle resolution." Set `handle_resolution: confirmed | redirected | unresolved`.
- If unresolved: write a stub report with the fact, exit for that handle.

### P4. Cache check (per source per handle)

- Steps:
  1. Read `.claude/agents/hanuman/cache/<handle>.json` if present.
  2. For each source key in the cache, check `fetched_at` against TTL.
  3. If within TTL and `cache: respect`: mark this source as cached.
  4. If outside TTL or `cache: bypass`: queue a fresh fetch.

### P5. Source fetch

- For each queued source:
  1. Issue a GET to the Kalodata MCP / TikTok public profile / Cruva MCP / web search.
  2. Capture response, timestamp, and source URL.
  3. Update the cache with `fetched_at: <UTC ISO8601>`.
  4. If fetch fails and a stale cache exists: use the stale cache, mark `[STALE: <source> data is <N>h old]`.

### P6. Data classification

- For each captured fact, tag with T1–T5 tier (per agent.md rubric).
- Note the "as of" date.

### P7. Fit assessment

- Compute audience overlap with the stated `purpose`.
- Estimate CPM tier (low / mid / high) by combining niche + size.
- Output a recommendation: strong fit / acceptable / weak fit / pass.
- Output a confidence: high / medium / low.

### P8. Risk flag scan

- Scan recent post titles and captions for off-brand keywords.
- Cross-check with WebSearch for "controversy" results.
- Flag any disclosure-pattern issues (e.g., low #ad usage on visibly sponsored posts).

### P9. Write report and log

- Compose the markdown report per `agent.md` format.
- Save to `research/creators/<handle>-<YYYYMMDD>.md`.
- Append to `logs/hanuman/<run_id>.log` a single line with run_id, target count, sources used, and write path.

### P10. Daily competitor TikTok content discovery (added 2026-05-11, revised v2)

A second procedure path, run on cron, NOT the per-creator scout path above.

**Why hashtag-first (revision 2026-05-11):** Initial v1 design scraped brand-owned TikTok accounts (@bloomnutrition, @goli, etc.). Empirical testing revealed these accounts post 3-10 videos per quarter — virtually no signal. The actual competitive content for DTC supplement brands lives in **creator-affiliate videos tagged with brand hashtags** (e.g., #bloomnutrition, #goli). Schema v2 makes hashtag discovery primary; known partner creators are an optional second pass.

**Trigger.** Nightly at 23:00 IST via `scripts/competitor-discovery.sh` (called by Nakula).

**Apify actors:**

- `clockworks/tiktok-hashtag-scraper` — for hashtag pass (primary signal source)
- `clockworks/free-tiktok-scraper` — for known-creator pass (use the `free-` variant; the non-free `tiktok-scraper` truncates output on free Apify tier)

**Inputs.**

- `competitors_file` — defaults to `.claude/agents/hanuman/competitors.yml` (schema v2)
- `date` — defaults to today in UTC
- Apify tokens — read from `.credentials.yml` (`apify.tokens` list) with rotation on 429/5xx/4xx

**Two-pass design.**

For each enabled competitor, the script generates work units:

- **Hashtag units** — one per entry in `competitors[].hashtags[]`. Calls `tiktok-hashtag-scraper` with `{"hashtags":[<tag>],"resultsPerPage":<videos_per_hashtag>}`.
- **Creator units** — one per entry in `competitors[].known_creators[]`. Calls `free-tiktok-scraper` with `{"profiles":[<handle>],"resultsPerPage":<videos_per_creator>}`.

Each video record carries provenance: `source: "hashtag" | "creator"` and `source_value: "<tag-or-handle>"`. Same video appearing under multiple work units within a brand is deduped by `video_id` (keep first).

**Recency filter.** After fetching, drop videos posted before `now - defaults.recency_window_hours` (default 168 = 7 days). This keeps the analyzed corpus focused on currently-trending content.

**Known-creator auto-discovery (future).** Sanjaya observes which creators repeatedly appear under a brand's hashtag posts. When a creator surfaces ≥N times for a brand over M days, Sanjaya may propose adding them to that brand's `known_creators[]` for the creator pass.

**Outputs.**

- Per brand per day: `competitor_content/raw/<slug>/<YYYY-MM-DD>.json` with this shape:

  ```json
  {
    "brand_slug": "bloom-nutrition",
    "handle": "bloomnu",
    "pulled_at_utc": "2026-05-11T17:30:00Z",
    "videos": [
      {
        "video_id": "7234567890",
        "url": "https://www.tiktok.com/@bloomnu/video/7234567890",
        "posted_at_utc": "2026-05-11T09:14:00Z",
        "views": 84200,
        "likes": 6100,
        "comments": 240,
        "shares": 980,
        "caption": "...",
        "hashtags": ["#bloom", "#greens"],
        "duration_seconds": 23,
        "thumbnail_url": "..."
      }
    ]
  }
  ```

- An update to `competitor_content/raw/.last-discovery` (single-line ISO8601 UTC timestamp) so Nakula's upstream-freshness check passes.

**Steps.**

1. Read `bhishma.md` (R1+R16 — required on every run).
2. Parse `competitors.yml`. Filter to `enabled: true`. Validate each `slug` follows the slug rules.
3. For each enabled competitor:
   1. Compute the dedup window: the previous day's `competitor_content/raw/<slug>/<YYYY-MM-DD>.json` (if it exists).
   2. Call Apify's TikTok scraper actor for the handle with `resultsPerPage: <videos_per_pull>` and `dateFrom: <yesterday>` (Apify's parameter names — confirm against actor docs).
   3. Dedup the response against the previous-day file (by `video_id`).
   4. Write the new-only video set to today's per-brand JSON.
   5. Log to `logs/hanuman/<run_id>-discovery.log`: brand, fetched count, kept-after-dedup count, error if any.
4. Write `competitor_content/raw/.last-discovery` with the current UTC ISO8601 timestamp.
5. If any brand fails (Apify timeout, handle 404, rate limit), continue with the others — partial success is acceptable. Failed brands are logged and surfaced in the run summary.
6. Run summary printed to stdout:
   - Per-brand: discovered N, kept M after dedup, errors: [...]
   - Total new videos this cycle: K
   - run_id: `hanuman-<YYYYMMDD-HHMMSSZ>-<6char-hash>` per R20.

**Constraints.**

- Read-only on TikTok. Never POST, never DELETE, never message a creator.
- No analysis happens in P10 — that's Arjuna's video-analyze job downstream.
- If Apify access is missing or the actor errors out repeatedly, write a stub JSON with `videos: []` and `error: "<reason>"`, exit gracefully. The pipeline continues; Sahadeva will flag the gap in next weekly audit.

**Cache.** Discovery results don't use the per-creator cache (P4) — each daily pull is intentionally fresh. The dedup window is the SOLE deduplication mechanism for this path.

## Heuristics

- _(none yet)_

## Confidence (read-only reference)

> Confidence weights are defined in `_meta/conductor/bhishma.md` under "Confidence-scoring weights."

## Run-id format (read-only reference)

> Run-id format is defined in `docs/RUN_ID_SPEC.md`.

## Change log

- 2026-05-10 — bootstrap — initial skill manual.
- 2026-05-11 — added P10 (daily competitor TikTok discovery procedure) for the competitor content analysis pipeline. Reads `competitors.yml`, writes per-brand per-day JSON to `competitor_content/raw/`.
- 2026-05-11 (v2) — revised P10 to hashtag-first design after empirical test showed brand-owned accounts have ~zero recent content. competitors.yml schema bumped to v2 with `hashtags[]` and `known_creators[]` per brand. Discovery script rewritten as two-pass (hashtag + creator) with provenance tagging, recency filter, and per-brand dedup by video_id.
