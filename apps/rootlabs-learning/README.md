# Root Labs — Mobile App

> A production-architected, demo-grade mobile app for **Root Labs**. Runs end-to-end on free tools with zero API keys. Designed to swap in real Shopify + Claude integrations via a single file when company API access lands.

---

## What this is

An Expo + React Native + TypeScript build of a wellness e-commerce app for Root Labs (a Mosaic Wellness brand). The app demonstrates the full discovery → product detail → save → checkout flow, the Mosaic mobile design pattern (matched to the rootlabs.co brand identity), and a production-grade service-adapter architecture.

**Status:** demo build. Runs on a real phone via Expo Go. No real money flows. No real auth. No external APIs.

## Run it

```bash
# First time only
cd apps/rootlabs-learning
npm install                # (already done — node_modules in place)

# Start the dev server
npx expo start

# Press 'i' for iOS simulator, 'a' for Android emulator,
# or scan the QR code with Expo Go on your phone.
```

If you hit a `Metro` or `babel` cache issue:

```bash
npx expo start -c   # clears cache
```

## What works in the demo

| Feature                                                                                                                             | Status                                              |
| ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Splash + goal-picker onboarding (4 wellness goals)                                                                                  | ✅                                                  |
| Bottom-tab navigation (For You · Shop · Science · Saved)                                                                            | ✅                                                  |
| For-You home with hero, featured products, 3 pillars, doctor endorsements, weekly science drop, customer testimonials, founder card | ✅                                                  |
| Shop with filter pills (All · Energy · Immunity · Vitality · General) + 2-column product grid                                       | ✅                                                  |
| Product Detail Page (PDP) with gallery placeholder, claims, ingredients deep-dive, cert summary, reviews, save-to-wishlist          | ✅                                                  |
| Science library with 8 articles + full article reader                                                                               | ✅                                                  |
| Saved (wishlist) — persists via AsyncStorage                                                                                        | ✅                                                  |
| Account screen (Mosaic-style menu list)                                                                                             | ✅                                                  |
| **Honest Reports** — 5 real third-party lab reports (Equinox Labs PDFs bundled in `assets/cert-pdfs/`)                              | ✅ inline preview · PDF viewer is `// PLUG IN HERE` |
| Cart with delivery band, qty stepper, totals, sticky CTA                                                                            | ✅                                                  |
| **"Coming soon" checkout pitch** — taps the CTA, shows the swap-in message to the company                                           | ✅ (the pitch moment)                               |

## What's deliberately mocked (and how to un-mock)

This is the **adapter pattern** centerpiece. Every external dependency lives behind a TypeScript interface with two implementations: a `.mock` (used now) and a stub for the real provider (commented out, to be implemented when API access lands).

Open [`src/services/index.ts`](./src/services/index.ts) — that's the single file the company changes to ship to production:

```ts
export const services = {
  auth: mockAuth, // → shopifyAuth      when Shopify Customer Accounts API lands
  products: mockProducts, // → shopifyProducts  when Shopify Storefront API lands
  aiCoach: mockAICoach, // → claudeAICoach    when Anthropic API key lands
  checkout: mockCheckout, // → shopifyCheckout  when Shopify Storefront API lands
  analytics: mockAnalytics, // → posthogAnalytics when PostHog key lands
};
```

**The pitch sentence:** _"Three to five files. Replace `.mock` imports with the production counterparts. App ships."_

## What's missing (intentional demo gaps)

| What                                    | Why                                                        | When unlocked                                                                                          |
| --------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Real product images                     | Demo uses placeholder cards                                | When the company shares CDN URLs or rights to use rootlabs.co images                                   |
| Real auth (Apple/Google/Shopify)        | Demo mocks user in AsyncStorage                            | When company creates Shopify Customer Accounts                                                         |
| Real Claude AI features                 | Demo uses canned responses per goal                        | When Anthropic API key + server proxy is provisioned                                                   |
| Real checkout                           | Demo cart works but `openCheckout()` returns "unavailable" | When Shopify Storefront API token is provisioned                                                       |
| Push notifications                      | Architecture supports `expo-notifications`                 | When notification strategy is approved                                                                 |
| Sentry / PostHog                        | Stubs in `services/analytics/`                             | When company decides on observability tooling                                                          |
| Real fonts (Matter, IBM Plex Sans)      | Demo falls back to system fonts for now                    | When font licenses are purchased (Matter is paid; Inter is the free substitute already pre-configured) |
| Actual image assets in `assets/images/` | Placeholders render product names instead                  | When asset licensing is confirmed                                                                      |

## Architecture quick-look

```
src/
├── app/                    ← Expo Router screens (file-based routing)
├── components/             ← 18 atomic + composed components
│   ├── primitives/         ← Text, Button, Pill, Input, StarRating
│   ├── app-shell/          ← TopBar, SearchBar, StickyCartBar
│   ├── product/            ← ProductCard, PriceRow, QtyStepper
│   ├── content/            ← HeroBanner, SectionHeader, MenuRow, TestimonialCard
│   └── rootlabs-specific/  ← ThreePillars, IngredientCard, CertPDFRow, FounderCard, DoctorEndorsementCard
├── design-system/          ← tokens.ts (exact hex from rootlabs.co), theme.ts, brand.ts
├── services/               ← THE ADAPTER PATTERN — 5 interfaces, 5 mocks, 1 DI container
│   ├── auth/
│   ├── products/
│   ├── ai-coach/
│   ├── checkout/
│   ├── analytics/
│   └── index.ts           ← THE PITCH FILE — single import-swap to go live
├── data/                   ← Mock JSON: products, ingredients, articles, doctors, reviews, certs
├── hooks/                  ← useCart, useUser
└── types/domain.ts         ← Shared type vocabulary
```

For the full pitch and adapter-swap diagram, see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## How the brand identity was extracted

Every hex value, font family, and brand phrase in this app came from the live Root Labs production site:

```bash
curl https://rootlabs.co/ | grep '_color":"#'   # exact theme JSON
```

The full extraction is documented in [`../../_audit/2026-05-14_rootlabs-design-extraction.md`](../../_audit/2026-05-14_rootlabs-design-extraction.md). The Mosaic mobile design pattern came from 27 iPhone screenshots of Be Bodywise + Man Matters apps, documented in [`../../_audit/2026-05-14_mosaic-design-system-extraction.md`](../../_audit/2026-05-14_mosaic-design-system-extraction.md).

This means **the colours, fonts, voice, and pillars in this app match the live brand exactly** — they aren't designer-guessed approximations.

## License & ownership

This is a learning / portfolio build by Kartavya during an internship at Mosaic Wellness. Not a Root Labs / Mosaic Wellness owned property. Hand-off to the company is the explicit goal.
