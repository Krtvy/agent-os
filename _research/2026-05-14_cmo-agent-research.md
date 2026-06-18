# Deep Research: AI Marketing Agents / Autonomous CMO Agent Systems

**Date:** 2026-05-14
**Purpose:** Feed a Hyperagent prompt that generates Claude 4 Sonnet/Opus runnable agent files for a local CMO agent system.
**Tier legend:** T1 = primary docs / canonical author / repo source. T2 = reputable secondary (HBR, Reforge, LangChain blog, Motion, Search Engine Land). T3 = community / anecdotal / aggregator blogs.

---

## TL;DR

The CMO-agent design space converged in 2025-2026 on three things: (1) Claude Code's `.claude/agents/*.md` subagent pattern is now the de-facto local-runnable agent format and dozens of marketing-flavored repos already ship in this shape; (2) the strongest open systems are not single "AI CMO" monoliths but _crews_ of 5-12 specialists (positioning, copy, SEO, paid, lifecycle, analyst) orchestrated by a thin lead agent; (3) the difference between a "demo CMO" and a "useful CMO" is whether the system encodes canonical strategy frameworks (Dunford positioning, Balfour Four Fits, Schwartz awareness stages, AARRR, Bullseye, StoryBrand) AND has memory of brand voice + prior decisions + measurement guardrails (incrementality, not last-click). Common failure modes — hallucinated metrics, generic copy, no brand voice, no compliance — are all _design_ failures, not model failures.

---

## Key Findings

- **CrewAI is the most-starred multi-agent framework (44.5k+ stars) and has a mature marketing-crew example pattern** with researcher + strategist + copywriter + image-gen roles [1, T1]. But CrewAI marketing examples are Python-runtime; for a Claude-native local deliverable the `.claude/agents/` pattern is a better fit.
- **LangChain's `social-media-agent` (2.6k stars, actively maintained April 2026)** is the cleanest open reference for a multi-graph marketing pipeline with human-in-the-loop approval. It registers 14 separate LangGraph graphs (generate_post, curate_data, supervisor, repurposer, verify_links, condense_loop, image_pipeline, human_node, schedule) [2, T1].
- **`talknerdytome-labs/claude-agents` is the closest existing analog to what Hyperagent should generate** — production-ready growth-marketing subagents as `.md` files with YAML frontmatter, MCP tool wiring. Current roster is small (website-intel, meta-ads-library, google-ads-library) which is an opportunity, not a moat [3, T1].
- **VoltAgent's `awesome-claude-code-subagents` (100+ agents)** establishes the naming + folder conventions: `categories/NN-domain/agent-name.md`, kebab-case, YAML frontmatter with `name / description / tools / model`. Marketing-relevant agents include `content-marketer`, `seo-specialist`, `product-manager`, `market-researcher` [4, T1].
- **The strongest stage-aware growth frameworks for emergent strategy are Balfour's Four Fits** (Market-Product, Product-Channel, Channel-Model, Model-Market) and **Reforge's growth-loop typology** (acquisition / retention / viral / content / paid loops). Both explicitly map company state → tactic and are encodable as conditional rules in agent prompts [5, T1] [6, T2].
- **Memory taxonomy has converged on episodic / semantic / procedural** (LangMem, Letta née MemGPT, Mem0, Zep). For a CMO agent this maps to: episodic = past campaigns + results; semantic = ICPs, positioning, brand voice; procedural = "how we run a launch / how we test ads" [7, T2].
- **Reddit/HN community pitfalls cluster around five themes** [T3]: (a) hallucinated metrics ("CTR was 4.2%" when the agent never had data access), (b) generic LLM-default copy that ignores brand voice, (c) "fully autonomous" claims that fail at integration/latency/compliance, (d) optimizing operational KPIs while strategy is broken, (e) Reddit/UGC platform bans for templated AI posts.
- **Measurement is the most under-encoded area in existing marketing agents**: MMM + incrementality + geo-holdouts are the 2026 stack, and almost no open-source marketing agent encodes the difference between correlation (MTA/last-click) and causation (lift tests) [8, T2].

---

## Detailed Analysis

### 1. Existing open-source agent stacks for marketing

**Framework landscape (May 2026):**

| Framework                 | Stars                     | Language   | Strength for marketing                           | Weakness                                    |
| ------------------------- | ------------------------- | ---------- | ------------------------------------------------ | ------------------------------------------- |
| CrewAI                    | 44.5k [T1]                | Python     | Role-play crews, marketing examples plentiful    | Heavy Python runtime; not Claude-native     |
| LangGraph                 | (top-tier LangChain)      | Python     | State machines, HITL, supervisor patterns        | Verbose; learning curve                     |
| AutoGen                   | Maintenance mode [T1]     | Python     | Conversation patterns                            | Now superseded by Microsoft Agent Framework |
| Mastra                    | 19k, 300k weekly npm [T2] | TypeScript | HITL primitives, Next.js                         | TS-only; not native to Claude Code          |
| MetaGPT                   | (large, T1)               | Python     | Hierarchical role assignment                     | Software-dev-focused, not marketing         |
| BabyAGI                   | (small, T1)               | Python     | Minimal proof-of-concept                         | Too thin for production marketing           |
| **Claude Code subagents** | N/A (spec) [T1]           | Markdown   | Native, local-runnable, per-agent context window | Less mature ecosystem than CrewAI           |

