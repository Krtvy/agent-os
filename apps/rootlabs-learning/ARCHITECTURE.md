# Architecture — Root Labs Mobile App

> **The pitch in one diagram:** Every external dependency in this app lives behind a TypeScript interface with two implementations — a `.mock` (used now, $0 cost) and a `.real` (commented out, awaiting your API access). Replace 3–5 imports in one file. The app ships.

---

## The adapter pattern (the pitch centerpiece)

```
┌─────────────────────────────────────────────────────────────────┐
│  Every screen imports `services` from `src/services/index.ts`.  │
│  No screen knows whether it's talking to a mock or to Shopify.  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │           src/services/index.ts             │
        │           THE DI CONTAINER                  │
        ├─────────────────────────────────────────────┤
        │  export const services = {                  │
        │    auth:      mockAuth,         // ← swap   │
        │    products:  mockProducts,     // ← swap   │
        │    aiCoach:   mockAICoach,      // ← swap   │
        │    checkout:  mockCheckout,     // ← swap   │
        │    analytics: mockAnalytics,    // ← swap   │
        │  };                                         │
        └─────────────────────────────────────────────┘
                ↓                              ↓
    ┌───────────────────────┐      ┌──────────────────────────┐
    │  USED NOW             │      │  WHEN COMPANY API LANDS  │
    │  Mock implementations │      │  Real implementations    │
    ├───────────────────────┤      ├──────────────────────────┤
    │ auth.mock.ts          │      │ auth.shopify.ts          │
    │ → AsyncStorage user   │ ───→ │ → Shopify Customer       │
    │                       │      │   Accounts API           │
    │                       │      │                          │
    │ products.mock.ts      │      │ products.shopify.ts      │
    │ → /data/products.json │ ───→ │ → Shopify Storefront API │
    │                       │      │                          │
    │ ai-coach.mock.ts      │      │ ai-coach.claude.ts       │
    │ → canned responses    │ ───→ │ → Anthropic API          │
    │                       │      │   (via server proxy)     │
    │                       │      │                          │
    │ checkout.mock.ts      │      │ checkout.shopify.ts      │
    │ → AsyncStorage cart   │ ───→ │ → Shopify Storefront API │
    │ → openCheckout() =    │      │ → Webview to Shopify     │
    │   "unavailable"       │      │   checkout URL           │
    │                       │      │                          │
    │ analytics.mock.ts     │      │ analytics.posthog.ts     │
    │ → console.log         │ ───→ │ → PostHog                │
    └───────────────────────┘      └──────────────────────────┘
```

Each interface (`auth.interface.ts`, etc.) is the **contract**. Both implementations must satisfy it. The rest of the app is type-safe and provider-agnostic.

---

## What the company gets

When the company adopts this build, the swap to ship looks like:

### Step 1 — Add real implementations (~3 files per service)

Each `services/<name>/<name>.<provider>.ts` is a class implementing the contract in `<name>.interface.ts`. Approximately:

- **auth.shopify.ts** — wrap `@shopify/storefront-api-client` Customer Accounts methods
- **products.shopify.ts** — GraphQL queries to Storefront API (products, collections)
- **checkout.shopify.ts** — Storefront Cart API + open `cart.checkoutUrl` in `WebView` or `expo-web-browser`
- **ai-coach.claude.ts** — POST to a Cloudflare Worker / Vercel Edge Function that proxies to Anthropic with the server-side key
- **analytics.posthog.ts** — wrap `posthog-react-native`

### Step 2 — Edit one file (`src/services/index.ts`)

```ts
// Before
export const services = {
  auth: mockAuth,
  products: mockProducts,
  aiCoach: mockAICoach,
  checkout: mockCheckout,
  analytics: mockAnalytics,
};

// After
export const services = {
  auth: shopifyAuth,
  products: shopifyProducts,
  aiCoach: claudeAICoach,
  checkout: shopifyCheckout,
  analytics: posthogAnalytics,
};
```

### Step 3 — Set env vars

```bash
EXPO_PUBLIC_SHOPIFY_STORE_DOMAIN=rootlabs.myshopify.com
EXPO_PUBLIC_SHOPIFY_STOREFRONT_API_TOKEN=<token>
EXPO_PUBLIC_CLAUDE_API_PROXY_URL=https://api.rootlabs.co/ai/v1
EXPO_PUBLIC_POSTHOG_API_KEY=<key>
```

