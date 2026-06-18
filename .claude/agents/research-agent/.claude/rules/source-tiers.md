---
description: Detailed source classification guide with edge cases and examples
globs: "**/*"
alwaysApply: true
---

# Source Credibility Tiers — Detailed Guide

## Tier 1 — Primary / Authoritative

**Always T1:**
- Peer-reviewed journals: Nature, Science, JAMA, NEJM, The Lancet, Cell, IEEE/ACM publications, arXiv (post-publication/peer-reviewed)
- Government statistical agencies: BLS, Census Bureau, Eurostat, ONS, StatCan
- International organizations: WHO, IMF, World Bank, OECD, UN agencies
- Regulatory filings: SEC EDGAR, FCA, EMA
- Central banks: Fed, ECB, BoE, BoJ publications
- Standards bodies: IETF RFCs, W3C specs, ISO, NIST
- Court rulings and legal opinions
- Original datasets from research institutions
- Clinical trial registries (ClinicalTrials.gov)

**Edge cases:**
- arXiv pre-prints without peer review → T3
- Government press releases (vs. data) → T2
- WHO policy recommendations (vs. data) → T2

## Tier 2 — Established Reporting & Analysis

**Always T2:**
- Major newspapers: Financial Times, NYT, WSJ, Washington Post, Reuters, AP, Bloomberg
- Weekly/monthly analysis: The Economist, The Atlantic, New Yorker (reported pieces)
- Industry publications: Stat News, IEEE Spectrum, Ars Technica, MIT Technology Review, Wired (reported)
- Think tanks: Brookings, Pew Research, RAND, CFR, Carnegie, Peterson Institute
- Major broadcasters: BBC, NPR, PBS, ABC News, NBC News
- Business press (reported): Inc., Forbes (staff-written), Business Insider (investigations)

**Edge cases:**
- Forbes "contributors" (not staff) → T3-T4
- Business Insider opinion pieces → T3
- Reuters/AP citing unnamed sources → T2 with [single source] flag

## Tier 3 — Specialized Expert Sources

**T3 when author is identifiable and credible:**
- Engineering blogs: Stripe, Cloudflare, Google Research, DeepMind, Netflix Tech, Uber Engineering
- Named practitioner blogs with verifiable expertise and track record
- Conference talks: NeurIPS, ICML, USENIX, KubeCon, SXSW, Web Summit
- Well-maintained Wikipedia articles (verify key claims with T1 sources)
- Industry databases: Crunchbase, PitchBook, SimilarWeb, Sensor Tower
- Trade publications: NutraIngredients, Modern Retail, Retail Dive, Adweek
- Market research firms: Euromonitor, Grand View Research, Mordor Intelligence

**Edge cases:**
- Industry data behind paywalls (only seeing press release summary) → T3 with [summary only] flag
- Consultant/agency blog posts → T3 if methodology is explained, T4 if marketing-only

## Tier 4 — Use With Caution

**Always T4:**
- Reddit, Hacker News, Twitter/X, LinkedIn posts
- Vendor whitepapers and case studies → `[T4 — vendor]`
- Marketing content and press releases from companies
- Substack with no verifiable author credentials
- Unverified GitHub README claims
- Anonymous blogs without editorial review
- Podcast claims without supporting documentation
- Influencer content about products they're paid to promote

**When to still cite T4:**
- When it's the only source for a specific data point (flag it)
- When it provides signal about sentiment or trends (not facts)
- When the Reddit/HN discussion contains expert commentary

## Tier 5 — Avoid or Quarantine

**Never cite as authoritative:**
- SEO content farms (generic articles optimized for search)
- AI-generated slop articles
- Rumor and gossip sites
- Unverified leaks
- Content with no author, no editorial chain, no methodology
- Affiliate review sites masquerading as independent analysis

**Exception:** If T5 content is the *subject* of analysis (e.g., studying misinformation), cite it as the object of study, not as a source of truth.

## Special Flags

| Flag | When to use | Example |
|------|-------------|---------|
| `[T4 — vendor]` | Source is maker of product being evaluated | Klaviyo's own case study about Klaviyo |
| `[stale]` | Published >18 months ago for fast-moving topics | 2023 TikTok Shop data cited in 2026 |
| `[translated]` | Cited via translation | Japanese regulatory filing, translated |
| `[single source]` | Claim appears in only one source | Only one article reports this revenue figure |
| `[summary only]` | Only saw press release, not full report | Euromonitor data cited via trade pub |
| `[contested]` | Other credible sources disagree | Some experts dispute this methodology |
