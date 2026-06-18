# Rootlabs Mobile App — Phase 1 → Phase 2 Blueprint

**Date:** 2026-05-14 (05:30 IST)
**Status:** Phase 1 complete. Phase 2 architecture defined. Ready to scaffold on Kartavya's sign-off.
**Inputs consumed:**

- `_audit/2026-05-14_rootlabs-design-extraction.md` (Rootlabs.co web tokens via curl)
- `_audit/2026-05-14_mosaic-design-system-extraction.md` (BB + MM screenshot extraction)
- 3 cert PDFs (Equinox Labs reports — Aflatoxin, Heavy Metals, Pesticide)
- `_audit/2026-05-14_rootlabs-app-strategy-lock.md` (project mission, constraints)

---

## Part A — Unified design system (Rootlabs mobile)

### A.1 Design tokens (the single source of truth)

```ts
// tokens.ts — these are the values every component reads from
export const colors = {
  // Brand (Rootlabs-specific — from Shopify theme JSON)
  brand: "#13523B", // primary forest green
  brandDark: "#01563E", // hover/pressed
  brandTeal: "#108474", // verified badges, social proof
  accent: "#E5732E", // warm orange — discount/urgency
  ratingStar: "#fbcd0a", // yellow stars

  // Surfaces (Rootlabs uses warm cream, NOT pure white — important differentiator)
  bg: "#FEF8F3", // primary background
  bgAlt: "#F2F0E8", // alternating section bg
  bgClinical: "#f9fafb", // for science/clinical sections
  surfaceWarm: "#E8DDD3", // peach accent

  // Text
  textPrimary: "#1e1e1e", // near-black, gentler than pure black
  textSecondary: "#343434", // dividers / secondary
  textTertiary: "#808191", // strike-through MRP / micro-copy
  white: "#FFFFFF",

  // System (inherited from Mosaic — no need to re-invent)
  success: "#22A06B", // toast / "Doctor will call" band
  successBg: "#E7F4EC",
  warning: "#FEF3C7", // savings band bg
  error: "#EF4444", // red badge
  errorBg: "#FEE2E2", // logout button bg
  border: "#E5E7EB", // card borders / dividers
};

export const typography = {
  // Rootlabs uses 3 fonts on web; mobile we use 2 (Matter requires paid license,
  // Inter is the free substitute that pairs cleanly with Figtree)
  display: "Inter", // headlines, hero text — display weight
  body: "Figtree", // body, UI, labels
  // (italic-script accent for "*women*"/"*roots*" emphasis handled via fontStyle, not separate face)
  sizes: {
    display1: 32,
    display2: 24,
    display3: 20,
    body: 16,
    bodySmall: 14,
    micro: 12,
  },
  weights: {
    regular: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
};

export const spacing = {
  // 4-point grid (industry standard, matches Mosaic spacing)
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const radius = {
  // From Mosaic observation: cards ≈ 12, buttons ≈ pill (height/2), chips ≈ 16
  sm: 8,
  md: 12,
  lg: 16,
  pill: 9999,
};

export const elevation = {
  card: { offsetY: 2, blur: 8, opacity: 0.06 },
  sticky: { offsetY: -2, blur: 12, opacity: 0.1 },
  modal: { offsetY: 8, blur: 24, opacity: 0.2 },
};
```

### A.2 Component inventory (18 atoms — locked from Mosaic extraction)

