# TRD — Household OS
## Technical Requirements Document
> Version: 1.0 | Date: June 25, 2026 | Author: Kartavya Joshi
> Depends on: PRD.md, RESEARCH.md

---

## 1. SYSTEM ARCHITECTURE

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│   Web App (Next.js)    Mobile (React Native)   WhatsApp     │
└────────────────────────┬────────────────────────────────────┘
                         │ REST / WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                   │
│              Auth │ Rate limiting │ Request routing         │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
Household  Meal Plan  Grocery   Staff Mgmt  Comms
Service    Engine     Service   Service     Service
   │          │          │          │          │
   └──────────┴──────────┴──────────┴──────────┘
                         │
              ┌──────────▼──────────┐
              │    PostgreSQL DB     │
              │    Redis Cache       │
              │    Gemini AI API     │
              └─────────────────────┘
```

### Core Services

| Service | Responsibility |
|---|---|
| **Household Service** | Profile, dietary matrix, household members, preferences |
| **Meal Planning Engine** | Weekly plan generation, recipe selection, festival awareness |
| **Grocery Service** | Pantry tracking, shopping list, BigBasket/Zepto integration |
| **Staff Management** | Schedules, attendance, SOPs, leave calendar |
| **Communication Service** | WhatsApp message generation and delivery |
| **Notification Service** | Daily reminders, alerts, morning briefings |
| **Dataset Service** | Indian recipe DB, dietary rules DB, festival calendar |

---

## 2. TECH STACK

### Backend
```
Language:      Python 3.12+
Framework:     FastAPI (async, high performance, OpenAPI auto-docs)
Database:      PostgreSQL 16 (primary data store)
Cache:         Redis 7 (sessions, meal plan cache, rate limiting)
Queue:         Celery + Redis (async tasks: WhatsApp sends, grocery syncs)
AI:            Gemini 2.5 Flash (meal planning, instruction generation, image recognition)
               Groq LLaMA 70B (fallback, cost optimization)
```

### Frontend
```
Web:           Next.js 14 (SSR, good for SEO, WhatsApp web redirect)
Mobile:        React Native (iOS + Android, later phase)
UI:            Tailwind CSS + shadcn/ui
State:         Zustand (lightweight)
```

### Infrastructure
```
Hosting:       Railway.app (simple, India-friendly, no AWS complexity at MVP)
Storage:       Cloudflare R2 (images, SOP PDFs — free tier generous)
Monitoring:    Sentry (errors) + Logfire (FastAPI native observability)
CI/CD:         GitHub Actions
```

### External APIs
```
WhatsApp:      Twilio WhatsApp API (easier sandbox vs Meta Business API)
               Upgrade to Meta WhatsApp Business API at 1000+ users
Grocery:       BigBasket affiliate deep links (no public API exists)
               Zepto app deep links
               Future: Blinkit affiliate API (has one)
Payments:      Razorpay (if subscription model added later)
```

---

## 3. DATA MODELS (ERD Preview)

### Core Entities

```sql
-- HOUSEHOLD
CREATE TABLE households (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100),           -- "Sharma Family"
    city            VARCHAR(50),            -- "Delhi NCR"
    tier            VARCHAR(20),            -- "tier1"
    primary_user_id UUID REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT now()
);

-- HOUSEHOLD MEMBERS
CREATE TABLE household_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    name            VARCHAR(100),
    age             INTEGER,
    role            VARCHAR(50),            -- "primary", "spouse", "child", "parent"
    diet_profile_id UUID REFERENCES diet_profiles(id)
);