**Marketing-specific repos worth borrowing from:**

1. `langchain-ai/social-media-agent` (2.6k stars) — _T1_. Multi-graph LangGraph pipeline: URL → content parse → relevance check → marketing report → post draft → image → human approve → schedule. Pull patterns: HITL interrupt nodes, agent-inbox UX, multi-graph composition [2, T1].
2. `talknerdytome-labs/claude-agents` — _T1_. Three competitive-intel agents as `.md` files; demonstrates that the `.claude/agents/` format works for marketing analysis. Files: `website-intel.md`, `meta-ads-library.md`, `google-ads-library.md`. Tools wired: Firecrawl, WebFetch, TodoWrite, WebSearch, MCP servers for Meta Ads Library and Google Ads Transparency Center [3, T1].
3. `VoltAgent/awesome-claude-code-subagents` — _T1_. 100+ agents catalog. Reference for folder convention (`categories/08-business-product/`, `categories/10-research-analysis/`), YAML frontmatter shape, and model routing (`opus` / `sonnet` / `haiku`) [4, T1].
4. `kostja94/marketing-skills` — _T1_. 160+ open-source marketing skills (SEO, social, paid ads, 40+ page types) packaged for Cursor / Claude Code / OpenClaw [9, T1].
5. `coreyhaines31/marketingskills` — _T1_. Claude-Code marketing skills covering CRO, copy, SEO, analytics, growth engineering [10, T1].
6. `chinmaydk99/Multiagent-Marketing-Campaign-Generator` — _T1_. LangGraph multi-agent campaign generator (smaller, reference for state-machine shape) [11, T1].
7. `agentuity/agent-social-marketing` — _T1_. TypeScript multi-agent: Manager + Copywriter + Scheduler [12, T1].
8. CrewAI marketing examples in `crewAIInc/crewAI-examples` — _T1_. Marketing Strategy Crew + Campaign-AI pattern (researcher + strategist + copywriter + image-gen) [1, T1].

