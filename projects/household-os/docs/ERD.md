# ERD — Household OS
## Entity Relationship Document
> Version: 1.0 | Date: June 25, 2026 | Author: Kartavya Joshi
> Depends on: TRD.md, PRD.md

---

## 1. ENTITY MAP (Visual Overview)

```
┌──────────┐     ┌─────────────────┐     ┌──────────────┐
│  users   │────<│household_members│>────│ diet_profiles│
└──────────┘     └─────────────────┘     └──────────────┘
     │                   │
     │ (primary_user)    │ (belongs to)
     ▼                   ▼
┌──────────────────────────────────────────────────────┐
│                    households                        │
└──────────────────────────────────────────────────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│meal_plans│  │  staff   │  │  pantry  │  │household │
└──────────┘  └──────────┘  │  _items  │  │_prefs    │
     │              │        └──────────┘  └──────────┘
     │              │              │
     ▼              ▼              │
┌──────────┐  ┌──────────┐        │
│grocery   │  │ staff_   │        │
│_lists    │  │attendance│        │
└──────────┘  └──────────┘        │
     │              │              │
     ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│grocery_  │  │ cook_    │  │grocery_  │
│items     │  │instruct- │  │_products │
└──────────┘  │ions      │  └──────────┘
              └──────────┘

┌──────────────────────────────────────────────────────┐
│              REFERENCE DATA (static)                  │
├──────────────┬───────────────┬───────────────────────┤
│  recipes     │ festival_cal  │  ingredients_master   │
└──────────────┴───────────────┴───────────────────────┘
      │
      │ (many-to-many)
      ▼
┌──────────────┐
│recipe_       │
│ingredients   │
└──────────────┘
```

---

## 2. FULL TABLE DEFINITIONS

### AUTHENTICATION & USERS

```sql
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone               VARCHAR(15) UNIQUE NOT NULL,    -- WhatsApp-linked phone
    phone_verified      BOOLEAN DEFAULT false,
    email               VARCHAR(255) UNIQUE,
    name                VARCHAR(100) NOT NULL,
    language            VARCHAR(20) DEFAULT 'en',       -- en|hi|mr|kn|ta|te
    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now(),
    last_active         TIMESTAMP,
    is_active           BOOLEAN DEFAULT true
);

-- Index
CREATE INDEX idx_users_phone ON users(phone);
```

---

### HOUSEHOLDS

```sql
CREATE TABLE households (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(100) NOT NULL,           -- "Sharma Family"
    primary_user_id     UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    city                VARCHAR(50) NOT NULL,            -- "Delhi NCR"
    state               VARCHAR(50),                    -- "Delhi"
    tier                VARCHAR(10) DEFAULT 'tier1',    -- tier1|tier2|tier3
    timezone            VARCHAR(50) DEFAULT 'Asia/Kolkata',
    whatsapp_group_id   VARCHAR(100),                   -- optional WA group
    morning_brief_time  TIME DEFAULT '07:00',           -- when to send daily brief
    cook_brief_time     TIME DEFAULT '07:30',           -- when to send cook message
    onboarding_complete BOOLEAN DEFAULT false,
    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now()
);

-- Index
CREATE INDEX idx_households_primary_user ON households(primary_user_id);
```

---

### HOUSEHOLD MEMBERS

```sql
CREATE TABLE household_members (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    user_id             UUID REFERENCES users(id),      -- NULL if child/non-app member
    name                VARCHAR(100) NOT NULL,
    age                 INTEGER,
    gender              VARCHAR(10),                    -- male|female|other
    role                VARCHAR(30) NOT NULL,           -- primary|spouse|child|parent|other
    diet_profile_id     UUID REFERENCES diet_profiles(id),
    is_active           BOOLEAN DEFAULT true,
    added_at            TIMESTAMP DEFAULT now()
);

-- Indexes
CREATE INDEX idx_hm_household ON household_members(household_id);
CREATE INDEX idx_hm_diet_profile ON household_members(diet_profile_id);
```

---

### DIET PROFILES

