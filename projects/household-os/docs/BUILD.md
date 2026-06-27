# BUILD.md — Household OS
## Phase-by-Phase Build Plan
> Version: 1.0 | Date: June 25, 2026 | Author: Kartavya Joshi
> Depends on: PERSONAS.md, ERD.md, TRD.md, DATASET-PLAN.md

---

## BUILD PHILOSOPHY

**One persona at a time. Ship it. Use it. Then expand.**

Build order: Solo → Bachelors → Solo Parent → Girls Flat → Joint Family
Reason: complexity increases in this order. Each persona validates the core loop
before adding the next layer of complexity.

```
PHASE 0  Foundation         (Week 1-2)   — project setup, database, datasets
PHASE 1  Persona 5: Solo    (Week 3-4)   — core loop: meal plan → grocery list
PHASE 2  Persona 2: Bachelors (Week 5-6) — adds: multi-person, budget tracking
PHASE 3  Persona 3: Solo Parent (Week 7-8) — adds: child profile, tiffin planner
PHASE 4  Persona 4: Girls Flat (Week 9-10) — adds: rotation, cost splitting
PHASE 5  Persona 1: Joint Family (Week 11-12) — adds: cook, WhatsApp, festival
PHASE 6  Polish + Deploy    (Week 13)    — deployment, monitoring, onboarding
```

---

## PHASE 0 — FOUNDATION
**Week 1-2 | Goal: Project skeleton + datasets loaded + DB seeded**

### 0.1 Project Setup
```bash
# Create project structure
mkdir -p household-os/{backend,frontend,data,scripts,tests}
cd household-os

# Backend setup
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic redis celery
pip install google-generativeai groq httpx python-dotenv pillow

# Database
# Install PostgreSQL 16 locally or use Railway.app free tier
# Redis via Docker: docker run -d -p 6379:6379 redis:7

# Frontend setup (later)
# cd ../frontend && npx create-next-app@latest . --typescript --tailwind
```

### 0.2 Database Setup
```bash
# Initialize Alembic for migrations
alembic init migrations

# Create tables in order (respecting FK dependencies):
# 1. users
# 2. diet_profiles
# 3. households
# 4. household_members
# 5. household_preferences
# 6. ingredients_master
# 7. recipes
# 8. recipe_ingredients
# 9. festival_calendar
# 10. meal_plans
# 11. pantry_items
# 12. grocery_lists, grocery_items
# 13. staff
# 14. staff_attendance
# 15. cook_instructions
# 16. meal_feedback
# 17. grocery_products

# Run migration
alembic upgrade head
```

### 0.3 Dataset Loading (Week 1)
```bash
# Run in order — each script depends on the previous

python scripts/01_download_sources.sh        # Download Kaggle + GitHub recipes
python scripts/02_build_recipe_db.py         # Merge + deduplicate
python scripts/03_enrich_recipes.py          # AI enrichment (Groq — free)
python scripts/04_build_ingredients.py       # Ingredient master list with flags
python scripts/05_build_festival_calendar.py # 20+ festivals, 2026-2028
python scripts/09_validate_all.py            # Quality checks
python scripts/10_load_to_postgres.py        # Seed the database
```

**Validation gates before moving to Phase 1:**
- [ ] `recipes` table has > 5,000 rows
- [ ] All recipes have `is_vegetarian`, `has_onion`, `has_garlic` populated
- [ ] `festival_calendar` has ≥ 18 festivals for 2026
- [ ] `ingredients_master` has ≥ 500 rows with dietary flags
- [ ] DB responds to basic queries in < 100ms

### 0.4 Environment Setup
```python
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/householdos
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid    # for WhatsApp (Phase 5)
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886   # Twilio sandbox
SECRET_KEY=your_jwt_secret
```

---

## PHASE 1 — PERSONA 5: SOLO BACHELOR/BACHELORETTE
**Week 3-4 | "Kartavya's meal planner"**
**Goal: Core loop working end-to-end for 1 person**

### What gets built
```
User registration + phone auth
    ↓
Household setup (type: solo, 1 member, diet profile)
    ↓
Weekly meal plan generation (AI, constraint-aware)
    ↓
Grocery list from meal plan (ingredient extraction)
    ↓
Grocery deep links (BigBasket/Zepto)
    ↓
Basic web UI to view plan + list
```

### Task breakdown

**Backend (Week 3)**

