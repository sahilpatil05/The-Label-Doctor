# Ingredient Detection System Documentation

## Overview

The Ingredient Detection System is a comprehensive ingredient database and detection engine that automatically identifies ingredients from OCR text, matches them against a curated database, and provides detailed metadata including allergen information, categories, and synonyms.

## Architecture

### Core Components

#### 1. **TextPreprocessor Class**
Cleans and normalizes OCR text for ingredient detection.

**Key Features:**
- Lowercase conversion and whitespace normalization
- Multi-word ingredient preservation (e.g., "palm oil", "soy lecithin")
- Intelligent text splitting while preserving ingredient boundaries
- Removal of quantity and descriptor information
- Handling of special characters and formatting

**Methods:**
- `preprocess(text)` - Cleans raw OCR text
- `split_ingredients(text)` - Splits text into individual ingredients
- `clean_ingredient(ingredient)` - Cleans individual ingredient strings

**Example:**
```python
processor = TextPreprocessor()
cleaned = processor.preprocess("INGREDIENTS: Sugar, Palm OIL, Wheat flour, Milk")
# Output: "sugar, palm oil, wheat flour, milk"

ingredients = processor.split_ingredients("sugar, palm oil; wheat and milk")
# Output: ['sugar', 'palm oil', 'wheat', 'milk']
```

#### 2. **IngredientDatabase Class**
Manages the comprehensive ingredient database and performs lookups.

**Database Structure:**
- **Format:** JSON-based (`ingredients_database.json`)
- **Total Ingredients:** 54 base ingredients with 220+ synonyms
- **Fields per ingredient:**
  - `name` - Official ingredient name
  - `synonyms` - Array of alternative names/variations
  - `category` - Single or multiple categories (allergen, oil, preservative, etc.)
  - `allergen` - Boolean flag
  - `allergen_type` - Type of allergen (gluten, dairy, peanut, etc.)
  - `description` - Brief description

**Sample Entry:**
```json
{
  "wheat": {
    "name": "Wheat",
    "synonyms": ["wheat flour", "whole wheat", "wheat gluten"],
    "category": ["allergen", "base_ingredient"],
    "allergen": true,
    "allergen_type": "gluten",
    "description": "Cereal grain containing gluten"
  }
}
```

**Search Methods:**
- `search_exact(query)` - Exact match search
- `search_fuzzy(query, threshold=0.8)` - Fuzzy matching for misspellings
- `get_all_ingredients()` - Get all ingredient keys

**Example:**
```python
db = IngredientDatabase()
ingredient = db.search_exact("sugar")  # Returns Ingredient object
result = db.search_fuzzy("suger", threshold=0.8)  # Returns (Ingredient, confidence_score)
```

#### 3. **Ingredient Class**
Represents a single ingredient with metadata.

**Properties:**
- `name` - Official ingredient name
- `synonyms` - List of alternative names
- `category` - List of categories
- `allergen` - Boolean allergen flag
- `allergen_type` - Type of allergen
- `description` - Ingredient description

**Methods:**
- `to_dict()` - Convert to dictionary representation

#### 4. **IngredientDetector Class**
Main detection engine combining all components.

**Core Method:**
`detect_ingredients(ocr_text, enable_fuzzy=True, fuzzy_threshold=0.8)`

**Returns:**
```python
{
    'total_detected': 8,
    'total_unmatched': 0,
    'detected_ingredients': [
        {
            'original_text': 'sugar',
            'cleaned_text': 'sugar',
            'matched_name': 'Sugar',
            'category': ['sweetener', 'base_ingredient'],
            'allergen': False,
            'allergen_type': None,
            'match_confidence': 1.0,
            'match_type': 'exact'
        },
        # ... more ingredients
    ],
    'unmatched_ingredients': [],
    'allergens_found': 2,
    'allergen_types': ['gluten', 'dairy'],
    'categories': ['allergen', 'base_ingredient', 'oil'],
    'summary': {
        'total': 8,
        'matched': 8,
        'unmatched': 0,
        'match_rate': '100.0%'
    }
}
```