```
components/
├── primitives/
│   ├── Text.tsx              # typed: display1 | display2 | body | bodySmall | micro
│   ├── Button.tsx            # variants: filled | outlined | link | destructive
│   ├── Pill.tsx              # discount, "#1 seller", "Top Rated", "get it today"
│   ├── Input.tsx             # rounded rect, label above, helper below
│   ├── Toast.tsx             # green pill with ✓
│   ├── StarRating.tsx        # 5 stars + numeric
│   └── Chip.tsx              # filter pills (horizontal scroll)
│
├── app-shell/
│   ├── TopBar.tsx            # wordmark + search/profile/cart/wallet icons
│   ├── BottomTabNav.tsx      # 3-tab: For You · Shop · Saved (Rootlabs swap: no Doctors)
│   ├── StickyCartBar.tsx     # "You have items in cart" floating above tab nav
│   └── SearchBar.tsx         # rotating placeholder, magnifying glass
│
├── product/
│   ├── ProductCard.tsx       # 2-col grid card: image, name, For:, price, ADD
│   ├── DiscountPill.tsx      # green % off
│   ├── PriceRow.tsx          # current bold + struck-through MRP grey
│   └── QtyStepper.tsx        # [- 1 +] in cart
│
├── content/
│   ├── HeroBanner.tsx        # top-of-Home pastel hero card
│   ├── CarouselDots.tsx      # pagination indicator
│   ├── TestimonialCard.tsx   # photo + name+city + stars + quote
│   ├── VideoReviewCard.tsx   # video thumbnail + play button + quote framing
│   ├── SectionHeader.tsx     # "Trending Categories" bold-left + optional "View All" right
│   └── MenuRow.tsx           # account/list items: icon + title + subtitle + chevron
│
├── rootlabs-specific/
│   ├── IngredientCard.tsx    # deep-dive on PDP (Shilajit / Ashwagandha / Sea Moss etc.)
│   ├── FounderCard.tsx       # "Influencing Our Voice — Mayank Kumar"
│   ├── CertPDFRow.tsx        # links to Equinox lab reports
│   ├── ThreePillars.tsx      # Carefully crafted · Maximum absorption · Science-backed
│   └── DoctorEndorsementCard.tsx # Dr. Christianson + Dr. Appelhans
```

### A.3 Screen list (locked from strategy + framework)

```
screens/
├── splash/SplashScreen.tsx              # logo + 0.8s delay → onboarding or home
├── onboarding/GoalPicker.tsx            # 4 wellness goals: Energy / Immunity / Vitality / General
├── tabs/
│   ├── ForYouScreen.tsx                 # home: hero + matched products + science teaser + 3 pillars + doctors + testimonials
│   ├── ShopScreen.tsx                   # catalog: left rail categories + product grid
│   └── SavedScreen.tsx                  # wishlist (AsyncStorage)
├── product/PDPScreen.tsx                # gallery + claims + ingredients + cert links + reviews + Add to Saved
├── science/
│   ├── ScienceHomeScreen.tsx            # list of long-form articles
│   └── ArticleScreen.tsx                # single article reader
├── account/
│   ├── AccountScreen.tsx                # menu list (login optional, mostly placeholder)
│   ├── HonestReportsScreen.tsx          # list of cert PDFs grouped by product
│   └── CertViewerScreen.tsx             # inline PDF viewer
└── shared/
    └── CartPreviewScreen.tsx            # non-functional cart — explicit "Coming soon: company API integration" — the pitch moment
```

---

## Part B — The "Honest Reports" feature (informed by the 3 PDFs)

### B.1 What the cert PDFs actually are

All 3 read are from **Equinox Labs Private Limited** (CIN: U74999MH2017PTC297024, Navi Mumbai) — a real third-party testing lab with offices in Mumbai, Bangalore, Hyderabad, Noida, Kolkata, Chennai.

**Sample tested:** "Be Bodywise Shilajit Gummies, Batch No. SSHG24001, Mfg. Date: 07/2024" — so the cert PDFs in `ui-data/` are BB-branded but represent the Mosaic group's standard testing infrastructure. Rootlabs (also Mosaic) uses the same lab.

**Standard report panels:**
| Panel | Parameters tested | Verdict pattern |
|---|---|---|
| **Aflatoxin** | 4 (B1, B2, G1, G2) | All BLQ — "Below Limit of Quantification" |
| **Heavy Metals** | 3 (Barium, Copper, Selenium) | Conforms to FSSAI limits; Copper 0.57 mg/kg (NMT 30.0) |
| **Pesticide** | 211 chemicals tested | Nearly all BLQ |
| **Allergen** | (similar template, unread) | Standard panel |
| **Gluten** | (similar template, unread) | Standard panel |

**Report structure (every PDF):**