-- DIET PROFILE (the core complexity)
CREATE TABLE diet_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_diet           VARCHAR(20),        -- vegetarian|non_veg|vegan|jain|eggetarian
    religion            VARCHAR(30),        -- hindu|muslim|jain|sikh|christian|other
    no_beef             BOOLEAN DEFAULT false,
    no_pork             BOOLEAN DEFAULT false,
    no_root_veg         BOOLEAN DEFAULT false,   -- Jain restriction
    halal_only          BOOLEAN DEFAULT false,
    fasting_days        JSONB,              -- {"monday": false, "tuesday": true, ...}
    disliked_ingredients TEXT[],            -- ["mushrooms", "bitter gourd"]
    allergies           TEXT[],
    spice_level         VARCHAR(10)         -- mild|medium|hot
);

-- FESTIVAL CALENDAR (static reference table)
CREATE TABLE festival_calendar (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100),           -- "Navratri"
    year            INTEGER,
    start_date      DATE,
    end_date        DATE,
    religions       TEXT[],                 -- ["hindu"]
    restrictions    JSONB,
    /* restrictions example:
    {
      "no_meat": true,
      "no_onion": true,
      "no_garlic": true,
      "no_alcohol": true,
      "grains_allowed": false,
      "allowed_foods": ["sabudana", "kuttu", "sama rice", "fruits"],
      "fasting_type": "full_day|one_meal|no_fast"
    } */
    regions         TEXT[]                  -- ["north_india", "all_india"]
);

-- RECIPES (Indian recipe database)
CREATE TABLE recipes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200),           -- "Dal Makhani"
    name_hindi      VARCHAR(200),           -- "दाल मखनी"
    cuisine_region  VARCHAR(50),            -- "north_indian|south_indian|maharashtrian|..."
    meal_type       VARCHAR(20),            -- "breakfast|lunch|dinner|snack"
    course          VARCHAR(30),            -- "main|side|bread|rice|dessert|beverage"
    diet_tags       TEXT[],                 -- ["vegetarian", "jain_friendly"]
    base_diet       VARCHAR(20),            -- "vegetarian"
    festival_ok     TEXT[],                 -- ["navratri"] — festivals where this is allowed
    prep_time_min   INTEGER,
    cook_time_min   INTEGER,
    servings        INTEGER,
    difficulty      VARCHAR(10),            -- "easy|medium|hard"
    ingredients     JSONB,
    /* ingredients example:
    [
      {"item": "masoor dal", "quantity": 1, "unit": "cup", "category": "dal"},
      {"item": "butter", "quantity": 2, "unit": "tbsp", "category": "dairy"}
    ] */
    instructions    TEXT,                   -- full recipe
    cook_instruction TEXT,                  -- simplified for cook (Hindi-friendly)
    nutrition       JSONB,                  -- calories, protein, carbs, fat per serving
    tags            TEXT[]                  -- ["popular", "quick", "winter", "summer"]
);

-- MEAL PLANS
CREATE TABLE meal_plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    week_start      DATE,
    week_end        DATE,
    status          VARCHAR(20),            -- "draft|approved|active|completed"
    created_by      VARCHAR(20),            -- "ai|user"
    approved_at     TIMESTAMP,
    meals           JSONB
    /* meals example:
    {
      "monday": {
        "breakfast": {"recipe_id": "...", "recipe_name": "Poha"},
        "lunch": [
          {"recipe_id": "...", "recipe_name": "Dal Tadka", "course": "main"},
          {"recipe_id": "...", "recipe_name": "Aloo Jeera", "course": "side"},
          {"recipe_id": "...", "recipe_name": "Roti", "course": "bread"}
        ],
        "dinner": [...]
      },
      ...
    } */
);

-- PANTRY / INVENTORY
CREATE TABLE pantry_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    ingredient      VARCHAR(100),
    category        VARCHAR(50),            -- "dal|spice|grain|dairy|vegetable|oil"
    quantity        DECIMAL,
    unit            VARCHAR(20),
    reorder_level   DECIMAL,               -- trigger reorder when below this
    last_updated    TIMESTAMP DEFAULT now()
);

