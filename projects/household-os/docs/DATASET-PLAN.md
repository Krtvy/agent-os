# DATASET-PLAN — Household OS
## Dataset Strategy Document
> Version: 1.0 | Date: June 25, 2026 | Author: Kartavya Joshi
> Depends on: ERD.md, RESEARCH.md

---

## OVERVIEW

We need 8 datasets. 3 can be sourced (existing, free). 5 must be built (proprietary moat).

```
SOURCE (existing, free)            BUILD (proprietary, our moat)
────────────────────               ────────────────────────────────
DS1: Indian Recipes (Kaggle)  →    DS4: Ingredient Dietary Flags
DS2: Nutrition Data (HF)      →    DS5: Festival Calendar (20+ festivals)
DS3: HCES Expenditure (MOSPI) →    DS6: Cook Instruction Templates (Hindi)
                                   DS7: Indian Pantry Staples DB
                                   DS8: Grocery Product Catalogue
```

**Build order (what blocks what):**
```
DS1 (recipes) + DS4 (ingredient flags)
    → enables: constraint engine, meal planning
    → WEEK 1 priority

DS5 (festival calendar)
    → enables: festival-aware meal planning
    → WEEK 1 priority

DS6 (cook instructions) + DS7 (pantry staples)
    → enables: WhatsApp cook briefings, grocery lists
    → WEEK 2 priority

DS8 (grocery products)
    → enables: platform deep links, price estimates
    → WEEK 3 priority (can launch without it)

DS2 + DS3 (nutrition + expenditure)
    → enables: nutrition analysis, market sizing (analytics only)
    → NOT blocking MVP
```

---

## DS1 — INDIAN RECIPES DATABASE

### What exists
| Source | Size | URL | License |
|---|---|---|---|
| Cleaned Indian Recipes | 6,500 recipes | kaggle.com/datasets/sooryaprakash12/cleaned-indian-recipes-dataset | Open |
| IndianFoodDatasetGeneration | 6,000+ recipes | github.com/kanishk307/IndianFoodDatasetGeneration | MIT |
| Indian Foods + Images | ~1,200 recipes | kaggle.com/datasets/kishanpahadiya/indian-food-and-its-recipes-dataset-with-images | Open |

**Total base: ~8,000-9,000 recipes with significant overlap**

### Gap analysis
The Kaggle dataset has: name, ingredients, instructions, cuisine, flavor_profile
**Missing completely:**
- `meal_type` (breakfast/lunch/dinner) — not in source
- `course` (main/side/bread/rice/raita) — not in source
- Dietary flags (`is_vegetarian`, `is_jain`, `has_onion`, `has_garlic`, etc.)
- `cook_instruction` — simplified Hindi version for cook
- Festival suitability tags
- `popularity_score` — no usage data
- Nutrition data — partially in HuggingFace dataset

### Build plan

**Step 1: Download source datasets**
```bash
cd projects/household-os/data/raw
# Kaggle download (needs kaggle CLI)
pip install kaggle
kaggle datasets download sooryaprakash12/cleaned-indian-recipes-dataset
kaggle datasets download kishanpahadiya/indian-food-and-its-recipes-dataset-with-images

# GitHub clone
git clone --depth=1 https://github.com/kanishk307/IndianFoodDatasetGeneration ./indian-food-dataset
```

**Step 2: Merge and deduplicate**
```python
# scripts/build_recipe_db.py

import pandas as pd
from rapidfuzz import fuzz

def merge_recipe_datasets():
    # Load all sources
    df1 = pd.read_csv('raw/Cleaned_Indian_Food_Dataset.csv')
    df2 = pd.read_csv('raw/Indian_Food_Dataset.csv')  # kanishk307

    # Normalize column names
    df1 = df1.rename(columns={
        'TranslatedRecipeName': 'name',
        'TranslatedIngredients': 'ingredients_raw',
        'TranslatedInstructions': 'instructions',
        'Cuisine': 'cuisine_region',
        'Course': 'course_raw',
        'Diet': 'diet_raw',
        'PrepTimeInMins': 'prep_time_min',
        'CookTimeInMins': 'cook_time_min',
    })

    # Deduplicate by fuzzy name matching (threshold 85)
    seen_names = set()
    unique_recipes = []
    for _, row in df1.iterrows():
        is_dup = any(fuzz.ratio(row['name'], seen) > 85 for seen in seen_names)
        if not is_dup:
            seen_names.add(row['name'])
            unique_recipes.append(row)

    return pd.DataFrame(unique_recipes)
```