```
[ ] POST /api/v1/auth/send-otp        (phone-based auth)
[ ] POST /api/v1/auth/verify-otp
[ ] POST /api/v1/households            (create household, type: solo)
[ ] POST /api/v1/households/{id}/members
[ ] PUT  /api/v1/diet-profiles/{id}    (set vegetarian/non-veg, restrictions)
[ ] POST /api/v1/meal-plans/generate   (the core AI call)
[ ] GET  /api/v1/meal-plans/{id}
[ ] PUT  /api/v1/meal-plans/{id}/meals/{day}  (edit a day)
[ ] GET  /api/v1/grocery-lists/from-plan/{plan_id}
[ ] GET  /api/v1/grocery-lists/{id}/links
```

**Meal Plan Generation — Core Algorithm (Week 3)**

```python
# backend/services/meal_planner.py

class MealPlannerService:

    async def generate_weekly_plan(
        self,
        household: Household,
        week_start: date
    ) -> MealPlan:

        # Step 1: Build constraint set for this household
        constraint_engine = DietaryConstraintEngine(household, week_start)
        constraints = constraint_engine.build_constraints()

        # Step 2: Check for active festivals this week
        festivals = await self.festival_repo.get_active(
            start=week_start,
            end=week_start + timedelta(days=6),
            religions=household.get_all_religions()
        )

        # Step 3: Get recently used recipes (avoid repeats)
        recent_recipes = await self.meal_plan_repo.get_recent_recipe_ids(
            household_id=household.id,
            days=14
        )

        # Step 4: Generate day-by-day plan
        plan = {}
        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)
            day_festival = next(
                (f for f in festivals
                 if f.start_date <= current_date <= f.end_date),
                None
            )

            day_constraints = constraints.copy()
            if day_festival:
                day_constraints = constraint_engine.apply_festival(
                    day_constraints, day_festival
                )

            plan[current_date.strftime('%A').lower()] = {
                'date': current_date.isoformat(),
                'festival': day_festival.name if day_festival else None,
                'breakfast': await self._select_meal(
                    meal_type='breakfast',
                    constraints=day_constraints,
                    exclude_ids=recent_recipes,
                    max_time=20
                ),
                'lunch': await self._select_thali(
                    constraints=day_constraints,
                    exclude_ids=recent_recipes,
                    household_prefs=household.preferences
                ),
                'dinner': await self._select_dinner(
                    constraints=day_constraints,
                    exclude_ids=recent_recipes,
                    lighter=True
                )
            }

        # Step 5: AI enhancement pass
        plan = await self._ai_enhance(plan, household, festivals)

        return await self.meal_plan_repo.create(
            household_id=household.id,
            week_start=week_start,
            meals=plan,
            generated_by='ai'
        )

    async def _select_thali(self, constraints, exclude_ids, household_prefs):
        """
        Indian lunch = thali: main + side + bread/rice (+ optional raita)
        Ensure complementary courses (dal + dry sabzi, not 2 gravies)
        """
        main = await self._select_meal(
            meal_type='lunch', course='main',
            constraints=constraints, exclude_ids=exclude_ids
        )

        # If main is a dal, pick a dry sabzi as side
        # If main is a gravy, can pick another gravy or a dal
        side_course = 'side'
        if main and main.dish_type == 'dal':
            side_constraints = {**constraints, 'dish_type__in': ['dry_sabzi']}
        else:
            side_constraints = constraints

        side = await self._select_meal(
            meal_type='lunch', course='side',
            constraints=side_constraints,
            exclude_ids=exclude_ids + ([main.id] if main else [])
        )

        bread = await self._select_bread(household_prefs)

        return [c for c in [main, side, bread] if c]
```

**Grocery List Generation (Week 3)**

