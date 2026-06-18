# Kalodata — Platform Knowledge for Hanuman

> **Imported 2026-05-13 04:19 IST** from `/Users/mosaic/creator-intel/platforms/kalodata.com-map.md` (mapped 2026-04-29 live from a logged-in browser session).
>
> **Product URL:** https://www.kalodata.com
> **Auth:** Google OAuth only — no email/password signup. Session persists in browser cookies.
> **Plan in use at Rootlabs:** Professional ($83.2/mo) — confirmed via `/Users/mosaic/creator-intel/PROJECT-STORY.md`.
>
> The full content below is the **canonical Kalodata UI map** as walked top-to-bottom in a logged-in session. Every nav item, every filter, every page, every creator-profile section — captured as it appears in the actual product. This is the authoritative reference Hanuman uses for any Kalodata-touching task.
>
> ⚠ **Critical operational caveat from `PROJECT-STORY.md`**: Kalodata aggressively locks accounts on suspected scraping. Concurrency >1 is enough to trigger a lock. Even at 2-second pacing the cumulative daily quota can fire `risk-dispose-type: triggerTooManyTimes`. The internal endpoint `POST /creator/detail/total` returns exact category-filtered GMV (e.g., `cateIds: [700645]` = Health) — but use with extreme rate-limit discipline. **Default: tell Kartavya the manual playbook steps unless an explicit task budget for automation is approved.**
>
> Vidura's third-party research **integrated 2026-05-13 04:33 IST** (see appendix at end of file — 14 tier-tagged sources A1–A14 covering pricing reviews, competitive comparisons vs FastMoss/EchoTik, Trustpilot billing complaints, and Reddit-reported data-accuracy gaps). The canonical UI map below remains the operational ground truth; the appendix adds context, not authority.
>
> Companion files: [`apify.md`](apify.md) · [`cruva.md`](cruva.md) · [`README.md`](README.md). Operational story: `/Users/mosaic/creator-intel/PROJECT-STORY.md`.

---

# Kalodata Site Map

**Site:** Kalodata — TikTok Shop analytics & insights
**URL:** https://www.kalodata.com
**Mapped:** 2026-04-29
**Mapped while logged in as:** Abhinav ([REDACTED]), **Professional** plan, region **United States**, shop **RootLabs**
**Auth method:** Google OAuth only (no email/password). Session persists in browser cookies.
**Public marketing pillars:** Trending Product Analysis · Influencer Collaboration · Advertising Optimization · Competitor Insight
**Data scale claims:** 200M+ products · 250M+ creators · 400M+ videos & livestreams · 1000 days history
**Data caveat (per Kalodata FAQ):** "Data is processed by algorithm, for reference only" — small variations from real-world numbers expected; Kalodata explicitly says NOT to use it for partner commission settlements or performance evaluations.

---

## Global Header (every authenticated page)

Left to right:

| Element            | Behavior                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| Kalodata logo      | Returns to /explore                                                                               |
| TikTok pill (▾)    | Platform switcher: TikTok / Amazon / Shopee (cross-platform requires Professional+ tier)          |
| Explore            | /explore (dashboard)                                                                              |
| Category ▾         | Dropdown: **Category Ranking** (/category) and **Market Landscape** (/overview, Enterprise-gated) |
| Shop               | /shop                                                                                             |
| Creator            | /creator                                                                                          |
| Product            | /product                                                                                          |
| Video & Ad         | /video (has AI badge)                                                                             |
| Livestream         | /livestream                                                                                       |
| APP                | App download (icon)                                                                               |
| 🇺🇸 United States ▾ | Region switcher (purchased per-region: US-only or US/UK/EU bundle)                                |
| Pricing            | /pricing                                                                                          |
| Theme toggle       | Light/dark                                                                                        |
| Avatar (initial)   | User dropdown → see "Avatar dropdown" below                                                       |

### Avatar dropdown items

- **Plan badge** ("Professional" / "Starter" / "Enterprise") + Edit link
- User name + email
- Membership Management
- My Following
- Live Recording (with red dot when new recordings ready)
- Contact us
- User Guide
- Blog
- Log out

---

## Page-by-Page

### `/` (homepage, public)

Marketing site. Headline stats (200M+/250M+/400M+/1000 days), client logos (Cool-Vita, MAYBELLINE, JNSO, BIOAQUA, Etowalin, WOOK?, Kelaya), four feature mocks (Trending Products, Influencer Collaboration, Advertising Optimization, Competitor Insight), FAQ. CTA "Start Free 7-day Trial" → forces /signup → Google OAuth. **No email/password signup option.**

### `/explore` (dashboard, authenticated)

