# Higgsfield AI — Practical Evaluation for AI Video Production

_Research date: 2026-05-15. Pricing and feature data verified live against the Higgsfield MCP server on this date._

---

## TL;DR

Higgsfield is a San Francisco–based AI video platform (founded 2023, $1.3B valuation, ~15M users) that has evolved from a single in-house video model into a **multi-model aggregator** wrapped in opinionated creator tooling. Its real edge is not raw video quality — Kling 3.0, Veo 3.1, and Sora 2 are accessible from many places — but the **layer on top**: 60–70+ cinematic camera presets ("DoP"), the Soul image model for consistent characters/UGC, Lipsync Studio ("Speak"), Marketing Studio for one-click product ads, and a Virality Predictor. It is the right tool for short-form social/UGC/ad creative and cinematic 4–15s clips; it is the wrong tool for narrative shorts >15s, broadcast deliverables, or anyone needing temporal consistency over a full minute. The platform also carries non-trivial reputational risk from a February 2026 backlash over deceptive "unlimited" plans, deepfake marketing, and a deleted "we ended 20 creative jobs" post [T2].

---

## 1. What Higgsfield Is

**Company.** Higgsfield AI, founded 2023 by Alex Mashrabov (ex-Snap, led generative AI at Snap; previously sold AI Factory to Snap in 2020 for $166M) and Erzat Dulat. Headquartered in San Francisco with ties to Kazakhstan's Astana Hub [1, T2; 2, T2].

**Funding & scale.**

- Seed: $8M, April 2024, led by Menlo Ventures [3, T3]
- Series A: $50M, September 2025, led by GFT Ventures [4, T3]
- Series A extension: $80M, January 2026, led by Accel — valuation **$1.3B** [1, T2]
- Total raised: ~$138M
- Reported scale (Jan 2026, company-stated): **~15M users**, **$200M ARR run-rate** [1, T2]

**Product positioning.** Browser-based end-to-end AI video creation suite launched March 2025 [2, T2]. The product has repositioned itself from "AI video model" to **multi-model creator platform** — explicitly aggregating Sora 2, Veo 3 / 3.1, Kling 2.6 / 3.0, Seedance 2.0, Hailuo, Wan, Grok Imagine, plus its own Higgsfield Soul (images) and Cinema Studio Video (video) [verified live via MCP `models_explore`, T1].

**Audience.** Officially: "consumers, creators, and social media teams" — but TechCrunch notes Higgsfield positions itself "primarily as a professional marketing tool" rather than casual content [1, T2]. Sweet spot in 2026: short-form UGC/ad creators, marketing teams, and indie filmmakers who want cinematic camera language without learning Runway-level controls.

---

## 2. Capabilities

### Video generation modes (verified Tier 1 via MCP)

- **Image-to-video** — all video models accept a `start_image` (some also `end_image`)
- **Text-to-video** — supported on Grok Imagine, Veo 3.1, Cinema Studio Video, Marketing Studio
- **Character consistency** — Soul Cast (cinematic character identity), Wan 2.7 (character-consistent + audio sync), Seedance 2.0 (reference-driven identity, multi-SKU)
- **Lip sync** — dedicated **Lipsync Studio** ("Speak"): upload audio, pick/generate avatar, get talking-head with natural lip movement [5, T1]
- **Camera control** — Cinema Studio Video v2 exposes genre (`action / horror / comedy / western / suspense / intimate / spectacle`) plus `pro/std` mode; broader UI exposes 60–70+ presets (Bullet Time, Crash Zoom, Dolly Zoom, Orbit, Crane, Earth Zoom-Out, 360 Rotation) [6, T3; 7, T3]
- **Marketing Studio** — one-click product ads sized for TikTok/Reels, with brand-kit-aware prompts, avatars, ad-format presets, and hook/setting libraries [verified live via MCP, T1]

### Signature features explained