- Header: Equinox Test Report + Issue date
- Customer info: Client (Mosaic Wellness Private Limited), Address, Contact, Sample Description
- Sample particulars: Sampling Protocol, Sampling/Receipt/Analysis dates, Sample Quantity & Condition
- Results table: Sr. No. | Parameter | Units | Method | Result | (Limits)
- Signed by Mr. Sachin Tambe, Technical Manager - Instrumentation
- 6 notes (validity, reproduction, advertising-prohibition disclaimers)
- "Your Testing and Auditing Partner" tagline

### B.2 "Honest Reports" screen design (Rootlabs mobile)

```
[← Back]  Honest Reports

We test every batch. Every result is public.

──────────────────────────────────────────────
Shilajit Gummies
Batch SSHG24001 · Mfg. Jul 2024 · Tested Jul 2024
──────────────────────────────────────────────
🛡 Aflatoxin       All 4 toxins: BLQ          [PDF ›]
🛡 Heavy Metals    Conforms to FSSAI limits   [PDF ›]
🛡 Pesticide       211 chemicals tested · all BLQ [PDF ›]
🛡 Allergen        No allergens detected      [PDF ›]
🛡 Gluten          Below detection            [PDF ›]
──────────────────────────────────────────────
Tested by Equinox Labs · CIN U74999MH2017PTC297024
Independent third-party · NABL accredited
──────────────────────────────────────────────

[ tap any PDF → opens CertViewerScreen with inline PDF render via react-native-pdf ]
```

**Why this is a strong pitch moment:**
The "Honest Report" link in the Rootlabs.co nav 404'd when I tried to fetch it via curl. The website has the marketing claim ("7 cert badges") but no actual report page. **The mobile app being the first surface where customers can actually tap and read the lab report is a real product win, not just a demo.** Walk into the company with this exact screen and the pitch writes itself.

### B.3 What goes in `assets/cert-pdfs/`

```
assets/cert-pdfs/
├── shilajit-gummies/
│   ├── aflatoxin.pdf       # = BB-Shilajit-Gummies-AFLATOXIN-test-report.pdf
│   ├── allergen.pdf
│   ├── gluten.pdf
│   ├── heavy-metals.pdf
│   └── pesticide.pdf
└── README.md               # "Replace these with Rootlabs-branded reports when company provides"
```

The PDFs ship inside the app bundle for the demo. When the company adopts, they swap to Rootlabs-branded versions tested for their products. Path stays the same — zero code change.

---

## Part C — Architecture skeleton (the production-grade adapter pattern)

### C.1 Folder structure (the visible architecture)