**Step 3: AI enrichment with Gemini (batch processing)**
```python
# scripts/enrich_recipes_with_ai.py
# Uses Gemini to add missing fields in batches of 20

ENRICHMENT_PROMPT = """
For this Indian recipe, provide the following in JSON:
Recipe: {recipe_name}
Ingredients: {ingredients}

Fill in:
{
  "meal_type": "breakfast|lunch|dinner|snack|dessert",
  "course": "main|side|bread|rice|raita|salad|chutney|dessert|beverage",
  "is_vegetarian": true|false,
  "is_vegan": true|false,
  "is_jain": true|false,  // no onion, garlic, potato, carrot, ginger
  "is_sattvic": true|false, // no onion, garlic only
  "has_onion": true|false,
  "has_garlic": true|false,
  "has_root_veg": true|false,
  "has_dairy": true|false,
  "has_eggs": true|false,
  "has_meat": true|false,
  "has_fish": true|false,
  "festival_ok": ["navratri", "ekadashi"],  // festivals where this is allowed
  "season": ["winter", "summer", "monsoon", "all"],
  "difficulty": "easy|medium|hard",
  "tags": ["quick", "one_pot", "popular", "healthy"],
  "cook_instruction_hi": "short Hindi instruction for cook (max 2 sentences)"
}
"""

# Cost estimate: 8,000 recipes × 500 tokens = 4M tokens
# Gemini 2.5 Flash free tier: 1M tokens/day → 4 days to enrich all
# Or use Groq (LLaMA 70B) for free unlimited
```

**Step 4: Validate and clean**
```python
# Quality checks:
# - meal_type must be one of: breakfast|lunch|dinner|snack|dessert
# - If has_onion=True or has_garlic=True → is_jain must be False
# - If has_meat=True → is_vegetarian must be False
# - festival_ok cannot include 'navratri' if has_onion=True
# - cook_instruction_hi must be < 150 characters

def validate_recipe(recipe: dict) -> list[str]:
    errors = []
    if recipe['has_onion'] and recipe['is_jain']:
        errors.append("Jain recipe cannot have onion")
    if recipe['has_meat'] and recipe['is_vegetarian']:
        errors.append("Vegetarian recipe cannot have meat")
    if 'navratri' in recipe['festival_ok'] and recipe['has_onion']:
        errors.append("Navratri recipe cannot have onion")
    return errors
```

**Target output:** `data/processed/recipes.csv` — 6,000+ validated recipes

---

## DS2 — NUTRITION DATA

### What exists
- HuggingFace: `bharat-raghunathan/indian-foods-dataset` — nutrition for common Indian dishes
- Indian Food Composition Tables (IFCT 2017) — official government publication, partial
- USDA FoodData Central — not India-specific but has basic nutrients

### Build plan
```python
# Map recipe names → IFCT/HuggingFace nutrition data
# For unmatched recipes: Gemini to estimate nutrition based on ingredients
# Low priority for MVP — needed for Phase 4 nutrition feature

# Target columns: calories|protein_g|carbs_g|fat_g|fiber_g per serving
```

**MVP Status: SKIP — add in Phase 4**

---

## DS3 — HOUSEHOLD EXPENDITURE DATA (Analytics Only)

### What exists
- HCES 2023-24 microdata at `microdata.gov.in` (free, requires registration)
- Used for: market sizing, pricing benchmarks, grocery spend validation

### Download process
```bash
# Register at microdata.gov.in
# Download: HCES 2023-24 → Urban → Household Level Data
# Files: hh_level.csv, person_level.csv, food_item_level.csv
```

**MVP Status: DOWNLOAD for reference, not integrated into product**

---