```sql
CREATE TABLE diet_profiles (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    VARCHAR(100),               -- "Maa's Diet"

    -- Base classification
    base_diet               VARCHAR(20) NOT NULL,
    -- CHECK: vegetarian|non_vegetarian|vegan|jain|eggetarian|pescatarian

    -- Religion-based restrictions
    religion                VARCHAR(30),               -- hindu|muslim|jain|sikh|christian|other|none
    no_beef                 BOOLEAN DEFAULT false,
    no_pork                 BOOLEAN DEFAULT false,
    no_root_vegetables      BOOLEAN DEFAULT false,     -- Jain: no onion/garlic/potato/carrot etc.
    halal_only              BOOLEAN DEFAULT false,
    kosher_only             BOOLEAN DEFAULT false,

    -- Day-of-week fasting
    fasting_days            JSONB DEFAULT '{}',
    -- Example: {"tuesday": true, "thursday": true}
    -- When fasting_days[day]=true → use festival_calendar fasting rules for that day

    -- Specific fasting types per day
    fasting_type            JSONB DEFAULT '{}',
    -- Example: {"tuesday": "fruits_only", "thursday": "one_meal"}
    -- Types: full_fast|fruits_only|one_meal|no_grains|sattvic

    -- Ingredient-level restrictions
    disliked_ingredients    TEXT[] DEFAULT '{}',       -- ["mushrooms", "bitter gourd"]
    allergies               TEXT[] DEFAULT '{}',       -- ["peanuts", "shellfish"]
    cannot_eat              TEXT[] DEFAULT '{}',       -- hard block, different from allergy

    -- Preferences
    spice_level             VARCHAR(10) DEFAULT 'medium',  -- mild|medium|hot|very_hot
    preferred_cuisines      TEXT[] DEFAULT '{}',       -- ["north_indian", "punjabi"]
    avoided_cuisines        TEXT[] DEFAULT '{}',
    oil_preference          VARCHAR(30),               -- mustard|groundnut|sunflower|ghee

    created_at              TIMESTAMP DEFAULT now(),
    updated_at              TIMESTAMP DEFAULT now()
);

-- Root vegetables list (for Jain restriction)
-- ['onion', 'garlic', 'potato', 'carrot', 'ginger', 'radish',
--  'beet', 'turnip', 'leek', 'spring_onion', 'shallot']
```

---

### HOUSEHOLD PREFERENCES

```sql
CREATE TABLE household_preferences (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id            UUID UNIQUE NOT NULL REFERENCES households(id) ON DELETE CASCADE,

    -- Meal structure
    has_breakfast           BOOLEAN DEFAULT true,
    has_lunch               BOOLEAN DEFAULT true,
    has_dinner              BOOLEAN DEFAULT true,
    has_evening_snack       BOOLEAN DEFAULT false,

    -- Bread preference
    bread_type              VARCHAR(30) DEFAULT 'roti',  -- roti|chapati|paratha|rice|both
    servings_per_meal       INTEGER DEFAULT 4,

    -- Cook preferences
    max_cook_time_breakfast INTEGER DEFAULT 20,          -- minutes
    max_cook_time_lunch     INTEGER DEFAULT 60,
    max_cook_time_dinner    INTEGER DEFAULT 45,

    -- Regional preference
    primary_cuisine_region  VARCHAR(50),                 -- north_indian|south_indian|etc.
    secondary_cuisines      TEXT[] DEFAULT '{}',

    -- Grocery preferences
    preferred_grocery_app   VARCHAR(30) DEFAULT 'bigbasket',  -- bigbasket|zepto|blinkit
    grocery_day             VARCHAR(10) DEFAULT 'saturday',   -- day to do weekly shop
    organic_preferred       BOOLEAN DEFAULT false,

    -- Notification preferences
    notify_meal_plan_ready  BOOLEAN DEFAULT true,
    notify_grocery_list     BOOLEAN DEFAULT true,
    notify_staff_absent     BOOLEAN DEFAULT true,
    notify_pantry_low       BOOLEAN DEFAULT true,

    updated_at              TIMESTAMP DEFAULT now()
);
```

---

### RECIPES (Reference Data)