```
apps/rootlabs-learning/
├── README.md                              # 1-page: how to run + "what the company plugs in"
├── ARCHITECTURE.md                        # The pitch — adapter swap-in diagram
├── package.json
├── app.json                               # Expo config
├── tsconfig.json
├── .env.example
├── .gitignore
│
├── src/
│   ├── app/                               # Expo Router (file-based routing)
│   │   ├── _layout.tsx                    # Root layout: providers + theme
│   │   ├── index.tsx                      # Splash → routes to onboarding or tabs
│   │   ├── onboarding/
│   │   │   └── goal-picker.tsx
│   │   ├── (tabs)/                        # Bottom-tab nav layout
│   │   │   ├── _layout.tsx                # BottomTabNav rendered here
│   │   │   ├── for-you.tsx
│   │   │   ├── shop.tsx
│   │   │   └── saved.tsx
│   │   ├── product/[slug].tsx             # Dynamic PDP route
│   │   ├── science/
│   │   │   ├── index.tsx
│   │   │   └── [slug].tsx                 # Article reader
│   │   └── account/
│   │       ├── index.tsx
│   │       ├── honest-reports.tsx
│   │       └── cert/[productSlug]/[panel].tsx  # PDF viewer
│   │
│   ├── components/                        # The 18-component inventory above
│   │   ├── primitives/
│   │   ├── app-shell/
│   │   ├── product/
│   │   ├── content/
│   │   └── rootlabs-specific/
│   │
│   ├── design-system/
│   │   ├── tokens.ts                      # colors, typography, spacing, radius
│   │   ├── theme.ts                       # ThemeProvider + useTheme()
│   │   └── icons.ts                       # Re-export Lucide icons used
│   │
│   ├── services/                          # ⚡ THE ADAPTER PATTERN — pitch centerpiece
│   │   ├── auth/
│   │   │   ├── auth.interface.ts          # Contract: { signIn, signOut, getUser }
│   │   │   ├── auth.mock.ts               # ← USED NOW (fake user object)
│   │   │   └── auth.shopify.ts            # ⚠ PLUG IN HERE — Shopify Customer Accounts
│   │   ├── products/
│   │   │   ├── products.interface.ts      # Contract: { list, getBySlug, search }
│   │   │   ├── products.mock.ts           # ← USED NOW (reads /data/products.json)
│   │   │   └── products.shopify.ts        # ⚠ PLUG IN HERE — Shopify Storefront API
│   │   ├── ai-coach/
│   │   │   ├── ai-coach.interface.ts      # Contract: { recommend, explain }
│   │   │   ├── ai-coach.mock.ts           # ← USED NOW (canned responses per goal)
│   │   │   └── ai-coach.claude.ts         # ⚠ PLUG IN HERE — Anthropic Claude API
│   │   ├── checkout/
│   │   │   ├── checkout.interface.ts      # Contract: { initCart, addItem, openCheckout }
│   │   │   ├── checkout.mock.ts           # ← USED NOW (fake order confirmation)
│   │   │   └── checkout.shopify.ts        # ⚠ PLUG IN HERE — Shopify webview
│   │   ├── analytics/
│   │   │   ├── analytics.interface.ts     # Contract: { track, identify, screen }
│   │   │   ├── analytics.mock.ts          # ← USED NOW (console.log)
│   │   │   └── analytics.posthog.ts       # ⚠ PLUG IN HERE — PostHog (free tier)
│   │   ├── storage/                       # Local-only — no adapter needed
│   │   │   └── storage.ts                 # AsyncStorage wrapper for wishlist, prefs
│   │   └── index.ts                       # The DI container — single file the company changes
│   │
│   ├── data/                              # Static JSON — mock backend
│   │   ├── products.json                  # 10 Rootlabs SKUs from rootlabs.co
│   │   ├── articles.json                  # ~8 science articles
│   │   ├── reviews.json                   # Sample reviews per product
│   │   ├── doctors.json                   # Dr. Christianson + Dr. Appelhans
│   │   ├── ingredients.json               # Shilajit, Ashwagandha, Sea Moss, etc.
│   │   └── cert-reports.json              # Metadata for PDFs in assets/cert-pdfs/
│   │
│   ├── hooks/                             # Custom React hooks
│   │   ├── useProducts.ts
│   │   ├── useSaved.ts                    # wishlist
│   │   └── useTheme.ts
│   │
│   ├── utils/
│   │   ├── format.ts                      # price, date formatting
│   │   └── validation.ts
│   │
│   └── types/
│       └── domain.ts                      # Product, Review, Article, Cert, User types
│
├── assets/
│   ├── images/
│   │   ├── products/                      # Pulled from rootlabs.co CDN
│   │   ├── doctors/
│   │   └── ingredients/
│   ├── cert-pdfs/                         # The 5 Equinox PDFs we have
│   │   └── shilajit-gummies/
│   ├── fonts/
│   │   ├── Figtree-Regular.ttf
│   │   ├── Figtree-Medium.ttf
│   │   ├── Figtree-Bold.ttf
│   │   └── Inter-*.ttf
│   └── splash.png
│
└── .github/
    └── workflows/
        └── eas-build.yml                  # CI build with EAS (free tier)
```

### C.2 The single file the company changes