```python
# backend/services/grocery_service.py

class GroceryService:

    async def generate_from_meal_plan(
        self,
        meal_plan: MealPlan,
        household: Household
    ) -> GroceryList:

        # Step 1: Extract all ingredients needed this week
        required = defaultdict(lambda: {'quantity': 0, 'unit': ''})

        for day, day_meals in meal_plan.meals.items():
            for meal_slot in ['breakfast', 'lunch', 'dinner']:
                recipes = day_meals.get(meal_slot, [])
                if isinstance(recipes, dict):
                    recipes = [recipes]

                for recipe_ref in recipes:
                    recipe = await self.recipe_repo.get(recipe_ref['recipe_id'])
                    ingredients = await self.recipe_ingredient_repo.get_for_recipe(
                        recipe.id
                    )
                    for ing in ingredients:
                        # Scale to household serving size
                        scaled_qty = ing.quantity * (
                            household.preferences.servings_per_meal / recipe.servings
                        )
                        required[ing.ingredient_id]['quantity'] += scaled_qty
                        required[ing.ingredient_id]['unit'] = ing.unit

        # Step 2: Check pantry — what do we already have?
        pantry = await self.pantry_repo.get_for_household(household.id)
        pantry_map = {item.ingredient_id: item for item in pantry}

        # Step 3: Calculate what to buy
        to_buy = []
        for ing_id, needed in required.items():
            in_pantry = pantry_map.get(ing_id)
            in_pantry_qty = in_pantry.quantity if in_pantry else 0

            buy_qty = max(0, needed['quantity'] - in_pantry_qty)
            if buy_qty > 0:
                ingredient = await self.ingredient_repo.get(ing_id)
                to_buy.append({
                    'ingredient_id': ing_id,
                    'ingredient_name': ingredient.name,
                    'required_qty': needed['quantity'],
                    'in_pantry_qty': in_pantry_qty,
                    'to_buy_qty': buy_qty,
                    'unit': needed['unit'],
                    'platform_link': self._get_deeplink(
                        ingredient.bigbasket_keyword,
                        household.preferences.preferred_grocery_app
                    )
                })

        return await self.grocery_repo.create(
            household_id=household.id,
            meal_plan_id=meal_plan.id,
            items=to_buy
        )
```

**Frontend (Week 4)**

```
[ ] /onboarding    — household type picker + member setup + diet profile
[ ] /plan          — weekly meal plan grid (7 days × 3 meals)
[ ] /plan/edit     — swap a single dish
[ ] /grocery       — shopping list with checkboxes + platform links
[ ] /profile       — household settings
```

**Solo-specific features:**
```
[ ] "Cooking for 1" quantity scaling (halve all ingredient quantities)
[ ] Beginner recipe filter (max 20 min, max 5 ingredients)
[ ] Zomato spend comparison widget ("This week's plan = ₹420 vs ₹4,200 on Swiggy")
[ ] Fridge rescue: "What can I make with X, Y, Z?"
```

**Phase 1 done when:**
- [ ] Kartavya can sign up, set up his household, get a 7-day meal plan
- [ ] Meal plan respects his dietary preferences
- [ ] Grocery list generates with BigBasket deep links
- [ ] Can edit a single day's meals
- [ ] UI is functional (not beautiful yet)

---

## PHASE 2 — PERSONA 2: TWO BACHELORS
**Week 5-6 | Rohan & Arjun's flat**
**Adds: multi-person, separate dietary tracks, grocery splitting, budget tracker**

### New capabilities
```
[ ] Multi-member household (2 people, different diets)
[ ] Separate meal tracks per person for non-shared meals
    (Rohan's chicken dinner ≠ Arjun's veg dinner)
[ ] Grocery cost splitting (₹ per person)
[ ] Budget mode: "5 dinners under ₹1,000 total"
[ ] Weekly spend comparison: home cooking vs estimated Swiggy
[ ] Shared grocery list with "bought by" tracking
```

### New API endpoints
```
[ ] POST /api/v1/households/{id}/preferences/budget-mode
[ ] GET  /api/v1/grocery-lists/{id}/split     — cost split per member
[ ] GET  /api/v1/analytics/spend-comparison   — home vs delivery estimate
[ ] POST /api/v1/meal-plans/{id}/member-override  — member-specific meal
```

### Key data challenge: split dietary tracks
```python
# When household has member A (veg) + member B (non-veg):
# Lunch: both eat the same veg meal (easy)
# Dinner: A wants dal-roti, B wants chicken-roti
# Solution: generate SHARED meals for shared slots
#           generate SEPARATE recommendations for divergent slots

async def generate_split_plan(household, week_start):
    # Find common dietary ground (intersection)
    shared_constraints = get_shared_constraints(household.members)

    # For each day/meal:
    # If all members can eat the same thing → shared meal
    # If dietary conflict → separate tracks with note

    for day in week:
        lunch = select_from_shared_constraints()  # always shared
        dinner = maybe_split_by_diet()  # veg + non-veg option
```

---

## PHASE 3 — PERSONA 3: SOLO PARENT + CHILD
**Week 7-8 | Priya & Aarav**
**Adds: child profile, school tiffin planner, under-30-min filter, Aarav-approved tags**

