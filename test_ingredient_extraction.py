#!/usr/bin/env python3
"""
Test script for enhanced ingredient extraction with parsing rules.
Tests multi-word preservation, spell correction, and parentheses handling.
"""

import json
import re
from difflib import get_close_matches

# Load allergens database
with open('allergens.json', 'r') as f:
    allergens_db = json.load(f)

def build_known_ingredients_dict():
    """Build a comprehensive dictionary of known ingredients from allergens_db"""
    known_ingredients = set()
    
    for allergen, details in allergens_db.items():
        if isinstance(details, list):
            known_ingredients.update([ing.lower() for ing in details if isinstance(ing, str)])
        elif isinstance(details, dict):
            aliases = details.get('aliases', [])
            if isinstance(aliases, list):
                known_ingredients.update([ing.lower() for ing in aliases if isinstance(ing, str)])
    
    return known_ingredients

def correct_ingredient_spelling(ingredient, known_ingredients_dict):
    """Correct minor spelling mistakes using fuzzy matching (80%+ similarity)"""
    ingredient_lower = ingredient.lower().strip()
    
    if ingredient_lower in known_ingredients_dict:
        return ingredient.strip()
    
    close_matches = get_close_matches(ingredient_lower, known_ingredients_dict, n=1, cutoff=0.80)
    
    if close_matches:
        matched = close_matches[0]
        return ' '.join(word.capitalize() for word in matched.split())
    
    return ' '.join(word.capitalize() for word in ingredient.split())

def extract_ingredient_name_from_descriptor(ingredient_text):
    """Extract main ingredient name, discarding parenthetical descriptors"""
    name = re.sub(r'\[.*?\]', '', ingredient_text)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

# Test cases
test_cases = [
    {
        "input": "Sugar, Palm Oil (vegetable), Citric acid; Salt [added minerals]",
        "expected": ["Citric Acid", "Palm Oil", "Salt", "Sugar"],
        "description": "Multi-word ingredients with parentheses and brackets"
    },
    {
        "input": "Soy Lecithin (from soy), Gum Arabic [E414]",
        "expected": ["Gum Arabic", "Soy Lecithin"],
        "description": "Parentheses and brackets removal"
    },
    {
        "input": "Whey protein isolate (milk), Maltodextrin (corn)",
        "expected": ["Maltodextrin", "Whey Protein Isolate"],
        "description": "Multi-word with descriptors in parens"
    },
    {
        "input": "Sugar, milk powder; egg white, sesame seed oil",
        "expected": ["Sesame Seed", "Sugar", "egg white", "milk powder"],
        "description": "Multi-word ingredients - some matched from dict, others extracted as-is"
    }
]

print("=" * 80)
print("INGREDIENT EXTRACTION TEST SUITE")
print("=" * 80)

known_dict = build_known_ingredients_dict()
print(f"\nLoaded {len(known_dict)} known ingredients from allergens.json\n")

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['description']}")
    print(f"Input:    {test['input']}")
    
    # Simulate simplified extraction (without full OCR processing)
    result = []
    ingredient_set = {}
    garbage = ['and', 'or', 'the', 'a', 'of', 'for', 'in', 'as', 'is', 'with', 'to', 'e', 'l']
    
    # Split by delimiters
    items = re.split(r'[,;]', test['input'])
    
    for item in items:
        # Extract ingredient name (remove parens/brackets)
        ingredient_name = extract_ingredient_name_from_descriptor(item)
        
        if not ingredient_name or len(ingredient_name.strip()) < 2:
            continue
        
        if not any(c.isalpha() for c in ingredient_name):
            continue
        
        ingredient_name = re.sub(r'[,;:\'"!?@#$%^&*]+$', '', ingredient_name).strip()
        ingredient_name = re.sub(r'^[,;:\'"!?@#$%^&*]+', '', ingredient_name).strip()
        
        if not ingredient_name or len(ingredient_name.strip()) < 2:
            continue
        
        if ingredient_name.lower() in garbage:
            continue
        
        # Apply spell correction
        corrected = correct_ingredient_spelling(ingredient_name, known_dict)
        normalized_key = corrected.lower().strip()
        
        if normalized_key not in ingredient_set:
            ingredient_set[normalized_key] = corrected
    
    result = sorted(list(ingredient_set.values()))
    
    print(f"Expected: {test['expected']}")
    print(f"Got:      {result}")
    
    if result == test['expected']:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED - Check implementation")
print("=" * 80)