**How they structure roles** — the convergent pattern (across CrewAI marketing crew, social-media-agent, agentuity, and Jasper's documented agent architecture) is:

- **Orchestrator / lead** — receives brief, decomposes, routes
- **Researcher / market intel** — competitive analysis, trend pulls
- **Strategist / brand** — positioning, ICP, message framework
- **Copywriter** — long-form, ad copy, hooks (often split by channel)
- **Designer / brief-writer** — image / video creative brief
- **Channel specialist(s)** — SEO, Meta, Google, lifecycle, organic social
- **Analyst / measurement** — pulls metrics, reads dashboards, flags anomalies
- **Compliance / brand-voice guardian** — final QA pass

Conspicuously _missing_ from most open systems: an explicit **Positioning agent** (Dunford / JTBD), an **Awareness-stage router** (Schwartz), and a **Growth-stage diagnostician** (Balfour).

### 2. Community signal — what works, what fails

**Reddit (r/AI_Agents, r/LocalLLaMA, r/marketing) and HN themes, late 2025-2026 [T3]:**

- _"Boring beats autonomous"_ — practitioners report wins on narrow, measurable automations (invoice-style "produce campaign brief from inputs," "audit landing page") and frustration with "fully autonomous CMO" claims [13, T3].
- _Hallucinated metrics_ — agents confidently report numbers they never had data access to; fix is to gate metric claims behind tool calls and refuse to invent numbers (system prompt rule, not a model fix) [14, T3].
- _Generic copy_ — LLM-default voice ("Unlock the power of...") leaks through without explicit brand-voice memory + few-shot exemplars + a Brand Voice Guardian reviewer agent [15, T3].
- _Strategy-vs-execution mismatch_ — "Measure revenue contribution and CLV, not just operational metrics. If your agents are perfectly executing a flawed strategy, you've only accelerated your way to poor results — set business outcome KPIs from day one" [16, T2].
- _Reddit-specific ban risk_ — Reddit aggressively bans templated AI posts; behavioral analysis (timing patterns), content analysis (template detection), API monitoring [17, T2]. Implication: a CMO agent's "Reddit playbook" must be _advisory_, not autoposting.
- _Human-in-the-loop is the dominant production pattern_ — social-media-agent, agentuity, and the MarTech pitfalls guide all converge on "AI drafts, human approves" rather than full automation, especially for anything that hits paid channels or public posts [2, T1] [18, T2].
- _Governance triad_: input controls, output review, disclosure standards [18, T2]. Encode all three in the system.

### 3. Knowledge frameworks — the canon

Each item: name — 1-line — tier.

**Positioning / strategy**

- **STP** (Segmentation, Targeting, Positioning) — classical Kotler triad; the baseline of audience selection [T2].
- **Jobs-To-Be-Done (Christensen / Moesta)** — customers "hire" products to make progress; Moesta's _Four Forces of Progress_ (push, pull, anxiety, habit) is the operational version [19, T1] [20, T2].
- **April Dunford 5-component positioning** — competitive alternatives, unique attributes, value (+ proof), target market, market category (+ bonus: relevant trends) [21, T1].
- **Category Design (Play Bigger)** — design and dominate a new category rather than compete in an existing one [T2].
- **Blue Ocean Strategy (Kim & Mauborgne)** — uncontested market space via value innovation [T2].
- **Porter's Five Forces** — industry structure (rivalry, new entrants, substitutes, buyer/supplier power) [T2].
- **4Ps / 7Ps** — product, price, place, promotion (+ people, process, physical evidence) [T2].
- **Ansoff Matrix** — market penetration / development / product development / diversification [T2].
- **BCG Matrix** — stars / cash cows / question marks / dogs [T2].

**Growth / funnel**

- **AARRR / Pirate Metrics (Dave McClure, 2007)** — Acquisition, Activation, Retention, Referral, Revenue. Each stage pairs with a north-star (CPC, time-to-value, logo churn, viral coefficient, LTV-CAC) [22, T1].
- **AAARRR** — adds Awareness as stage 0 [T2].
- **North Star Metric (Sean Ellis lineage)** — one guiding outcome tied to value delivery [T2].
- **Bullseye Framework (Weinberg & Mares, _Traction_)** — 19 channels: viral, PR, unconventional PR, SEM, social/display ads, offline ads, SEO, content marketing, email, engineering as marketing, targeting blogs, BD, sales, affiliate, existing platforms, tradeshows, offline events, speaking, community. 5-step process: brainstorm → rank (A/B/C) → prioritize (inner 3) → test → focus on 1. 50/50 rule (product / traction) [23, T1].
- **ICE / RICE prioritization** — ICE (Sean Ellis): Impact × Confidence × Ease, 1-10 each. RICE (Intercom): (Reach × Impact × Confidence) / Effort [24, T2].
- **RFM** — Recency, Frequency, Monetary segmentation for retention [T2].

**Brand**

- **Aaker brand equity** — awareness, perceived quality, associations, loyalty, other assets [T2].
- **12 Jungian archetypes (Mark & Pearson, _The Hero and the Outlaw_)** — Innocent, Everyman, Hero, Outlaw, Explorer, Creator, Ruler, Magician, Lover, Caregiver, Jester, Sage [25, T2].
- **Brand Key (Unilever)** — root strengths, competitive environment, target, insight, benefits, values/personality, reason to believe, discriminator, essence [T2].
- **Golden Circle (Sinek)** — Why → How → What [T2].

**Content / messaging**

- **StoryBrand SB7 (Donald Miller)** — Character with a Problem meets a Guide who gives a Plan, calls them to Action, helping them avoid Failure and reach Success. Customer is hero, brand is guide [26, T1].
- **AIDA** — Attention, Interest, Desire, Action [T2].
- **PAS** — Problem, Agitate, Solution [T2].
- **BAB** — Before, After, Bridge [T2].
- **Eugene Schwartz 5 Stages of Awareness (_Breakthrough Advertising_, 1966)** — Unaware, Problem Aware, Solution Aware, Product Aware, Most Aware. Match copy to where prospect _is_, not where you wish they were. Foundational [27, T1].
- **Cialdini's 7 principles** — Reciprocity, Commitment/Consistency, Social Proof, Authority, Liking, Scarcity, Unity (added 2016) [28, T2].

**Distribution / growth loops**

- **Balfour's Four Fits** — Market-Product, Product-Channel, Channel-Model, Model-Market. "Products are built to fit with channels. Channels do not mold to products." Required for $100M+ [5, T1].
- **Growth Loops (Reforge)** — closed systems where outputs reinvest as inputs; types: new-user / returning-user / defensibility / efficiency. Loops > funnels for compounding [6, T2].
- **T2D3 (Neeraj Agrawal)** — triple revenue 2 years, then double 3 years = $1M to $100M in 5-6 years [29, T2].
- **Unit economics: CAC, LTV, LTV:CAC (≥3:1 healthy), CAC payback (<12mo SaaS; <18mo VC-backed), NRR, Rule of 40, Magic Number** [30, T2].
- **NPS** — net promoter score; tracks referral propensity [T2].

**Performance / measurement**

- **MMM (Marketing Mix Modeling)** — aggregated channel-level econometric model; answers "if I shift $1M from display to CTV, what happens?" [8, T2].
- **MTA (Multi-Touch Attribution)** — user-level path; weaker post-privacy, still useful for in-platform decisions [8, T2].
- **Incrementality testing / geo-holdouts / conversion lift** — matched geo pairs, expose one, hold one dark, measure causal lift. The 2026 stack: MMM + always-on incrementality + platform attribution, triangulated [8, T2].

**Channel-specific playbooks**

- **Meta / TikTok creative testing** — 3-5 variations per test, test hook (first 1-3s) separately from body; metrics: 3-sec view rate, hook rate, hold rate, CPC by hook, CTR. Motion's framework is the public standard [31, T2].
- **Google Ads STAG over SKAG** — since 2018 close-variant expansion and smart bidding favor 3-20 themed keywords per ad group; SKAG only for high-value niche [32, T2].
- **SEO: E-E-A-T + topical authority + pillar/cluster** — March 2026 core update elevated E-E-A-T and penalized thin AI content; pillar pages 3-5k words; clustered sites see ~40% organic lift vs un-clustered [33, T2].
- **Klaviyo flows (DTC)** — six revenue flows: welcome series, abandoned cart (3-email seq is 6.5× revenue vs single), browse abandonment, post-purchase, winback (90/120/180-day), sunset [34, T2].
- **Influencer / UGC** — creator-content unlocks; brief = hook + product + CTA; whitelist for paid amplification [T2].

### 4. Agent architecture patterns

**Single orchestrator vs. crew.** The honest answer: a single thick orchestrator hits context-window limits fast on marketing work (positioning doc + ICP + 3 competitor sites + ad library + brand-voice exemplars + measurement plan). Claude Code's subagent model (each agent gets its own context window; parent receives only the output) is the natural solution [35, T1]. Pattern: thin **CMO orchestrator** that decomposes briefs and routes; specialists each own a domain with their own context, tools, and memory.

**Memory taxonomy (LangMem / Letta / Mem0 convention)** [7, T2]:

- **Episodic** — past campaigns, experiments, decisions, outcomes (`memory/episodes/`)
- **Semantic** — facts: ICPs, positioning, brand voice rules, market category, glossary (`memory/semantic/`)
- **Procedural** — how we do things: launch playbook, ad-test SOP, weekly review (`memory/procedural/` or `skills/`)
- **Brand-voice memory** — a special semantic slice: archetype, tone rules, banned phrases, ten exemplar paragraphs from real human copy

LangMem's _procedural memory_ feature lets agents rewrite their own system prompts based on feedback — useful pattern but requires guardrails for a CMO agent (don't let it drift its own brand voice) [7, T2].