- **"Just Ask – Get AI-Powered Insights"** — free-text textbox + 6 quick-prompt buttons:
  - Seller Analysis · Account Analysis · Product Selection Suggestions · Influencer Marketing · Video Creation · Kalodata Usage Inquiry
  - Each request consumes "credits" (Starter: 10/mo · Professional: 70/mo bonus · Enterprise: unlimited). Recharge $9.99/100 credits.
- **Two top tabs:** 🔥 Hot-selling Ranking | 🗂️ My Following
- **Sub-tabs (under My Following / Hot-selling):** Product · Creators · Shops · Video · Script
- **Date filter:** Yesterday · Last 7 / 30 / 90 / 180 Days · Last 365 days _(Enterprise-only; greyed)_
- **Group** dropdown for grouping followed items
- **KPI cards** when on Shops tab: Shop Number · Revenue · Self-Account Revenue · Affiliate Revenue · Shopping Mall Revenue
- **Add Shops** button (CTA)
- **Kalodata Academy** strip with 6 quick-launch tiles: Trending Products / Competitors' List / Affiliate Creators / Brand Strategy / Hot Videos / Hot Lives + blog post tiles
- **Onboarding tutorial banner** — "Watch Now" video walk-through

### `/category` — Category Ranking

- **Page title:** "Category Rank in United States TikTok"
- **Tabs:** All Categories | 🌱 Blue Ocean Niche Categories _(preset: Revenue Growth Rate >0, Top 3 Shop Revenue Ratio 0–50, Category Level L3)_ | 🔥 Rapid Growth Categories _(preset: Revenue Growth Rate ≥100%)_
- **Filters (left rail):** Dates · Category · Category Level · Revenue($) · Revenue Growth Rate · Revenue per Shop($) · Top 3 Shop Revenue Ratio · Top 10 Shop Revenue Ratio
- **Save selected filters** option · Reset · Submit
- **Search:** category name (Enter to search)
- **Toolbar icons:** play (video help), settings, **Export** (gated)
- **Table columns:** Category · Revenue · Best-selling Products · Revenue Growth Rate · Revenue Trend · Number of Shops
- **Pagination:** up to ~255 pages of category data (Last 30 Days)
- **Footer:** "Data processed by algorithm, for reference only."
- **Snapshot of top 5 (Last 30 Days, captured 2026-04-29):** Beauty & Personal Care $314.18m (-6.47%) · Womenswear & Underwear $236.39m (+2.74%) · Sports & Outdoor $137.40m (+0.65%) · Health $113.69m (-10.82%) · Nutrition & Wellness $109.77m (-11.10%).

### `/overview` — Market Landscape _(Enterprise-gated)_

- **Treemap** of all 27 L1 categories with sub-category drill-down (clickable to nest in)
- **Toggle:** Show Sub-Category · Color Preference (Blue Up, Red Down)
- **Right-side metric cards (all gated):** Core Metric · Price Range (Avg. Unit Price visible: $22.20) · New Product Performance (New Product Market Share: 8.26%)
- **Sales Strategy** section
- **Lock overlay:** "Upgrade to Enterprise to view the data" → View Sample Data | Unlock Now
- **Filter rail:** same shape as Category Ranking
- **What's visible without Enterprise:** treemap layout + sub-category growth-rate text labels (e.g., Beauty & Personal Care -24.21%, Skincare -20.71%, Makeup -34.11%, Fragrance -21.66%, etc. — note all categories show negative MoM growth at this snapshot).

### `/shop` — Shop Rank

- **Tabs:** All Shops | 💼 Best Self-Operated Shops | 🧩 Best Brand Shops | 🔥 Sales Grow Rapidly
- **Filters:** Dates · Category · Revenue($) · Revenue Source · Revenue Growth Rate · Avg. Unit Price($) · Seller Type
- **Search:** shop name
- **Star icon** on each row → adds to "My Following"
- **Table columns:** Shop Info · Revenue · Best-selling Products · Revenue Trend · Revenue Growth Rate · Item Sold · Avg. Unit Price · Self-Operated Accounts Revenue · Affiliate Revenue · Shopping Mall Revenue · Live Revenue · Video Revenue · Product Card Revenue
- **Top 5 (Last 30 Days):** medicube US Store $19.78m · Shark Home $14.90m · QVC, Inc $14.31m · Dr.Melaxin $13.76m · Halara US $10.45m

### `/creator` — Creator Rank ⭐ (primary page for our use case)

- **Tabs:** All Creators | (user-saved) **Health | Live | 25K+** | 🆕 Emerging Creators | 🎬 Top Video Creators | 🎦 Top Live Creators
- **Filters:**
  - **Basic:** Dates · Category · Revenue($) · Revenue Source · Revenue Trend
  - **Advanced:** Account Type · Followers · Engagement Rate · **Creator Contact** · **MCN Status** · Creator Debut Time · Avg. Unit Price($)
  - **Followers:** Age (and other audience demographics)
