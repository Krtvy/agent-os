# Research-Agent — Handoff / Progress Save

> **Last update:** 2026-05-11 · **Session origin:** Rootlab competitive-intel sprint (May 6–7) · **Status:** Paused mid-stream by user

## What this project is

A standing competitive-intel operation for **Rootlab** (Mosaic Wellness's US TikTok-Shop supplement brand — MagAshwa gummies + Magnesium + Alpha GPC). Produces deep brand profiles, cross-brand synthesis, and recurring monthly snapshots so Rootlab decisions are continuously informed by what 15 reference brands are executing.

## What's been built (all surviving in `docs/`)

**Growth playbook (one-shot deliverable):**

- `2026-05-06_rootlab_growth_playbook.html` — 20 prioritized actions across acquisition / retention / conversion / habit-change (top-level in this folder, not in `docs/`)

**Competitor profiles (15, in `docs/competitor_profiles/`):**

- Tier A — TikTok-Shop natives (deep coverage, all 4 dimensions): nello, neuro, snap_supplements, maryruths, goli, bloom_nutrition
- Tier B — adjacent stress/sleep/focus: magic_mind, moon_juice, hims_hers_adaptogens, calm _(Natural Vitality CALM — see Correction below)_
- Tier C — established/retail benchmarks: ag1, ritual, seed, olly, momentous

**Synthesis artifacts in `docs/`:**

- `competitor_matrix.html` — 15 brands × 4 dimensions, color-coded known / partial / gap
- `creator_commissions_sidebyside.md` — explicit gap-fill with real commission data
- `campaign_cadence_calendar.md` — 12-month rolling promo calendar
- `habit_tactics_inventory.md` — every observed habit tactic, prioritized menu

**Original research pillars (pre-existing, reused):**

- `docs/research_acquisition.md`, `research_retention.md`, `research_conversion.md`, `research_habits.md`
- `docs/doc_brand_case_studies.md` (8 legacy brand case studies — Tier-C profiles supersede)
- `docs/doc_personalization_report.md`

**Templates (in project `.claude/templates/` — verify they survived the reorg):**

- `competitor_profile_template.md` — fixed D1–D4 schema
- `monthly_snapshot_template.md` — ≤4-hr monthly cadence template

## The four-dimension profile schema (load this into memory before resuming)

Every profile fills:

- **D1** — Creator program & affiliate design (commission %, payout structure, sample policy, gamification, creator scale, Spark Ads, compliance brief)
- **D2** — Site & app teardown (PDP, hero claim, quiz funnel, bundle structure, free shipping, sub default, sub discount, app)
- **D3** — Deals & campaign cadence (always-on, sub %, BFCM, holiday calendar, bundle %, volume, promo cadence)
- **D4** — Habit-change tactics (packaging cues, dosage, onboarding, SMS/wallet, identity framing, community, streaks)

Each profile ends with **"What Rootlab should steal / NOT copy"** — that's the deliverable, not the description.

## Material correction logged (do not repeat)

The **"Calm" profile (`calm.md`) was rewritten on May 7** — original was based on Calm Inc. (the meditation app, $596M revenue 2024), which **does not currently sell a supplement**. The actual on-shelf competitor is **Natural Vitality CALM** — 1982-founded magnesium brand, owned by Nutranext → WM Partners LP. The file now correctly profiles Natural Vitality. If a future Calm-Inc. supplement launch happens, that's a high-threat new entrant (watchlist).

## Concrete commission data captured May 7 (the dataset's biggest gap-fill)

- **Goli:** 10–25% tiered; 25% unlocks at $5K creator GMV. Non-cash rewards: iPhones, Miami retreats, BMW. $4.1M/mo TikTok Shop + $3.8M/mo Amazon halo.
- **Nello:** Shopify Collabs payouts; **Nello Nation Facebook Group + monthly competitions + meet-ups**. "Performance-based, revisited per results."
- **NeuroGum:** **Discord-tier creator guild** with GMV thresholds + luxury rewards + founder engagement. 13% US brand awareness 2024. One creator (@Espindeezy) drove $450K in a month. Investors: Scooter Braun, Gary Vaynerchuk, Steve Aoki.
- **Bloom:** Dual-track — public ShareASale + exclusive Ambassador program. Best-fit content types: "What I eat in a day," gym vlogs, morning routines.
- **Industry effective cost:** A 15% nominal commission → ~26.6% true cost when accounting for platform-funded subsidies, co-funded shipping, and clawbacks. Model affiliate unit economics at 25–30%, not nominal.
- **80/20 holds at scale:** Physician's Choice ran 2,000+ creators; **top 10% (200 creators) drove 80% of revenue.**

## Recommended Rootlab program design (current synthesis)

| Tier                              | Compensation                                        | Scale target            | Source pattern                             |
| --------------------------------- | --------------------------------------------------- | ----------------------- | ------------------------------------------ |
| Long-tail volume (5K–50K)         | 15% baseline + samples + Shopify Collabs            | 500–1,000+/mo           | Bloom + Nello + Goli baseline              |
| Mid-tier wellness (50K–500K)      | 20%, unlocks at $3K creator GMV + sample priority   | 50–100                  | Goli's tiered structure (slightly tighter) |
| Credentialed (RDs, MDs, trainers) | 25% + Spark Ad whitelist + branded credibility card | 20–30                   | Seed University + MaryRuth's               |
| Top-tier creator guild            | Discord-tier with founder access + non-cash rewards | 20–50 proven performers | NeuroGum + Goli rewards                    |
| Expert co-creators                | Co-branded protocol or revenue share / equity       | 1–3 named               | Momentous model                            |

Plus: trackable URL per creator day 1 (AG1), 60-day CPA-cut review (Seed), Spark Ad spend = 20% of organic-creator GMV (Neuro), model true cost 25–30% of GMV.

## Open thread — where to pick up

**Task #5** ("gap-fill sprint") is functionally complete but never marked done because the session was interrupted. **The one thing not yet generated** is the inaugural monthly snapshot at `docs/snapshots/2026-05.md` — template lives in `.claude/templates/monthly_snapshot_template.md`. ≤4 hours of effort to produce.

After that, the system's quarterly cadence is owed (rebuild category numbers in `dtc-supplements.md`, refresh all Tier A profiles, scan for new entrants).

## Highest-priority remaining gaps (for next snapshot)

1. **Specific commission % for SNAP, MaryRuth's, Magic Mind, Moon Juice, Natural Vitality CALM** — still unknown. Sign up as TikTok Shop creator → receive program invites.
2. **Site teardowns** for Nello, SNAP (D2 is thin for these).
3. **Onboarding email + cancel flow** for every Tier A — sign up + capture over 30 days.
4. **Verify the Calm Inc. watchlist** quarterly — any supplement-line launch = high-threat entrant.

## How to resume

1. Read this file.
2. `ls docs/competitor_profiles/` to confirm the 15 profiles are intact.
3. Open `docs/competitor_matrix.html` in browser for the 1-screen overview.
4. Read `CLAUDE.md` (project rules, especially the Competitive Monitoring System section).
5. Pick: (a) generate May 2026 snapshot, (b) deepen a specific profile, or (c) generate a new synthesis cut.

## Filesystem notes

- Original location `/Users/mosaic/research-agent/` was deleted between May 7 and May 11.
- Current home: `/Users/mosaic/projects/observer-test/.claude/agents/research-agent/`
- Sibling output folder (different project context): `/Users/mosaic/projects/observer-test/research/` — has May 7 / May 8 work (`rootlabs_customer_playbook_v3.md`, `rootlabs_emails_feed.html`) that may be related but is separate from this research-agent's outputs.
- An archive `research-agent-complete.tar.gz` exists in this folder — safety net if anything else gets reorganized.