**Tools the CMO crew needs:**

- Web search + fetch (WebSearch, WebFetch, Firecrawl)
- Competitor scraping (website-intel pattern)
- Ad library MCP servers — Meta Ads Library, Google Ads Transparency Center, TikTok Creative Center
- Keyword research (Ahrefs/Semrush MCP if available; else SERP scrape)
- Analytics readers — GA4, Klaviyo, Shopify, Triple Whale (MCP where available)
- Copy generation (native)
- Image/video brief generation (markdown brief; pass to human or to image-gen)
- Document write / read (Read, Write, Edit)
- Memory I/O (filesystem)

**Claude Code subagent format** [35, T1]:

```yaml
---
name: brand-voice-guardian
description: Reviews all outbound copy for brand-voice fit. Use proactively after any copywriter agent output.
tools: Read, Write, Edit, Grep, Glob
model: sonnet
---
[system prompt body]
```

Files live in `.claude/agents/*.md` (project) or `~/.claude/agents/*.md` (user). Subagents are invoked by the main agent when the description matches the task. This maps cleanly to a CMO crew: each specialist is a `.md` file the orchestrator delegates to.

### 5. The emergent-strategy angle

The goal — "you're at $1M ARR with weak retention → here's the loop to fix it" — requires the agent to _diagnose_ before _prescribing_. The encodable conditional logic comes from:

- **Balfour's Four Fits** [5, T1] gives a structured diagnostic: which fit is breaking? Question Tree:
  1. Do paying customers describe the problem the way you describe it? (Market-Product)
  2. Does your distribution channel match how your product spreads? (Product-Channel)
  3. Does your CAC fit your ARPU? (Channel-Model)
  4. Does your TAM × capture × ARPU clear the revenue goal? (Model-Market)
- **Reforge growth-loop typology** [6, T2] gives the prescription: weak retention → install a retention loop; weak acquisition → audit product-channel fit before adding channels; saturation → new loop, not louder paid.
- **Schwartz awareness stages** [27, T1] gives the messaging prescription per audience: unaware → big idea / education; problem-aware → empathy + reframe; solution-aware → comparison + proof; product-aware → offer + risk reversal; most-aware → urgency + clear CTA.
- **Lenny / Reforge stage gates** — between Seed and Series B is the "Momentum Canyon"; retention is the foundation, loops are the engine [6, T2].

Encode these as a `diagnostician.md` skill the CMO calls first when given a brief like "we need to grow."

### 6. Common pitfalls to design against

| Pitfall                                      | Source                                | Design counter                                                                |
| -------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------- |
| Hallucinated metrics                         | r/AI_Agents, MarTech [13, 18, T2/T3]  | Hard rule: no numeric claim without a tool-call provenance log                |
| Generic LLM-default copy                     | HN, multiple [15, T3]                 | Brand Voice Guardian agent + 10 exemplar paragraphs + banned-phrase list      |
| "Fully autonomous" overreach                 | r/LocalLLaMA, MarTech [13, 18, T2/T3] | HITL gates on anything outbound or paid                                       |
| Last-click attribution claims                | Deducive, eMarketer [8, T2]           | Encode MMM + incrementality vocabulary; explicit caveat strings               |
| Strategy execution without strategy          | Data Axle [16, T2]                    | Diagnostician runs Four Fits before tactics                                   |
| Platform ToS violations (Reddit, X)          | Linkeddit, Aibrify [17, T2]           | Channel-specific compliance rules in playbook files; no autoposting on Reddit |
| Brand voice drift via self-rewriting prompts | LangMem doc [7, T2]                   | Brand voice memory is _read-only_ for the agent; updates require human commit |
| Optimizing operational KPIs not revenue      | MarTech [18, T2]                      | North Star + CAC/LTV/NRR mandatory in every campaign brief                    |