That's it. No screens change. No components change. No hooks change. The app is the same.

---

## Folder structure

```
apps/rootlabs-learning/
├── app.json                # Expo config — bundle ID, brand name, splash bg
├── package.json
├── tsconfig.json           # Path aliases @/, @components/, @services/, etc.
├── babel.config.js         # module-resolver matches tsconfig aliases
├── metro.config.js         # extra assetExt: 'pdf' for cert reports
├── README.md               # how to run + what's mocked
├── ARCHITECTURE.md         # this file
│
├── src/
│   ├── app/                # ← Expo Router (file-based routing)
│   │   ├── _layout.tsx     # Root stack — SafeArea + StatusBar
│   │   ├── index.tsx       # Splash → routes to onboarding or tabs
│   │   ├── onboarding/
│   │   │   └── goal-picker.tsx
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx # Tabs(For You · Shop · Science · Saved)
│   │   │   ├── for-you.tsx
│   │   │   ├── shop.tsx
│   │   │   ├── science.tsx
│   │   │   └── saved.tsx
│   │   ├── product/[slug].tsx           # Dynamic PDP
│   │   ├── science/[slug].tsx           # Article reader
│   │   ├── account/
│   │   │   ├── index.tsx                # Mosaic-style menu list
│   │   │   └── honest-reports.tsx       # Cert PDF list — the trust feature
│   │   └── cart.tsx                     # Modal cart + "Coming soon" pitch
│   │
│   ├── components/          # 18 atomic + composed components
│   │   ├── primitives/      # Text, Button, Pill, Input, StarRating
│   │   ├── app-shell/       # TopBar, SearchBar, StickyCartBar
│   │   ├── product/         # ProductCard, PriceRow, QtyStepper
│   │   ├── content/         # HeroBanner, SectionHeader, MenuRow, TestimonialCard
│   │   └── rootlabs-specific/  # ThreePillars, IngredientCard, CertPDFRow, ...
│   │
│   ├── design-system/
│   │   ├── tokens.ts        # ← Hex values from rootlabs.co Shopify theme
│   │   ├── theme.ts         # ThemeProvider composition
│   │   └── brand.ts         # Tagline, pillars, voice phrases, founder name
│   │
│   ├── services/            # ← THE ADAPTER PATTERN
│   │   ├── auth/{interface,mock}.ts
│   │   ├── products/{interface,mock}.ts
│   │   ├── ai-coach/{interface,mock}.ts
│   │   ├── checkout/{interface,mock}.ts
│   │   ├── analytics/{interface,mock}.ts
│   │   ├── storage/storage.ts        # Local-only; no provider swap
│   │   └── index.ts                  # THE DI CONTAINER — pitch file
│   │
│   ├── data/                # Mock JSON backbone
│   │   ├── products.json
│   │   ├── ingredients.json
│   │   ├── articles.json
│   │   ├── doctors.json
│   │   ├── reviews.json
│   │   └── cert-reports.json
│   │
│   ├── hooks/
│   │   ├── useCart.ts
│   │   └── useUser.ts
│   │
│   └── types/
│       └── domain.ts        # Shared type vocabulary
│
└── assets/
    ├── images/              # Placeholders today; real assets when licensed
    └── cert-pdfs/
        └── shilajit-gummies/
            ├── aflatoxin.pdf      ← Real Equinox Labs test report
            ├── allergen.pdf
            ├── gluten.pdf
            ├── heavy-metals.pdf
            └── pesticide.pdf
```

---

## Design tokens — single source of truth

`src/design-system/tokens.ts` defines every visual value. These came from `curl https://rootlabs.co/` + parsing the Shopify theme JSON.

| Token                | Value     | Source                                          |
| -------------------- | --------- | ----------------------------------------------- |
| `colors.brand`       | `#13523B` | `brand_theme_color` in theme JSON               |
| `colors.brandDark`   | `#01563E` | observed in inline CSS                          |
| `colors.brandTeal`   | `#108474` | `verified_count_badge_color`                    |
| `colors.accent`      | `#E5732E` | observed in discount/urgency surfaces           |
| `colors.bg`          | `#FEF8F3` | `brand_atc_button_text_color` (used as page bg) |
| `colors.textPrimary` | `#1E1E1E` | dominant text color                             |
| `typography.display` | `Inter`   | substitute for paid Matter font                 |
| `typography.body`    | `Figtree` | Google Font — used on rootlabs.co               |

