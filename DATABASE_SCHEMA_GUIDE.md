# Ingredient Database Schema & Expansion Guide

## Database Structure

### File Location
```
ingredients_database.json
```

### Root Structure
```json
{
    "metadata": { ... },
    "ingredients": { ... }
}
```

## Metadata Section

```json
{
    "metadata": {
        "version": "1.0",
        "last_updated": "2026-04-01",
        "total_ingredients": 54,
        "source": "Manual curation + food allergen databases",
        "license": "Open source",
        "maintainer": "Label Doctor Team"
    }
}
```

**Fields:**
- `version` - Database schema version
- `last_updated` - Last modification date (YYYY-MM-DD)
- `total_ingredients` - Count of ingredients
- `source` - Where ingredients were sourced
- `license` - License information
- `maintainer` - Database maintainer

## Ingredient Entry Schema

### Complete Entry Example

```json
{
    "wheat": {
        "name": "Wheat",
        "synonyms": [
            "wheat flour",
            "whole wheat",
            "wheat gluten",
            "durum wheat",
            "whole grain wheat",
            "wheat grain",
            "wheat starch"
        ],
        "category": ["allergen", "base_ingredient"],
        "allergen": true,
        "allergen_type": "gluten",
        "description": "Cereal grain containing gluten protein, commonly used in baking and grains"
    }
}
```

### Field Reference

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| **Key** | string | Yes | `wheat` | Kebab-case ID (no spaces or special chars) |
| **name** | string | Yes | `"Wheat"` | Official ingredient name (title case) |
| **synonyms** | array | Yes | `["wheat flour", ...]` | Alternative names and variations |
| **category** | string\|array | Yes | `"allergen"` or `["allergen", "base_ingredient"]` | One or more categories |
| **allergen** | boolean | Yes | `true` or `false` | Whether it's a known allergen |
| **allergen_type** | string\|null | No | `"gluten"` | Only if allergen=true |
| **description** | string | Yes | `"Cereal grain..."` | Brief description (100-200 chars) |

## Supported Categories

### Primary Categories

| Category | Use Cases |
|----------|-----------|
| `allergen` | Recognized allergen (must have allergen_type) |
| `base_ingredient` | Core ingredient (sugar, salt, flour, etc.) |
| `oil` | Oil or fat (palm, olive, soybean, etc.) |
| `preservative` | Food preservative (citric acid, benzoate, etc.) |
| `emulsifier` | Emulsifying agent (lecithin, mono-glycerides, etc.) |
| `thickener` | Thickening agent (xanthan gum, guar gum, etc.) |
| `sweetener` | Sweetening agent (aspartame, sucralose, etc.) |
| `nutrient` | Vitamin or mineral (vitamin A, iron oxide, etc.) |
| `additive` | Other food additive (not preservative) |
| `flavor` | Flavoring (vanilla, natural flavors, etc.) |

### Category Assignment Rules

- **Always categorize** - Every ingredient must have at least one category
- **Multiple categories** - Use array if multiple apply
- **Allergen + type** - Always include allergen_type if allergen=true
- **At least one** - Never leave category empty

### Category Examples

```json
{
    "wheat": {
        "name": "Wheat",
        "category": ["allergen", "base_ingredient"],
        "allergen": true,
        "allergen_type": "gluten"
    },
    "palm_oil": {
        "name": "Palm Oil",
        "category": ["oil", "additive"],
        "allergen": false
    },
    "xanthan_gum": {
        "name": "Xanthan Gum",
        "category": ["thickener", "additive"],
        "allergen": false
    },
    "sodium_benzoate": {
        "name": "Sodium Benzoate",
        "category": ["preservative", "additive"],
        "allergen": false
    }
}
```

## Supported Allergen Types

### Major Allergens

| Type | Description | Examples |
|------|-------------|----------|
| `gluten` | Gluten-containing grains | Wheat, barley, rye, gluten |
| `dairy` | Milk-based products | Milk, whey, casein, butter |
| `egg` | Egg-based products | Egg, egg white, egg yolk |
| `peanut` | Peanut allergen | Peanut, arachis oil, monkey nuts |
| `tree_nuts` | Tree nut allergens | Almonds, cashews, walnuts, etc. |
| `soy` | Soy-based products | Soy, soy lecithin, soy protein |
| `fish` | Fish-based products | Fish, anchovies, fish sauce |
| `shellfish` | Shellfish allergens | Shrimp, crab, lobster, clam |
| `sesame` | Sesame seeds/oil | Sesame seeds, sesame oil |
| `mustard` | Mustard products | Mustard seed, mustard powder |
| `sulfites` | Sulfite preservatives | Sulfur dioxide, metabisulfite |