```ts
// src/services/index.ts — the dependency-injection container

// Mock implementations (used now)
import { mockAuth } from "./auth/auth.mock";
import { mockProducts } from "./products/products.mock";
import { mockAICoach } from "./ai-coach/ai-coach.mock";
import { mockCheckout } from "./checkout/checkout.mock";
import { mockAnalytics } from "./analytics/analytics.mock";

// Production implementations (commented — uncomment when company API access lands)
// import { shopifyAuth } from './auth/auth.shopify';
// import { shopifyProducts } from './products/products.shopify';
// import { claudeAICoach } from './ai-coach/ai-coach.claude';
// import { shopifyCheckout } from './checkout/checkout.shopify';
// import { posthogAnalytics } from './analytics/analytics.posthog';

export const services = {
  auth: mockAuth, // → shopifyAuth      when company provides Customer Accounts API
  products: mockProducts, // → shopifyProducts  when company provides Storefront API
  aiCoach: mockAICoach, // → claudeAICoach    when company provides Claude API key
  checkout: mockCheckout, // → shopifyCheckout  when company provides Storefront API
  analytics: mockAnalytics, // → posthogAnalytics when ready
};
```

**The pitch sentence:** _"Open `src/services/index.ts`. Five imports. Replace `.mock` with the real implementations. App ships."_

### C.3 Interface contracts (the API the company sees)

```ts
// products.interface.ts
export interface ProductsService {
  list(filter?: { goal?: WellnessGoal; category?: string }): Promise<Product[]>;
  getBySlug(slug: string): Promise<Product | null>;
  search(query: string): Promise<Product[]>;
}

// auth.interface.ts
export interface AuthService {
  getCurrentUser(): User | null;
  signInWithApple(): Promise<User>;
  signInWithGoogle(): Promise<User>;
  signOut(): Promise<void>;
}

// checkout.interface.ts
export interface CheckoutService {
  initCart(items: CartItem[]): Promise<Cart>;
  addItem(productSlug: string, qty: number): Promise<Cart>;
  removeItem(productSlug: string): Promise<Cart>;
  openCheckout(cartId: string): Promise<{ status: "completed" | "cancelled" }>;
}

// ai-coach.interface.ts
export interface AICoachService {
  recommendProducts(
    goal: WellnessGoal,
    context?: string,
  ): Promise<ProductRecommendation[]>;
  explainIngredient(ingredient: string): Promise<string>;
}
```

When the company plugs in real services, they implement these interfaces. **The rest of the app code never changes** — because every screen imports from `services` not from `services/*/mock`.

---

## Part D — Mock data schemas (what the demo runs on)

### D.1 products.json (extracted from rootlabs.co)

```json
[
  {
    "slug": "alpha-gummies-60s",
    "name": "Alpha Gummies",
    "pack": "60 gummies",
    "subtitle": "High-potency daily essentials",
    "price": 32.00,
    "mrp": 39.99,
    "currency": "USD",
    "image": "products/alpha-gummies-60s.jpg",
    "gallery": [
      "products/alpha-gummies-60s-1.jpg",
      "products/alpha-gummies-60s-2.jpg"
    ],
    "claims": ["High Potency", "No Sugar Added", "Clean & Vegan", "One-Month Supply"],
    "ingredients": ["shilajit", "ashwagandha", "sea-moss"],
    "goals": ["energy", "vitality", "general"],
    "description": "Carefully crafted...",
    "subscription": { "available": true, "interval": "monthly", "discountPct": 15 },
    "certs": ["aflatoxin", "allergen", "gluten", "heavy-metals", "pesticide"],
    "rating": 4.7,
    "reviewCount": 142
  },
  {
    "slug": "alpha-gummies-120s",
    "name": "Alpha Gummies",
    "pack": "120 gummies",
    "price": 56.99,
    ...
  }
]
```

### D.2 ingredients.json (key for PDP deep-dive)

```json
[
  {
    "slug": "shilajit",
    "name": "Shilajit",
    "tagline": "The Himalayan resin",
    "origin": "Himalayan altitudes 16,000–18,000 ft",
    "benefits": ["energy", "absorption", "trace minerals"],
    "scientificName": "Mumijo",
    "bioavailability": "Enhanced via ShilAbsorb™ proprietary process",
    "shortDescription": "Carefully sourced from Himalayan altitudes...",
    "longDescription": "...",
    "icon": "ingredients/shilajit.png"
  },
  {
    "slug": "ashwagandha",
    "name": "Ashwagandha",
    "tagline": "Adaptogen for modern stress",
    "scientificName": "Withania somnifera",
    "form": "KSM-66 (full-spectrum root extract)",
    ...
  }
]
```

