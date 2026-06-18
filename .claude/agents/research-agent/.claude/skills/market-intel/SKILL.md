---
name: Market Intelligence
description: Market sizing, trend analysis, and category research. Produces data-rich reports with market size, growth rates, key players, emerging trends, and competitive landscape maps.
---

# Market Intelligence Skill

You are executing a market intelligence workflow — structured research on a market, category, or industry.

## Inputs Required

Ask the user (if not provided):
1. **Market/category** — what industry or product category?
2. **Geography** — global, US, EU, specific countries?
3. **Time horizon** — current state, 3-year forecast, 5-year?
4. **Depth** — quick overview or comprehensive deep-dive?

## Research Framework

### Market Sizing & Growth
- Current market size (TAM, SAM, SOM if possible)
- Historical growth rate (CAGR over 3-5 years)
- Projected growth (forward CAGR)
- Key growth drivers and headwinds
- Sources: Euromonitor, Grand View Research, Statista, IBISWorld, industry associations [T2-T3]

### Competitive Landscape
- Market leaders by revenue/share
- Emerging challengers and disruptors
- Recent M&A activity
- Funding/investment trends
- Market concentration (fragmented vs. consolidated)

### Consumer Trends
- Demand drivers (demographic, behavioral, technological)
- Emerging consumer preferences
- Channel shifts (DTC, social commerce, retail)
- Price sensitivity and premiumization trends

### Regulatory & Macro Environment
- Key regulations affecting the market
- Pending regulatory changes
- Macro factors (economic, geopolitical, technological)

### Category-Specific Data
- For **supplements**: ingredient trends, claim types, format preferences (gummy, powder, capsule), distribution channels, FDA/FTC landscape
- For **DTC/ecommerce**: AOV benchmarks, conversion rates, CAC trends, channel mix, subscription penetration
- For **social commerce**: platform GMV, creator economy size, affiliate structures

## Output Format

Always render as a **webpage** with:
- Executive summary (3-5 sentences)
- Key metrics dashboard (stat cards)
- Market size chart or table
- Competitive landscape table
- Trend analysis with timeline
- Source bibliography with tiers
- Data confidence notes

## Data Quality Rules

- Market size figures need at least 2 independent estimates
- If estimates diverge >30%, note the range and explain why
- Government/statistical agency data [T1] over consultancy estimates [T3]
- Always note the methodology (top-down vs. bottom-up, survey sample size)
- Flag any figures that are extrapolations vs. measured data

## Reference Data

For DTC supplement market intelligence, see:
- `docs/doc_brand_case_studies.md` — brand-level metrics and benchmarks
- `docs/doc_personalization_report.md` — technology and tools landscape
- `docs/research_acquisition.md` — TikTok Shop and social commerce data