-- GROCERY LISTS
CREATE TABLE grocery_lists (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    meal_plan_id    UUID REFERENCES meal_plans(id),
    created_at      TIMESTAMP DEFAULT now(),
    status          VARCHAR(20),            -- "pending|ordered|delivered"
    items           JSONB,
    /* items example:
    [
      {"ingredient": "masoor dal", "quantity": 500, "unit": "g",
       "in_pantry": 200, "to_buy": 300, "platform": "bigbasket",
       "product_link": "https://bigbasket.com/..."}
    ] */
    ordered_via     VARCHAR(30),            -- "bigbasket|zepto|blinkit|manual"
    ordered_at      TIMESTAMP
);

-- STAFF
CREATE TABLE staff (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    name            VARCHAR(100),
    role            VARCHAR(30),            -- "cook|maid|driver|gardener"
    phone           VARCHAR(15),            -- WhatsApp number
    language        VARCHAR(30),            -- "hindi|marathi|kannada|..."
    days_of_week    TEXT[],                 -- ["monday", "tuesday", "wednesday", ...]
    start_time      TIME,
    end_time        TIME,
    monthly_wage    DECIMAL,
    joining_date    DATE,
    status          VARCHAR(20)             -- "active|on_leave|terminated"
);

-- STAFF ATTENDANCE
CREATE TABLE staff_attendance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id        UUID REFERENCES staff(id),
    date            DATE,
    status          VARCHAR(20),            -- "present|absent|half_day|holiday"
    marked_at       TIMESTAMP,
    note            TEXT
);

-- COOK INSTRUCTIONS (daily briefings)
CREATE TABLE cook_instructions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id    UUID REFERENCES households(id),
    staff_id        UUID REFERENCES staff(id),
    date            DATE,
    meal_plan_day   JSONB,                  -- the day's meals
    instruction_text TEXT,                  -- generated WhatsApp message
    instruction_hindi TEXT,                 -- Hindi version
    sent_at         TIMESTAMP,
    whatsapp_msg_id VARCHAR(100),           -- Twilio/Meta message ID
    status          VARCHAR(20)             -- "generated|sent|delivered|read"
);
```

---

## 4. THE DIETARY CONSTRAINT ENGINE

This is the most complex technical component. It must solve:

**Input:** Household dietary matrix + upcoming festival + date + member preferences
**Output:** List of valid recipes for that day + constraints applied

### Constraint Priority Order
```
1. ALLERGY          → Hard block (never suggest)
2. RELIGION         → Hard block (halal, no beef, no root veg)
3. FESTIVAL         → Temporary hard block for festival duration
4. FASTING DAY      → Restrict to specific fasting-safe foods
5. BASE DIET        → Filter by vegetarian/non-veg/vegan/jain
6. DISLIKES         → Soft block (avoid, but can override)
7. SPICE LEVEL      → Preference filter
8. REPEAT RULE      → No same dish within 4 days
9. VARIETY          → Balance across cuisines and courses
```

### Implementation
```python
class DietaryConstraintEngine:
    def __init__(self, household: Household, date: date):
        self.household = household
        self.date = date
        self.festival = self._get_active_festival(date)
        self.member_profiles = household.get_diet_profiles()

    def get_valid_recipes(self, meal_type: str, course: str) -> list[Recipe]:
        """
        Returns recipes valid for ALL household members on this date.
        Uses intersection of constraints (most restrictive member wins).
        """
        base_query = Recipe.objects.filter(
            meal_type=meal_type,
            course=course
        )

        # Apply constraints in priority order
        constraints = self._build_constraint_set()
        filtered = self._apply_constraints(base_query, constraints)

        # Apply repeat rule (no same dish in last 4 days)
        recent = self._get_recent_dishes(days=4)
        filtered = filtered.exclude(id__in=recent)

        return filtered.order_by('?')[:20]  # return top 20 candidates

    def _build_constraint_set(self) -> dict:
        """
        Merge constraints from all household members.
        Most restrictive wins (intersection, not union).
        """
        constraints = {
            "exclude_ingredients": set(),
            "required_diet_tags": set(),
            "festival_restrictions": {},
        }

        for member in self.member_profiles:
            # Add member's allergies and dislikes
            constraints["exclude_ingredients"].update(member.allergies)

            # Jain overrides all: no root veg
            if member.base_diet == "jain":
                constraints["exclude_ingredients"].update(
                    ["onion", "garlic", "potato", "carrot", "ginger",
                     "radish", "beet", "turnip"]
                )

            # Vegetarian overrides non-veg for that meal
            if member.base_diet == "vegetarian":
                constraints["required_diet_tags"].add("vegetarian")

            # Festival restrictions
            if self.festival:
                festival_rules = self.festival.restrictions
                if festival_rules.get("no_meat"):
                    constraints["required_diet_tags"].add("vegetarian")
                if festival_rules.get("no_onion"):
                    constraints["exclude_ingredients"].add("onion")
                if festival_rules.get("no_garlic"):
                    constraints["exclude_ingredients"].add("garlic")

        return constraints