---

## Synthesis — for the Hyperagent prompt

### Top 5 GitHub repos to borrow patterns from

1. **`langchain-ai/social-media-agent`** [2, T1] — multi-graph orchestration + HITL approval pattern (graph names, interrupt nodes, agent inbox UX).
2. **`talknerdytome-labs/claude-agents`** [3, T1] — direct precedent for `.claude/agents/*.md` growth-marketing agents with MCP tool wiring (Firecrawl, Ads Library MCP).
3. **`VoltAgent/awesome-claude-code-subagents`** [4, T1] — naming conventions, folder taxonomy (`categories/NN-domain/`), YAML frontmatter shape, model routing.
4. **`crewAIInc/crewAI-examples`** Marketing Strategy Crew + Campaign-AI [1, T1] — researcher/strategist/copywriter/image-gen role split.
5. **`kostja94/marketing-skills`** [9, T1] — library of 160+ procedural marketing skills to mine for the `skills/` folder.

### Top 10 knowledge frameworks the agent MUST encode

1. **April Dunford 5-component positioning** [21, T1]
2. **Jobs-To-Be-Done + Moesta Four Forces of Progress** [19, 20, T1/T2]
3. **Brian Balfour's Four Fits** (Market-Product → Product-Channel → Channel-Model → Model-Market) [5, T1]
4. **Reforge growth loops** (acquisition/retention/viral/content/paid) [6, T2]
5. **AARRR / Pirate Metrics + North Star metric** [22, T1]
6. **Bullseye Framework** (19 channels + 5-step process) [23, T1]
7. **Eugene Schwartz 5 Stages of Awareness** [27, T1]
8. **StoryBrand SB7** (customer-as-hero, brand-as-guide) [26, T1]
9. **Cialdini's 7 principles of persuasion** [28, T2]
10. **MMM + Incrementality + Geo-holdout measurement stack** [8, T2]

Honorable mentions to include in `knowledge/`: 12 Jungian archetypes, ICE/RICE, CAC/LTV unit economics, Klaviyo six-flow stack, STAG (not SKAG) for Google Ads, E-E-A-T + topical authority for SEO, AIDA/PAS/BAB copy formulas.

### Recommended file/folder structure

```
cmo-agent-system/
├── CLAUDE.md                          # operator manual: how to use the system, brief format, escalation rules, output expectations
├── README.md
├── .claude/
│   └── agents/                        # the crew
│       ├── 00-cmo-orchestrator.md     # thin lead, decomposes briefs, routes
│       ├── 01-diagnostician.md        # Four Fits + AARRR diagnostic before prescribing
│       ├── 02-positioning-strategist.md  # Dunford + JTBD + category
│       ├── 03-icp-researcher.md       # ICP, segmentation, voice-of-customer
│       ├── 04-competitor-analyst.md   # website-intel + ad library
│       ├── 05-content-strategist.md   # pillar/cluster, editorial calendar
│       ├── 06-copywriter.md           # long-form + landing pages (Schwartz-aware)
│       ├── 07-ads-copywriter.md       # paid hooks + ad copy (Motion testing framework)
│       ├── 08-seo-specialist.md       # E-E-A-T, topical authority, technical SEO
│       ├── 09-paid-media-planner.md   # Meta/TikTok/Google strategy
│       ├── 10-lifecycle-marketer.md   # Klaviyo flows, retention, segmentation
│       ├── 11-organic-social-strategist.md  # platform-native, no autoposting
│       ├── 12-influencer-ugc-planner.md
│       ├── 13-analyst-measurement.md  # MMM/incrementality/dashboards
│       ├── 14-brand-voice-guardian.md # final QA pass on all outbound copy
│       └── 15-compliance-reviewer.md  # platform ToS, ad policy, regulated-category rules
├── skills/                            # procedural how-tos invoked by agents
│   ├── campaign-brief.md
│   ├── creative-test-plan.md
│   ├── channel-audit.md
│   ├── launch-playbook.md
│   ├── weekly-review.md
│   ├── positioning-workshop.md
│   ├── icp-interview-synthesis.md
│   ├── ad-test-readout.md
│   ├── seo-audit.md
│   ├── lifecycle-flow-audit.md
│   └── incrementality-test-design.md
├── knowledge/                         # framework canon, one file each
│   ├── positioning/
│   │   ├── dunford-5-component.md
│   │   ├── jobs-to-be-done.md
│   │   ├── stp.md
│   │   ├── category-design.md
│   │   └── porter-5-forces.md
│   ├── growth/
│   │   ├── balfour-four-fits.md
│   │   ├── reforge-growth-loops.md
│   │   ├── aarrr-pirate-metrics.md
│   │   ├── north-star-metric.md
│   │   ├── bullseye-framework.md
│   │   └── ice-rice-prioritization.md
│   ├── brand/
│   │   ├── jungian-12-archetypes.md
│   │   ├── aaker-brand-equity.md
│   │   └── golden-circle.md
│   ├── messaging/
│   │   ├── schwartz-awareness-stages.md
│   │   ├── storybrand-sb7.md
│   │   ├── cialdini-7-principles.md
│   │   └── aida-pas-bab.md
│   ├── measurement/
│   │   ├── mmm-vs-mta-vs-incrementality.md
│   │   ├── geo-holdout-design.md
│   │   ├── unit-economics-cac-ltv.md
│   │   └── rule-of-40.md
│   └── channels/
│       ├── meta-tiktok-creative-testing.md
│       ├── google-ads-stag.md
│       ├── seo-eeat-topical-authority.md
│       ├── klaviyo-six-flows.md
│       └── influencer-ugc-briefs.md
├── workflows/                         # canonical multi-agent chains
│   ├── new-brand-launch.md            # diagnostician → positioning → ICP → channel plan → creative → measurement plan
│   ├── growth-diagnosis.md            # Four Fits diagnostic → loop prescription
│   ├── creative-sprint.md             # weekly ad-test cycle
│   ├── quarterly-planning.md
│   └── weekly-marketing-review.md
├── playbooks/                         # vertical / context-specific overlays
│   ├── dtc-ecommerce.md
│   ├── b2b-saas.md
│   ├── marketplace.md
│   ├── consumer-app.md
│   ├── early-stage-0-to-1m.md         # pre-PMF playbook
│   ├── scale-1m-to-10m.md             # post-PMF, channel-first
│   └── scale-10m-plus.md              # diversification, brand
└── memory/
    ├── brand-voice/
    │   ├── archetype.md               # which Jungian archetype + rationale
    │   ├── tone-rules.md
    │   ├── banned-phrases.md
    │   └── exemplars/                 # 10 real human-written examples per format
    ├── semantic/
    │   ├── icps.md                    # primary ICP + secondary
    │   ├── positioning.md             # Dunford output
    │   ├── product-truths.md          # what's actually true about the product
    │   └── glossary.md
    ├── episodic/
    │   ├── campaigns/                 # one md per past campaign with brief + results + lessons
    │   └── decisions/                 # decision log
    └── procedural/
        └── (cross-refs to skills/)
```