## Usage Examples

### Basic Ingredient Detection

```python
from ingredient_detector import IngredientDetector

detector = IngredientDetector()

# Detect ingredients from OCR text
ocr_text = """
INGREDIENTS: Sugar, Palm Oil, Wheat Flour, Milk Powder,
Soy Lecithin, Peanuts, Citric Acid, Natural Flavors
"""

results = detector.detect_ingredients(ocr_text)

print(f"Matched: {results['total_detected']}")
print(f"Match rate: {results['summary']['match_rate']}")

for ingredient in results['detected_ingredients']:
    print(f"- {ingredient['matched_name']} ({ingredient['match_confidence']:.0%})")
    if ingredient['allergen']:
        print(f"  ⚠️ ALLERGEN: {ingredient['allergen_type']}")
```

### Fuzzy Matching for Typos

```python
# Enable fuzzy matching to handle OCR errors and typos
results = detector.detect_ingredients(ocr_text, enable_fuzzy=True, fuzzy_threshold=0.8)

# If OCR recognizes "suger" instead of "sugar":
# - Exact match fails
# - Fuzzy match succeeds with 80%+ confidence
```

### Search for Specific Ingredient

```python
# Search ingredient database
ingredient_info = detector.search_ingredient("soy lecithin")
# Returns:
# {
#     'name': 'Soy Lecithin',
#     'synonyms': ['spi lecithin'],
#     'category': ['emulsifier', 'additive'],
#     'allergen': True,
#     'allergen_type': 'soy',
#     'description': 'Emulsifier derived from soybeans'
# }
```

### Direct Database Access

```python
from ingredient_detector import IngredientDatabase

db = IngredientDatabase()

# Exact search
wheat = db.search_exact("wheat")
print(f"Allergen: {wheat.allergen}")
print(f"Type: {wheat.allergen_type}")

# Fuzzy search with threshold
result = db.search_fuzzy("peanite", threshold=0.75)
if result:
    ingredient, confidence = result
    print(f"Match: {ingredient.name} ({confidence:.0%})")
```

## Integration with Flask API

The ingredient detector is integrated into the `/api/scan` endpoint:

### Request

```javascript
const response = await fetch('/api/scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        image: base64_image_data,
        userAllergens: ['peanut', 'milk'],
        userId: 'user123',
        foodCategory: 'snack'
    })
});
```

### Response

The API response includes database detection results:

```json
{
    "success": true,
    "extracted_ingredients": ["sugar", "palm oil", "wheat", ...],
    "database_detection": {
        "enabled": true,
        "detected_ingredients": [
            {
                "matched_name": "Sugar",
                "category": ["sweetener"],
                "allergen": false,
                "match_confidence": 1.0
            },
            ...
        ],
        "allergen_info": [
            {
                "ingredient": "Wheat",
                "allergen_type": "gluten",
                "category": ["allergen", "base_ingredient"],
                "confidence": 1.0
            }
        ],
        "summary": {
            "total": 8,
            "matched": 8,
            "unmatched": 0,
            "match_rate": "100.0%"
        },
        "allergen_types": ["gluten"],
        "categories": ["allergen", "base_ingredient", "oil"]
    },
    ...
}
```

## Database Expansion

The ingredient database is designed for easy expansion without code changes.

### Adding New Ingredients

Edit `ingredients_database.json` and add entries to the `ingredients` object:

```json
{
    "metadata": {
        "version": "1.0",
        "last_updated": "2026-04-01",
        "total_ingredients": 54
    },
    "ingredients": {
        "existing_ingredient": { ... },
        "new_ingredient": {
            "name": "New Ingredient",
            "synonyms": ["alias1", "alias2"],
            "category": ["category1", "category2"],
            "allergen": true/false,
            "allergen_type": "allergen_type" or null,
            "description": "Brief description"
        }
    }
}
```

### Example: Adding Honey