| Feature                                   | What it actually does                                                                                                                                                                                                                         |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Soul / Soul 2.0**                       | Higgsfield's proprietary **image** model. Tuned for UGC, fashion editorial, skin texture, fabric, and commercial portraiture. Outputs up to 2K. `soul_id` parameter persists a character identity across generations [T1].                    |
| **Soul Cinema / Cinema Studio Image 2.5** | Cinema-grade stills up to **4K**, dramatic lighting [T1].                                                                                                                                                                                     |
| **DoP (Director of Photography)**         | Higgsfield's name for its cinematic camera-control layer. Sits on top of any underlying video model and applies pan/tilt/dolly/tracking/zoom + 60+ named presets _before_ generation rather than as post [8, T3].                             |
| **Speak / Lipsync Studio**                | Audio-driven talking-avatar generation with natural lip sync [5, T1].                                                                                                                                                                         |
| **Steal**                                 | Style-replication / "remix" tool — let users replicate the look of a reference. Has drawn criticism (see §8) [9, T2].                                                                                                                         |
| **Virality Predictor**                    | Scores clips ≤15s on three metrics: **Hook Score** (first-second stopping power), **Hold Rate** (estimated retention), **Brain Heatmap** (neural-attention visualization). Black box: no published training set or accuracy metrics [10, T3]. |
| **Marketing Studio**                      | Templated product-ad generator with brand kits, avatars, hooks, and ad-format presets — produces TikTok/Reels-ready videos and image ads [T1].                                                                                                |

### Output specs (verified Tier 1)

- **Max resolution**: image up to **4K** (Seedream 4.5, Cinema Studio Image, Nano Banana Pro/2 via Higgsfield); video up to **1080p** on most pipes, **4K** on Kling 3.0 "4k" mode [T1]
- **Max duration**: most video models cap at **5–15 seconds per clip**; Seedance 2.0 range 4–15s, Kling 3.0 3–15s, Veo 3.1 fixed 4/6/8s, Cinema Studio Video 3.0 4–15s [T1]
- **Audio**: native audio supported on Kling 2.6/3.0, Veo 3, Veo 3.1, Wan 2.7, Grok Imagine, Marketing Studio (`generate_audio` flag) [T1]
- **Watermark**: free tier outputs are watermarked; paid tiers (Plus / Ultra) are not [unverified — Higgsfield public pricing page returned no content via WebFetch, only secondary sources confirm]

### Known limitations (triangulated)

- **Temporal coherence degrades beyond ~10s**: gestures warp, characters mutate mid-scene, looping animations break [11, T3; 12, T3]
- **Content moderation false positives**: "may contain protected content" rejections on innocuous prompts (auto-refunds credits, but disrupts flow) [11, T3]
- **Text/logo rendering in background elements** distorts [11, T3]
- **Failure rate on batches**: one reviewer logged ~50% failure on second-batch parallel generations [11, T3]
- **Hands and fast motion** still problematic on most underlying models, including Higgsfield's own Cinema Studio [12, T3]
- **NSFW**: blocked by platform filters; the policy is enforced but inconsistently — Higgsfield itself has been criticized for its marketing using sexually-suggestive deepfakes of named celebrities [9, T2]

---

## 3. Models Available on Higgsfield

**This is the most important clarification**: Higgsfield is **primarily an aggregator** that wraps third-party video models AND ships its own. Verified live via the MCP `models_explore` endpoint on 2026-05-15 [T1]:

### Higgsfield-proprietary

- **Soul 2.0** (image, UGC/fashion/character)
- **Soul Cinema / Cinema Studio Image 2.5** (image, up to 4K)
- **Soul Cast** (character identity)
- **Soul Location** (environment/background)
- **Cinema Studio Video** / **Cinema Studio Video v2** / **Cinema Studio Video 3.0** (video, with genre + camera control)
- **Marketing Studio** (video) / **Marketing Studio Image** / **DTC Ads** (image, brand-kit-aware)

### Third-party models exposed

