# Rootlabs Mobile App — Strategy Lock

**Date:** 2026-05-14 (drafted 05:08 IST)
**Status:** Phase 0 — draft, awaiting Kartavya sign-off on the 5-part framework

---

## Project mission (the honest one)

This is **not** a shipped app. This is an **intern-built portfolio piece + advocacy artifact**.

The end-state success condition is **not** "app is in the App Store earning revenue." It is:

> When the app is polished enough that swapping in 3 API keys would make it ship-ready, Kartavya walks into Rootlabs / Mosaic Wellness and says:
> _"Here is the app. Try it on your phone right now. The only thing missing is API access — when you give me that, here are the 3 files I swap to go live."_

The demo **is** the pitch. The polish **is** the leverage.

---

## Hard constraints

- **No paid APIs.** Intern budget = $0. Anything that costs even a Google Cloud signup is deferred.
- **No company API access yet.** Rootlabs / Mosaic does not currently give Kartavya access to their Shopify Storefront API, customer DB, or any internal endpoint.
- **No App Store submission.** Demo runs on real phones via **Expo Go** — free, no Apple Developer account needed.
- **No real money flows.** No checkout. "Add to wishlist" is the closest to commerce the app gets in v1.
- **No medical / health-claim authoring.** Every product description and ingredient claim must be **verbatim from rootlabs.co** — we don't make new claims, we mirror existing ones (which the company's lawyers already cleared).

---

## What we deliberately defer (these are the company's problem when they adopt the project)