### D.3 articles.json (8 weekly science drops)

```json
[
  {
    "slug": "ashwagandha-night-or-morning",
    "title": "Why Ashwagandha at night, not morning",
    "category": "Adaptogens",
    "readTimeMin": 4,
    "publishedWeek": 1,
    "heroImage": "articles/ashwagandha-night.jpg",
    "summary": "Cortisol curves, KSM-66 dosing, and the case for evening protocols.",
    "body": "...",
    "linkedProducts": ["alpha-gummies-60s"]
  },
  ...
]
```

### D.4 doctors.json

```json
[
  {
    "slug": "douglas-christianson",
    "name": "Dr. Douglas Christianson",
    "credentials": "Naturopathic Doctor",
    "school": "Bastyr University",
    "photo": "doctors/christianson.jpg",
    "endorsementQuote": "...",
    "verified": true
  },
  {
    "slug": "kristy-appelhans",
    "name": "Dr. Kristy Appelhans",
    "credentials": "NMD",
    "specialty": "Pharmacovigilance",
    "yearsOfPractice": 17,
    "photo": "doctors/appelhans.jpg",
    "endorsementQuote": "..."
  }
]
```

### D.5 cert-reports.json

```json
[
  {
    "productSlug": "shilajit-gummies",
    "batchNumber": "SSHG24001",
    "manufactureDate": "2024-07",
    "testedBy": "Equinox Labs Private Limited",
    "testedByCIN": "U74999MH2017PTC297024",
    "panels": [
      {
        "name": "Aflatoxin",
        "parameters": 4,
        "verdict": "All toxins below detection",
        "summary": "BLQ on B1, B2, G1, G2",
        "pdfPath": "cert-pdfs/shilajit-gummies/aflatoxin.pdf"
      },
      {
        "name": "Heavy Metals",
        "parameters": 3,
        "verdict": "Conforms to FSSAI limits",
        "summary": "Barium BLQ · Copper 0.57 mg/kg (limit 30) · Selenium BLQ",
        "pdfPath": "cert-pdfs/shilajit-gummies/heavy-metals.pdf"
      },
      {
        "name": "Pesticide",
        "parameters": 211,
        "verdict": "All chemicals below detection",
        "summary": "211 pesticides screened · all BLQ",
        "pdfPath": "cert-pdfs/shilajit-gummies/pesticide.pdf"
      },
      {
        "name": "Allergen",
        "parameters": 1,
        "verdict": "No allergens detected",
        "pdfPath": "cert-pdfs/shilajit-gummies/allergen.pdf"
      },
      {
        "name": "Gluten",
        "parameters": 1,
        "verdict": "Below detection",
        "pdfPath": "cert-pdfs/shilajit-gummies/gluten.pdf"
      }
    ]
  }
]
```

---

## Part E — The 6 screens (ASCII wireframes)

### E.1 Splash + Goal Picker

```
┌──────────────────────────────┐
│                              │
│                              │
│        [Rootlabs logo]       │
│                              │
│      Handpicked in nature.   │
│      Perfected in science.   │
│                              │
│                              │
│  What brings you here today? │
│                              │
│  ┌──────────────┐ ┌─────────┐│
│  │  ⚡ Energy   │ │ 🛡 Immun.││
│  └──────────────┘ └─────────┘│
│  ┌──────────────┐ ┌─────────┐│
│  │  🌱 Vitality │ │ ✨ Gen.  ││
│  └──────────────┘ └─────────┘│
│                              │
│   [   Continue (skip) →  ]   │
└──────────────────────────────┘
```

### E.2 For You (home)