## DS4 — INGREDIENT DIETARY FLAGS (BUILD — WEEK 1 PRIORITY)

### Why we build this
No public dataset has:
- `is_root_vegetable` (Jain constraint — 12 specific vegetables)
- `is_allium` (onion, garlic, leek, spring onion)
- Regional names (Hindi/Marathi/Kannada/Tamil equivalents)
- Common Indian grocery search terms per platform

### Build approach

**Part A: Core list (manual + AI)**
```python
# Start with known categories, then AI-expand

ROOT_VEGETABLES = [
    "potato", "carrot", "radish", "turnip", "beet", "sweet_potato",
    "yam", "cassava", "taro", "colocasia", "arrowroot"
]

ALLIUMS = [
    "onion", "garlic", "leek", "spring_onion", "shallot",
    "chives", "scallion"
]

# Use Gemini to generate complete Indian ingredient list by category
CATEGORY_PROMPT = """
List ALL ingredients commonly used in Indian cooking in the category: {category}
For each ingredient provide:
{
  "name": "english_name",
  "name_hindi": "hindi_name",
  "name_marathi": "marathi_name (if known)",
  "name_tamil": "tamil_name (if known)",
  "is_root_vegetable": true|false,
  "is_allium": true|false,
  "is_meat": true|false,
  "is_seafood": true|false,
  "is_dairy": true|false,
  "shelf_life_days": integer,
  "storage_type": "fridge|pantry|freezer",
  "typical_pack_size": "500g|1kg|12pieces|etc",
  "bigbasket_search_term": "best search term for BigBasket"
}
"""

CATEGORIES = [
    "dals_and_legumes", "grains_and_flours", "whole_spices",
    "ground_spices", "masala_blends", "fresh_vegetables",
    "root_vegetables", "leafy_greens", "gourds", "fruits",
    "dairy_products", "oils_and_ghee", "nuts_and_seeds",
    "dried_fruits", "condiments_and_pickles", "sweeteners",
    "meat_and_poultry", "seafood", "eggs", "beverages",
    "baking_ingredients", "packaged_foods"
]
```

**Part B: Quality validation**
```python
# Auto-validation rules:
# 1. If is_allium=True → name must be in ['onion', 'garlic', 'leek', ...]
# 2. If is_root_vegetable=True → is_allium must be False (they're separate)
# 3. If is_meat=True → is_dairy must be False
# 4. shelf_life_days=0 for fresh vegetables (buy same day)
# 5. All root vegetables: is_root_vegetable=True AND in Jain exclusion list
```

**Target output:** `data/processed/ingredients_master.csv`
**Size:** ~800-1,200 ingredients
**Build time:** 2-3 days (Gemini batch calls, manual review)

---

## DS5 — FESTIVAL CALENDAR (BUILD — WEEK 1 PRIORITY)

### Why we build this
**No dataset of this exists publicly.** Partial information is scattered across Wikipedia, Drik Panchang, religion-specific websites. The dietary rules layer is entirely missing from all sources.

### Build approach

**Part A: Festival list and dates (2026-2030)**
```python
FESTIVALS_TO_COVER = [
    # Hindu (high impact on diet)
    {"name": "Navratri", "occurrences": 2, "dietary_impact": "high"},
    {"name": "Ekadashi", "occurrences": 24, "dietary_impact": "high"},  # monthly
    {"name": "Diwali", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Holi", "occurrences": 1, "dietary_impact": "low"},
    {"name": "Janmashtami", "occurrences": 1, "dietary_impact": "high"},
    {"name": "Maha Shivratri", "occurrences": 1, "dietary_impact": "high"},
    {"name": "Ram Navami", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Ganesh Chaturthi", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Durga Puja", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Karva Chauth", "occurrences": 1, "dietary_impact": "high"},
    {"name": "Raksha Bandhan", "occurrences": 1, "dietary_impact": "low"},
    {"name": "Makar Sankranti", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Baisakhi", "occurrences": 1, "dietary_impact": "low"},
    # Muslim
    {"name": "Eid ul-Fitr", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Eid ul-Adha", "occurrences": 1, "dietary_impact": "medium"},
    {"name": "Ramadan", "occurrences": 1, "dietary_impact": "high"},  # month-long
    # Jain
    {"name": "Paryushana", "occurrences": 1, "dietary_impact": "high"},  # 8-10 days strict
    # Sikh
    {"name": "Guru Nanak Jayanti", "occurrences": 1, "dietary_impact": "low"},
    {"name": "Gurpurab events", "occurrences": "multiple", "dietary_impact": "low"},
    # National
    {"name": "Christmas", "occurrences": 1, "dietary_impact": "low"},
]
```