```

---

## 5. MEAL PLANNING ENGINE

### Weekly Plan Generation Algorithm

```python
class WeeklyMealPlanner:
    def generate(self, household: Household, week_start: date) -> MealPlan:
        plan = {}
        used_recipes = set()

        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)
            engine = DietaryConstraintEngine(household, current_date)

            day_plan = {}

            # BREAKFAST (single dish or two items)
            breakfast = self._select_recipe(
                engine, "breakfast", "main", used_recipes,
                max_cook_time=20  # quick breakfast
            )
            day_plan["breakfast"] = [breakfast]
            used_recipes.add(breakfast.id)

            # LUNCH (Indian thali: main + side + bread/rice)
            lunch_main = self._select_recipe(engine, "lunch", "main", used_recipes)
            lunch_side = self._select_recipe(
                engine, "lunch", "side", used_recipes,
                complement=lunch_main  # ensure dal+dry sabzi or gravy+dry
            )
            lunch_bread = self._select_bread_or_rice(engine, household.preferences)
            day_plan["lunch"] = [lunch_main, lunch_side, lunch_bread]
            used_recipes.update([lunch_main.id, lunch_side.id])

            # DINNER (lighter than lunch typically)
            dinner = self._generate_dinner(engine, used_recipes, day_offset)
            day_plan["dinner"] = dinner

            plan[current_date.strftime("%A").lower()] = day_plan

        # AI enhancement pass: ask Gemini to review and improve
        plan = self._ai_enhance(plan, household)

        return MealPlan(household=household, week_start=week_start, meals=plan)

    def _ai_enhance(self, plan: dict, household: Household) -> dict:
        """
        Pass the rule-generated plan through Gemini for:
        - Variety check (too much paneer? Too much dal?)
        - Nutritional balance check
        - Seasonal appropriateness
        - Cuisine rotation (not 5 days of north Indian)
        """
        prompt = f"""
        Review this weekly meal plan for an Indian household.
        Household profile: {household.summary()}
        Current plan: {json.dumps(plan)}

        Check for:
        1. Protein variety (not same dal 3 days running)
        2. Cuisine variety (mix North/South/regional)
        3. Nutritional balance (enough vegetables, not too heavy)
        4. Seasonal appropriateness (current season: {self._get_season()})

        Return improved plan in same JSON format with brief reason for any changes.
        """
        # Gemini call
        response = gemini_client.generate(prompt, schema=MealPlanSchema)
        return response.plan
```

---

## 6. WHATSAPP INTEGRATION

### Architecture
```
User approves meal plan in app
    → Instruction Generator creates cook message
    → Message queued in Celery
    → Celery sends via Twilio WhatsApp API at 7:00 AM daily
    → Delivery status webhook updates cook_instructions table
    → Cook replies → routed back to Priya via app
```

### Message Format (Cook — Hindi)
```
🍽️ आज का खाना - {date} ({day_hindi})

🌅 नाश्ता: {breakfast}