### Recommended agent roster (CMO crew)

The 16-agent roster above is the full deck. Minimum viable launch crew = 8: **cmo-orchestrator, diagnostician, positioning-strategist, copywriter, ads-copywriter, lifecycle-marketer, analyst-measurement, brand-voice-guardian.** Add the rest as the system matures.

### Common pitfalls to design _against_ (recap)

1. **No hallucinated metrics** — system prompt rule in every analyst agent: "If you do not have a tool-call result for a number, say so. Never estimate a metric from prior knowledge."
2. **No generic copy** — every copywriter agent must read `memory/brand-voice/` before drafting; brand-voice-guardian reviews every output.
3. **HITL on all outbound** — never autopost paid, never autopost Reddit/Discord/X; lifecycle email and SEO content require human approve gates.
4. **Diagnose before prescribe** — orchestrator routes "we need to grow"-shaped briefs to `diagnostician` first, not to `paid-media-planner`.
5. **Causation over correlation** — analyst-measurement agent flags any last-click claim and proposes incrementality test design.
6. **Brand voice memory is read-only** — only humans commit changes to `memory/brand-voice/`.
7. **Compliance is its own agent** — regulated categories (health, finance, gambling) get a hard pre-publish gate.
8. **Channel-stage match** — early-stage playbook forbids enterprise channels; scaled-stage playbook forbids one-channel dependence.

---

## Source Bibliography

[1] CrewAI — `crewAIInc/crewAI` (44.5k stars, 2026) and `crewAIInc/crewAI-examples`. _T1._ https://github.com/crewaiinc/crewai | Why cited: dominant multi-agent framework; marketing crew examples.

[2] LangChain — `langchain-ai/social-media-agent` (2.6k stars, active April 2026). _T1._ https://github.com/langchain-ai/social-media-agent | Why cited: cleanest open multi-graph marketing pipeline with HITL.

[3] `talknerdytome-labs/claude-agents` — production growth-marketing subagents for Claude Code. _T1._ https://github.com/talknerdytome-labs/claude-agents | Why cited: closest existing analog to the target deliverable shape.

[4] `VoltAgent/awesome-claude-code-subagents` — 100+ Claude Code subagents. _T1._ https://github.com/VoltAgent/awesome-claude-code-subagents | Why cited: folder/naming/frontmatter conventions.

[5] Brian Balfour — _Four Fits for $100M+ Growth_. _T1._ https://brianbalfour.com/four-fits-growth-framework | Why cited: canonical stage-aware growth framework.

[6] Reforge — _Growth Loops Are the New Funnels_. _T2._ https://www.reforge.com/blog/growth-loops | Why cited: loop typology + replaces funnel framing.