**Part B: Date calculation**
- Hindu festivals follow the Vikram Samvat lunar calendar (shifts every year)
- Use `ephem` Python library or `drik_panchang` API for accurate dates
- Build for 2026-2030 (5-year table = enough for MVP)

```python
# For Ekadashi (twice monthly, every fortnight):
# Use drik-panchang API or compute from lunar calendar

import ephem

def get_ekadashi_dates(year: int) -> list[date]:
    """Compute all Ekadashi dates for a given year."""
    # Ekadashi = 11th tithi of lunar fortnight (waxing + waning)
    # There are ~24-25 Ekadashis per year
    ...
```

**Part C: Dietary rules per festival (manual research + AI validation)**
```python
# Each festival gets a detailed restrictions JSON
# Sources: Drik Panchang, Vrat Katha books, community dietary guides
# AI review: Gemini validates against known sources

NAVRATRI_RESTRICTIONS = {
    "no_meat": True,
    "no_fish": True,
    "no_eggs": True,
    "no_onion": True,
    "no_garlic": True,
    "no_alcohol": True,
    "no_regular_grains": True,  # no wheat, rice, maize
    "allowed_grains": ["kuttu", "sabudana", "sama_rice", "singhara_flour"],
    "allowed_foods": [
        "fruits", "milk", "curd", "paneer", "makhana",
        "sweet_potato", "colocasia", "raw_banana"
    ],
    "special_notes": "Variations exist — some communities allow potato; some fast completely on Ashtami/Navami",
    "sendha_namak_only": True,  # Rock salt only, not table salt
}
```

**Part D: Special dishes per festival**
```python
# For each festival → list of traditional dishes
# Cross-reference with DS1 recipe database
# Tag recipes with festival_ok[] accordingly

FESTIVAL_DISHES = {
    "navratri": ["sabudana_khichdi", "kuttu_ki_puri", "aloo_ki_sabzi",
                 "makhana_kheer", "banana_halwa", "sama_chawal"],
    "eid": ["biryani", "sheer_khurma", "sewaiyan", "nihari",
            "haleem", "shami_kebab", "korma"],
    "janmashtami": ["panjiri", "panchamrit", "makhana_kheer",
                    "gopalkala", "dhaniya_panjiri"],
    "diwali": ["besan_ladoo", "kaju_katli", "gulab_jamun",
               "chakli", "chivda", "shankarpali"],
}
```

**Target output:** `data/processed/festival_calendar.json`
**Coverage:** 20+ festivals × 5 years (2026-2030) = ~100+ entries
**Build time:** 3-4 days (research + Gemini validation)

---

## DS6 — COOK INSTRUCTION TEMPLATES (BUILD — WEEK 2)

### What we need
WhatsApp messages to cook in Hindi/regional languages that are:
- Short (under 150 characters per dish)
- In cook-friendly language (katori not ml, pao not grams)
- Action-oriented ("Dal mein tadka lagao, sukh jane tak pakao")

### Build approach

**Part A: Unit conversion table (Indian kitchen)**
```python
COOK_UNITS = {
    "1 cup": "1 katori",
    "2 tbsp": "2 chammach",
    "1 tsp": "1 chhotee chammach",
    "100g onion": "1 bada pyaaz",
    "500g chicken": "adha kilo murga",
    "200g paneer": "ek packet paneer",
    "1 liter milk": "ek packet doodh",
    "2 medium potatoes": "2 aloo",
}
```