```sql
CREATE TABLE recipes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(200) NOT NULL,          -- "Dal Makhani"
    name_hindi          VARCHAR(200),                   -- "दाल मखनी"
    name_regional       JSONB DEFAULT '{}',
    -- Example: {"marathi": "डाळ मखनी", "kannada": "ದಾಲ್ ಮಖನಿ"}

    -- Classification
    meal_type           VARCHAR(20) NOT NULL,           -- breakfast|lunch|dinner|snack|dessert
    course              VARCHAR(30) NOT NULL,           -- main|side|bread|rice|raita|salad|dessert
    cuisine_region      VARCHAR(50) NOT NULL,           -- north_indian|south_indian|punjabi|etc.
    dish_type           VARCHAR(30),                    -- curry|dry_sabzi|dal|rice|bread|soup

    -- Dietary tags (denormalized for query speed)
    base_diet           VARCHAR(20) NOT NULL,           -- vegetarian|non_veg|vegan|jain
    is_vegetarian       BOOLEAN NOT NULL DEFAULT true,
    is_vegan            BOOLEAN NOT NULL DEFAULT false,
    is_jain             BOOLEAN NOT NULL DEFAULT false,  -- no root veg
    is_sattvic          BOOLEAN NOT NULL DEFAULT false,  -- no onion/garlic
    is_gluten_free      BOOLEAN NOT NULL DEFAULT false,
    has_dairy           BOOLEAN NOT NULL DEFAULT false,
    has_eggs            BOOLEAN NOT NULL DEFAULT false,
    has_meat            BOOLEAN NOT NULL DEFAULT false,
    has_fish            BOOLEAN NOT NULL DEFAULT false,
    is_halal_friendly   BOOLEAN NOT NULL DEFAULT true,

    -- Festival suitability
    festival_ok         TEXT[] DEFAULT '{}',
    -- Example: ['navratri', 'ekadashi', 'janmashtami']
    festival_exclude    TEXT[] DEFAULT '{}',
    -- Example: ['eid'] -- if needs pork/non-halal

    -- Contains root vegetables? (for Jain)
    has_onion           BOOLEAN DEFAULT false,
    has_garlic          BOOLEAN DEFAULT false,
    has_root_veg        BOOLEAN DEFAULT false,

    -- Time and effort
    prep_time_min       INTEGER NOT NULL DEFAULT 10,
    cook_time_min       INTEGER NOT NULL DEFAULT 20,
    total_time_min      INTEGER GENERATED ALWAYS AS (prep_time_min + cook_time_min) STORED,
    difficulty          VARCHAR(10) DEFAULT 'medium',   -- easy|medium|hard
    servings            INTEGER DEFAULT 4,

    -- Instructions
    instructions        TEXT,                           -- full recipe (English)
    cook_instruction    TEXT,                           -- simplified for cook (brief, English)
    cook_instruction_hi TEXT,                           -- Hindi version for cook

    -- Nutrition (per serving)
    calories            INTEGER,
    protein_g           DECIMAL(5,1),
    carbs_g             DECIMAL(5,1),
    fat_g               DECIMAL(5,1),
    fiber_g             DECIMAL(5,1),

    -- Metadata
    source              VARCHAR(50),                    -- kaggle|manual|user_contributed
    image_url           TEXT,
    popularity_score    INTEGER DEFAULT 0,              -- updated by feedback loop
    season              TEXT[] DEFAULT '{}',            -- ['winter', 'monsoon', 'all']
    tags                TEXT[] DEFAULT '{}',
    -- Example: ['quick', 'popular', 'one_pot', 'leftover_friendly']

    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now(),
    is_active           BOOLEAN DEFAULT true
);

-- Indexes for constraint engine
CREATE INDEX idx_recipes_meal_type ON recipes(meal_type);
CREATE INDEX idx_recipes_diet ON recipes(is_vegetarian, is_vegan, is_jain);
CREATE INDEX idx_recipes_region ON recipes(cuisine_region);
CREATE INDEX idx_recipes_time ON recipes(total_time_min);
CREATE INDEX idx_recipes_tags ON recipes USING GIN(tags);
CREATE INDEX idx_recipes_festival ON recipes USING GIN(festival_ok);
```

