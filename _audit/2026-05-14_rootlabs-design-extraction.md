# Rootlabs.co — Design System Extraction

**Date:** 2026-05-14
**Source:** Live HTML + Shopify theme settings pulled via curl from `https://rootlabs.co/`
**Why this exists:** Captures the _exact_ design tokens (hex codes, fonts, copy, structure) directly from the production site — richer than WebFetch text summary, doesn't require Playwright.

---

## 1. Brand Colour Palette — Exact Hex (from Shopify theme settings JSON)

### Primary brand

| Hex           | Where used                                                                                                                                                                            | Role                                                                      |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **`#13523B`** | `brand_theme_color` · `brand_text_color` · `tertiary_color` · `brand_atc_button_color` · `buy_now_button_text_color` · `badge_star_color` · `widget_star_color` · `--text` on hero    | **PRIMARY — deep forest green.** The Rootlabs brand color.                |
| **`#01563E`** | Heavy inline usage (36x)                                                                                                                                                              | Darker green variant — likely hover state or alt brand surface            |
| **`#108474`** | `all_reviews_text_color` · `verified_count_badge_color` · `featured_carousel_header_background_color` · `widget_ugc_primary_button_background_color` · `medals_widget_elements_color` | **Teal-green accent** — used for social proof / reviews / verified badges |

### Background / surface

| Hex           | Role                                                                                  |
| ------------- | ------------------------------------------------------------------------------------- |
| **`#FEF8F3`** | Primary cream background (`brand_atc_button_text_color`) — warm off-white             |
| **`#F2F0E8`** | Alternate warm cream — section dividers                                               |
| **`#E8DDD3`** | Peach/skin warm tone — likely band-aid color for accents                              |
| **`#f9fafb`** | Neutral light gray (`medals_widget_background_color`) — for clinical-feeling sections |

### Text / structural

| Hex                    | Role                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **`#000000`** / `#000` | Pure black — used in `stories_title_font_color`, `product_info_text_color`                                         |
| **`#1e1e1e`**          | Near-black body text (25x in inline)                                                                               |
| **`#343434`**          | Dark grey — `atc_color`, `brand_divider_color`, `carousel_heading_color`, `product_tile_shopnow_custom_text_color` |
| **`#808191`**          | Mid-grey — `mrp_text_color` (struck-through MRP / strike-through pricing)                                          |
| **`#FFFFFF`**          | Pure white — buttons text, UGC widget arrows                                                                       |
| **`#eeeeee`**          | Light grey — `featured_carousel_arrow_color`                                                                       |

### Accent / call-out

| Hex                                           | Role                                                     |
| --------------------------------------------- | -------------------------------------------------------- |
| **`#E5732E`**                                 | **Warm orange** — likely discount badges / urgency CTAs  |
| **`#fbcd0a`**                                 | Star-rating yellow (`widget_rating_filter_color`)        |
| **`#5a8472`** · **`#3C5E52`** · **`#29644D`** | Green tonal variants — gradient stops or section banding |

### Quick reference — TL;DR

- **Hero brand:** `#13523B` (forest green)
- **Background:** `#FEF8F3` (warm cream)
- **Body text:** `#1e1e1e` (near-black)
- **Accent / CTA secondary:** `#E5732E` (warm orange)
- **Social proof / verified:** `#108474` (teal)

---

## 2. Typography

CSS classes observed throughout the markup:

- **`ibm`** — likely IBM Plex Sans (used for `.hero__title`, `.section-dev-title`, `.h5`)
- **`matter`** — likely Matter (`.section-dev-title.matter`, `.footer__block__title.matter`)
- **`Figtree`** — explicitly named in inline `font-family` declarations

So Rootlabs uses **a 3-font system**: one display/header serif-or-sans (Matter), one body sans (IBM Plex / Figtree), and Figtree as a probable system fallback. **For the mobile app, mirroring this with 2 system fonts (one display, one body) gets us 90% of the visual match.**

---

## 3. Navigation Structure (from homepage HTML)

```
Our products  ·  Science  ·  About  ·  What else  ·  Blog  ·  Contact us  ·  Become an affiliate
```

**Actual page slugs that resolve (HTTP 200):**