**Part B: Recipe → Cook instruction converter**
```python
COOK_INSTRUCTION_PROMPT = """
Convert this recipe to a simple cook instruction in Hindi.
Recipe: {recipe_name}
Full instructions: {instructions}
Ingredients: {ingredients}

Rules:
1. Maximum 2-3 sentences
2. Use Indian kitchen measurements (katori, chammach, pao)
3. Simple Hindi words only — no English, no technical terms
4. Focus on what the cook should DO, not background info
5. Mention timing: "15 minute pakao" not "cook until golden"

Example good instruction:
"Ek katori daal 30 minute bheego. Pressure cooker mein 3 seeti lagao.
 Phir tamatar aur masale daalo, 10 minute pakao."

Example bad instruction:
"Soak 200g of masoor lentils for half an hour. 
 Cook in pressure cooker for 3 whistles on medium flame."

Generate Hindi cook instruction:
"""

# Run Gemini on all 6,500 recipes
# Cost: 6,500 × 300 tokens = ~2M tokens = 2 days on free Gemini tier
# Or use Groq LLaMA 70B (free, unlimited)
```

**Part C: Morning briefing templates**
```python
# WhatsApp message templates for the daily morning brief
MORNING_BRIEF_HINDI = """🍽️ {date_hindi} का खाना

🌅 नाश्ता:
{breakfast_items}

☀️ दोपहर:
{lunch_items}

🌙 रात:
{dinner_items}

{missing_items_section}

{festival_note}
"""

MISSING_ITEMS_TEMPLATE = "⚠️ लाना है: {items_list}"
FESTIVAL_NOTE_TEMPLATE = "🙏 आज {festival_name} है। {festival_food_note}"
```

**Target output:** `data/processed/cook_instructions.json` (per-recipe)
**Build time:** 3-4 days (Gemini/Groq batch calls)

---

## DS7 — INDIAN PANTRY STAPLES DATABASE (BUILD — WEEK 2)

### What we need
A reference of what items every Indian household should always have, with:
- Typical quantity kept
- Reorder trigger level
- Average consumption rate (how fast it depletes)
- Platform search term for reordering

### Build approach

**Part A: Core pantry list by category**
```python
PANTRY_STAPLES = {
    "dals": [
        {"name": "toor dal", "typical_qty": 1000, "unit": "g",
         "reorder_level": 200, "monthly_consumption": 800},
        {"name": "masoor dal", "typical_qty": 500, "unit": "g",
         "reorder_level": 100, "monthly_consumption": 500},
        {"name": "chana dal", "typical_qty": 500, "unit": "g", ...},
        {"name": "urad dal", "typical_qty": 500, "unit": "g", ...},
        {"name": "moong dal", "typical_qty": 500, "unit": "g", ...},
    ],
    "grains": [
        {"name": "rice", "typical_qty": 5000, "unit": "g",
         "reorder_level": 1000, "monthly_consumption": 4000},
        {"name": "wheat flour (atta)", "typical_qty": 5000, "unit": "g", ...},
        {"name": "semolina (sooji/rava)", "typical_qty": 500, "unit": "g", ...},
        {"name": "besan", "typical_qty": 500, "unit": "g", ...},
        {"name": "poha", "typical_qty": 500, "unit": "g", ...},
    ],
    "whole_spices": [
        {"name": "cumin seeds (jeera)", "typical_qty": 100, "unit": "g", ...},
        {"name": "mustard seeds (rai)", "typical_qty": 100, "unit": "g", ...},
        {"name": "cardamom (elaichi)", "typical_qty": 50, "unit": "g", ...},
        {"name": "cinnamon (dalchini)", "typical_qty": 50, "unit": "g", ...},
        {"name": "cloves (laung)", "typical_qty": 50, "unit": "g", ...},
        {"name": "bay leaves (tej patta)", "typical_qty": 20, "unit": "g", ...},
    ],
    "ground_spices": [
        {"name": "turmeric powder (haldi)", "typical_qty": 200, "unit": "g", ...},
        {"name": "red chilli powder", "typical_qty": 200, "unit": "g", ...},
        {"name": "coriander powder (dhania)", "typical_qty": 200, "unit": "g", ...},
        {"name": "cumin powder (jeera powder)", "typical_qty": 100, "unit": "g", ...},
        {"name": "garam masala", "typical_qty": 100, "unit": "g", ...},
        {"name": "amchur (dry mango powder)", "typical_qty": 100, "unit": "g", ...},
        {"name": "kitchen king masala", "typical_qty": 100, "unit": "g", ...},
    ],
    "oils_ghee": [
        {"name": "refined oil / sunflower oil", "typical_qty": 1000, "unit": "ml", ...},
        {"name": "mustard oil", "typical_qty": 1000, "unit": "ml", ...},
        {"name": "ghee", "typical_qty": 500, "unit": "g", ...},
    ],
    "dairy": [
        {"name": "milk", "typical_qty": 2, "unit": "l",
         "shelf_life_days": 2, "daily_consumption": 0.5},
        {"name": "curd (dahi)", "typical_qty": 500, "unit": "g", ...},
        {"name": "paneer", "typical_qty": 200, "unit": "g",
         "shelf_life_days": 5, "note": "buy when needed for recipe"},
    ],
    "fresh_daily": [
        {"name": "onion", "typical_qty": 1000, "unit": "g",
         "reorder_days": 7, "note": "buy weekly"},
        {"name": "tomato", "typical_qty": 500, "unit": "g",
         "reorder_days": 3},
        {"name": "ginger", "typical_qty": 100, "unit": "g", ...},
        {"name": "garlic", "typical_qty": 100, "unit": "g", ...},
        {"name": "green chillies", "typical_qty": 50, "unit": "g", ...},
        {"name": "coriander leaves", "typical_qty": 50, "unit": "g",
         "shelf_life_days": 3},
    ],
}
# Total: ~80-120 pantry staples
```