### Assignment Rules

- **Only for allergens** - allergen_type only if allergen=true
- **Specific types** - Use standardized types from the list above
- **One per ingredient** - Each ingredient gets one allergen type
- **Null if not allergen** - Set to null or omit if allergen=false

## Expansion: Adding New Ingredients

### Step 1: Identify Need

Additions needed when:
- OCR frequently misses ingredient
- Test results show low match rate
- User-submitted missing ingredient
- New product format/category

### Step 2: Create Entry

Template:
```json
{
    "ingredient_key": {
        "name": "Official Name",
        "synonyms": ["variation1", "variation2", "variation3"],
        "category": ["primary_category"],
        "allergen": false,
        "allergen_type": null,
        "description": "Brief description"
    }
}
```

### Step 3: Guidelines

**Key (field name):**
- Lowercase
- Underscores for spaces
- No special characters
- Unique identifier

**Name:**
- Title case
- Common/official name
- 1-3 words typically

**Synonyms:**
- Common variations
- Regional names
- Abbreviations
- Misspellings to support
- Include at least 3

**Description:**
- 50-150 characters
- Clear and concise
- Include usage context if relevant

### Step 4: Real-World Examples

#### Example 1: Adding Honey

```json
{
    "honey": {
        "name": "Honey",
        "synonyms": [
            "bee honey",
            "raw honey",
            "honeycomb",
            "honey powder",
            "honey extract"
        ],
        "category": ["sweetener", "base_ingredient"],
        "allergen": false,
        "allergen_type": null,
        "description": "Natural sweetener produced by honeybees from flower nectar"
    }
}
```

#### Example 2: Adding Gelatin

```json
{
    "gelatin": {
        "name": "Gelatin",
        "synonyms": [
            "animal gelatin",
            "beef gelatin",
            "pork gelatin",
            "gelatin powder",
            "gel"
        ],
        "category": ["base_ingredient", "additive"],
        "allergen": false,
        "allergen_type": null,
        "description": "Protein derived from collagen, used as gelling agent in desserts and candies"
    }
}
```

#### Example 3: Adding Tree Nut

```json
{
    "almond": {
        "name": "Almond",
        "synonyms": [
            "almond meal",
            "almond flour",
            "sliced almonds",
            "almond powder",
            "ground almond"
        ],
        "category": ["allergen", "base_ingredient", "nutrient"],
        "allergen": true,
        "allergen_type": "tree_nuts",
        "description": "Tree nut from almond tree, high in protein and healthy fats"
    }
}
```

#### Example 4: Adding New Additive

```json
{
    "tartaric_acid": {
        "name": "Tartaric Acid",
        "synonyms": [
            "cream of tartar",
            "potassium bitartrate",
            "tartrate",
            "tartaric acid salt"
        ],
        "category": ["preservative", "additive"],
        "allergen": false,
        "allergen_type": null,
        "description": "Organic acid naturally found in grapes, used as preservative and pH regulator"
    }
}
```

## Database Maintenance

### Regular Tasks

**Weekly:**
- Review unmatched ingredients from scans
- Identify frequent OCR errors
- Note user submissions

**Monthly:**
- Add 10-20 high-demand ingredients
- Update synonyms based on patterns
- Review allergen accuracy

**Quarterly:**
- Full database audit
- Update metadata
- Test all entries
- Verify allergen classifications

### Audit Checklist

- [ ] All required fields present
- [ ] No duplicate entries (by key or name)
- [ ] Allergen entries have allergen_type
- [ ] Non-allergen entries have allergen_type as null
- [ ] Synonyms are variations, not duplicates
- [ ] Categories are from approved list
- [ ] No typos in descriptions
- [ ] Grammar and capitalization correct

### Duplicate Prevention

Keep log of:
```json
{
    "key": "ingredient_key",
    "name": "Ingredient Name",
    "date_added": "2026-04-01",
    "added_by": "team_member",
    "reason": "Frequently unmatched in scans"
}
```

## Database Statistics

### Current State
- **Total Ingredients:** 54
- **Total Synonyms:** 220+
- **Allergen Entries:** 16
- **Categories Represented:** 10
- **Average Synonyms/Ingredient:** 4.1

### Coverage