---

### RECIPE INGREDIENTS (Junction Table)

```sql
CREATE TABLE recipe_ingredients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id           UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id       UUID NOT NULL REFERENCES ingredients_master(id),
    quantity            DECIMAL(8,2) NOT NULL,
    unit                VARCHAR(20) NOT NULL,
    -- Standard units: g|kg|ml|l|cup|tbsp|tsp|piece|bunch|handful
    unit_household      VARCHAR(30),
    -- Cook-friendly unit: "1 katori"|"2 chammach"|"1 pyaaz"
    is_optional         BOOLEAN DEFAULT false,
    substitutes         TEXT[],                         -- ingredient names that can replace
    preparation_note    VARCHAR(200),
    -- Example: "finely chopped", "soaked overnight", "julienned"

    UNIQUE(recipe_id, ingredient_id)
);

CREATE INDEX idx_ri_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_ri_ingredient ON recipe_ingredients(ingredient_id);
```

---

### INGREDIENTS MASTER (Reference Data)

```sql
CREATE TABLE ingredients_master (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(100) UNIQUE NOT NULL,   -- "masoor dal"
    name_hindi          VARCHAR(100),                   -- "मसूर की दाल"
    name_regional       JSONB DEFAULT '{}',

    -- Classification
    category            VARCHAR(50) NOT NULL,
    -- dal|grain|spice|vegetable|fruit|dairy|oil|meat|fish|egg
    -- condiment|sweetener|nut|herb|flour|preserved
    sub_category        VARCHAR(50),
    -- spice → whole_spice|ground_spice|masala_blend
    -- vegetable → root|leafy|gourd|other
    is_root_vegetable   BOOLEAN DEFAULT false,          -- for Jain constraint
    is_allium           BOOLEAN DEFAULT false,          -- onion, garlic, leek
    is_meat             BOOLEAN DEFAULT false,
    is_seafood          BOOLEAN DEFAULT false,
    is_dairy            BOOLEAN DEFAULT false,
    is_egg              BOOLEAN DEFAULT false,

    -- Pantry tracking
    shelf_life_days     INTEGER,                        -- 0 = use same day (fresh veg)
    storage_type        VARCHAR(20),                    -- fridge|pantry|freezer
    reorder_unit        VARCHAR(20) DEFAULT 'g',        -- standard buying unit
    typical_pack_size   DECIMAL,                        -- 500 (g), 1 (kg), 12 (eggs)

    -- Grocery linking
    bigbasket_keyword   VARCHAR(100),                   -- search term for BB
    zepto_keyword       VARCHAR(100),
    common_brands       TEXT[] DEFAULT '{}',

    created_at          TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_ingredients_category ON ingredients_master(category);
CREATE INDEX idx_ingredients_root_veg ON ingredients_master(is_root_vegetable);
```

---

### FESTIVAL CALENDAR (Reference Data)

```sql
CREATE TABLE festival_calendar (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(100) NOT NULL,          -- "Navratri"
    name_hindi          VARCHAR(100),                   -- "नवरात्रि"
    year                INTEGER NOT NULL,
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,

    -- Applicability
    religions           TEXT[] NOT NULL,                -- ['hindu']|['islam']|['all']
    regions             TEXT[] DEFAULT '{"all_india"}', -- regional festivals
    is_national         BOOLEAN DEFAULT false,

    -- Fasting details
    fasting_type        VARCHAR(30),
    -- full_fast|fruits_only|one_meal|no_grains|sattvic|no_restriction

    -- Dietary restrictions during this festival
    restrictions        JSONB NOT NULL DEFAULT '{}',
    /*
    {
      "no_meat": true,
      "no_fish": true,
      "no_eggs": true,
      "no_onion": true,
      "no_garlic": true,
      "no_alcohol": true,
      "no_regular_grains": true,
      "no_root_vegetables": false,
      "allowed_grains": ["kuttu", "sabudana", "sama_rice"],
      "allowed_foods": ["fruits", "milk", "curd", "paneer"],
      "special_note": "Variations exist by community"
    }
    */

    -- Special dishes for this festival
    special_dishes      TEXT[] DEFAULT '{}',
    -- ["sabudana_khichdi", "kuttu_puri", "makhana_kheer"]

    -- Grocery implications
    demand_surge_items  TEXT[] DEFAULT '{}',
    -- Items to stock up before: ["sabudana", "kuttu_flour", "sendha_namak"]

    notes               TEXT,
    created_at          TIMESTAMP DEFAULT now(),

    UNIQUE(name, year)
);

CREATE INDEX idx_festival_dates ON festival_calendar(start_date, end_date);
CREATE INDEX idx_festival_religions ON festival_calendar USING GIN(religions);
CREATE INDEX idx_festival_year ON festival_calendar(year);
```