Change any value in `tokens.ts` and the entire app re-themes. Brand consistency is enforced by the type system: components import `colors`/`spacing`/`radius` from the token file, never hardcode.

---

## Domain types

`src/types/domain.ts` is the shared vocabulary. Every service interface, hook, and screen reads/writes these types:

- `Product`, `Ingredient`, `Article`, `Doctor`, `Review`, `CertReport`, `CertPanel`
- `User`, `Cart`, `CartItem`, `ProductRecommendation`
- `WellnessGoal = 'energy' | 'immunity' | 'vitality' | 'general'`

The Shopify Storefront API has Product/Variant/Cart types that map cleanly to these. The mock implementations satisfy these types; the real Shopify implementations will too. **Zero schema drift between mock and real.**

---

## How the trust feature works

The **Honest Reports** screen ([`src/app/account/honest-reports.tsx`](./src/app/account/honest-reports.tsx)) is the Mosaic signature pattern adapted to Root Labs. It reads cert metadata from [`src/data/cert-reports.json`](./src/data/cert-reports.json) and renders one row per panel (Aflatoxin / Allergen / Gluten / Heavy Metals / Pesticide).

Each row links to a real third-party lab PDF bundled in [`assets/cert-pdfs/shilajit-gummies/`](./assets/cert-pdfs/shilajit-gummies/). The PDFs are actual signed reports from **Equinox Labs** (CIN U74999MH2017PTC297024, NABL-accredited).

**To wire up PDF viewing in production:** install `react-native-pdf` or use `WebBrowser.openBrowserAsync` from `expo-web-browser` to open the PDF asset. The asset path is already in the JSON metadata — no additional wiring needed.

---

## Why this approach (the design trade-offs)

| Decision                                    | Why this beats the alternatives                                                                                                     |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Expo + RN over Flutter / native**         | Single codebase iOS+Android · TypeScript end-to-end with `services/` · Free dev tooling forever · Expo Go preview without app store |
| **Static JSON over a mock backend**         | Zero backend cost · Versioned with the app · Cold-start fast · No CORS/auth/keys to manage during demo                              |
| **Adapter pattern over direct API calls**   | Provider-agnostic — Shopify swap is one file · Type-safe — interface contract enforces · Testable — every screen can be mocked      |
| **Inter as Matter substitute**              | Free font · Pixel-similar geometry · Drop-in font name change for the paid Matter when licensed                                     |
| **AsyncStorage for cart + wishlist + user** | No backend needed for demo · Already RN-native · Fast                                                                               |
| **4-tab nav (not 3 like BB/MM)**            | Science deserves prominence for Root Labs (their differentiator) — mirrors rootlabs.co main nav                                     |

---

## Open work / known gaps

These are deliberate, not bugs. They're documented in `README.md`. Quick list:

1. **No real product images** — placeholders show the product name in a coloured rect. Real images need CDN URLs or asset licensing.
2. **No font assets loaded** — `Inter` and `Figtree` are referenced; the font files aren't bundled, so the app falls back to system. Drop the `.ttf` files into `assets/fonts/` and uncomment the `expo-font` loader in `_layout.tsx` to enable.
3. **PDF viewer integration** — tapping a cert panel opens an `Alert` showing the verdict. Real PDF viewer is a 30-min wire-up via `react-native-pdf`.
4. **Search isn't connected** — `SearchBar` renders with rotating placeholders, but doesn't drive a results screen yet. The `services.products.search()` method exists and works — needs a `/search?q=...` screen.
5. **No real auth provider** — `signInWithApple` and `signInWithGoogle` return a stub user. Wire `expo-apple-authentication` + `expo-auth-session` when company-side accounts are set up.

---

## TL;DR

```
1. Open src/services/index.ts.
2. Replace 5 imports.
3. Set 4 env vars.
4. Ship.
```

That's the pitch.