```json
{
    "honey": {
        "name": "Honey",
        "synonyms": ["bee honey", "raw honey"],
        "category": ["sweetener", "base_ingredient"],
        "allergen": false,
        "allergen_type": null,
        "description": "Natural sweetener produced by bees"
    }
}
```

## Supported Categories

- **allergen** - Known allergen
- **base_ingredient** - Core ingredient
- **oil** - Oil or fat
- **preservative** - Food preservative
- **emulsifier** - Emulsifying agent
- **thickener** - Thickening agent
- **sweetener** - Sweetening agent
- **nutrient** - Vitamin or mineral
- **additive** - Food additive
- **flavor** - Flavoring

## Allergen Types

- `gluten` - Gluten-containing
- `dairy` - Dairy product
- `peanut` - Peanut allergen
- `tree_nuts` - Tree nut allergen
- `soy` - Soy allergen
- `fish` - Fish allergen
- `shellfish` - Shellfish allergen
- `sesame` - Sesame allergen
- `egg` - Egg allergen

## Matching Algorithms

### 1. Exact Matching
- Direct match against ingredient name
- Direct match against synonyms
- Case-insensitive and whitespace-normalized
- **Confidence:** 100%

### 2. Fuzzy Matching
- Uses Python's `SequenceMatcher` for similarity scoring
- Levenshtein distance-based comparison
- Configurable threshold (default: 0.8 or 80%)
- **Confidence:** Score × 100%

### Similarity Scoring

```
Query: "suger"
Match: "sugar"
Similarity: 80% (4 matching characters out of 5)
Result: Match found if threshold ≤ 80%
```

## Performance Characteristics

- **Database Load Time:** ~100ms
- **Single Ingredient Detection:** ~1-5ms
- **Full Text Detection (10-30 ingredients):** ~50-200ms
- **Memory Usage:** ~2-5MB for full database and synonyms

## Testing

Run the included test suite to validate functionality:

```bash
python test_ingredient_detector.py
```

Tests include:
- ✓ Database loading
- ✓ Text preprocessing
- ✓ Ingredient detection
- ✓ Fuzzy matching
- ✓ Search functionality

## Troubleshooting

### Database Not Found

```
⚠ Ingredient database not found at ingredients_database.json
```

**Solution:** Ensure `ingredients_database.json` is in the project root directory.

### No Matches Found

Common causes:
1. Very short ingredient names (< 2 characters)
2. Threshold too high for fuzzy matching
3. Ingredient not in database

**Solutions:**
- Increase database ingredients
- Lower fuzzy threshold (0.7-0.75)
- Add ingredient as new entry

### Low Match Rate

If match rate is below 80%:
1. Check text preprocessing - unusual formatting?
2. Verify fuzzy threshold settings
3. Review unmatched ingredients for patterns
4. Consider expanding database

## API Reference

### IngredientDetector

```python
class IngredientDetector:
    def __init__(self, db_path='ingredients_database.json')
    def detect_ingredients(ocr_text, enable_fuzzy=True, fuzzy_threshold=0.8) -> Dict
    def search_ingredient(query) -> Dict or None
```

### TextPreprocessor

```python
class TextPreprocessor:
    def preprocess(text) -> str
    def split_ingredients(text) -> List[str]
    def clean_ingredient(ingredient) -> str
```

### IngredientDatabase

```python
class IngredientDatabase:
    def __init__(self, db_path='ingredients_database.json')
    def load_database()
    def search_exact(query) -> Ingredient or None
    def search_fuzzy(query, threshold=0.8) -> Tuple[Ingredient, float] or None
    def get_all_ingredients() -> List[str]
```

## Future Enhancements

- Semantic embeddings for advanced similarity matching
- Multi-language ingredient detection
- Machine learning-based allergen prediction
- Real-time database updates
- Integration with external nutrition APIs
- Support for E-number food additives database
- Regional ingredient variations

## Conclusion

The Ingredient Detection System provides a robust, extensible foundation for accurate ingredient identification and allergen detection. With fuzzy matching for OCR errors, a comprehensive database, and an easy expansion mechanism, it enables reliable food safety analysis across various product categories.