[7] Mem0 / Atlan / Hermes OS / Vektor — AI agent memory frameworks 2026; LangMem episodic/semantic/procedural taxonomy; Letta (MemGPT). _T2._ https://mem0.ai/blog/state-of-ai-agent-memory-2026 | Why cited: convergent memory taxonomy.

[8] Deducive / eMarketer / Liftlab / Measured / SegmentStream — _MMM + Incrementality + Geo-holdout, 2026 stack_. _T2._ https://www.deducive.com/blog/2025/12/12/our-guide-to-marketing-attribution-incrementality-and-mmm-for-2026 | Why cited: triangulated measurement is the 2026 standard.

[9] `kostja94/marketing-skills` — 160+ marketing skills for Cursor / Claude Code. _T1._ https://github.com/kostja94/marketing-skills | Why cited: skill library to mine.

[10] `coreyhaines31/marketingskills` — marketing skills for Claude Code agents. _T1._ https://github.com/coreyhaines31/marketingskills | Why cited: CRO/copy/SEO/analytics skill set.

[11] `chinmaydk99/Multiagent-Marketing-Campaign-Generator` — LangGraph multi-agent campaign generator. _T1._ https://github.com/chinmaydk99/Multiagent-Marketing-Campaign-Generator | Why cited: reference state machine.

[12] `agentuity/agent-social-marketing` — TS multi-agent (Manager + Copywriter + Scheduler). _T1._ https://github.com/agentuity/agent-social-marketing | Why cited: minimal viable crew.

[13] Reddit/HN community synthesis on AI agent pitfalls (r/AI_Agents, r/LocalLLaMA, HN), 2026. _T3._ | Why cited: pitfall surfacing.

[14] AIToolDiscovery / AgentsIndex — _Best AI Agents: What Reddit Actually Uses in 2026_. _T3._ https://www.aitooldiscovery.com/guides/best-ai-agents-reddit | Why cited: hallucinated-metric pattern.

[15] Search Engine Land — _How to train in-house LLMs on brand voice_. _T2._ https://searchengineland.com/guide/how-to-train-in-house-llms-on-brand-voice | Why cited: brand-voice drift pattern.

[16] Data Axle — _How to avoid AI pitfalls in 2026: A marketer's guide_. _T2._ https://www.data-axle.com/resources/blog/avoid-ai-pitfalls-in-marketing/ | Why cited: strategy-vs-execution caveat.

[17] Linkeddit / Aibrify — _Best Subreddits for AI Marketing 2026 / How to use AI for Reddit marketing without ToS risk_. _T2._ https://linkeddit.com/blog/best-subreddits-for-ai-marketing-2026 | Why cited: Reddit autoposting risk.

[18] MarTech — _6 common agentic AI pitfalls and how to avoid them_. _T2._ https://martech.org/six-common-agentic-ai-pitfalls-and-how-to-avoid-them/ | Why cited: governance triad.

[19] GoPractice — _Jobs to Be Done: Theory and Frameworks_. _T1_ (Christensen + Moesta + Ulwick canonical). https://gopractice.io/product/jobs-to-be-done-the-theory-and-the-frameworks/ | Why cited: JTBD canonical synthesis.

[20] HBR — _Know Your Customers' Jobs to Be Done_ (Christensen et al., 2016). _T2._ https://hbr.org/2016/09/know-your-customers-jobs-to-be-done | Why cited: HBR canonical exposition.

[21] April Dunford — _Obviously Awesome_ (2019). _T1._ https://www.aprildunford.com/books | Why cited: 5-component positioning.

[22] Dave McClure — _Startup Metrics for Pirates_ (2007); PostHog / Amplitude / FourWeekMBA secondaries. _T1._ https://mcgaw.io/wp-content/uploads/2016/04/PirateMetrics_Final.pdf | Why cited: AARRR canonical deck.

[23] Gabriel Weinberg & Justin Mares — _Traction_ (Bullseye + 19 channels). _T1._ https://brianbalfour.com/essays/traction-the-bullseye-framework | Why cited: 19-channel + 5-step process.

[24] Growth Method / ProductPlan / Kaizenko — ICE (Sean Ellis) and RICE (Intercom). _T2._ https://growthmethod.com/ice-framework/ | Why cited: experiment prioritization.

[25] Mark & Pearson — _The Hero and the Outlaw_ (2002); Visme / JD Meier secondaries. _T2._ https://visme.co/blog/brand-archetypes/ | Why cited: 12 archetypes canonical.

[26] Donald Miller — _Building a StoryBrand_ (2017) + _Building a StoryBrand 2.0_ (Jan 2025). _T1._ https://welldressedwalrus.com/7-parts-of-a-storybrand-framework/ | Why cited: SB7 framework.

[27] Eugene Schwartz — _Breakthrough Advertising_ (1966). _T1._ https://betweenthelinescopy.com/blog/stages-of-awareness/ | Why cited: 5 stages of awareness, foundational copywriting frame.

[28] Robert Cialdini — _Influence_ (1984) + Unity addition (2016); ASU W.P. Carey / IAW secondaries. _T2._ https://www.influenceatwork.com/7-principles-of-persuasion/ | Why cited: 7 principles of persuasion.