---

### MEAL PLANS

```sql
CREATE TABLE meal_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    week_start          DATE NOT NULL,
    week_end            DATE NOT NULL,

    -- Status flow: draft → approved → active → completed
    status              VARCHAR(20) NOT NULL DEFAULT 'draft',
    generated_by        VARCHAR(20) DEFAULT 'ai',       -- ai|user
    generation_model    VARCHAR(50),                    -- gemini-2.5-flash
    approved_by         UUID REFERENCES users(id),
    approved_at         TIMESTAMP,

    -- The actual plan (denormalized JSON for read speed)
    meals               JSONB NOT NULL DEFAULT '{}',
    /*
    {
      "monday": {
        "date": "2026-06-29",
        "is_festival": false,
        "festival_name": null,
        "breakfast": [
          {
            "recipe_id": "uuid",
            "recipe_name": "Poha",
            "recipe_name_hi": "पोहा",
            "course": "main",
            "servings": 4
          }
        ],
        "lunch": [
          {"recipe_id": "...", "recipe_name": "Dal Makhani", "course": "main"},
          {"recipe_id": "...", "recipe_name": "Aloo Jeera", "course": "side"},
          {"recipe_id": "...", "recipe_name": "Roti", "course": "bread"},
          {"recipe_id": "...", "recipe_name": "Raita", "course": "raita"}
        ],
        "dinner": [
          {"recipe_id": "...", "recipe_name": "Rajma", "course": "main"},
          {"recipe_id": "...", "recipe_name": "Jeera Rice", "course": "rice"}
        ]
      }
    }
    */

    -- Constraints applied during generation
    constraints_applied JSONB DEFAULT '{}',
    -- Which dietary rules were applied, for auditability

    -- User feedback
    rating              INTEGER,                        -- 1-5 after week completes
    feedback            TEXT,

    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now(),

    UNIQUE(household_id, week_start)
);

CREATE INDEX idx_meal_plans_household ON meal_plans(household_id);
CREATE INDEX idx_meal_plans_dates ON meal_plans(week_start, week_end);
CREATE INDEX idx_meal_plans_status ON meal_plans(status);
```

---

### PANTRY ITEMS

```sql
CREATE TABLE pantry_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    ingredient_id       UUID NOT NULL REFERENCES ingredients_master(id),
    ingredient_name     VARCHAR(100) NOT NULL,          -- denormalized for speed

    -- Current stock
    quantity            DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit                VARCHAR(20) NOT NULL,           -- g|kg|ml|l|pieces
    expiry_date         DATE,
    purchase_date       DATE,

    -- Reorder settings
    reorder_level       DECIMAL(10,2),                  -- trigger reorder below this
    reorder_quantity    DECIMAL(10,2),                  -- how much to order

    -- Tracking
    last_updated        TIMESTAMP DEFAULT now(),
    updated_by          VARCHAR(20) DEFAULT 'user',     -- user|ai|barcode_scan

    UNIQUE(household_id, ingredient_id)
);

CREATE INDEX idx_pantry_household ON pantry_items(household_id);
CREATE INDEX idx_pantry_low_stock ON pantry_items(household_id, quantity)
    WHERE quantity IS NOT NULL;
```

---

### GROCERY LISTS