```
┌──────────────────────────────┐
│ Root Labs   🔍 👤 🛒(2)      │
├──────────────────────────────┤
│ 🔍 Search "Shilajit Gummies" │
├──────────────────────────────┤
│ ╔══════════════════════════╗ │
│ ║  Handpicked in *nature*. ║ │
│ ║  Perfected in science.   ║ │  ← Hero (cream BG)
│ ║  [Shop now ›]            ║ │
│ ╚══════════════════════════╝ │
│                              │
│ For your goal: Energy        │
│ ┌─────────┐ ┌─────────┐      │
│ │ image   │ │ image   │      │
│ │ Alpha60 │ │ Alpha120│      │
│ │ $32 $40 │ │ $57 $65 │      │
│ │ [ADD]   │ │ [ADD]   │      │
│ └─────────┘ └─────────┘      │
│                              │
│ ─── 3 pillars ───            │
│  🌿 Carefully crafted        │
│  🧬 Maximum absorption       │
│  📚 Science-backed           │
│                              │
│ From experts we trust        │
│ [Dr. C avatar][Dr. A avatar] │
│                              │
│ This week from the lab       │
│ ┌──────────────────────────┐ │
│ │ Why Ashwagandha at night,│ │  ← Weekly science drop
│ │ not morning. 4 min read →│ │     (retention hook)
│ └──────────────────────────┘ │
│                              │
│ Loved by 142+ customers      │
│ [testimonial carousel...]    │
│                              │
├──────────────────────────────┤
│ 🏠 For You · 🛍 Shop · 💾 Sav │  ← Bottom tab nav
└──────────────────────────────┘
```

### E.3 Shop

```
┌──────────────────────────────┐
│ Shop                  🔍 🛒  │
├─────┬────────────────────────┤
│ [im]│ ┌──────────────────────┐│
│ All │ │ Hero banner            ││
│     │ │ "Shilajit Gummies"     ││
│ [im]│ │ [Shop ›]               ││
│ Energy│└──────────────────────┘│
│     │                          │
│ [im]│ ┌─────────┐ ┌─────────┐  │
│ Immun│ │ Alpha60 │ │ Alpha120│ │
│     │ │ $32     │ │ $57     │ │
│ [im]│ │ ★4.7    │ │ ★4.8    │ │
│ Vital│ │ [ADD]   │ │ [ADD]   │ │
│     │ └─────────┘ └─────────┘  │
│ [im]│ ┌─────────┐ ┌─────────┐  │
│ Gen │ │ Turmeric│ │ Sea Moss│  │
│     │ │ ...     │ │ ...     │  │
│     │ └─────────┘ └─────────┘  │
├─────┴──────────────────────────┤
│ 🏠 · 🛍 Shop · 💾 Saved        │
└────────────────────────────────┘
```

### E.4 PDP

```
┌──────────────────────────────┐
│ ← Back                  🛒(2)│
├──────────────────────────────┤
│ [horizontal gallery 1/9]     │
│      ← image →               │
│ ● ● ● ○ ○ ○ ○ ○ ○            │
├──────────────────────────────┤
│ Alpha Gummies (60s)          │
│ ★★★★★ 4.7  (142 reviews)     │
│ $32.00  $40.00  -20%         │
│                              │
│ ✓ High Potency               │
│ ✓ No Sugar Added             │
│ ✓ Clean & Vegan              │
│ ✓ One-Month Supply           │
│                              │
│ ─── Ingredients ───          │
│ ┌──────────────────────────┐ │
│ │ 🌿 Shilajit              │ │
│ │ Himalayan resin · 16k ft │ │
│ │ Read more ›              │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ 🌱 Ashwagandha (KSM-66) │ │
│ │ Adaptogen · Read more ›  │ │
│ └──────────────────────────┘ │
│                              │
│ ─── Tested for ───           │
│ 🛡 Aflatoxin · BLQ           │
│ 🛡 Heavy Metals · Within FDA │
│ 🛡 Pesticide · 211 tested    │
│ 🛡 Allergen · None           │
│ 🛡 Gluten · None             │
│  [ View all reports ›]       │
│                              │
│ ─── Reviews ───              │
│ ★ 4.7 · Ishita, age 31       │
│ "Energy boost is real..."    │
│                              │
├──────────────────────────────┤
│ [  Save to Wishlist ❤  ]     │  ← Primary CTA (NOT "buy" in v1)
│ Subscribe & save 15% [info]  │
└──────────────────────────────┘
```

