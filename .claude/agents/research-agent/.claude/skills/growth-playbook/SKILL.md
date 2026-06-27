---
name: Career Playbook
description: Tactical career development recommendations for AI engineers. Covers skill gap analysis, portfolio positioning, job market targeting, interview preparation, and networking — specific, implementable actions prioritized by impact.
---

# Growth Playbook Skill

You are building a tactical growth playbook — actionable recommendations for a specific brand, prioritized by impact and implementation effort.

## Inputs Required

Ask the user (if not provided):
1. **Brand name and description** — what do they sell, where, to whom?
2. **Current channels** — where do they acquire customers today?
3. **Known metrics** (if any) — AOV, conversion rate, retention rate, CAC
4. **Primary goal** — acquire more customers, retain better, increase order value, all of the above?
5. **Stage** — early (< $1M), scaling ($1-10M), growth ($10M+)?

## Research Streams

Run these research streams in parallel (use subagents for speed):

### Stream 1: Acquisition
- What channels work best for this category right now?
- What content formats and ad creatives are performing?
- Influencer/affiliate program structures in the category
- Referral and viral loop mechanics
- Organic/SEO opportunities

### Stream 2: Retention & Loyalty
- Subscription model best practices for the category
- Loyalty program designs with ROI data
- Post-purchase flows (email, SMS, push) with benchmarks
- Community building strategies
- Churn prevention and win-back tactics

### Stream 3: Conversion & AOV
- Website CRO opportunities
- Bundling strategies with pricing data
- Deals and promotions (what works vs. erodes margin)
- Upsell/cross-sell mechanics
- Checkout optimization

### Stream 4: Behavior Change
- Habit formation frameworks relevant to the product
- Onboarding and first-30-day strategies
- Content/education strategies that shift perception
- Gamification and engagement mechanics

### Stream 5: Competitive Benchmarks
- What are top competitors doing in each area above?
- What metrics define "good" in this category?
- Where is there whitespace or underserved opportunity?

## Output Format

Render as a **webpage** with:

### Executive Summary
3-5 sentences with the top 3 recommendations

### Key Metrics Dashboard
Stat cards with the most impactful data points found

### Detailed Findings by Stream
Each stream gets a section with specific tactics, data, and source citations

### Prioritized Action Plan
Numbered list with priority badges:
- **Immediate (30 days)** — highest impact, lowest effort
- **Short-term (60-90 days)** — high impact, moderate effort
- **Medium-term (3-6 months)** — requires infrastructure
- **Long-term (6-12 months)** — strategic investments

Each action includes: what to do, expected impact (with data), estimated effort, and relevant benchmarks.

### Source Bibliography
Numbered, tier-tagged, with URLs and dates

## Reference Data

For DTC supplement/wellness brands, pre-researched data available in:
- `docs/research_acquisition.md` — TikTok Shop, creator commerce, paid social benchmarks
- `docs/research_retention.md` — Subscription, loyalty, post-purchase, community data
- `docs/research_conversion.md` — CRO, bundling, deals, checkout, upsell data
- `docs/research_habits.md` — Behavioral science, habit formation, packaging, gamification
- `docs/doc_brand_case_studies.md` — 8 brand case studies with metrics
- `docs/doc_personalization_report.md` — Data, personalization, segmentation, attribution

**Load these files first** before searching — they contain 60+ sources already researched and tier-tagged. Only search for additional data to fill gaps or get more recent information.

## Quality Rules

- Every recommendation must cite at least one source with a tier badge
- Include expected impact data where available (% lifts, $ values)
- Flag recommendations that are "best practice consensus" vs. "single case study"
- Note dependencies between recommendations (e.g., "requires subscription infrastructure first")
- Be honest about what you don't know — include a Gaps section