- **Google**: Veo 3, Veo 3.1 (preview / fast / lite), Nano Banana, Nano Banana 2, Nano Banana Pro
- **ByteDance**: Seedance 1.5 Pro, Seedance 2.0, Seedream 4.5, Seedream 5.0 Lite
- **Kling**: Kling 2.6, Kling 3.0 (std / pro / 4k), Kling O1 Image
- **Hailuo / Minimax**: Minimax Hailuo (variants `minimax`, `minimax-fast`, `minimax-2.3`, `minimax-2.3-fast`)
- **Wan**: Wan 2.6, Wan 2.7 (audio-sync, character-consistent)
- **xAI**: Grok Imagine (image + video)
- **Black Forest Labs**: Flux 2.0 (pro/flex/max), Flux Kontext Max
- **OpenAI**: GPT Image 1.5, GPT Image 2
- **Tongyi-MAI**: Z Image

**Sora 2 is referenced in Higgsfield marketing** [7, T3] but **does NOT appear in the live model list** on 2026-05-15 [T1]. That tracks: OpenAI announced in March 2026 that Sora's web/app would sunset on April 26, 2026 and the API on September 24, 2026 [13, T3]. Treat any "Higgsfield + Sora 2" claim as time-bounded.

---

## 4. Pricing & Plans (as of 2026-05-15, verified Tier 1 via MCP)

### Tiers

| Plan         | Monthly  | Annual                   | Credits/mo       | Notes                                                                                                                                      |
| ------------ | -------- | ------------------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Free**     | $0       | —                        | 10/day           | Limited models, 1 concurrent job, watermarked [14, T3]                                                                                     |
| **Starter**  | $15      | —                        | low              | Entry tier [14, T3; 15, T3]                                                                                                                |
| **Plus**     | $49      | ~$39/mo annual           | 1,000            | Unlimited gens on select models [14, T3]                                                                                                   |
| **Ultra**    | $129     | **$99/mo annual** ([T1]) | **3,000** ([T1]) | Up to 8 parallel videos + 8 parallel images, "all models", early access, "70% cheaper per credit" [T1]; scalable to 9,000 credits [14, T3] |
| **Business** | $89/seat | $62/seat annual          | —                | Team features [14, T3]                                                                                                                     |

**Top-up credit packs** (verified Tier 1):

- 500 credits — $26 (~19 cr/$)
- 1,000 credits — $49 (~20 cr/$)
- 2,000 credits — $95 (~21 cr/$)
- 4,000 credits — $190 (~21 cr/$) — most popular

### Credit economics (Tier 1, Ultra-plan tooltips)

"3,000 credits/month ≈ **12,000 images** or **~500 videos** or **~100 character generations**" [T1].

- ≈ 0.25 credits per image (cheap models)
- ≈ 6 credits per video (averaged across models/durations)
- ≈ 30 credits per character generation

Hands-on Unite.AI confirmed **192 credits** for a single 8-second 1080p dual-batch video [11, T3] — i.e. premium-tier models burn credits 30x faster than the averaged rate. Triangulates with the widely-cited Reddit/reviewer complaint that "10 iterative attempts on a Sora 2 prompt can wipe out a monthly Starter budget" [12, T3].

### Commercial use

Higgsfield outputs on paid plans are commercially usable per Higgsfield's product positioning [T1 product copy refers to "DTC ads", "marketing", "TikTok/Reels-ready"]; full ToS language **[unverified]** — confirm before high-stakes commercial use.

### Caveat

The Ultra annual tier shows live promotions (May 2026) bundling **365-day unlimited** on Seedream 4.5/5.0 Lite, Flux 2.0 Pro, Nano Banana, Kling O1 Image, GPT Image, plus a **7-day unlimited** burst on Nano Banana Pro/2 and Kling 3.0, and **5,000–10,000 free Soul V2 & Cinema gens** [T1]. These rotate monthly — always re-check at point of purchase.

---

## 5. Comparison vs Sora 2 / Runway Gen-4 / Veo 3 / Kling 2 / Hailuo