**Target output:** `data/processed/pantry_staples.json`
**Build time:** 1 day (manual + AI review)

---

## DS8 — GROCERY PRODUCT CATALOGUE (BUILD — WEEK 3)

### What we need
For each ingredient in DS4: the best matching product on BigBasket/Zepto with:
- Product name, brand, pack size, price
- Platform-specific URL / search term
- Availability (in-stock indicator)

### Build approach

**Phase 1: Deep links only (MVP — no scraping)**
```python
def get_grocery_deeplink(ingredient: str, platform: str) -> str:
    """
    Generate platform-specific search deep link.
    No scraping, no API needed.
    Works as affiliate / referral traffic.
    """
    encoded = urllib.parse.quote(ingredient)
    links = {
        "bigbasket": f"https://www.bigbasket.com/ps/?q={encoded}&nc=as",
        "zepto": f"https://zeptonow.com/search?query={encoded}",
        "blinkit": f"https://blinkit.com/s/?q={encoded}",
        "instamart": f"https://www.swiggy.com/instamart/search?query={encoded}"
    }
    return links.get(platform, links["bigbasket"])
```

**Phase 2: BigBasket catalogue (Week 3 — using agent-browser)**
```python
# agent-browser is already installed on the system
# Use it to scrape BigBasket product catalogue

# Run via team_coordinator or Nakula cron job:
# "Scrape BigBasket for: masoor dal, toor dal, basmati rice [category: dals+grains]"
# Save to grocery_products table

SCRAPE_CATEGORIES = [
    "dals-and-pulses", "rice-and-rice-products", "atta-flours-sooji",
    "oils-ghee", "dry-fruits-nuts", "spices-masala", "salt-sugar-jaggery",
    "dairy-milk-products", "tea-coffee-beverages"
]
```

**Phase 3: Price tracking (Ongoing — weekly Nakula job)**
```python
# Nakula jobs.yml entry:
# - name: grocery-price-sync
#   schedule: "0 6 * * 0"  # Sunday 6 AM
#   command: "python scripts/sync_grocery_prices.py"
#   timeout_minutes: 30
```

**Target output:** `data/processed/grocery_products.csv`
**Initial size:** ~2,000 products (top items from each category)
**Build time:** 3-4 days (agent-browser scraping in batches)

---

## BUILD SCRIPTS STRUCTURE