[29] Neeraj Agrawal / Battery Ventures — T2D3. _T2._ https://www.t2d3.pro/ | Why cited: stage-aware revenue benchmark.

[30] Beancount.io / Drivetrain / FullCast — SaaS unit economics benchmarks 2026. _T2._ https://beancount.io/blog/2026/05/10/saas-metrics-founders-must-track-2026-ltv-cac-nrr-churn-cac-payback-benchmarks-guide | Why cited: CAC/LTV/NRR benchmarks.

[31] Motion — _Creative Strategy Bootcamp 2026_ + _Motion metrics for Meta and TikTok_. _T2._ https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/meta-tiktok-cheat-sheet | Why cited: Meta/TikTok creative testing standard.

[32] SiteCentre / Store Growers — _STAG vs SKAG 2026_. _T2._ https://www.sitecentre.com.au/blog/stag-vs-skag-campaigns | Why cited: Google Ads structure 2026 best practice.

[33] DigitalApplied / SEO-Kreativ / Evertune — _E-E-A-T + Topical Authority + Google March 2026 Core Update_. _T2._ https://www.digitalapplied.com/blog/seo-content-clusters-2026-topic-authority-guide | Why cited: 2026 SEO ground truth.

[34] Klaviyo Help Center + Chase Dimond + Flowium — _Klaviyo Flows Guide 2026_. _T2._ https://www.chasedimond.com/klaviyo-flows-guide | Why cited: DTC lifecycle flow stack.

[35] Anthropic — _Create custom subagents_ (Claude Code docs). _T1._ https://code.claude.com/docs/en/sub-agents | Why cited: official subagent spec (YAML frontmatter, `.claude/agents/`).

---

## Confidence Assessment

- **Strong evidence, convergent** — frameworks canon (Dunford, Balfour, AARRR, Schwartz, StoryBrand, Cialdini, Bullseye, JTBD): multiple T1 sources + decades of practitioner adoption.
- **Strong evidence, convergent** — Claude Code subagent format (official T1 docs + multiple T1 implementation repos).
- **Convergent** — measurement stack 2026 (MMM + incrementality + platform attribution, triangulated): T2 sources across Deducive, eMarketer, Liftlab, Measured, SegmentStream all agree.
- **Convergent** — agent memory taxonomy (episodic/semantic/procedural): convergent across LangMem, Letta, Mem0, Zep.
- **Mostly convergent, some contested** — STAG vs SKAG: 2026 consensus is STAG, but a minority case for SKAG on high-value niche keywords persists.
- **Single-source / anecdotal** — specific community pitfall framings: aggregated from T3 Reddit/HN summaries; underlying frustrations are real but specific quotes were paraphrased through aggregators, not pulled from primary threads. Marked T3.
- **Speculative** — exact star counts and "what's best in 2026" framework rankings shift quarterly; treat numerics as ±20%.

---

## Gaps & Open Questions

- **Did not retrieve full Reddit thread primary text** — relied on aggregators (AIToolDiscovery, Linkeddit, ai-agent-ops); a future pass should pull representative threads from `r/AI_Agents`, `r/marketing`, `r/SaaS` directly with quoted timestamps.
- **No direct fetch of Reforge growth-loops post** (403 on WebFetch); used T2 summary articles. The full Reforge essay would add nuance on loop _typology_ (acquisition vs retention vs viral vs paid vs content-driven specifics).
- **Did not benchmark agent-system performance** — no public eval of how well existing marketing agent crews actually perform on real briefs; LoCoMo-style memory benchmarks exist but no marketing-specific eval set.
- **Brand-voice training is under-documented in OSS** — every reference says "use exemplars + style guide" but few repos show _how_ (file format, retrieval pattern, drift detection). Open opportunity for the Hyperagent output.
- **MCP server availability for marketing tools** — Meta Ads Library MCP exists (used by talknerdytome-labs), but coverage is uneven: Klaviyo, GA4, Triple Whale, TikTok Creative Center MCP servers are inconsistent or missing.
- **Regulated-vertical compliance** — health, finance, gambling, crypto each have distinct rules; this report did not enumerate them per-vertical.

## Suggested Next Steps

1. **Pull primary threads** — direct fetches of top 10 `r/AI_Agents` and `r/marketing` posts on AI marketing agents with quoted excerpts and dates, to replace T3 aggregator sourcing.
2. **Audit existing MCP servers** — enumerate which marketing-tool MCP servers exist (Meta Ads Library, Klaviyo, GA4, Shopify, Triple Whale, TikTok Creative Center, Semrush, Ahrefs) with link to repo + tool list each.
3. **Build a brand-voice training reference** — pick one open-source brand (e.g., Linear, Ghost, Plausible) and document an exemplar `memory/brand-voice/` directory based on their public copy.
4. **Vertical playbook depth** — write the first vertical playbook (DTC e-commerce) end-to-end as a worked example, then derive the others.
5. **Regulated-category compliance overlays** — separate research pass for health/finance/gambling/crypto disclosure and ad-policy rules.
6. **Eval harness** — design a small benchmark (10 marketing briefs of different shapes: launch, retention crisis, channel diversification, rebrand) to score generated agent systems on.
