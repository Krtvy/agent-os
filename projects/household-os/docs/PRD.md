# PRD — Household OS
## Product Requirements Document
> Version: 1.0 | Date: June 25, 2026 | Author: Kartavya Joshi
> Based on: RESEARCH.md (India Household Deep Brief)

---

## 1. THE PROBLEM

### What breaks every day in an Indian urban household

Urban Indian households — specifically nuclear families with domestic staff in Tier 1 cities — face a coordination problem that no technology has solved:

**The daily decision stack (all before 9 AM):**
1. What should we cook today?
2. Do we have the ingredients for it?
3. What needs to be ordered from BigBasket/Zepto?
4. Has the cook arrived? What instructions do I give her?
5. Is the maid coming today or calling in sick again?
6. Did anyone tell the cook about the guest coming for dinner?

This happens **every single day**, and it happens inside the head of one person — almost always the primary female adult in the household. She carries 305 minutes of unpaid cognitive work daily, on top of paid employment.

### The numbers that prove the pain
- Women: **305 min/day** unpaid household work vs men's 88 min/day
- **67%** of urban households waste food due to improper meal planning
- **₹50,000+ wasted per household annually** in food waste alone
- **60,000 households simultaneously searching for domestic help** in Delhi at any given time
- **No app exists that connects meal planning → ingredients → grocery → cook instruction → feedback**

### Why now
- Supply side getting solved (Snabbit $180M, Pronto $100M, Urban Company IPO) — daily help is increasingly available
- Quick commerce (Blinkit/Zepto) solved 10-min delivery — grocery fulfillment is commoditized
- **The intelligence layer — what to order, what to cook, how to brief the cook — is completely open**
- 10-min home help hit 1.3M orders in December 2025 (+50-60% from October) — market is real

---

## 2. TARGET USER

### Primary User: "Priya"
- **Who:** Urban Indian woman, 28-45, working professional or household manager
- **Where:** Delhi NCR, Bangalore, Mumbai, Pune (Tier 1)
- **Household:** Nuclear family, 3-5 members, 1-2 domestic workers (cook + maid)
- **Income:** SEC A/A1, household income ₹15-40 lakh/year
- **Device:** Smartphone-native, active WhatsApp user, uses BigBasket + Blinkit + Swiggy
- **Pain:** Carries the entire household cognitive load. Knows exactly what's broken but has no tool to fix it.
- **Motivation:** Wants the household to run smoothly without her having to think about it every morning

### Secondary User: "The Cook"
- **Who:** Part-time or full-time cook, 25-55, female
- **Literacy:** Variable Hindi literacy; likely WhatsApp-fluent via voice notes
- **Relationship:** Serves 3-6 households; semi-loyal to 1-2 primary employers
- **Needs:** Clear daily instructions in her language; simplified interface; no app downloads preferred
- **Interface:** WhatsApp-first; voice notes; image-based communication

### Influencer Users (not primary, but must accommodate)
- **Spouse:** Food preferences, occasional instruction giving
- **Children:** Taste preferences, meal veto power
- **Remote in-laws:** Dietary guidance via WhatsApp (often communicated directly to cook, bypassing Priya)

---

## 3. SOLUTION: Household OS

### Vision
"Don't tell me, Tell M" — the household runs itself.

### What it does (the end-to-end loop)

```
Meal Plan (weekly)
    ↓
Ingredient Check (pantry awareness)
    ↓
Grocery Order (BigBasket/Zepto integration)
    ↓
Cook Instruction (WhatsApp-native, vernacular)
    ↓
Staff Schedule (who comes when, SOP compliance)
    ↓
Feedback + Learning (what worked, what to repeat)
    ↓
Next Week's Plan (smarter, more personalized)
```

**No product today connects all these nodes. M does.**

---

## 4. FEATURES (MOSCW)

### Must Have — MVP (Month 1-2)

**M1: Household Profile Setup**
- Onboarding captures: household size, dietary restrictions (religious, personal), allergies, regional cuisine preference, cuisine rotation habits
- Dietary matrix: Vegetarian/Non-veg/Vegan/Jain/Halal + day-of-week fasting patterns + festival calendar
- Staff profile: cook name, days, hours, languages spoken, dishes they can make
- Pantry staples baseline: what the household always keeps

**M2: Weekly Meal Planner (Indian-first)**
- Generates 7-day meal plan: breakfast + lunch + dinner per day
- Considers: household dietary matrix, weekly rotation (no dish repeated within 4 days), nutritional balance
- Handles combination meals (dal + sabzi + roti/rice + raita) — not single-dish planning
- Festival-aware: automatically adjusts for Navratri, Ekadashi, Eid, etc. based on household calendar
- Cook editable: Priya can swap dishes, cook can confirm or flag difficulty

**M3: Smart Grocery List**
- From meal plan → ingredient extraction → stock-check against pantry → grocery list
- One-tap integration with BigBasket/Zepto/Instamart to add to cart
- Weekly staples auto-replenishment (milk, curd, bread, eggs if applicable)
- Reduces duplicate buying, covers shortages before they happen

**M4: Cook Communication (WhatsApp-native)**
- Daily morning message to cook: today's menu in Hindi/regional language with voice note option
- Keeps message concise: "Aaj lunch mein dal makhani aur palak paneer. Raat ko rajma chawal."
- Priya reviews and sends with one tap
- Cook can reply (voice note) if something is missing or she's late

**M5: Staff Scheduler**
- Calendar view of who comes when
- Same-day absence notification flow (cook/maid messages M → Priya gets alert → reschedule options)
- Recurring schedule management
- Leave calendar (festivals, personal leave)

### Should Have — V1.1 (Month 3-4)