| Model / Tool                     | Best for                                                                                                           | Weakness                                                                   | Cost (rough)                                      | Max length   | Commercial use   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- | ------------------------------------------------- | ------------ | ---------------- |
| **Higgsfield**                   | Cinematic camera control, UGC/ads, character consistency via Soul, multi-model access from one sub                 | In-house video weak vs leaders; temporal coherence >10s; reputational risk | $49–$129/mo                                       | 4–15s/clip   | Yes (paid tiers) |
| **Sora 2 / Sora 2 Pro (OpenAI)** | Most photoreal output when prompted well                                                                           | **Sunsetting Apr–Sep 2026** [13, T3]; availability risk                    | Bundled w/ ChatGPT Pro                            | ~20s typical | Yes              |
| **Runway Gen-4 / 4.5**           | Pro creative control: motion brush, reference-character consistency, granular camera moves                         | Steeper learning curve; per-second cost adds up                            | $15–$95/mo + credits                              | 10–16s       | Yes              |
| **Google Veo 3 / 3.1**           | Strongest **all-arounder**: prompt adherence, native audio, 4K landscape/portrait, narrative shots [16, T3]        | Fixed durations (4/6/8s); less stylistic personality                       | Bundled w/ Google AI Pro/Ultra, or via Higgsfield | 4–8s         | Yes              |
| **Kling 3.0**                    | Cinematic lighting, complex motion (hair, liquids, fabric), multi-shot storyboard, native cross-cut audio [16, T3] | Less prompt-adherence than Veo; China-hosted                               | Direct sub or via Higgsfield                      | 5–15s        | Yes              |
| **Minimax Hailuo 2.3**           | Natural physics, facial emotion at 1080p; cheapest premium tier                                                    | Lower max duration; weaker camera control                                  | Cheapest of the set                               | 6–10s        | Yes              |

### Where Higgsfield specifically beats each

- **vs Sora 2**: still available; richer creator UI (Soul, presets, Lipsync, Virality Predictor); not facing imminent sunset
- **vs Runway**: lower friction for cinematic-camera presets — Runway's motion-brush is more powerful but slower to learn; Higgsfield's "pick a preset, pick a genre, generate" wins on speed-to-shot
- **vs Veo 3**: gives you Veo 3 _plus_ Soul (character) and Marketing Studio in one bill — strictly additive
- **vs Kling 3.0**: same — Kling 3.0 is **already on Higgsfield** [T1]; aggregation is the value
- **vs Hailuo**: better identity persistence (Soul Cast) and richer ad/UGC tooling

### Where Higgsfield loses

- **Best raw video quality**: Veo 3.1 / Kling 3.0 are the underlying engines anyway, but if you want Sora 2 specifically for ad-hoc clips, ChatGPT Pro is cheaper while it lasts
- **Long-form narrative (>15s coherent)**: nobody is great at this yet, but Runway Gen-4 + Sora 2 are stronger when stitched
- **Granular post-style control**: Runway still wins on motion-brush + masking
- **Trust / safety**: Higgsfield has open controversy (§8); enterprise buyers may prefer Google / Adobe / Runway

### Counter-evidence / dissent (CRITICAL)

Curious Refuge benchmarks Higgsfield's **in-house video model at 3.7/10** across Prompt Adherence, Temporal Consistency, Visual Fidelity, Motion Quality, Style — saying "as a standalone video generator it isn't quite ready yet" and that its value is the suite, not the core model [17, T3]. Unite.AI's review is far more positive, but explicitly tests **Cinema Studio + multi-model workflows** [11, T3]. **Both reviewers agree**: the platform is greater than the proprietary model. Don't buy Higgsfield expecting its own video model to beat Veo or Kling — buy it for the layer.

---

## 6. When Higgsfield Is the Right Choice (and When It Isn't)

### Reach for Higgsfield when

- Producing **short-form ad creative / UGC** (Marketing Studio is purpose-built)
- You need **cinematic camera language** without prompt-engineering it (DoP presets)
- You need **a consistent character** across multiple shots (Soul Cast / Soul 2.0)
- You're producing **talking-head avatars** with custom audio (Lipsync Studio)
- You want to **A/B different underlying models** (Veo vs Kling vs Seedance) on one bill without juggling logins
- You want a **virality sniff-test before posting** (Virality Predictor — directionally useful, not a substitute for A/B testing [10, T3])

### Reach for something else when