```
projects/household-os/
├── data/
│   ├── raw/                    ← downloaded source files
│   │   ├── kaggle_recipes/
│   │   ├── hf_nutrition/
│   │   └── mospi_hces/
│   ├── processed/              ← cleaned, enriched, ready to load
│   │   ├── recipes.csv
│   │   ├── ingredients_master.csv
│   │   ├── festival_calendar.json
│   │   ├── pantry_staples.json
│   │   ├── grocery_products.csv
│   │   └── cook_instructions.json
│   └── validation/             ← QA reports
│       ├── recipe_validation_report.csv
│       └── ingredient_flag_audit.csv
├── scripts/
│   ├── 01_download_sources.sh       ← download Kaggle + GitHub datasets
│   ├── 02_build_recipe_db.py        ← merge + deduplicate recipes
│   ├── 03_enrich_recipes.py         ← AI enrichment (dietary flags, Hindi)
│   ├── 04_build_ingredients.py      ← build ingredient master list
│   ├── 05_build_festival_calendar.py ← compute dates + dietary rules
│   ├── 06_generate_cook_instructions.py ← Hindi cook instructions
│   ├── 07_build_pantry_staples.py   ← pantry reference data
│   ├── 08_scrape_grocery_products.py ← BigBasket catalogue
│   ├── 09_validate_all.py           ← run all validation checks
│   └── 10_load_to_postgres.py       ← load processed data into DB
└── docs/
    └── DATASET-PLAN.md             ← this file
```

---

## PRIORITY + TIMELINE

| Week | Datasets | Enables |
|---|---|---|
| **Week 1** | DS1 (recipes) + DS4 (ingredient flags) + DS5 (festival calendar) | Constraint engine + meal planner works |
| **Week 2** | DS6 (cook instructions) + DS7 (pantry staples) | WhatsApp messages + grocery lists |
| **Week 3** | DS8 (grocery products Phase 1 — deep links) | Grocery ordering |
| **Week 4** | DS8 Phase 2 (BigBasket scrape) | Product matching + price estimates |
| **Later** | DS2 (nutrition) + DS3 (HCES) | Analytics features |

---

## DATA QUALITY STANDARDS

Every dataset must pass before loading to PostgreSQL:

```python
QUALITY_GATES = {
    "recipes": {
        "min_count": 5000,
        "required_fields": ["name", "meal_type", "course", "is_vegetarian",
                            "cook_time_min", "ingredients_raw"],
        "no_nulls": ["name", "meal_type", "is_vegetarian"],
        "dietary_logic_checks": True,   # Jain can't have onion, etc.
        "festival_logic_checks": True,   # Navratri can't have onion, etc.
        "hindi_instruction_min_pct": 80, # 80% recipes must have Hindi cook_instruction
    },
    "ingredients_master": {
        "min_count": 500,
        "required_fields": ["name", "category", "is_root_vegetable", "is_allium"],
        "no_nulls": ["name", "category"],
        "jain_completeness": True,       # all root veg must be flagged
    },
    "festival_calendar": {
        "min_festivals": 18,
        "years_covered": [2026, 2027, 2028],
        "required_fields": ["name", "start_date", "religions", "restrictions"],
        "navratri_count": 2,             # spring + autumn Navratri per year
        "ekadashi_count_min": 20,        # at least 20 Ekadashis per year
    }
}
```

---

## ESTIMATED TOTAL BUILD EFFORT

| Dataset | Days | Method |
|---|---|---|
| DS1 Recipes | 2 days | Download + Gemini/Groq enrichment (automated) |
| DS4 Ingredients | 2 days | Gemini generation + manual review |
| DS5 Festival Calendar | 3 days | Research + manual coding + Gemini validation |
| DS6 Cook Instructions | 2 days | Groq batch processing (automated) |
| DS7 Pantry Staples | 1 day | Manual list + AI review |
| DS8 Grocery Products | 3 days | agent-browser scraping |
| **Total** | **13 days** | **~2.5 weeks of part-time work** |

**Costs: ₹0** — All AI calls on Groq free tier + Gemini free tier.