- **Search:** "Search creator's name or handle and press Enter to search"
- **Table columns:** Creator Info · Revenue · Item Sold · Followers · Follower Change · Best-selling Products · Revenue Trend · Content Views · Creator Debut Time · Avg. Unit Price
- **Per-row actions:** Star (follow), TikTok external link icon
- **Top 5 (Last 30 Days):** @based ($2.52m, 3.1m followers) · @be.lush ($2.42m, 257.2k) · @trending_ttok ($2.13m, 194.3k) · @bestiebriitt ($1.54m, 129.6k) · @hannahbentl... ($1.28m, 57.4k)

### `/creator/detail?id=<creatorId>&region=US&dateRange=[start,end]&cateValue=[]` — Creator Profile ⭐

**URL pattern** (capture creator id from row, then build URL — also opens via in-row click in new tab).

Sections from top to bottom:

1. **Header**
   - Avatar · `@handle` · Follow button · Live Recordings button
   - **MCN Status** badge ("Not Signed" / signed agency name)
   - **Shop link** (clickable to shop detail)
   - **Debut Time** (account creation date on TikTok Shop)
   - **Creator Bio** (TikTok bio text)
   - **Followers** (with audience-quality help tooltips: "Majority Male/Female", age band like "18-24")
   - **Last 30 Days Products** (count of products promoted)
   - **Creator Contact** card on the right (email or TikTok handle, with copy icon — exporting bulk requires Professional plan or recharge $69.9/1000)
   - **The earliest date recorded:** YYYY-MM-DD (Kalodata's tracking start)

2. **Filter bar:** All Shops dropdown · All Categories dropdown · Date range picker · quick-pick (Yesterday/Last 7/30/90/180/365)

3. **Core Metrics card** (toggle: Default Mode | Interactive Mode)
   - 8 KPI tiles + revenue trend chart on the right
   - **Tiles:** Revenue · Live Revenue · Video Revenue · Showcase & Other Revenue · Avg. Unit Price · Live Views · Video Views · Follower Change
   - Each tile shows total + per-day average
   - Click a tile to switch the chart to that metric

4. **Shop section**
   - Lists shops the creator is affiliated with
   - Columns: Shop Info · Revenue · Product Count · Item Sold
   - Per-row Export (gated)

5. **Video & Ad section**
   - Filters: Product Attached · Ad Revenue Ratio · Ad View Ratio · Ad Spend · Ad ROAS
   - Columns: Video (thumbnail + caption + duration) · Product · Revenue · Views · Ad Revenue Ratio · Ad View Ratio · Ad Spend · Ad ROAS · Publish Date
   - Each row clickable into video detail

6. **Product section**
   - Filters: Shipping Option
   - Columns: Product Info · Revenue · Item Sold · Avg. Unit Price

7. **Live section**
   - "Subscribe to full live recordings" CTA (recharge $3.99 / 5 recordings)
   - Live recording table (when available)

8. **Followers section** (NEW badge)
   - **Gender** pie chart
   - **Age** donut chart
   - **Top 5 Locations** bar chart
   - **Top 5 Languages** bar chart
   - **Active Hours** bar chart (24-hour distribution)

### `/product` — Product Rank

- **Tabs:** All Products | 🆕 Top New Products | 👍 High Potential Affiliate | 🔥 Sales Grow Rapidly | 🎬 Top Video Products
- **Filters:** Dates · Category · Revenue($) · Item Sold · Revenue Source (Content) · Revenue Source (Channel) · Revenue Growth Rate · Avg. Unit Price($) · Is Affiliate Product · Creator Number · Creator Conversion Ratio · Shipping Option · Launch Date · Commission Rate
- **Search:** product name (use local language)
- **Toolbar:** image-search button (gated to Professional+) · grid/list view · **Create Shoppable Videos** (AI feature) · Export
- **Table columns:** Product Info · Revenue · Revenue Trend · Revenue Growth Rate · Item Sold · Avg. Unit Price · Commission Rate · Creator Count · Launch Date · Creator Conversion Rate
- **Notable competitor (relevant for MagAshwa context):** Toplux Magnesium Complex 8 Essential Magnesium — $2.88m revenue, +18% growth, 204.09k items sold (Last 30 Days)

### `/video` — Video & Ad Rank

- **Tabs:** All Videos | 🎯 High ROAS | 📊 High Organic Traffic Sales Videos | 🏅 Low-Follower Sales Videos
- **Filters:** Dates · Category · Revenue($) · Revenue Trend · **Ads:** Ad View Ratio · Ad Spend · Ad ROAS · Views · Creator Followers · Duration(s) · Creator Debut Time · Publish Date
- **Search:** hashtag or keyword
- **Toolbar:** **Create Shoppable Videos** (AI badge)
- **Per-row CTA:** "Video Toolkit" link (per-video deeper analysis)
- **Table columns:** Video · Revenue · Item Sold · Revenue Trend · Views · Ad View Ratio · Ad Spend · Ad ROAS · Publish Date
- AD-tagged videos (paid ads) shown alongside organic.

### `/livestream` — Livestream Rank

- **Tabs:** All Livestreams | 💁 Low-Follower High-Revenue Lives | 💼 Shop Self-Operated Lives | 🎦 Lives With Recording
- **Filters:** Dates · Category · Revenue($) · **Live Recording** · Product Source · Creator Followers · Avg. Unit Price($) · Time Range
- **Recording-status legend** above table: Long Recording / Snippet / No Recording (icons on cover)
- **Search:** creator name or handle
- **Table columns:** Livestream Content (thumbnail, title, @creator) · Revenue · Best-selling Products · Live Time (start ~ end + duration) · Views · GPM
- **Top 3 (Last 30 Days):** @simplymandys "Birthday Mega Live" $806.95k (10h23m) · @based "60% OFF SPRING SALES" $319.31k (89h11m) · @jeffreestar "ABDUCTION 24 HR SHOP LIVE" $221.88k (24h2m)

### `/pricing`

**Three tiers (USD/month, 20% off Yearly):**

|                                | Starter $38.3/mo         | Professional $83.2/mo   | Enterprise (Custom — "Contact CHARM" partner) |
| ------------------------------ | ------------------------ | ----------------------- | --------------------------------------------- |
| Searches/day                   | 50                       | 250                     | unlimited                                     |
| Top shops/creators per search  | 10                       | 500                     | full                                          |
| Detail pages/day               | 100                      | 500                     | unlimited                                     |
| Data range                     | 90 days (excl. category) | 180 days                | full                                          |
| AI Credits/mo                  | 10                       | 70 (limited-time bonus) | (varies)                                      |
| Sub-accounts                   | 0                        | 1                       | custom                                        |
| Cross-platform (Amazon/Shopee) | ❌                       | ✅                      | ✅                                            |
| Export creator contacts        | ❌                       | ✅                      | ✅                                            |
| Video-Ads analysis             | ❌                       | ✅                      | ✅                                            |
| Creator contacts               | ❌                       | ✅                      | ✅                                            |
| Image Search                   | ❌                       | ✅                      | ✅                                            |
| **Market Landscape analysis**  | ❌                       | ❌                      | ✅                                            |
| 1-on-1 Professional consulting | ❌                       | ❌                      | ✅                                            |
| **Shop detail pages**          | ❌                       | ❌                      | ✅                                            |
| API access                     | ❌                       | ❌                      | ✅                                            |

**Recharge add-ons (one-off purchases):**

- Credits: $9.99 / 100
- Live Record: $3.99 / 5 recordings
- Video Download: $0.59 / 10 videos
- Sub-Account: $59.9 / month
- Data export: $69.9 / 1000 items
- Creator contacts export: $69.9 / 1000 items

**Customized Data Report (one-off):** From $358 — Data Export · Category Strategy · Brand Diagnosis (talk to team).

**Region toggle:** "United States" or "US, UK & EU" — the country/region you can view is locked at purchase time. Switching regions later requires repurchase.

### Other public pages

- `/blog` — blog (off-domain link in header: kalodata.com/blog)
- `/contact` — contact form
- `/legal/privacy` and `/legal/terms`
- `/sitemap.xml`

---

## Creator Search Workflow (Lookup Mode)

To find a creator on Kalodata:

```
1. Navigate to https://www.kalodata.com/creator
   → If redirected to /signup, session expired. Ask user to log in via Google OAuth.
2. Click the search input ("Search creator's name or handle and press Enter to search")
3. Type the handle (with or without @) or display name, press Enter
4. Search returns full-text matches in the All Creators tab — exact handle is usually #1
5. Click the creator handle in the row (it's a styled blue text link inside the
   "Creator Info" column — NOT the small TikTok logo icon, which opens external TikTok)
   → Profile opens in a NEW TAB at /creator/detail?id=<numeric_id>&region=US&dateRange=[...]
6. Optional shortcut: capture data-row-key from the row's <tr> (numeric creator id)
   and build the URL directly:
   https://www.kalodata.com/creator/detail?id=<id>&language=en-US&currency=USD&region=US&dateRange=%5B%22YYYY-MM-DD%22%2C%22YYYY-MM-DD%22%5D&cateValue=%5B%5D
```

## Creator Profile Data Extraction

On the profile page, scroll vertically — all sections are stacked:

1. Header → name, follower count, MCN status, debut date, bio, **TikTok contact handle**, follower demographics summary
2. Core Metrics → 8 KPIs + chart (Revenue, Live Revenue, Video Revenue, Showcase & Other Revenue, Avg. Unit Price, Live Views, Video Views, Follower Change)
3. Shop table → which shops they sell for + revenue per shop
4. Video & Ad table → top videos with revenue, views, ad spend, **ROAS** — the "is this creator running paid amplification" signal
5. Product table → top products they've promoted with revenue + units
6. Live table → live recordings (subscription-gated, $3.99/5)
7. Followers section → Gender, Age, Top 5 Locations, Top 5 Languages, Active Hours (charts only — no raw % text in DOM, must read SVG/tooltips)

To extract structured data: use `browser_evaluate` to walk the table rows. Each row has a stable `data-row-key` (Kalodata creator/product/video ID). Tables are Ant Design (`.ant-table-row`).

---

## Gated Features (what costs more)

- **Last 365 days date range** — Enterprise only
- **Market Landscape (`/overview`)** — Enterprise only
- **Shop detail pages** — Enterprise only
- **Cross-platform Selection (Amazon, Shopee)** — Professional+
- **Image Search** (find products by image) — Professional+
- **Video-Ads analysis** (full Ad Spend / Ad ROAS columns) — Professional+
- **Export creator contacts in bulk** — Professional+ or recharge $69.9/1000
- **Live recordings** — recharge $3.99/5 or built into higher plans
- **Video downloads** — recharge $0.59/10
- **API access** — Enterprise only (via Charm partner)

For Abhinav's account (current user, **Professional**): everything above except Market Landscape, Shop detail pages, 365-day range, and API is available. Live Recording and bulk exports require recharge top-ups.

---

## AI Features

1. **Just Ask** (on /explore) — chat with Kalodata's data. Six prompt templates: Seller Analysis, Account Analysis, Product Selection Suggestions, Influencer Marketing, Video Creation, Kalodata Usage Inquiry. Each query consumes credits.
2. **Create Shoppable Videos** — generate TikTok-ready shoppable video content (button on /product and /video). AI-badged.
3. **AI badges** appear on Video & Ad in the nav, and on the "Just Ask" widget — the platform is actively pushing AI usage.

---

## Gotchas / Known Issues

- **Login is Google OAuth only.** No email/password fallback. If your Google account doesn't have access, sign-up may auto-create a new free trial account.
- **Hovering nav dropdowns is timing-sensitive** — Ant Design dropdowns close on mouseleave. If you need to click a sub-item, navigate directly to the URL instead (Category Ranking → `/category`, Market Landscape → `/overview`).
- **Profile clicks open a NEW TAB** — make sure to switch to it via `browser_tabs` before extracting data.
- **First `<tr>` in some `tbody` is empty** (artifact of Ant Design fixed-column layout). Skip rows where innerText is whitespace-only when extracting.
- **Tables have horizontal scroll** — many columns are off-screen on first load. Use `browser_evaluate` to read full row text rather than relying on the visible viewport.
- **Onboarding tooltip** ("365 Days Data — Enterprise...") shows on first load of /explore. Click "Got it" or `browser_press_key('Escape')` to dismiss before automating.
- **Region/currency are encoded in URL params** — `region=US&currency=USD&language=en-US`. Don't change them mid-session unless the user has purchased that region.
- **Watermarks** ("Kalodata") are stamped across screenshots of tables — visual only, doesn't affect text extraction.
- **The "Hot-selling Ranking" tab** on /explore was not deeply explored in this map — it's the public ranking view (everyone), while "My Following" is the private dashboard. Worth a follow-up exploration.
- **TikTok platform pill (next to logo)** has Amazon/Shopee in its dropdown for Professional+ accounts — re-explore if cross-platform lookup is ever needed.
- **The avatar dropdown swallowed clicks on the United States flag** during exploration — the flag is technically clickable to switch region but only between regions you've purchased; if you only have US, it shows current selection.

---

## Data caveats to surface in any Creator Dossier

When using Kalodata data for the user, always remind them of Kalodata's own warnings:

- "Data processed by algorithm, for reference only" — printed at the bottom of every ranking table.
- Per Kalodata FAQ: "transaction amounts and ad spending might have small variations from real-world numbers."
- Per Kalodata FAQ: NOT to be used for "partner commission settlements or performance evaluations."
- Models are retrained daily, so historical numbers can shift slightly between visits.

Treat Kalodata as **directional**, not authoritative. For absolute numbers (commissions, payouts), defer to TikTok Shop's own seller dashboard.

---

# Appendix: Third-Party Research (Vidura, 2026-05-13)

> Everything below is sourced from public internet research -- blog reviews, comparison articles, YouTube tutorials, Trustpilot, Reddit, and news coverage. It complements the UI map above with market context, competitive positioning, pricing history, community sentiment, and gaps the UI map cannot answer.

## Company background

- **Founded:** circa 2021-2022 (conflicting reports) [A8, T4]
- **Headquarters:** China (reports vary between Ningbo and Hong Kong) [A8, T4]
- **Founding team:** Former members of TikTok's global e-commerce division -- "key members in the development of TikTok Shop from the beginning" [A1, T3] [A5, T3]. This is the primary credibility claim and appears across nearly every review.
- **PitchBook profile exists** at pitchbook.com/profiles/company/539029-90 but funding details not publicly accessible [A8, T4].
- **LinkedIn:** linkedin.com/company/kalodata (HK-based per LinkedIn) [A8, T4]
- **Related product:** `kaloboost.com` -- "AI-Powered Automated TikTok Affiliate Platform With Best Data Support." Relationship to Kalodata unclear (same parent company? Separate product?).

## What this platform is (third-party perspective)

**One-liner:** TikTok Shop analytics and intelligence platform -- product research, creator discovery, shop benchmarking, video/livestream performance tracking, and competitive analysis across multiple TikTok Shop markets.

**What KIND of data lives here (vs Cruva vs Apify):**

- **vs Cruva:** Cruva is your CRM -- it manages YOUR affiliates (outreach, samples, DMs, CRM pipeline). Kalodata is your market intelligence -- it shows what's happening across ALL of TikTok Shop (any product, any creator, any shop, any category). Cruva knows your affiliates deeply; Kalodata knows the market broadly.
- **vs Apify:** Apify scrapes public TikTok profile data (followers, posts, video metadata). Kalodata has commerce-layer data (GMV, units sold, revenue, commission estimates) that public TikTok profiles do not expose. Apify is plumbing; Kalodata is intelligence.

## Pricing evolution and third-party confirmation

The UI map's pricing table (from the live `/pricing` page on 2026-04-29) is authoritative. Third-party sources confirm and add context:

- **Professional plan price increase:** Multiple sources [A13, T3] confirm a recent increase from $99.99 to $109.99/month (monthly billing). The annual-equivalent is $83.20/month, matching the UI map.
- **Starter plan:** $49.99/month (monthly) or ~$38.30/month (annual). Matches UI map.
- **Enterprise:** Custom pricing. Third-party estimates range $229-$599/month [A13, T3] -- unconfirmed.
- **Free trial:** 7 days, no credit card required. Confirmed across all sources [A1, T3].
- **No refunds** after subscription begins [A1, T3].
- **Promo codes:** Code "NOAH" reported to give 10% off [A1, T3] (likely affiliate-specific).
- **Group buy services:** `toolsurf.com` offers shared Kalodata access from $15/month [A13, T3] -- not officially sanctioned, may violate ToS.

## Competitive positioning

### vs FastMoss [A3, T3] [A14, T3]

| Dimension               | Kalodata                                       | FastMoss                                           |
| ----------------------- | ---------------------------------------------- | -------------------------------------------------- |
| **Metaphor**            | "Tactical sniper scope"                        | "Macro-strategic radar"                            |
| **Data refresh**        | Every 15 minutes                               | Daily (some claims: real-time for certain metrics) |
| **Historical depth**    | Up to 500-1000 days                            | 28-90 days (plan-dependent)                        |
| **Geographic coverage** | ~8-10 markets confirmed                        | 15-17 countries claimed                            |
| **Database size**       | 200M+ creators                                 | 250M+ creators                                     |
| **Pricing (monthly)**   | $38-110/mo                                     | $14-46/mo (significantly cheaper)                  |
| **Target user**         | Brands, agencies, serious sellers              | Agencies, enterprise, multi-market operators       |
| **Unique features**     | Ex-TikTok team, AI credits, Amazon data (Pro+) | AI content creation toolbox, script analysis       |
| **Creator contacts**    | Pro+ plan, 1,000/month                         | Up to 6,000/day on Ultimate                        |

_Synthesis:_ FastMoss is cheaper and has broader country coverage. Kalodata has deeper historical data and faster refresh. For US-focused operations (Rootlabs' primary market), Kalodata's depth advantage matters more than FastMoss's breadth.

### vs EchoTik [A3, T3]

- EchoTik is the budget option ($9-$19/month)
- Focuses on "Growth Velocity" detection -- flagging products with sudden surges in creator mentions before they appear on top-seller lists
- Includes a Chrome extension
- More visual/simplified UX, popular with indie sellers
- Less data depth than Kalodata; better for product discovery on a budget

### vs TikTok Shop's own seller dashboard

- TikTok's dashboard has accurate data for YOUR shop but no cross-market intelligence
- Kalodata provides the competitive/market view that TikTok's dashboard lacks

## Community sentiment

### Positive signals

- "Best analytical tool if you want to do e-commerce in TikTok" (Trustpilot) [A9, T4]
- Multiple review sites rate positively for trend spotting and product discovery [A1, T3] [A2, T3]
- User-friendly interface praised consistently [A1, T3] [A5, T3]
- Ex-TikTok team background cited as trust factor [A1, T3] [A14, T3]

### Negative signals

- **Data accuracy:** Reddit users (r/TikTokShop) report significant discrepancies between Kalodata metrics and their own TikTok Shop account data -- products showing zero sales in Kalodata had real volume, and vice versa [A2, T3] [A9, T4].
- **Billing complaints:** Trustpilot (~7 reviews total, small sample) includes reports of being charged after cancellation with no customer service response [A9, T4].
- **Starter plan frustration:** Users feel paywalled -- top 10 results per search, no contact exports, limited data range [A2, T3].
- **Transparency:** Pricing not shown on homepage; forces sign-up to see plans [A1, T3].
- **UI polish:** "UI/UX and software polish are sometimes criticized" [A4, T3].
- **No permanent free tier:** Only a 7-day trial, then pay or lose access [A5, T3].

### Dissent on data reliability

This is the most important disagreement in the evidence. Kalodata itself warns "data is processed by algorithm, for reference only" and explicitly says not to use it for commission settlements. Some users take this caveat seriously and use Kalodata for trend identification only. Other users treat the revenue numbers as approximately accurate and make business decisions on them. **The truth is likely: Kalodata's relative signals (trending up vs down, this product vs that product) are reliable; absolute numbers (exact GMV, exact units sold) are estimates with meaningful error bars.**

## Geographic coverage (consolidated from all sources)

**Confirmed markets:** US, UK, Indonesia, Vietnam, Thailand, Malaysia, Singapore, Philippines, Brazil, EU countries (unspecified which)

**Region purchase model:** Per the UI map, regions are purchased at subscription time. US-only or US/UK/EU bundle. Switching regions requires repurchase. Rootlabs' Professional plan likely covers US only (or US/UK/EU if the bundle was purchased -- check the region switcher in a live session).

## API access (third-party perspective)

- Enterprise-only, confirmed across all sources [A1, T3] [A6, T4] [A12, T4]
- **6 modules:** Category, Shop, Creator, Product, Video, Livestream
- **20+ endpoints** -- each module has ranking + detail endpoints
- **Auth:** Apply for access key, pass in request header
- **Request/response format:** JSON with `region`, `language`, `currency`, `date_range` parameters
- **Partial documentation available** on Scribd [A12, T4] but it's a preview, not full specs
- **API accessed via "Charm" partner** (per the pricing page)

The UI map notes the internal endpoint `POST /creator/detail/total` (with `cateIds` filter for category-specific GMV). This is not part of the public API; it's an internal browser-session endpoint heavily rate-limited.

## Scraping feasibility

**Not viable for production use.** [A6, T4]

- Cloudflare WAF (enterprise-grade) with JS challenges and CAPTCHAs
- Rate limiting per IP/session
- IP blocking (datacenter IPs flagged)
- Browser fingerprinting (canvas, WebGL, fonts, plugins)
- Login required via Google OAuth (complicates automation)
- React/Next.js frontend -- data in `__NEXT_DATA__` script tags
- Even `/robots.txt` returns a Cloudflare challenge
- The UI map's anti-scraping warning is critical: concurrency >1 triggers account locks, cumulative daily quota fires `risk-dispose-type: triggerTooManyTimes`

**No Apify Actor wraps Kalodata.** There are TikTok Shop scrapers on Apify (devcake, excavator, ace_scraper) that pull overlapping but less rich data directly from TikTok Shop -- not from Kalodata's processed analytics layer.

## Appendix sources

```
[A1]  "Kalodata Review (2026): I tried it (Is it Worth it?)" -- TipsOnBlogging, 2025-06 -- [T3]
      https://tipsonblogging.com/2025/06/kalodata-review/
      Why: Detailed hands-on review with pricing breakdown, feature walkthrough, honest limitations.

[A2]  "Kalodata Review 2026: Is It Worth It for TikTok Shop?" -- WinningHunter, 2026 -- [T3]
      https://winninghunter.com/insights/kalodata-review/
      Why: Independent review from a competing tool; 7.0/10 rating; surfaces data accuracy complaints.

[A3]  "FastMoss vs Kalodata 2026: Which TikTok Analytics Wins?" -- Dashboardly, 2025 -- [T3]
      https://www.dashboardly.io/post/fastmoss-vs-kalodata-the-2025-battle-for-tiktok-shop-analytics-supremacy
      Why: Head-to-head comparison with pricing, features, geographic scope, target personas.

[A4]  "Kalodata Review (2025): TikTok Shop Analytics for E-commerce" -- ProductHunter.co, 2025 -- [T3]
      https://producthunter.co/kalodata-review/
      Why: Independent review covering geographic scope (US/UK/EU/Brazil/SEA), database scale.

[A5]  "The Ultimate Review of Kalodata" -- BrandTheBoss, undated -- [T3]
      https://brandtheboss.com/kalodata-tiktok-review/
      Why: Database scale claims (100M products, 200M creators, 300M video/livestream), data caveat.

[A6]  "How to Scrape Kalodata: TikTok Shop Data Extraction Guide" -- Automatio, undated -- [T4]
      https://automatio.ai/how-to-scrape/kalodata
      Why: Technical detail on anti-bot protections, extractable data fields, regional coverage.

[A7]  "Kalodata MYSG - Malaysia & Singapore" -- Facebook page -- [T4]
      https://www.facebook.com/KalodataMalaysia/
      Why: Confirms MY/SG market coverage via official regional social presence.

[A8]  "Kalodata Company Profile" -- BounceWatch / PitchBook references -- [T4]
      Sources: bouncewatch.com, pitchbook.com (both partially gated)
      Why: Company background (founded ~2021-2022, HQ China/HK). Limited accessibility.

[A9]  "Kalodata Reviews | Read Customer Service Reviews" -- Trustpilot -- [T4]
      https://www.trustpilot.com/review/kalodata.com
      Why: User complaints about billing/cancellation. Small sample (~7 reviews).

[A10] "Kalodata Reviewed -- Features, Pricing Policy & More" -- VidAU.ai, undated -- [T3]
      https://www.vidau.ai/kalodata-the-new-smart-way-to-win-tiktok-sales/
      Why: Feature detail on Product Explorer, Creator Insights, Shop Analytics, AI Video Analysis.

[A11] "Kalodata" -- Apple App Store listing -- [T4 -- vendor]
      https://apps.apple.com/us/app/kalodata/id6670308912
      Why: Confirms mobile app existence.

[A12] "Kalodata Open API Overview and Modules" -- Scribd (partial) -- [T4]
      https://www.scribd.com/document/980319331/Kalodata-Open-API-1
      Why: Partial API docs confirming 6 modules and 20+ endpoints.

[A13] "How Much is Kalodata? Real Pricing (January 2026)" -- Simptok, 2026-01 -- [T3]
      https://simptok.com/how-much-is-kalodata/
      Why: Current pricing with plan comparison, Professional plan price increase noted.

[A14] "Kalodata vs Fastmoss (2026): In-depth Comparison" -- TipsOnBlogging, 2025-05 -- [T3]
      https://tipsonblogging.com/2025/05/kalodata-vs-fastmoss/
      Why: Detailed competitive comparison, historical depth, pricing, feature differentiation.
```

## What the third-party research adds that the UI map doesn't cover

1. **Company background:** Founded by ex-TikTok e-commerce team, ~2021-2022, HQ in China. Not visible from the product itself.
2. **Competitive context:** How Kalodata compares to FastMoss, EchoTik, and Kixmon on price, coverage, refresh speed, and target user.
3. **Community sentiment:** Reddit and Trustpilot complaints about data accuracy and billing -- operational risk signals.
4. **Pricing history:** Professional plan increased 10% recently. Annual vs monthly savings are ~16-30%.
5. **Geographic coverage confirmation:** UI map shows a region switcher but doesn't enumerate all markets. Third-party sources confirm at least 10 markets.
6. **API details beyond "Enterprise-gated":** 6 modules, 20+ endpoints, JSON format, access key auth. Still incomplete without full docs.
7. **Kaloboost relationship:** Unknown but worth tracking.

## Remaining gaps (manual walkthrough or Kartavya escalation needed)

1. **Which region bundle does Rootlabs' account have?** US-only or US/UK/EU? Check the region switcher in a live session.
2. **Full API documentation.** Only available to Enterprise customers. If Rootlabs ever upgrades, capture the full spec like we did for Cruva.
3. **Amazon data integration on Professional plan.** What Amazon data is exposed? How does it integrate? No third-party source explains this clearly.
4. **Kaloboost.** Same company? Complementary product? Worth investigating if Rootlabs needs automated affiliate management on TikTok Shop.
5. **Data methodology.** How does Kalodata actually source its data? Scraping TikTok Shop? Data partnership? The ex-TikTok credential is suggestive but the actual data pipeline is opaque.
6. **Shopee data.** The platform pill includes Shopee for Professional+ accounts. What Shopee markets and data are available? Not covered by any third-party source.