- **Narrative shorts >15s** with consistent characters → Runway Gen-4 + manual stitching, or Veo 3.1 + careful prompts
- **Broadcast / client deliverables at >1080p with motion polish** → still hand off to traditional tools after AI-generated b-roll
- **Music videos with synced-to-beat cuts** → use Kling 3.0 directly (multi-shot storyboard mode is its strength) [16, T3]
- **Enterprise-safe workflows** with audit trails / IP indemnity → Adobe Firefly Video or Google Veo directly
- **You're price-sensitive** and only need occasional clips → ChatGPT Pro (Sora 2 while available) or Veo via Google AI Pro is cheaper

---

## 7. Best Practices & Gotchas

### Prompt patterns that work [11, T3; 6, T3]

- **Specify lighting**: "neon", "practical lights", "rim light", "high-detail skin texture"
- **Layer physical effects**: fluid dynamics, steam, particles, depth-of-field
- **Camera language**: focal length, aperture, movement type ("35mm anamorphic, f/1.4, slow dolly-in")
- **Use genre tags**: noir, drama, epic, intimate observer — these are surfaced as parameters on Cinema Studio Video v2 [T1]
- **Start from an image, not text**, for anything where identity matters — Soul/Nano Banana → feed into Veo 3.1 or Kling 3.0 as `start_image`

### Common failure modes [11, T3; 12, T3; 17, T3]

- Background text/logos warp — keep them out of the frame or accept the distortion
- Long gestures (>3s) and looping animation drift
- Content-moderation false positives on innocuous prompts — Higgsfield does auto-refund the credits
- Batch generation occasionally fails one of two parallel jobs — budget extra credits
- Hands and fast motion still imperfect on all models

### Virality Predictor — useful, with caveats

- Treat **Hook Score** and **Hold Rate** as **directional**, not authoritative — Higgsfield publishes neither training data nor accuracy metrics [10, T3]
- It's a **classifier without an iteration loop** — it doesn't tell you how to fix a low score, only that one exists
- Not a substitute for a real A/B test on the actual platform [10, T3]

---

## 8. Recent Reception (2025–2026)

### Praise

- Multiple 2026 reviewers call Higgsfield "the strongest multi-model AI video platform on the market" [7, T3]
- Unite.AI specifically praises Cinema Studio 3.5's "director-level control" and Soul's character consistency [11, T3]
- Growth numbers (15M users, $200M ARR) are extraordinary and broadly accepted [1, T2]

### Controversy (February 2026) — the elephant in the room

A coordinated backlash hit Higgsfield in early February 2026, documented by **The Register** [9, T2] and **Times of Central Asia** [18, T3]:

1. **"Ended 20 creative jobs" post** — Higgsfield's official X account boasted its motion-design tool had ended 20+ creative jobs; artists revolted; post was deleted [9, T2]
2. **"Unlimited" plans that weren't** — users reported aggressive bans on heavy users of advertised-as-unlimited Nano Banana Pro and Kling tiers; refunds refused [9, T2; 18, T3]
3. **Wrapper-with-throttling complaints** — tester Ian Hudson: platform is "a wrapper for other services" with artificial 4–10 hour wait times for 5-minute videos [9, T2]
4. **Unauthorized deepfake marketing** — promotional materials allegedly featured Sydney Sweeney, Zendaya, Donald Trump, and Elon Musk without authorization; some clips reportedly contained "racist and sexually explicit language" attributed to cartoon characters [18, T3]
5. **Astroturfing accusations** — critics alleged paid/coordinated review activity
6. **X account suspended** on 2026-02-09 [18, T3]

The Wikipedia article on Higgsfield AI [2, T2] does **not** mention these controversies as of this research date — suggesting either editorial scrubbing or pending update. The Register and Times of Central Asia coverage is detailed and corroborating; Trustpilot reviews skew negative on customer-service/billing issues [reflected across [18, T3], [19, T3]].

**Implication for evaluation**: the _tool_ is genuinely capable. The _company_ is operating under reputational scrutiny that may affect support quality, pricing stability, and enterprise viability. For Rootlabs-style usage (creative production from one account), this is a risk but probably not a blocker; for client-facing or contract work, factor it in.