### New capabilities
```
[ ] Child member profile with "picky eater" settings
[ ] School tiffin planner (5-day, what Aarav will actually eat)
[ ] Tiffin-specific recipe category (non-messy, finger food, no curry)
[ ] Quick dinner filter: under 30 minutes (tired parent mode)
[ ] "Aarav-approved" recipe tag (user-curated, grows over time)
[ ] Separate meal generation: Priya's healthy + Aarav's preferred
[ ] Nutrition check: "Did Aarav get vegetables this week?"
```

### New API endpoints
```
[ ] POST /api/v1/meal-plans/generate/tiffin   — 5-day tiffin plan
[ ] PUT  /api/v1/recipes/{id}/child-approve   — mark as child-approved
[ ] GET  /api/v1/meal-plans/filters/quick     — under-30-min meals
[ ] GET  /api/v1/analytics/child-nutrition    — weekly nutrition for child
```

### Tiffin planner logic
```python
TIFFIN_RULES = {
    'not_messy': True,          # no dripping curries in a box
    'no_refrigeration': True,   # holds fine at room temp for 4 hours
    'finger_food_preferred': True,
    'max_components': 2,        # box shouldn't have 5 containers
    'school_policy': 'no_junk', # no chips, no chocolate
    'child_approved_only': True  # only from approved list
}

TIFFIN_IDEAS = [
    "paratha + curd",
    "idli + sambar (in thermos)",
    "sandwich (butter + cucumber + cheese)",
    "curd rice + papad",
    "vegetable poha",
    "fruit box + crackers",
    "paneer roll (paratha + paneer bhurji)",
]
```

---

## PHASE 4 — PERSONA 4: THREE GIRLS FLAT
**Week 9-10 | Anika, Rhea & Meghna**
**Adds: cooking rotation, grocery cost splitting, health mode toggle, pantry tracker**

### New capabilities
```
[ ] Cooking rotation tracker (whose turn, what they made, rating)
[ ] Flat WhatsApp group integration ("What's for dinner" → M decides)
[ ] Grocery cost splitting with Splitwise-style settlement
[ ] Individual health mode toggle (Meghna's keto/IF/regular switching)
[ ] Pantry image recognition (take photo → M identifies ingredients)
[ ] "What can we make with what's in the fridge?" feature
[ ] Budget: per-person food spend tracker
```

### New API endpoints
```
[ ] POST /api/v1/households/{id}/cooking-rotation
[ ] GET  /api/v1/households/{id}/cooking-rotation/tonight
[ ] POST /api/v1/households/{id}/members/{mid}/health-mode
[ ] GET  /api/v1/pantry/suggestions    — recipes from current pantry
[ ] POST /api/v1/pantry/photo-scan     — Gemini Vision ingredient detection
[ ] GET  /api/v1/grocery-lists/{id}/settle  — who owes what
```

### Grocery splitting logic
```python
class GrocerySettlement:
    def calculate(self, grocery_list: GroceryList) -> dict:
        """
        Items can be:
        - shared equally (milk, oil, spices)
        - per-person (Rhea buys chicken, Anika buys soy milk)
        """
        shared_items = [i for i in grocery_list.items if i.shared]
        personal_items = [i for i in grocery_list.items if not i.shared]

        shared_per_person = sum(i.price for i in shared_items) / 3

        settlement = {}
        for member in household.members:
            personal = sum(i.price for i in personal_items
                          if i.bought_by == member.id)
            settlement[member.name] = shared_per_person + personal

        return settlement
```

---

## PHASE 5 — PERSONA 1: JOINT FAMILY
**Week 11-12 | The Sharma Household**
**Adds: WhatsApp cook communication, festival mode, multi-generation diet, guest mode**

### New capabilities
```
[ ] Staff management (cook, maid profiles)
[ ] WhatsApp cook instruction (Twilio sandbox → real API)
[ ] Multi-generation dietary profiles (Dadi's Ekadashi, son's non-veg)
[ ] Festival mode: auto-switch meal plan for Navratri/Diwali etc.
[ ] Guest mode: "8 people for dinner Saturday, 2 are Jain"
[ ] Bulk serving size scaling (cook for 8)
[ ] SOP library for cook (dish-specific household preferences)
[ ] Attendance tracking + absence alerts
```