**Allergens:** 16/14 major allergens
- ✓ Gluten (wheat, barley)
- ✓ Dairy (milk, whey, casein)
- ✓ Egg
- ✓ Peanut
- ✓ Tree Nuts
- ✓ Soy
- ✓ Fish
- ✓ Shellfish
- ✓ Sesame

**Base Ingredients:** 8
- Sugar, Salt, Water, Starch, Flour, Yeast, etc.

**Oils & Fats:** 10
- Palm, soybean, sunflower, olive, canola, corn, coconut, etc.

**Additives:** 20+
- Preservatives, emulsifiers, thickeners, sweeteners, flavors

## Database Query Examples

### Search by Category

```python
allergens = [ing for ing in db.ingredients.values() if 'allergen' in ing.category]
preservatives = [ing for ing in db.ingredients.values() if 'preservative' in ing.category]
```

### Search by Allergen Type

```python
gluten_items = [ing for ing in db.ingredients.values() if ing.allergen_type == 'gluten']
dairy_items = [ing for ing in db.ingredients.values() if ing.allergen_type == 'dairy']
```

### Find Entries with Multiple Categories

```python
multi_category = [ing for ing in db.ingredients.values() if len(ing.category) > 1]
```

## Performance Notes

- **Load Time:** ~100ms (54 ingredients, 220+ synonyms)
- **Exact Search:** O(1) - Direct lookup
- **Fuzzy Search:** O(n) - All ingredients compared
- **Memory:** ~2-5MB for full database

### Scaling

Current database supports:
- **100+ ingredients** - ~200-250ms load time
- **500+ ingredients** - ~500-800ms load time
- **1000+ ingredients** - ~1-2 seconds load time

For large-scale use, consider:
1. Database indexing
2. Search caching
3. Lazy loading categories
4. Paginated access

## Format Validation

### JSON Schema

```json
{
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["version", "last_updated", "total_ingredients"]
        },
        "ingredients": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["name", "synonyms", "category", "allergen", "description"],
                "properties": {
                    "name": { "type": "string" },
                    "synonyms": { 
                        "type": "array",
                        "items": { "type": "string" },
                        "minItems": 1
                    },
                    "category": { 
                        "oneOf": [
                            { "type": "string" },
                            { "type": "array" }
                        ]
                    },
                    "allergen": { "type": "boolean" },
                    "allergen_type": { 
                        "oneOf": [
                            { "type": "string" },
                            { "type": "null" }
                        ]
                    },
                    "description": { "type": "string" }
                }
            }
        }
    }
}
```

## Troubleshooting

### Issue: Low Match Rate

**Diagnosis:**
```bash
# Check unmatched ingredients
data = json.load(open('ingredients_database.json'))
print(f"Total ingredients: {len(data['ingredients'])}")

# Test with known ingredient
detector.search_ingredient('unknown_ingredient')
```

**Solution:**
1. Review unmatched items
2. Identify patterns
3. Add missing ingredients
4. Adjust fuzzy threshold

### Issue: Duplicate Entries

**Detection:**
```python
names = [ing['name'].lower() for ing in db.ingredients.values()]
duplicates = [name for name in names if names.count(name) > 1]
```

**Prevention:**
- Check before adding
- Use consistent naming
- Log additions

### Issue: Synonym Conflicts

**Example:**
```json
{
    "corn": { "name": "Corn", "synonyms": ["corn oil"] },
    "corn_oil": { "name": "Corn Oil", "synonyms": ["corn"] }
}
```

**Solution:**
- Keep synonyms specific
- Avoid full ingredient names as synonyms
- Test matching logic

## Backup & Recovery

### Regular Backups

```bash
# Daily backup
cp ingredients_database.json ingredients_database.backup.json

# Versioned backup
cp ingredients_database.json ingredients_database.v$(date +%Y%m%d).json
```

### Version Control

Use Git to track changes:
```bash
git add ingredients_database.json
git commit -m "Add honey and tartaric acid ingredients"
```

## Future Enhancements

1. **Nutritional Info** - Add calories, protein, carbs, fats
2. **Origins** - Track ingredient source countries
3. **Certifications** - Organic, fair-trade, GMO-free flags
4. **Pricing** - Cost per unit
5. **Supply Chain** - Manufacturer information
6. **EFSA Codes** - E-number additives
7. **Multilingual** - Support other languages
8. **ML Integration** - Auto-categorization

---

**Database Version:** 1.0
**Last Updated:** 2026-04-01
**Status:** Production Ready
**Maintenance:** Ongoing