### E.5 Saved (wishlist)

```
┌──────────────────────────────┐
│ Saved                        │
├──────────────────────────────┤
│ 2 products in your list      │
│                              │
│ ┌──────────────────────────┐ │
│ │ [im] Alpha Gummies 60s   │ │
│ │      $32  ★ 4.7  [×]     │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ [im] Turmeric Gummies    │ │
│ │      $28  ★ 4.5  [×]     │ │
│ └──────────────────────────┘ │
│                              │
│ ─── You might also like ───  │
│ ┌─────────┐ ┌─────────┐      │
│ │ Sea Moss│ │ Maca    │      │
│ └─────────┘ └─────────┘      │
│                              │
│ ⚠ Checkout: coming when      │
│   company API integration    │
│   lands. (See README §3)     │
├──────────────────────────────┤
│ 🏠 · 🛍 · 💾 Saved           │
└──────────────────────────────┘
```

### E.6 Honest Reports → Cert Viewer

```
┌──────────────────────────────┐
│ ← Honest Reports             │
├──────────────────────────────┤
│ We test every batch.         │
│ Every result is public.      │
│                              │
│ ─── Shilajit Gummies ───     │
│ Batch SSHG24001 · Jul 2024   │
│                              │
│ 🛡 Aflatoxin              ›  │
│ 4 toxins · All BLQ           │
│ ──────────────               │
│ 🛡 Heavy Metals           ›  │
│ Conforms to FSSAI limits     │
│ ──────────────               │
│ 🛡 Pesticide              ›  │
│ 211 chemicals · all BLQ      │
│ ──────────────               │
│ 🛡 Allergen               ›  │
│ No allergens detected        │
│ ──────────────               │
│ 🛡 Gluten                 ›  │
│ Below detection              │
│                              │
│ Tested by Equinox Labs       │
│ Independent · NABL accredited│
└──────────────────────────────┘
```

---

## Part F — What's pending Kartavya sign-off (Phase 0 still open)

1. **5-part framework** in strategy lock — yes / rewrite?
2. **Repo location** — `apps/rootlabs-learning/` inside this repo, or separate?
3. **iOS-first or Android-first?**
4. **Brand naming** — "Rootlabs" or "Root Labs"?
5. **Cart screen approach** — non-functional "Coming soon" CTA (per E.5) or omit entirely?

Once these 5 are answered, **Phase 2 scaffolding can run autonomously** — I'd:

- Create the folder structure exactly as Part C describes
- Init `package.json` + `app.json` + `tsconfig.json` + `.gitignore`
- Write the 5 interface contracts (auth, products, ai-coach, checkout, analytics)
- Write the 5 mock implementations
- Write `services/index.ts` (the DI container) — the swap-in centerpiece
- Write the design-system tokens file
- Write at least 3 primitive components (Text, Button, Pill) to prove the pattern works
- Drop the 5 cert PDFs into `assets/cert-pdfs/shilajit-gummies/`
- Write `README.md` (1-page pitch) + `ARCHITECTURE.md` (swap-in diagram)

Estimated scaffolding time: ~45 minutes of focused work, all reversible (it's a new folder, deletable in one command).

---

## Tonight's stop point

This blueprint is durable on disk. Phase 1 is complete. Phase 2 scaffolding awaits sign-off on the 5 open questions.

**Three files now define the project:**

1. [\_audit/2026-05-14_rootlabs-app-strategy-lock.md](_audit/2026-05-14_rootlabs-app-strategy-lock.md) — WHY + WHAT
2. [\_audit/2026-05-14_rootlabs-design-extraction.md](_audit/2026-05-14_rootlabs-design-extraction.md) + [\_audit/2026-05-14_mosaic-design-system-extraction.md](_audit/2026-05-14_mosaic-design-system-extraction.md) — DESIGN
3. [\_audit/2026-05-14_rootlabs-app-blueprint.md](_audit/2026-05-14_rootlabs-app-blueprint.md) (this file) — HOW + ARCHITECTURE