- FDA / FTC / state-by-state compliance posture
- Apple Pay / Google Pay / Shopify Storefront checkout integration
- App Store / Play Store submission and review
- PCI compliance
- Real auth (Sign in with Apple, Google, Shopify customer accounts)
- Sentry / PostHog / production observability
- ATT / privacy manifests
- Push notification infrastructure (Expo Push API exists but we won't wire it in v1)
- Real product catalog sync (we use a static JSON snapshot)

For each of these, the codebase will have a **clearly labeled `// PLUG IN HERE`** comment showing the company's engineering team exactly where they wire up production.

---

## The free-only stack

| Layer           | Free tool                                                        | Cost when scaling                                         |
| --------------- | ---------------------------------------------------------------- | --------------------------------------------------------- |
| Framework       | Expo + React Native + TypeScript                                 | Free forever for dev                                      |
| Preview         | Expo Go on phone                                                 | Free                                                      |
| Data            | Static JSON files in repo (products / reviews / science content) | $0 storage                                                |
| Local state     | AsyncStorage + Expo SQLite                                       | $0                                                        |
| Auth (mock)     | Fake user object on first launch                                 | Replace with real auth — adapter slot                     |
| AI (mock)       | Pre-written canned responses for "recommend a product"           | Replace with Claude/Gemini — adapter slot                 |
| Icons           | Lucide React Native (MIT)                                        | Free forever                                              |
| Fonts           | Figtree (Google Fonts) + Inter as Matter-substitute              | Free; later: license Matter if Rootlabs wants exact-match |
| Animations      | React Native Reanimated (built into Expo)                        | Free                                                      |
| Version control | GitHub free tier (private repo)                                  | Free up to small team                                     |
| Build (later)   | EAS Build free tier — 30 builds/month                            | Free; paid when needed                                    |

**Total monthly cost during development and demo: $0.**

---

## Phase sequence

```
Phase 0  Lock the 5-part app definition           (10 min, your sign-off — TODAY)
Phase 1  Extract Mosaic design system             (read 27 screenshots + integrate Shopify theme tokens)
Phase 2  Architecture skeleton with adapter slots (folder structure + "PLUG IN HERE" comments)
Phase 3  Build the screens with mock data         (Splash → Home → Catalog → PDP → Science → Saved)
Phase 4  Polish — animations, empty states        (demo-grade quality)
Phase 5  Demo packaging                           (README + screenshots + QR code for company)
```

---

## The 5-part framework (Kartavya — sign off or rewrite)

Draft, per the video's discipline. Read each part and tell me yes / rewrite.

### 1. Core function

**Help a user discover the right Rootlabs product for their wellness goal, and learn what's in it.**

- Not "buy" (no checkout in v1).
- Not "track habits."
- Not "log symptoms."
- The app's _one job_ in v1: _"I have a vague wellness concern → show me what's relevant, in a way I'd trust."_

### 2. Core loop

**Pick goal → see matched products → tap one → read science + reviews → save to wishlist → come back to learn more.**

- Repeat action: **browse + save**
- Not: log daily / scan barcode / chat with AI

### 3. Accessory features

- Product detail page (PDP) with ingredient deep-dive + linked cert PDFs
- "Our Science" educational content
- Doctor / customer trust band
- Cert-of-analysis PDFs viewable inline (we already have these in `ui-data/`)
- Wishlist / save-for-later

### 4. Surface area check

**6 screens total** for v1:

1. Splash + goal-picker (onboarding)
2. Home (hero + matched products + science teaser)
3. Catalog (browse all products)
4. PDP (the deep product page)
5. Science (educational long-form content)
6. Saved (wishlist)

**Explicitly cut from v1:**

- ~~Cart~~ — no checkout, so no cart
- ~~Account~~ — no real auth, so no profile
- ~~Quiz~~ — goal-picker IS the quiz, no separate flow
- ~~Push notifications~~ — Expo Push exists, but adds nothing to demo

### 5. Retention hook

**Weekly science drop.** Sunday push: _"This week from the Rootlabs lab: Why Ashwagandha at night, not morning."_

- Pre-written, 8 articles bundled in JSON
- Cycles weekly; once per Sunday a fresh card surfaces on Home
- For the demo: a "What's new this week?" card on Home that updates based on `Date.now()` against a hardcoded weekly schedule
- When company plugs in their CMS, the schedule becomes dynamic

**Alternatives considered:** streak counter (felt forced for a non-tracking app), quiz revisit (weak), purchase reminders (requires purchase data we don't have).

---

## The API swap-in points (the part the company will care about)

When Kartavya pitches this, this is what they'll show:

```
services/
├── auth/
│   ├── auth.interface.ts        ← The contract
│   ├── auth.mock.ts             ← Used now (returns fake user)
│   └── auth.shopify.ts          ← PLUG IN HERE — Shopify Customer Accounts API
│
├── products/
│   ├── products.interface.ts
│   ├── products.mock.ts         ← Used now (reads static JSON)
│   └── products.shopify.ts      ← PLUG IN HERE — Shopify Storefront API
│
├── ai-coach/
│   ├── ai-coach.interface.ts
│   ├── ai-coach.mock.ts         ← Used now (canned responses)
│   └── ai-coach.claude.ts       ← PLUG IN HERE — Anthropic Claude API
│
└── checkout/
    ├── checkout.interface.ts
    ├── checkout.mock.ts         ← Used now (fake order confirmation)
    └── checkout.shopify.ts      ← PLUG IN HERE — Shopify Checkout webview
```

**The pitch sentence:** _"Three files. Replace the imports of `.mock` with `.shopify` and `.claude`. App ships."_

That's the leverage move.

---

## Tonight's stop point

This file exists. Strategy is captured. Sleep.

**Tomorrow's first move:** Kartavya signs off on the 5-part framework above (or rewrites it), and we begin Phase 1 — read the screenshots in `ui-data/` and extract the Mosaic design system.

---

## Open questions for next session

1. **Sign-off on the 5-part framework** (above)
2. **Repo location** — `apps/rootlabs-learning/` inside this repo, or a separate repo (e.g. `~/projects/rootlabs-app/`)?
3. **iOS-first or Android-first?** Expo does both but the demo phone might be only one
4. **Brand naming in the app** — "Rootlabs" or "Root Labs" (the website uses both)?
5. **Pitch timing** — at what level of polish do you walk into the company? My suggestion: end of Phase 4 (Polish). Phase 5 (packaging) happens right before the pitch.