**S1: Pantry Tracker**
- Manual entry + photo-based inventory (Gemini Vision for ingredient recognition)
- Expiry tracking for perishables
- "Running low" alerts for staples
- Reduces food waste (67% of households waste due to poor planning)

**S2: Household SOP Library**
- Templated SOPs for common tasks (how to mop, how to cook X dish per household preference)
- Shareable with new cook/maid via WhatsApp PDF
- Reduces onboarding time when a worker changes
- Converts tribal knowledge into portable documentation

**S3: Guest Occasion Planning**
- "We have 8 guests Saturday" → expanded meal plan, ingredient multiplier, grocery surge list
- Menu suggestions for different guest types (pure veg relatives, office colleagues, etc.)

**S4: Feedback Loop**
- After each week: "How did meals go this week?" quick rating
- Dish ratings feed back into future planning ("family loved the butter chicken, suggest again next week")
- Cook performance notes (private, for Priya only)

### Could Have — V2 (Month 5+)

- Nutrition analysis (macro tracking, RDA compliance)
- Vendor management (electrician, plumber, AC service) with annual calendar
- Household budget tracking
- Multi-home management (managing in-laws' home remotely)
- Community recipes (neighborhood, building WhatsApp group recipe sharing)

### Won't Have (This Version)

- In-home sensors / IoT
- Payment processing to domestic workers
- Staff recruitment / marketplace
- Insurance or social security for workers
- Cooking instruction videos

---

## 5. CORE PRODUCT PRINCIPLES

**P1: Indian-first, not Indian-adapted**
Every feature is designed for Indian households natively — combination meals, regional diversity, festival calendar, dietary complexity, vernacular communication, WhatsApp as primary channel.

**P2: Cook is a user, not a recipient**
The cook's interface must be as thoughtfully designed as Priya's. Voice-first, image-based, Hindi/regional language native. An app Priya uses that ignores the cook will fail.

**P3: Intelligence compounds over time**
The more the household uses M, the smarter it gets — meal preferences, staff patterns, seasonal adjustments, family taste evolution. Week 1 is basic; Week 12 is magical.

**P4: Don't break existing habits**
Priya already uses WhatsApp to communicate with her cook. She uses BigBasket for groceries. She won't switch. M integrates INTO these habits, it doesn't replace them.

**P5: Respect the relationship**
Domestic worker relationships are not purely transactional. M should never frame the cook/maid as a "service provider." Language, tone, and design should honor the relationship's social dimension.

---

## 6. DATA STRATEGY

### Datasets to source (existing, free)
- Indian recipes: 6,500 recipes from Kaggle (sooryaprakash12) — foundation
- Regional tags + instructions: IndianFoodDatasetGeneration (GitHub/kanishk307)
- Nutritional data: HuggingFace (bharat-raghunathan)
- Household expenditure: HCES 2023-24 (microdata.gov.in — free, registration required)

### Datasets to BUILD (proprietary moat)
1. **Indian Dietary Restriction Matrix**
   - Religion × region × household type × day-of-week × festival calendar
   - Not available anywhere — must build from research + community data

2. **Festival Food Calendar**
   - 20+ festivals, each with: allowed foods, forbidden foods, fasting types, guest norms
   - Mapped to Gregorian calendar (festivals shift annually)

3. **Cook-Instruction Format Dataset**
   - Recipe → instruction translation into cook-friendly format
   - Shorter sentences, measurements in "katori/cup" not grams, ingredient substitutions

4. **Indian Pantry Staples Database**
   - Category: Dals, Spices, Grains, Dairy, Oils, Preserved
   - With: shelf life, average household consumption rate, reorder trigger quantity

5. **Indian Grocery Product Database**
   - SKU-level: BigBasket product catalogue (scraped), Zepto/Blinkit catalogue
   - Category, brand, MRP, unit, nutritional info

---

## 7. SUCCESS METRICS

| Metric | Target (3 months post-launch) |
|---|---|
| D7 retention | >50% |
| Weekly meal plan completion rate | >5 out of 7 days |
| Grocery integration usage | >60% of active users |
| Cook communication sent daily | >70% of active households |
| Self-reported food waste reduction | >30% |
| NPS | >50 |
| Staff scheduling conflicts resolved via app | >40% of absences |

---

## 8. OPEN QUESTIONS (for TRD)

1. **WhatsApp integration**: Use WhatsApp Business API (₹0.39-0.85/conversation) or build web-based chat that mimics WhatsApp?
2. **Grocery API**: BigBasket has no public API — scrape + affiliate link, or build catalog manually?
3. **Cook onboarding**: How do we onboard illiterate/semi-literate cooks without requiring them to download an app?
4. **Dietary matrix storage**: How do we model the multi-dimensional dietary restriction graph efficiently?
5. **Festival calendar**: Build once as a static structured database, or dynamic/crowdsourced?
6. **Regional cuisine engine**: How deep do we go in regional differentiation (North Indian vs South Indian vs Bengali vs Gujarati) at MVP?
7. **Privacy**: Household data is deeply personal. What's the minimum data collection principle?

---

## 9. RISKS

| Risk | Severity | Mitigation |
|---|---|---|
| Cook doesn't adopt new communication method | High | WhatsApp-native; no app download required for cook |
| Indian dietary complexity too hard to model at MVP | Medium | Start with 3 profiles (veg/non-veg/Jain); expand gradually |
| BigBasket/Zepto don't have public APIs | Medium | Build deep-link integration + affiliate; negotiate API access |
| User expects magic from day 1, gets utility | Medium | Set expectations clearly in onboarding; magic comes by Week 4 |
| Data privacy concerns for household data | Medium | Local-first storage; no household data sold |
| Competition from Snabbit/Pronto adding planning features | Low | They're supply-focused; intelligence layer requires different team/focus |