```sql
CREATE TABLE grocery_lists (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    meal_plan_id        UUID REFERENCES meal_plans(id),

    -- Type: weekly (from meal plan) or adhoc (manual add)
    list_type           VARCHAR(20) DEFAULT 'weekly',   -- weekly|adhoc|restock

    status              VARCHAR(20) DEFAULT 'pending',  -- pending|shared|ordered|delivered
    total_estimate_inr  DECIMAL(10,2),
    ordered_via         VARCHAR(30),                    -- bigbasket|zepto|blinkit|manual
    ordered_at          TIMESTAMP,
    delivered_at        TIMESTAMP,

    -- The list
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_grocery_household ON grocery_lists(household_id);
CREATE INDEX idx_grocery_status ON grocery_lists(status);
```

---

### GROCERY ITEMS

```sql
CREATE TABLE grocery_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grocery_list_id     UUID NOT NULL REFERENCES grocery_lists(id) ON DELETE CASCADE,
    ingredient_id       UUID REFERENCES ingredients_master(id),
    ingredient_name     VARCHAR(100) NOT NULL,

    -- Quantities
    required_qty        DECIMAL(10,2) NOT NULL,         -- total needed this week
    in_pantry_qty       DECIMAL(10,2) DEFAULT 0,        -- currently in pantry
    to_buy_qty          DECIMAL(10,2) NOT NULL,         -- required - in_pantry
    unit                VARCHAR(20) NOT NULL,
    quantity_unit_text  VARCHAR(50),                    -- "500g packet" for display

    -- Platform links
    platform            VARCHAR(30),                    -- bigbasket|zepto|blinkit
    platform_link       TEXT,                           -- deep link to product
    product_name        VARCHAR(200),                   -- "Tata Sampann Masoor Dal 500g"
    estimated_price     DECIMAL(8,2),

    -- Status
    status              VARCHAR(20) DEFAULT 'pending',  -- pending|added_to_cart|purchased
    is_checked          BOOLEAN DEFAULT false,

    -- Source
    added_from          VARCHAR(30) DEFAULT 'meal_plan',-- meal_plan|pantry_restock|manual
    recipe_ids          TEXT[] DEFAULT '{}',            -- which recipes need this

    created_at          TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_grocery_items_list ON grocery_items(grocery_list_id);
CREATE INDEX idx_grocery_items_status ON grocery_items(status);
```

---

### STAFF

```sql
CREATE TABLE staff (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,

    -- Identity
    name                VARCHAR(100) NOT NULL,
    role                VARCHAR(30) NOT NULL,           -- cook|maid|driver|gardener|nanny|other
    phone               VARCHAR(15),                    -- WhatsApp number (encrypted in app)
    whatsapp_opted_in   BOOLEAN DEFAULT false,          -- replied HAAN to enrollment
    language            VARCHAR(20) DEFAULT 'hi',       -- hi|mr|kn|ta|te|bn|gu

    -- Schedule
    days_of_week        TEXT[] NOT NULL,
    -- ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    start_time          TIME,
    end_time            TIME,
    is_live_in          BOOLEAN DEFAULT false,
    is_part_time        BOOLEAN DEFAULT true,
    households_count    INTEGER DEFAULT 1,              -- how many homes they serve

    -- Financial
    monthly_wage        DECIMAL(10,2),
    payment_day         INTEGER DEFAULT 1,              -- day of month
    advance_given       DECIMAL(10,2) DEFAULT 0,

    -- Profile
    joining_date        DATE,
    specialties         TEXT[] DEFAULT '{}',            -- ['north_indian', 'baking', 'continental']
    can_cook_cuisines   TEXT[] DEFAULT '{}',
    background_checked  BOOLEAN DEFAULT false,
    reference_contact   VARCHAR(100),

    status              VARCHAR(20) DEFAULT 'active',   -- active|on_leave|terminated
    leave_return_date   DATE,                           -- if on leave
    termination_date    DATE,
    termination_reason  TEXT,

    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_staff_household ON staff(household_id);
CREATE INDEX idx_staff_role ON staff(role);
CREATE INDEX idx_staff_status ON staff(status);
```