### WhatsApp cook instruction flow
```python
async def send_morning_brief(household_id: UUID, date: date):
    household = await repo.get(household_id)
    meal_plan = await repo.get_active_plan(household_id, date)
    staff = await repo.get_active_cook(household_id)

    if not staff or not staff.whatsapp_opted_in:
        return

    day_meals = meal_plan.meals.get(date.strftime('%A').lower())

    # Generate Hindi message
    message = await instruction_generator.create(
        meals=day_meals,
        language=staff.language,
        cook_name=staff.name,
        household_prefs=household.preferences
    )

    # Send via Twilio
    twilio_client.messages.create(
        from_=f"whatsapp:{TWILIO_FROM}",
        to=f"whatsapp:{staff.phone}",
        body=message
    )

    # Save instruction record
    await repo.create_cook_instruction(
        household_id=household_id,
        staff_id=staff.id,
        date=date,
        instruction_hindi=message,
        status='sent'
    )
```

---

## PHASE 6 — POLISH + DEPLOY
**Week 13**

### Deployment
```bash
# Backend: Railway.app
railway login
railway init household-os-api
railway add --database postgresql
railway add --redis
railway up

# Frontend: Vercel
vercel deploy

# Domain (later): householdos.in or getm-clone.in
```

### Monitoring setup
```bash
# Error tracking
pip install sentry-sdk
SENTRY_DSN=your_dsn

# Observability (already have Langfuse)
# Add to team_coordinator.py for AI meal planning traces

# Uptime monitoring: UptimeRobot (free tier, checks every 5 min)
```

### Onboarding polish
```
[ ] 5-question onboarding (household type → members → dietary setup → done)
[ ] First meal plan generated in < 30 seconds
[ ] Empty state: if no pantry data, assume pantry is empty (conservative)
[ ] Demo mode: show a sample Sharma family plan without signup
```

---

## FILE STRUCTURE

```
household-os/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app entry
│   │   ├── config.py
│   │   ├── database.py          ← Async PostgreSQL connection
│   │   ├── models/              ← SQLAlchemy ORM models
│   │   │   ├── household.py
│   │   │   ├── recipe.py
│   │   │   ├── meal_plan.py
│   │   │   ├── grocery.py
│   │   │   └── staff.py
│   │   ├── schemas/             ← Pydantic request/response models
│   │   ├── routers/             ← FastAPI route handlers
│   │   │   ├── auth.py
│   │   │   ├── households.py
│   │   │   ├── meal_plans.py
│   │   │   ├── grocery.py
│   │   │   └── staff.py
│   │   ├── services/            ← Business logic
│   │   │   ├── meal_planner.py  ← Core algorithm
│   │   │   ├── constraint_engine.py
│   │   │   ├── grocery_service.py
│   │   │   ├── whatsapp_service.py
│   │   │   └── ai_service.py
│   │   └── repositories/        ← DB queries
│   ├── migrations/              ← Alembic migrations
│   ├── tests/
│   │   ├── test_meal_planner.py
│   │   ├── test_constraints.py
│   │   └── test_grocery.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                 ← Next.js app router
│   │   │   ├── onboarding/
│   │   │   ├── plan/
│   │   │   ├── grocery/
│   │   │   └── settings/
│   │   ├── components/
│   │   └── lib/
│   └── package.json
├── data/
│   ├── raw/
│   ├── processed/
│   └── validation/
├── scripts/
│   ├── 01_download_sources.sh
│   ├── 02_build_recipe_db.py
│   ├── 03_enrich_recipes.py
│   ├── 04_build_ingredients.py
│   ├── 05_build_festival_calendar.py
│   ├── 09_validate_all.py
│   └── 10_load_to_postgres.py
└── docs/
    ├── RESEARCH.md
    ├── PRD.md
    ├── TRD.md
    ├── ERD.md
    ├── PERSONAS.md
    ├── DATASET-PLAN.md
    └── BUILD.md               ← this file
```

---

## WHAT WE BUILD FIRST TOMORROW

```
DAY 1 (today/tomorrow):
  1. Create project folder structure
  2. Set up FastAPI + PostgreSQL + Alembic
  3. Write migration for: users, diet_profiles, households, household_members
  4. Download Kaggle recipe dataset
  5. Run first enrichment script (100 recipes as test batch)

DAY 2:
  6. Complete recipe database enrichment (all 6,500)
  7. Build ingredient master list
  8. Write festival calendar (2026-2027)
  9. Load all to PostgreSQL
  10. Validate: query recipes by dietary constraint

DAY 3-4 (Phase 1 backend begins):
  11. Auth endpoints (OTP via SMS/WhatsApp)
  12. Household + member creation
  13. Diet profile setup
  14. Dietary constraint engine (core algorithm)
  15. First meal plan generation test

DAY 5:
  16. Grocery list generation
  17. Deep links for BigBasket/Zepto
  18. Basic API testing with Postman/curl
```