---

## Source Bibliography

[1] **AI video startup, Higgsfield, founded by ex-Snap exec, lands $1.3B valuation** — TechCrunch, 2026-01-15 — **T2**
https://techcrunch.com/2026/01/15/ai-video-startup-higgsfield-founded-by-ex-snap-exec-lands-1-3b-valuation/
Why cited: primary funding + valuation + revenue + user-count source.

[2] **Higgsfield AI** — Wikipedia (accessed 2026-05-15) — **T2**
https://en.wikipedia.org/wiki/Higgsfield_AI
Why cited: founders, founding year, HQ, product launch timing.

[3] **Higgsfield AI raises $8M Seed 2024-04-04** — Founder Lodge — **T3**
https://founderlodge.com/round/Higgsfield-AI-raises-8000000-Seed-2024-04-04-Alex-Mashrabov-MTg1MTM
Why cited: seed round confirmation.

[4] **Higgsfield: $50 Million Series A Raised To Transform AI Video Creation** — Pulse2 — **T3**
https://pulse2.com/higgsfield-50-million-series-a-raised-to-transform-ai-video-creation/
Why cited: Series A confirmation.

[5] **Lipsync Studio** — Higgsfield official — **T1**
https://higgsfield.ai/lipsync-studio
Why cited: official feature page for Speak/Lipsync.

[6] **Higgsfield AI Review 2026** — JustPickAI — **T3**
https://justpickai.com/blog/higgsfield-ai-review-2026
Why cited: camera-preset enumeration (60+ presets confirmed).

[7] **Higgsfield AI Review 2026** — freerdps — **T3**
https://freerdps.com/blog/higgsfield-ai-review/
Why cited: DoP definition, multi-model claim, 2026 reception.

[8] **Higgsfield vs Sora vs Veo: Which AI Video Model to Pick** — claudefa.st — **T3**
https://claudefa.st/blog/tools/mcp-extensions/higgsfield-vs-sora-vs-veo
Why cited: DoP / camera-control positioning.

[9] **AI video startup boasts it 'ended' jobs, gets backlash** — The Register, 2026-02-06 — **T2**
https://www.theregister.com/2026/02/06/higgsfield_ai_job_loss/
Why cited: reputable Tier-2 coverage of the February 2026 backlash.

[10] **Higgsfield Virality Predictor: Hook Score, Hold Rate, Brain Heatmap** — Pasquale Pillitteri — **T3**
https://pasqualepillitteri.it/en/news/2273/higgsfield-virality-predictor-hook-score-hold-rate-2026
Why cited: the only detailed breakdown of Virality Predictor metrics + the black-box caveat.

[11] **Higgsfield AI Review: I Made AI Films on a Budget Laptop** — Unite.AI — **T3**
https://www.unite.ai/higgsfield-ai-review/
Why cited: detailed hands-on with credit costs, failure modes, feature ratings.

[12] **Higgsfield Review 2026: Is It Worth It? Honest & In-Depth Analysis** — higgsfield-review.com — **T3**
https://higgsfield-review.com/
Why cited: limitations on temporal consistency, pricing concerns.

[13] **AI Video Generation 2026: Sora 2 vs Veo 3.1 vs Kling 3.0** — Lushbinary — **T3**
https://lushbinary.com/blog/ai-video-generation-sora-veo-kling-seedance-comparison/
Why cited: Sora 2 sunset dates (April 26 + September 24, 2026).

[14] **Higgsfield AI Pricing 2026** — Imagine.Art — **T3**
https://www.imagine.art/blogs/higgsfield-ai-pricing
Why cited: Free / Starter / Plus / Ultra / Business pricing breakdown.

[15] **Higgsfield AI Pricing 2026 — Real Plans, Credits & Cost Per Veo 3 Video** — vo3ai — **T3**
https://www.vo3ai.com/higgsfield-ai-pricing
Why cited: triangulation on plan pricing.