- `/` (home)
- `/collections/frontpage` (catalog)
- `/products/<slug>` (PDPs — e.g. `alpha-gummies-60s`)
- `/pages/science` ✓
- `/pages/our-story` ✓ (the "About" link)
- `/pages/contact` ✓
- `/blogs/news/<post>` (blog)

**Slugs that 404'd** (don't exist on production):

- `/pages/about-us` · `/pages/about` · `/pages/honest-report` · `/pages/what-else` · `/pages/our-science` · `/pages/transparency` · `/pages/quality` · `/pages/testing`

So **"Honest Report" is not a page** — it may be a section anchor on the homepage or About page, or it may be on a different version of the site. **"What else"** also has no dedicated page — likely an anchor to a homepage section.

---

## 4. Brand Voice — Verbatim Phrases Pulled from Live HTML

### Hero / tagline candidates

- "Handpicked in nature."
- "Handpicked in Nature" (capitalized variant)
- "Born of the desire to return to our roots"
- "Expand Your Roots"
- "Right from the Roots"

### Headline labels (verbatim from `<h1>` / `<h2>`)

- "Influencing Our Voice" (About page, paired with founder name **"Mayank Kumar"**)
- "From Experts We Trust"
- "Our Customers Speak"
- "Expand Your Roots"
- "Right from the Roots"

### Brand pillars (3-up section)

- **Carefully crafted**
- **Maximum absorption**
- **Science-backed**

### Commerce micro-copy

- "Congratulations! Your order qualifies for free shipping"
- "You are $30 away from free shipping."
- "No more products available for purchase"
- "Shipping, taxes, and discount codes are calculated at checkout"
- "Your Cart is Empty"

### Footer

- "© Root Labs 2026. All rights reserved"
- Note: brand written as **"Root Labs"** (two words) in copyright, but as **"rootlabs"** (one word) in the domain. Both forms appear acceptable.

---

## 5. Founder Detail (new — not surfaced in earlier WebFetch)

**Mayank Kumar** is featured prominently on `/pages/our-story` under the headline **"Influencing Our Voice"** — suggesting a founder-story or influencer-led narrative angle. The site is built around a personal voice, not a corporate-anonymous one. Aligns with Mosaic's house style of founder-led brands.

---

## 6. What This Means for the Mobile App

| Design concern       | Constraint extracted                                                           |
| -------------------- | ------------------------------------------------------------------------------ |
| Primary brand colour | `#13523B` — deep forest green                                                  |
| Background           | `#FEF8F3` — warm cream (NOT pure white — important for warmth)                 |
| Body text            | `#1e1e1e` (not pure black — gentler)                                           |
| CTA / accent         | `#E5732E` warm orange OR `#13523B` for primary actions                         |
| Star ratings         | `#fbcd0a` yellow + `#13523B` for "verified"                                    |
| Section dividers     | `#343434`                                                                      |
| Strike-through MRP   | `#808191`                                                                      |
| Typography           | Display: Matter (or IBM Plex Sans) · Body: Figtree                             |
| Tone                 | Personal, founder-led, warm-clinical (Ayurvedic heritage + science vocabulary) |
| Hero phrase template | "Handpicked in nature. Perfected in science."                                  |
| 3-pillar pattern     | Carefully crafted / Maximum absorption / Science-backed                        |

---

## 7. Methodology Note (for replication)

How this was extracted, in one shell command pattern:

```bash
# 1. Pull homepage HTML
curl -sL https://<site>/ -o /tmp/page.html

# 2. Extract Shopify theme colour settings (works for any Shopify store)
grep -oE '"[a-z_]+_color":\s*"#[A-Fa-f0-9]{3,8}"' /tmp/page.html

# 3. Find all hex codes by frequency
grep -oE '#[A-Fa-f0-9]{6}' /tmp/page.html | sort | uniq -c | sort -rn

# 4. Extract headlines + body voice
grep -oE '<h[1-3][^>]*>[^<]+</h[1-3]>' /tmp/page.html
```

This pattern works on any Shopify-hosted site and gives more exact tokens than WebFetch's summary-style output. Worth saving as a `training/patterns/` entry once we have a second example.
