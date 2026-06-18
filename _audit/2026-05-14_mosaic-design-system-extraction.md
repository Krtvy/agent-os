# Mosaic Mobile App Design System — Extracted from Be Bodywise + Man Matters

**Date:** 2026-05-14
**Source:** 27 iPhone screenshots in `ui-data/IMG_7022.PNG` through `IMG_7048.PNG` (831×1800 each), Read top-to-bottom this session
**Purpose:** Identify the shared "Mosaic mobile" pattern language that the Rootlabs mobile app should inherit, vs. the brand-specific divergence (which we don't copy)

---

## 1. Source map — which screenshot is what

### Be Bodywise (IMG_7022 – IMG_7040)

| File     | Screen                                                                                              |
| -------- | --------------------------------------------------------------------------------------------------- |
| IMG_7022 | OTP entry — phone number input, "Your Wellness Partner" hero                                        |
| IMG_7023 | OTP verify — 4-digit code, "Get Personalized Treatments" hero, "OTP Sent" green toast               |
| IMG_7024 | For You (home) — search, lifestyle hero, product carousel, Trending Categories                      |
| IMG_7025 | For You scroll — Trending Categories grid + Shop by Concern + Bestsellers header                    |
| IMG_7026 | For You scroll — 2-column product grid, "Add to Cart" pattern                                       |
| IMG_7027 | For You scroll — more products with "For: <concern>" tags + % off badges                            |
| IMG_7028 | For You scroll — Shop by Product (Roll Ons / Serum / Gummies italic labels) + Ask the Experts       |
| IMG_7029 | For You scroll — Talk to Experts + "Connect with Friends" social-proof card                         |
| IMG_7030 | For You scroll — Loved by Women Everywhere (testimonial cards with star ratings)                    |
| IMG_7031 | For You scroll — Larger testimonial cards (Ishita / Gayathri)                                       |
| IMG_7032 | For You scroll — "Word on the street feed" with strike-through styling + video reviews              |
| IMG_7033 | For You scroll — More video reviews (Sonya / Jhanvi) with quote framing                             |
| IMG_7034 | For You scroll — "Loved by 300k+ women" social-proof badge in cursive                               |
| IMG_7035 | Shop tab — left vertical category rail + carousel hero + product grid (#1 seller / Top Rated chips) |
| IMG_7036 | Shop tab — different hero ("Triple Action De-Tan Sunscreen") + same grid                            |
| IMG_7037 | Shop tab — Hair category + Foli Advanced+ products                                                  |
| IMG_7038 | Shop tab — slightly different scroll position                                                       |
| IMG_7039 | Cart — items list + delivery urgency + recommended + BB Wallet + "Place Order" sticky CTA           |
| IMG_7040 | Cart scroll — more recommended products                                                             |

### Man Matters (IMG_7041 – IMG_7048)

| File     | Screen                                                                                                           |
| -------- | ---------------------------------------------------------------------------------------------------------------- |
| IMG_7041 | For You (home) — "Your treatment plan" doctor card, Stage 1 + Anti-Dandruff, total price, View Report / Buy Plan |
| IMG_7042 | Shop tab — left rail (All Products / Quick Delivery / Hair / Beard / etc.) + "Built for Indian Athletes" hero    |
| IMG_7043 | Shop tab — "Stop Guessing — Hair Loss" assessment-quiz hero                                                      |
| IMG_7044 | Doctors tab — Experts / Chats tabs, Self Assessment Report card, Available Experts (Dr. Devarshi Dubey)          |
| IMG_7045 | Account — Your Account menu: Address / Orders / Refer / MM Wallet / Payments / Notifications / FAQ etc           |
| IMG_7046 | Account scroll — FAQ / Contact / Privacy / **Honest Reports — batch test reports** / Logout (pink) + v895        |
| IMG_7047 | Cart — "Doctor will call for prescription" green band, 10% OFF discount progress, SAVE10 promo                   |
| IMG_7048 | Cart scroll — Recommended For You, "'FAMILY50' applied [REMOVE]" coupon, sticky CTA with savings %               |

---

## 2. THE Mosaic shared design system (inherit verbatim for Rootlabs)

These patterns are **identical across both brands** — they're the Mosaic house style.

### 2.1 App-shell pattern

**Top header (every primary screen):**

```
[Brand wordmark — left]  [🔍 Search]  [👤 Profile]  [🛒 Cart (red badge)]  [💼 Wallet (badge)]
```

**Bottom tab nav (every primary screen):** exactly 3 tabs

```
[ 🏠 For You ]   [ 🛍 Shop ]   [ 👨‍⚕️ Doctors ]
       ^^^^^^
   active tab: blue tint + icon highlight + label color shift to blue
```

**Sticky cart bar (appears mid-content when items in cart, above bottom nav):**

- Left: "You have items in cart — X Items" (or "View cart X item | ₹Y" on MM Shop)
- Right: "[View Cart]" filled blue pill + close X
- Dismissable

### 2.2 Search bar pattern

- Full-width rounded rectangle, 1px light grey border
- Magnifying glass icon left
- **Dynamic rotating placeholder**: "Search for 'Hair Growth Serum'" / "Search for 'Sunscreen'" / "Search for 'Gummies'" — cycles
- The placeholder is the brand's content marketing in disguise

### 2.3 Product card pattern (2-column grid is standard)

```
┌─────────────────┐
│                 │
│   PRODUCT IMG   │  ← square or 4:5 aspect, white BG
│                 │
├─────────────────┤
│ 30 ML  ROSEMARY │  ← variant chips (grey pill text)
│ Stage 1 Hair Loss│  ← For: <concern> in small grey label
│ Advanced Hair    │
│ Growth Serum     │  ← product name (2 lines max, bold)
│ ₹569 ₹649    ⭐4.5│  ← price + struck MRP + rating right
├─────────────────┤
│ [    ADD    ]   │  ← navy filled pill, white text
│   2 options     │  ← subtext if multi-variant
└─────────────────┘
```

**Chips that appear on cards:**

- "#1 seller" — cream/pale-yellow pill with serif text
- "Top Rated" — same treatment
- "get it today" — orange filled pill (urgency)
- "Selling Fast" — red label
- "New Launch" / "New" — red or accent pill
- "9% off" / "23% off" — green pill

### 2.4 Cart screen pattern

```
[← Back]  Cart

┌────────────────────────────────────────┐
│ 🚚 Order by 1PM, To get it tomorrow at │ ← yellow/cream urgency band
│    Mumbai                              │
└────────────────────────────────────────┘

[ Doctor will call for prescription...]   ← MM-only green compliance band
[ You saved ₹X on this order! ]           ← orange savings band (when applicable)

┌────────────────────────────────────────┐
│ 📦 Standard Delivery                  │
│ get it by Friday, 15th May 2026       │ ← delivery slot
│  ────────────────────────────────────  │
│ [img] 20% Urea Foot Roll On - 50ml   │
│       30 ML  UREA                     │
│                  [-] 1 [+]    ₹399    │ ← qty stepper + price
│ [img] 10% Urea Body Lotion - 200ml   │
│                  [-] 1 [+]    ₹399    │
└────────────────────────────────────────┘

🎁 10% OFF discount unlocked! 🎉           ← gamified unlock
[ progress bar showing how much more for next tier ]

[ Get 10% OFF on Prepaid orders          ]
[ Use Code SAVE10              [APPLY]   ] ← promo input

Recommended For You              [View All]
[2-column carousel of products with discount badges]

Offers & Benefits
'FAMILY50' applied                [REMOVE]  ← coupon applied state

🪪 BB Wallet  Balance: ₹0  PAY ₹769 GET ₹808  [Recharge]

══════════════════════════════════════════
  ₹758.5  ₹1956.5  61% OFF   [Place Order →]   ← sticky CTA bar
══════════════════════════════════════════
```

### 2.5 Account screen pattern

Standard menu list:

```
[← Back]  Your Account

[avatar]  Kartavya Joshi
          +91 9971978396

──────────────────────────────────────
📍  Address                          ›
    View or edit saved addresses
──────────────────────────────────────
📦  Orders                           ›
    Your order history
──────────────────────────────────────
📣  Refer your friends               ›
    Earn upto Rs 2500
──────────────────────────────────────
💼  MM Wallet                        ›
    ₹0
──────────────────────────────────────
🏦  Payment Methods                  ›
    Manage your saved payment methods
──────────────────────────────────────
🔔  Notification Settings            ›
    Enable or disable app notifications
──────────────────────────────────────
[ chat ]  FAQ                        ›
[ phone ] Contact Us                 ›
[shield]  Privacy Policy             ›
[checks]  Terms of Service           ›
[ ❤ doc ] Honest Reports             ›  ← KEY: links to batch test PDFs
                                          (this is where Rootlabs cert PDFs go)
──────────────────────────────────────
              v895 (3.4.0)            ← app version footer
       [        Logout         ]      ← pink-filled, red text
```

### 2.6 Doctors / Experts screen pattern

```
Doctors                                     [🔍] [👤] [🛒(1)] [💼(0)]

  Experts          Chats           ← tab switcher, blue underline active
  ━━━━━━━

Explore by Concern
[          grey rounded rect placeholder for concern grid          ]

┌────────────────────────────────────────┐
│ Self Assessment Report      #502430036 │
│ ─────────────────────────────────────  │
│ 📋 Your Self Assessment Report is Ready│
│    Start your journey toward better    │
│    health today.                       │
│ [        View My Report         ]      │ ← filled navy
└────────────────────────────────────────┘

▌Available Experts

┌─[ photo ]─┐  ✓ Verified
│           │  General Physician
│  Offline  │  MBBS
│ 7 yrs · 5 │  [English] [Hindi]
└───────────┘  Dr. Devarshi Dubey       →
```

### 2.7 Authentication pattern

```
[Header bar with title]

[ Hero banner: pale pastel background + brand-tagline headline + lifestyle photo ]

Page heading                              ← bold, left-aligned
Sub-heading prose

[ Input field (rounded rect, placeholder) ]

[ progressive context: "OTP sent via SMS and Whatsapp" ]
[ "Didn't receive OTP? Resend Now in 28 seconds" ]

(empty space — keyboard fills it)

══════════════════════════════════════════
[              Get OTP / Verify           ]   ← bottom-anchored CTA
══════════════════════════════════════════
By signing in you agree to our Terms · Privacy
```

### 2.8 Component micro-patterns

**Buttons:**

- **Primary filled**: navy blue, white text, fully-rounded pill (corner radius ≈ button height / 2)
- **Secondary outlined**: white BG, navy text, navy 1px border, same pill shape
- **Tertiary text link**: navy/cobalt, no underline, just blue text
- **Destructive**: light pink BG, red text (Logout)
- **Pill chip filter**: small rounded pill, grey-on-white or white-on-blue (active)

**Toasts:**

- Green pill with white checkmark + label, fades from top under header. E.g., "OTP Sent" with ✓ icon.

**Form inputs:**

- Rounded rect, 1px light grey border
- Label above input (bold)
- Helper/microtext below (light grey)
- Native iOS keyboard (not custom number pad)

**Star ratings:**

- Yellow filled stars (4 or 5 of 5)
- Grey empty stars
- Numeric rating shown alongside (e.g., "★ 4.3")

**Quote framing on testimonials:**

- Double-quote glyphs (") visible left and right, italic-ish
- White text on brand-color card OR brand-color text on white card

**Strike-through MRP:**

- Current price first, bold, larger
- MRP after, smaller, strike-through, mid-grey
- Sometimes a % off in green pill on right

**Italic-script callouts:**

- Special copywriting moments use italic cursive ("300k+ _women_", category labels "Roll Ons" / "Serum")
- Hand-writingy display font for emphasis, not body

---

## 3. Per-brand divergence — do NOT copy these to Rootlabs

| Element                 | Be Bodywise                                                                                | Man Matters                                                                                             | Rootlabs should...                                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Primary brand color** | Cobalt blue + pink accents (logo)                                                          | Royal/navy blue throughout                                                                              | Use **#13523B** forest green (already extracted from Shopify theme) — be the green one                                       |
| **Logo wordmark**       | Cursive "BE" + bold "Bodywise"                                                             | Lowercase stacked "man matters"                                                                         | Use Rootlabs wordmark from website (one-word "rootlabs" or two-word "Root Labs")                                             |
| **Hero aesthetic**      | Lifestyle imagery, women, soft pink/cream                                                  | Athletic, orange splashes, masculine clinical                                                           | **Botanical** — Himalayan mountain imagery, earthy textures, cream backgrounds (matches `#FEF8F3`)                           |
| **Brand voice**         | Confessional, social ("Loved by Women", "Word on the street feed", "Connect with Friends") | Diagnostic, medical ("Stop Guessing — Hair Loss", "Built for Indian Athletes", "Doctor has formulated") | **Heritage + clinical** — "Handpicked in nature. Perfected in science." Founder-led ("Influencing Our Voice — Mayank Kumar") |
| **Audience**            | Women's wellness, India                                                                    | Men's wellness, India                                                                                   | **Wellness-curious, US market, premium-but-approachable**                                                                    |
| **Doctor pattern**      | "Ask the Experts" + "Talk to Experts" — softer                                             | "Treatment plan" doctor card pre-built — clinical/Rx-style                                              | **Founder + 2 endorsed doctors** (Dr. Christianson, Dr. Appelhans from rootlabs.co) — no Rx flow                             |
| **Trust mechanic**      | Customer testimonials + 300k+ social proof                                                 | Doctor verification, treatment plans, batch test reports                                                | **Heritage + science + 7 cert badges + 2 doctors + customer reviews** — fewer customers, more credentialing                  |
| **Cart compliance**     | Standard                                                                                   | "Doctor will call for prescription" green band                                                          | Skip — no Rx in v1 (intern app, no real orders)                                                                              |

---

## 4. Mosaic design tokens (estimated from screenshots, will refine)

Hex values estimated visually — refine with a colour-picker tool against the PNGs if needed:

| Token                   | Be Bodywise          | Man Matters              | Mosaic-shared                                                  |
| ----------------------- | -------------------- | ------------------------ | -------------------------------------------------------------- |
| Primary blue            | ≈ `#1E60B5` (cobalt) | ≈ `#1B4F8A` (royal navy) | navy family                                                    |
| Active nav blue         | ≈ `#2E7BD8`          | ≈ `#2E7BD8`              | same                                                           |
| Logo accent (BB)        | Pink/Red on "B"      | —                        | brand-specific                                                 |
| Background              | `#FFFFFF`            | `#FFFFFF`                | white (Rootlabs uses **cream `#FEF8F3`** instead — divergence) |
| Body text               | ≈ `#1A1A1A`          | ≈ `#1A1A1A`              | near-black                                                     |
| Card border             | ≈ `#E5E7EB`          | ≈ `#E5E7EB`              | light grey                                                     |
| Struck MRP              | ≈ `#9CA3AF`          | ≈ `#9CA3AF`              | mid-grey                                                       |
| Discount % pill (green) | ≈ `#2A8C5C`          | ≈ `#2A8C5C`              | green                                                          |
| Urgency pill (orange)   | ≈ `#F97316`          | ≈ `#F97316`              | orange                                                         |
| Success toast           | ≈ `#22A06B`          | ≈ `#22A06B`              | green                                                          |
| Red badge (cart count)  | ≈ `#EF4444`          | ≈ `#EF4444`              | red                                                            |
| Compliance band BG (MM) | —                    | ≈ `#E7F4EC`              | —                                                              |
| Savings band BG         | ≈ `#FEF3C7`          | ≈ `#FEF3C7`              | pale yellow                                                    |
| Logout button BG        | ≈ `#FEE2E2`          | ≈ `#FEE2E2`              | light pink                                                     |

---

## 5. The Rootlabs translation — what we inherit, replace, invent

### Inherit verbatim from Mosaic (free design system, battle-tested)

- App shell (top header + bottom 3-tab nav)
- Search bar with rotating placeholder
- 2-column product grid
- Product card structure (image · name · For: · price · ADD)
- Cart screen flow (urgency band → items → recommended → wallet → sticky CTA)
- Account screen menu pattern
- Doctors tab structure
- All button styles (filled / outlined / link / destructive)
- Toast pattern
- Form input pattern
- Star rating treatment
- Strike-through MRP styling
- "Honest Reports" account menu item → links to the 5 cert PDFs

### Replace with Rootlabs identity (already extracted from rootlabs.co)

- **Primary color** → `#13523B` forest green (replaces Mosaic blue)
- **Background** → `#FEF8F3` cream (replaces Mosaic white) — important: this is the warm soul of Rootlabs
- **Wordmark** → "Root Labs" or "rootlabs" — actual lockup from site
- **Hero phrase template** → "Handpicked in nature. Perfected in science." / "Expand Your Roots" / "Right from the Roots"
- **Typography** → Figtree (body) + Matter or Inter (display) — replaces Mosaic's sans stack
- **Italic-script accent** → use for "_nature_" / "_roots_" / "_science_" emphasis (matches the Rootlabs voice fingerprint)
- **3 pillars callout** → "Carefully crafted · Maximum absorption · Science-backed" with green accent
- **Trust band** → Dr. Christianson + Dr. Appelhans + 7 cert badges + Mayank Kumar founder story
- **Discount badge color** → keep green (Rootlabs uses green for "% off" via Shopify theme) but check if it should be the orange `#E5732E` Rootlabs accent

### Invent for Rootlabs (no Mosaic-sibling equivalent)

- **"Our Science" tab content** — long-form educational articles (rootlabs.co has these, BB+MM don't)
- **Cert PDF inline viewer** — tap "Honest Reports" → list of batch reports → tap → PDF opens (we have the 5 cert PDFs already, drop them into the app's static assets)
- **Ingredient deep-dive on PDP** — Rootlabs leans on ingredient education more than Mosaic siblings do
- **Founder voice card** — "Influencing Our Voice — Mayank Kumar" on About / Science tab
- **Weekly science drop card on Home** — the retention hook from the strategy lock

### Cut from v1 (Mosaic has them, we don't)

- Cart compliance band ("Doctor will call for prescription") — no Rx flow
- Self Assessment quiz — replaced by simpler goal-picker on splash
- Treatment plan card — Rootlabs doesn't do Rx-style bundles
- Refer-a-friend (no real users to refer)
- Payment methods (no checkout in v1)
- Notification settings (no push in v1)
- Wallet / loyalty mechanic — defer until company decides

---

## 6. Component inventory for Phase 2 scaffolding

The atomic components we need to build (each gets one file in `components/` once we scaffold):

| Component                                         | Used in                          | Mosaic source                     |
| ------------------------------------------------- | -------------------------------- | --------------------------------- |
| `TopBar`                                          | every primary screen             | BB + MM home headers              |
| `BottomTabNav`                                    | every primary screen             | BB + MM bottom 3-tab              |
| `SearchBar`                                       | Home / Shop                      | BB + MM with rotating placeholder |
| `StickyCartBar`                                   | mid-content above tab nav        | BB + MM                           |
| `Button` (filled / outlined / link / destructive) | everywhere                       | BB + MM                           |
| `ProductCard`                                     | grids, carousels, recommended    | BB + MM 2-col                     |
| `Chip` (#1 seller, Top Rated, get it today, New)  | product cards                    | BB + MM                           |
| `DiscountPill` (% off green)                      | product cards, cart              | BB + MM                           |
| `StarRating`                                      | testimonials, product cards      | BB + MM                           |
| `Toast`                                           | post-action feedback             | BB OTP sent                       |
| `InputField`                                      | auth, promo codes                | BB OTP screens                    |
| `MenuRow` (icon + title + subtitle + chevron)     | Account screen                   | MM Account                        |
| `HeroBanner`                                      | top of Home + Shop               | BB lifestyle + MM athletic        |
| `CarouselDots`                                    | hero banners                     | BB Shop carousel                  |
| `TestimonialCard`                                 | Home scroll                      | BB "Loved by Women"               |
| `VideoReviewCard`                                 | Home scroll                      | BB "Word on the street feed"      |
| `CertPDFRow`                                      | "Honest Reports" account submenu | (Rootlabs-specific)               |
| `IngredientCard`                                  | PDP                              | (Rootlabs-specific — invent)      |
| `FounderCard`                                     | About / Science tab              | (Rootlabs-specific — invent)      |

That's ≈18 atomic components — manageable for Phase 2.

---

## 7. Open questions surfaced by this extraction

1. **Wallet/loyalty mechanic** — both BB and MM have it as a core revenue/retention pattern. Should Rootlabs mobile have it in v1 (faked) or leave the slot empty? My recommendation: **leave the slot empty in nav, build the screen later**, since it requires a real money mechanic to be meaningful.
2. **3-tab nav (For You / Shop / Doctors)** vs Rootlabs's possibly 4-tab structure (For You / Shop / Science / Saved)? Mosaic's 3 is the safer mirror; "Science" is more important for Rootlabs than "Doctors" since they don't have a consultation business model.
3. **Cart in v1?** Strategy lock says no cart since no checkout. But the demo will look strange without one. **Suggestion: include a non-functional Cart screen that shows "Coming soon — checkout integration pending company API access"** as the explicit pitch-moment.
4. **Bottom sticky "Place Order" bar** — even if non-functional, having it tells the company "this is where Shopify webview opens." Include it as a `// PLUG IN HERE` slot.

---

## 8. What's next

Phase 1 is now ~70% done. Remaining:

- Sample a few exact hex values from the screenshots with a colour picker tool (to convert my visual estimates to precise tokens)
- Read the 5 cert PDFs to confirm they're standard test reports (will inform the "Honest Reports" screen design)
- Cross-reference with the Rootlabs `_audit/2026-05-14_rootlabs-design-extraction.md` to merge into a single design system spec

Phase 2 (architecture skeleton) can start the moment Phase 1 is fully merged.