☀️ दोपहर का खाना:
  • {lunch_main}
  • {lunch_side}
  • {bread_type}

🌙 रात का खाना:
  • {dinner}

📦 आज जरूरी सामान: {missing_ingredients_if_any}

कोई सवाल हो तो जवाब दें। — M
```

### Message Format (Priya — English)
```
Good morning! 🌅 Today's household briefing:

🍳 Meals planned for today
  Breakfast: Poha
  Lunch: Dal Makhani + Aloo Gobhi + Roti
  Dinner: Rajma + Chawal

👩‍🍳 Cook: Sunita arrives at 8 AM ✓
🛒 3 items needed: onions, curd, green chilies
   → Add to Zepto cart

[View full week] [Edit today's meals] [Order groceries]
```

### Cook Onboarding (no app download required)
```
Step 1: Priya enters cook's WhatsApp number in app
Step 2: M sends cook a WhatsApp message:
        "Namaste! Main M hoon. {Priya_name} ke ghar ka sahayak.
         Aapko rozana subah khane ki list yahan bhejunga.
         Reply karein: HAAN (agree) ya NAHI (disagree)"
Step 3: Cook replies HAAN → enrolled
Step 4: Cook starts receiving daily morning messages
```

---

## 7. GROCERY INTEGRATION

### Phase 1: Deep Links (MVP — no API needed)
```python
def generate_grocery_deeplinks(items: list[GroceryItem]) -> dict:
    """
    Generate platform-specific deep links for grocery items.
    No API key needed — affiliate links.
    """
    links = {}
    for item in items:
        # BigBasket search deep link
        bb_query = urllib.parse.quote(item.ingredient)
        links[item.ingredient] = {
            "bigbasket": f"https://www.bigbasket.com/ps/?q={bb_query}",
            "zepto": f"https://zeptonow.com/search?query={bb_query}",
            "blinkit": f"https://blinkit.com/s/?q={bb_query}"
        }
    return links
```

### Phase 2: BigBasket Scraper (Month 2)
```python
# Use agent-browser (already installed) to scrape BigBasket product catalogue
# Map ingredients → BBSKUs → store in grocery_products table
# Update prices weekly via scheduled Nakula job
```

### Pantry → Grocery Logic
```
For each ingredient in this week's meal plan:
    required_quantity = sum(recipe_quantities × servings)
    in_pantry = pantry_items.get(ingredient).quantity
    to_buy = max(0, required_quantity - in_pantry)

    if to_buy > 0:
        add to grocery list with best_platform recommendation
```

---

## 8. FESTIVAL CALENDAR DATABASE

### Structure (JSON, static, built once)
```json
{
  "2026": [
    {
      "name": "Navratri",
      "name_hindi": "नवरात्रि",
      "start_date": "2026-10-02",
      "end_date": "2026-10-11",
      "religions": ["hindu"],
      "regions": ["all_india"],
      "fasting_type": "one_meal_or_fruits",
      "restrictions": {
        "no_meat": true,
        "no_fish": true,
        "no_eggs": true,
        "no_onion": true,
        "no_garlic": true,
        "no_alcohol": true,
        "no_regular_grains": true,
        "allowed_grains": ["kuttu", "sabudana", "sama rice", "singhara"],
        "allowed_foods": ["fruits", "milk", "curd", "paneer", "sweet potato",
                         "colocasia", "sabudana khichdi", "kuttu puri"]
      },
      "special_dishes": ["sabudana khichdi", "kuttu ki puri", "aloo ki sabzi",
                        "makhana kheer", "banana halwa"],
      "notes": "Variations exist — some fast completely, some eat one meal"
    },
    {
      "name": "Eid ul-Fitr",
      "start_date": "2026-03-20",
      "religions": ["islam"],
      "restrictions": {
        "halal_only": true,
        "no_pork": true
      },
      "special_dishes": ["biryani", "sheer khurma", "sewaiyan", "nihari",
                        "haleem", "kebabs"]
    }
    // ... 18 more festivals
  ]
}
```

---

## 9. API ENDPOINTS

### Household
```
POST   /api/v1/households                    — create household
GET    /api/v1/households/{id}               — get household
PUT    /api/v1/households/{id}/preferences   — update preferences
POST   /api/v1/households/{id}/members       — add member
PUT    /api/v1/households/{id}/members/{mid} — update member diet profile
```

### Meal Planning
```
POST   /api/v1/meal-plans/generate           — generate weekly plan (AI)
GET    /api/v1/meal-plans/{id}               — get meal plan
PUT    /api/v1/meal-plans/{id}/approve       — approve plan
PUT    /api/v1/meal-plans/{id}/meals/{day}   — edit a day's meals
GET    /api/v1/recipes/suggest               — suggest recipes with filters
```

### Grocery
```
GET    /api/v1/grocery-lists/from-plan/{plan_id}  — generate from meal plan
PUT    /api/v1/grocery-lists/{id}/items/{iid}     — update item quantity
GET    /api/v1/grocery-lists/{id}/links           — get platform deep links
POST   /api/v1/grocery-lists/{id}/order           — mark as ordered
```

### Staff
```
POST   /api/v1/staff                         — add staff member
GET    /api/v1/staff/{id}                    — get staff
POST   /api/v1/staff/{id}/attendance         — mark attendance
PUT    /api/v1/staff/{id}/absence            — log absence + reschedule
GET    /api/v1/staff/{id}/schedule           — get week schedule
```

### Cook Communication
```
POST   /api/v1/cook-instructions/generate    — generate today's message
POST   /api/v1/cook-instructions/{id}/send   — send via WhatsApp
GET    /api/v1/cook-instructions/today       — get today's instruction
```

### Webhooks (incoming)
```
POST   /webhooks/whatsapp                    — Twilio WhatsApp incoming
POST   /webhooks/bigbasket                   — order status (future)
```

---

## 10. PERFORMANCE REQUIREMENTS

| Operation | Target | Notes |
|---|---|---|
| Meal plan generation | < 5s | Gemini call + constraint engine |
| Grocery list generation | < 2s | DB query + pantry diff |
| WhatsApp message delivery | < 30s | Async via Celery |
| API response (typical) | < 200ms | Cached where possible |
| Recipe search | < 100ms | PostgreSQL full-text search |

---

## 11. SECURITY AND PRIVACY

- All household data encrypted at rest (PostgreSQL TDE)
- WhatsApp phone numbers hashed in logs
- No household meal data sold or used for training without explicit consent
- Cook's WhatsApp number stored encrypted
- Auth: JWT with 7-day refresh tokens
- Rate limiting: 100 req/min per user via Redis
- GDPR/PDPB (India) compliant data deletion on request

---

## 12. BUILD PHASES

### Phase 1 — Core Loop (Weeks 1-4)
- [ ] Household + member + diet profile models
- [ ] Festival calendar database (20 festivals, 2026-2027)
- [ ] Indian recipe database (6,500 from Kaggle + cleaned)
- [ ] Dietary constraint engine
- [ ] Basic meal plan generation
- [ ] WhatsApp integration (Twilio sandbox)
- [ ] Cook instruction generator (Hindi)

### Phase 2 — Grocery (Weeks 5-6)
- [ ] Pantry tracker
- [ ] Ingredient extraction from recipes
- [ ] Grocery list generation
- [ ] BigBasket/Zepto deep links

### Phase 3 — Staff Management (Weeks 7-8)
- [ ] Staff profiles + schedules
- [ ] Attendance tracking
- [ ] Absence notification flow
- [ ] SOP templates

### Phase 4 — Intelligence Layer (Weeks 9-12)
- [ ] Meal plan learning (feedback loop)
- [ ] Pantry image recognition (Gemini Vision)
- [ ] Nutritional analysis
- [ ] Guest occasion planning