---

### STAFF ATTENDANCE

```sql
CREATE TABLE staff_attendance (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id            UUID NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    household_id        UUID NOT NULL REFERENCES households(id),
    date                DATE NOT NULL,

    status              VARCHAR(20) NOT NULL,
    -- present|absent|half_day|holiday|leave_approved|public_holiday
    absent_reason       VARCHAR(100),                   -- sick|personal|family|festival|no_show
    notified_at         TIMESTAMP,                      -- when staff informed about absence
    notification_method VARCHAR(20),                    -- whatsapp|phone_call|in_person

    -- Replacement arranged?
    replacement_found   BOOLEAN DEFAULT false,
    replacement_staff_id UUID REFERENCES staff(id),

    -- Marking
    marked_by           UUID REFERENCES users(id),
    marked_at           TIMESTAMP DEFAULT now(),
    notes               TEXT,

    UNIQUE(staff_id, date)
);

CREATE INDEX idx_attendance_staff ON staff_attendance(staff_id, date);
CREATE INDEX idx_attendance_date ON staff_attendance(date);
```

---

### COOK INSTRUCTIONS

```sql
CREATE TABLE cook_instructions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    staff_id            UUID NOT NULL REFERENCES staff(id),
    date                DATE NOT NULL,

    -- The day's plan (denormalized from meal_plan for this cook)
    meal_plan_day       JSONB NOT NULL,                 -- full day's meals

    -- Generated messages
    instruction_text    TEXT NOT NULL,                  -- English version
    instruction_hindi   TEXT,                           -- Hindi version
    instruction_regional TEXT,                          -- cook's language version

    -- WhatsApp delivery
    whatsapp_number     VARCHAR(15),
    message_sid         VARCHAR(100),                   -- Twilio message SID
    sent_at             TIMESTAMP,
    delivered_at        TIMESTAMP,
    read_at             TIMESTAMP,
    status              VARCHAR(20) DEFAULT 'generated',
    -- generated|queued|sent|delivered|read|failed

    -- Cook's reply (if any)
    cook_reply          TEXT,
    cook_replied_at     TIMESTAMP,
    reply_type          VARCHAR(30),
    -- ok|missing_ingredient|late|absent|question

    created_at          TIMESTAMP DEFAULT now(),

    UNIQUE(staff_id, date)
);

CREATE INDEX idx_cook_inst_household ON cook_instructions(household_id, date);
CREATE INDEX idx_cook_inst_status ON cook_instructions(status);
```

---

### STAFF SOPs

```sql
CREATE TABLE staff_sops (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    staff_role          VARCHAR(30),                    -- cook|maid|all
    title               VARCHAR(200) NOT NULL,          -- "How to mop the floors"
    title_hindi         VARCHAR(200),
    content             TEXT NOT NULL,                  -- detailed instructions
    content_hindi       TEXT,
    category            VARCHAR(50),                    -- cleaning|cooking|security|general
    is_template         BOOLEAN DEFAULT false,          -- shareable template
    pdf_url             TEXT,                           -- generated PDF stored in R2
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT now(),
    updated_at          TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_sops_household ON staff_sops(household_id);
```

---

### FEEDBACK & RATINGS

```sql
CREATE TABLE meal_feedback (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id        UUID NOT NULL REFERENCES households(id),
    recipe_id           UUID NOT NULL REFERENCES recipes(id),
    meal_plan_id        UUID REFERENCES meal_plans(id),
    date                DATE NOT NULL,

    rating              INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    -- 1=never again, 2=ok, 3=good, 4=great, 5=family favourite
    liked_by            TEXT[] DEFAULT '{}',            -- member names who liked it
    disliked_by         TEXT[] DEFAULT '{}',
    notes               TEXT,
    -- "Too spicy", "Loved by kids", "Cook needs help with this"

    affects_planning    BOOLEAN DEFAULT true,
    -- false = one-off occasion, true = learn from this

    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT now(),

    UNIQUE(household_id, recipe_id, date)
);

-- This table drives the personalization engine
-- High rating + affects_planning=true → boost recipe popularity for this HH
-- Low rating + affects_planning=true → reduce suggestion frequency

CREATE INDEX idx_feedback_household ON meal_feedback(household_id);
CREATE INDEX idx_feedback_recipe ON meal_feedback(recipe_id);
```