[16] **Best AI Video Generator in 2026: Runway, Veo, Seedance, Kling & More** — Pixflow — **T3**
https://pixflow.net/blog/best-ai-video-generator/
Why cited: cross-model strength comparisons.

[17] **Higgsfield AI Video Generator Review** — Curious Refuge — **T3**
https://curiousrefuge.com/blog/higgsfield-ai-video-generator-review
Why cited: dissenting 3.7/10 benchmark; counter-evidence on in-house video quality.

[18] **Kazakh Startup Higgsfield AI: From "Unicorn" to Racism and Sexism Scandal** — Times of Central Asia — **T3**
https://timesca.com/kazakh-startup-higgsfield-ai-from-unicorn-to-racism-and-sexism-scandal/
Why cited: detailed account of deepfake marketing + X suspension.

[19] **Higgsfield AI Reviews** — Trustpilot — **T3**
https://www.trustpilot.com/review/higgsfield.ai
Why cited: aggregated user complaints on billing/refunds.

[T1] **Live Higgsfield MCP server** — accessed 2026-05-15 — **T1**
Sources: `models_explore` (list of 35+ models with parameters), `show_plans_and_credits` (Ultra plan structure, credit packs, pricing, promotions), `balance` (current credits + plan).

---

## Confidence Assessment

| Claim category                                            | Confidence                                                                                            |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Funding history, valuation, founders                      | **Strong** — TechCrunch + Wikipedia + multiple secondary sources converge                             |
| Live model lineup, pricing, credit economics              | **Strong** — verified Tier-1 against MCP today                                                        |
| Feature descriptions (Soul, DoP, Speak, Marketing Studio) | **Strong** — Tier-1 product pages + Tier-3 hands-on                                                   |
| Virality Predictor mechanics                              | **Moderate** — single detailed Tier-3 source; Higgsfield publishes no methodology                     |
| Comparative quality vs Veo / Kling / Sora / Runway        | **Moderate, contested** — reviewers disagree (Curious Refuge 3.7/10 vs Unite.AI rave); both reflected |
| February 2026 controversies                               | **Strong** — The Register (Tier 2) + Times of Central Asia + Trustpilot all corroborate               |
| Watermark policy on free tier                             | **Single source / unverified**                                                                        |
| Commercial-use license terms                              | **Unverified** — confirm against current ToS                                                          |

---

## Gaps & Open Questions

- **Exact watermark policy** on free tier — only secondary sources; Higgsfield's pricing page returned no scrapeable content
- **Current ToS commercial-use language** — should be confirmed before signing a paid plan for client work
- **Whether Sora 2 is still accessible via Higgsfield** as of May 2026 — not in the live `models_explore` response today; was reportedly available in early 2026
- **Virality Predictor accuracy** — Higgsfield has not published validation data; no third-party benchmark exists
- **Post-controversy management changes** — no public reporting on whether Higgsfield has changed practices since February 2026 X suspension
- **Enterprise / business-plan SLA terms** — only headline pricing is public

---

## Suggested Next Steps

1. **Run a head-to-head A/B inside the platform**: same brief, Cinema Studio Video 3.0 vs Kling 3.0 vs Veo 3.1 — measure credit-per-acceptable-output for Rootlabs' actual UGC/ad needs
2. **Test Soul Cast for MagAshwa creator-consistency** — generate one Soul Cast identity, then push that character through 5 ad concepts; verify cross-shot identity holds
3. **Test Marketing Studio with the real product** — feed a MagAshwa product image + brand kit and see whether DTC Ads quality matches the manual ad workflow
4. **Stress-test the Virality Predictor on a known dataset** — score 10 winning and 10 losing Rootlabs ads, check whether Hook Score + Hold Rate correlate with actual platform CTR/retention before relying on the metric
5. **Read current Higgsfield ToS** (Section: Output Rights / Commercial Use / IP Indemnity) before any client-facing production
6. **Set a credit-burn budget** for the first 30 days — Unite.AI's 192-cr-per-8s data point suggests Ultra's 3,000 credits ≈ ~15 premium 8-second clips, not the marketing's "500 videos"