---

### GROCERY PRODUCTS (Platform Catalogue)

```sql
CREATE TABLE grocery_products (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ingredient_id       UUID NOT NULL REFERENCES ingredients_master(id),
    platform            VARCHAR(30) NOT NULL,           -- bigbasket|zepto|blinkit
    product_name        VARCHAR(300) NOT NULL,
    brand               VARCHAR(100),
    sku_id              VARCHAR(100),                   -- platform's product ID
    url                 TEXT,
    pack_size           DECIMAL,
    pack_unit           VARCHAR(20),                    -- g|ml|pieces|kg|l
    price_inr           DECIMAL(8,2),
    is_available        BOOLEAN DEFAULT true,
    last_price_check    TIMESTAMP,
    last_availability_check TIMESTAMP,
    created_at          TIMESTAMP DEFAULT now(),

    UNIQUE(platform, sku_id)
);

CREATE INDEX idx_grocery_products_ingredient ON grocery_products(ingredient_id, platform);
```

---

## 3. RELATIONSHIP SUMMARY

| Relationship | Type | Notes |
|---|---|---|
| User → Household | 1:M (primary) | One user can own multiple households |
| Household → Members | 1:M | Household has multiple members |
| Member → DietProfile | M:1 | Each member has one diet profile |
| Household → MealPlan | 1:M | One plan per week per household |
| MealPlan → Recipes | M:M (via JSON) | Denormalized in meals JSONB for speed |
| Recipe → Ingredients | M:M | Via recipe_ingredients junction |
| Household → PantryItems | 1:M | One pantry per household |
| PantryItem → Ingredient | M:1 | Each pantry item = one ingredient |
| MealPlan → GroceryList | 1:1 | One grocery list per meal plan |
| GroceryList → GroceryItems | 1:M | Multiple items per list |
| GroceryItem → GroceryProduct | M:1 | Best product match per item |
| Household → Staff | 1:M | Multiple staff per household |
| Staff → Attendance | 1:M | Daily attendance records |
| Staff → CookInstructions | 1:M | Daily instruction per cook |
| MealPlan → CookInstruction | 1:1 per day | One instruction per day per cook |
| Recipe → Feedback | 1:M | Multiple feedback entries per recipe |
| FestivalCalendar | Reference | Standalone — queried by date range |

---

## 4. KEY DESIGN DECISIONS

**D1: JSONB for meal plans (not normalized day tables)**
Meal plans are read far more than written. Denormalizing into JSONB enables single-query reads with no joins. The weekly plan is created once and read ~50 times (daily briefings, cook instructions, grocery generation).

**D2: Diet profile at member level, not household level**
Every household member can have different dietary restrictions. The constraint engine takes the intersection (most restrictive wins). This correctly handles the non-veg husband + vegetarian mother scenario.

**D3: Festival calendar as a separate reference table (not embedded)**
Festivals need to be queried by date range across all households simultaneously (for cron jobs). A separate indexed table is more efficient than per-household JSON.

**D4: Cook instructions denormalize the day's meals**
When the cook instruction is generated, it copies the meal data so the instruction is a standalone artifact. If the meal plan changes after the instruction is sent, the sent instruction remains accurate.

**D5: WhatsApp phone numbers stored in staff table (not users)**
Most cooks won't create accounts. Their phone numbers are stored directly in the staff record and used only for outbound WhatsApp messages. Encrypted at the application layer.

**D6: Pantry uses ingredient_id (not free text)**
All pantry items must map to an ingredient in ingredients_master. This enables the ingredient → pantry quantity → to_buy calculation to work automatically. Free-text items create orphans.

**D7: Feedback drives personalization (not a generic ratings system)**
meal_feedback.affects_planning is the signal — a 5-star rating with affects_planning=true raises the recipe's household-specific score. This creates a household-specific recipe preference graph over time.
