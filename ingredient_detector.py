"""
Ingredient Detection Engine
Detects ingredients from OCR text and matches them against a comprehensive database
"""

import json
import re
import os
from typing import List, Dict, Tuple, Optional, Union
from difflib import SequenceMatcher
import warnings


class Ingredient:
    """Represents a detected ingredient with metadata"""
    
    def __init__(self, name: str, synonyms: List[str], category: Union[List[str], str],
                 allergen: bool = False, allergen_type: str = None, description: str = ""):
        """
        Args:
            name: Official ingredient name from database
            synonyms: List of alternative names
            category: Category or list of categories
            allergen: Whether this is an allergen
            allergen_type: Type of allergen (if applicable)
            description: Brief description
        """
        self.name = name
        self.synonyms = synonyms if isinstance(synonyms, list) else [synonyms]
        self.category = category if isinstance(category, list) else [category]
        self.allergen = allergen
        self.allergen_type = allergen_type
        self.description = description
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'synonyms': self.synonyms,
            'category': self.category,
            'allergen': self.allergen,
            'allergen_type': self.allergen_type,
            'description': self.description
        }
    
    def __repr__(self):
        return f"Ingredient({self.name}, allergen={self.allergen})"


class TextPreprocessor:
    """Preprocesses OCR text for ingredient detection"""
    
    def __init__(self):
        """Initialize text preprocessor"""
        # Common multi-word ingredients that should be preserved
        self.multi_word_ingredients = [
            'palm oil', 'soybean oil', 'sunflower oil', 'olive oil', 'canola oil', 'corn oil', 'coconut oil',
            'wheat flour', 'whole wheat', 'wheat gluten', 'durum wheat',
            'soy lecithin', 'sunflower lecithin',
            'citric acid', 'sodium benzoate', 'potassium sorbate',
            'xanthan gum', 'guar gum',
            'natural flavors', 'artificial flavors', 'natural flavor', 'artificial flavor',
            'vitamin a', 'vitamin c', 'vitamin d', 'vitamin d2', 'vitamin d3',
            'tree nuts', 'tree nut',
            'high fructose corn syrup', 'corn syrup',
            'whey protein', 'milk protein',
            'sesame seed', 'sesame oil',
            'soy protein', 'soy sauce',
            'ferrous sulfate', 'ferric oxide', 'iron oxide',
            'sodium chloride', 'salt',
            'baking powder', 'baking soda',
            'vanilla extract', 'vanilla bean',
            'cocoa powder', 'chocolate liquor',
            'monosodium glutamate', 'msg',
            'textured vegetable protein', 'tvp',
            'beef gelatin',
            'red 40', 'yellow 5', 'yellow 6', 'blue 1', 'green 3',
            'milk solids', 'milk powder', 'dried milk', 'milk fat',
            'egg white', 'egg yolk',
            'peanut butter', 'peanut oil', 'arachis oil',
            'vital wheat gluten', 'wheat protein',
            'emulsifier e322', 'e330', 'e411', 'e412', 'e415',
            'fd&c', 'fdc'
        ]
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess text for ingredient detection
        
        Args:
            text: Raw OCR text
        
        Returns:
            Cleaned text optimized for ingredient detection
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common non-ingredient text
        stop_patterns = [
            r'ingredients?\s*:?\s*',
            r'allergens?\s*:?\s*',
            r'contains?\s*:?\s*',
            r'may\s+contain\s*:?\s*',
            r'manufactured\s+on\s*:?\s*',
            r'processed\s+in\s*:?\s*',
            r'nutrition\s+facts.*',
            r'directions?\s*:?\s*',
        ]
        
        for pattern in stop_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def split_ingredients(self, text: str) -> List[str]:
        """
        Split text into individual ingredients
        Preserves multi-word ingredients
        
        Args:
            text: Preprocessed ingredient text
        
        Returns:
            List of individual ingredients
        """
        # First pass: replace multi-word ingredients with placeholders
        placeholders = {}
        temp_text = text.lower()
        
        for i, multi_word in enumerate(sorted(self.multi_word_ingredients, key=len, reverse=True)):
            placeholder = f"__PLACEHOLDER_{i}__"
            # Use word boundaries for matching
            pattern = r'\b' + re.escape(multi_word) + r'\b'
            if re.search(pattern, temp_text):
                temp_text = re.sub(pattern, placeholder, temp_text)
                placeholders[placeholder] = multi_word
        
        # Split by common delimiters
        # Split by comma, semicolon, newline, "and", "or"
        temp_text = re.sub(r'[,;/\n]', ' | ', temp_text)
        temp_text = re.sub(r'\s+and\s+', ' | ', temp_text)
        temp_text = re.sub(r'\s+or\s+', ' | ', temp_text)
        
        # Split by pipe delimiter
        parts = temp_text.split('|')
        
        # Restore multi-word ingredients
        ingredients = []
        for part in parts:
            part = part.strip()
            
            # Restore placeholders
            for placeholder, original in placeholders.items():
                part = part.replace(placeholder, original)
            
            if part:
                ingredients.append(part)
        
        return ingredients
    
    def clean_ingredient(self, ingredient: str) -> str:
        """
        Clean individual ingredient string
        
        Args:
            ingredient: Raw ingredient string
        
        Returns:
            Cleaned ingredient string
        """
        # Remove content in parentheses (e.g., "(contains milk)" stays but "(1.0, sulphate)" is removed)
        # Keep allergen info in parentheses, remove quantity/descriptor info
        
        # First remove quantity-related parentheses
        ingredient = re.sub(r'\([\d.,%\-]+(?:\s*(?:g|ml|oz|kg|l|tbsp|tsp|cup|cups|%))*\)', '', ingredient)
        
        # Remove other descriptive stuff in parentheses
        ingredient = re.sub(r'\([^)]*\)', '', ingredient)
        
        # Remove special characters except hyphens (e.g., 90%, *, &)
        ingredient = re.sub(r'[*&@#$%^!]', '', ingredient)
        
        # Remove leading/trailing numbers
        ingredient = re.sub(r'^\d+\s*', '', ingredient)
        ingredient = re.sub(r'\s*\d+$', '', ingredient)
        
        # Clean whitespace
        ingredient = re.sub(r'\s+', ' ', ingredient).strip()
        
        return ingredient


class IngredientDatabase:
    """Manages ingredient database and lookups"""
    
    def __init__(self, db_path: str = 'ingredients_database.json'):
        """
        Initialize ingredient database
        
        Args:
            db_path: Path to ingredients database JSON file
        """
        self.db_path = db_path
        self.ingredients: Dict[str, Ingredient] = {}
        self.all_synonyms: Dict[str, str] = {}  # Maps synonym to official name
        self.load_database()
    
    def load_database(self):
        """Load ingredients from JSON database"""
        try:
            # Try to find database in multiple locations
            search_paths = [
                self.db_path,
                os.path.join(os.path.dirname(__file__), self.db_path),
                os.path.join(os.path.dirname(__file__), '..', self.db_path),
            ]
            
            db_file = None
            for path in search_paths:
                if os.path.exists(path):
                    db_file = path
                    break
            
            if not db_file:
                print(f"⚠ Ingredient database not found at {self.db_path}")
                print(f"   Searched: {search_paths}")
                return
            
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ Loading ingredients database from {db_file}")
            
            # Parse ingredients
            for key, ing_data in data.get('ingredients', {}).items():
                ingredient = Ingredient(
                    name=ing_data.get('name', key),
                    synonyms=ing_data.get('synonyms', []),
                    category=ing_data.get('category', ''),
                    allergen=ing_data.get('allergen', False),
                    allergen_type=ing_data.get('allergen_type'),
                    description=ing_data.get('description', '')
                )
                
                self.ingredients[key] = ingredient
                
                # Build synonym map
                self.all_synonyms[ingredient.name.lower()] = key
                for synonym in ingredient.synonyms:
                    self.all_synonyms[synonym.lower()] = key
            
            print(f"✓ Loaded {len(self.ingredients)} ingredients with {len(self.all_synonyms)} synonyms")
        
        except Exception as e:
            print(f"✗ Error loading ingredient database: {e}")
    
    def search_exact(self, query: str) -> Optional[Ingredient]:
        """
        Exact search in database
        
        Args:
            query: Search term (lowercased)
        
        Returns:
            Ingredient if found, None otherwise
        """
        query = query.lower().strip()
        
        # Try exact match
        if query in self.all_synonyms:
            key = self.all_synonyms[query]
            return self.ingredients.get(key)
        
        return None
    
    def search_fuzzy(self, query: str, threshold: float = 0.8) -> Optional[Tuple[Ingredient, float]]:
        """
        Fuzzy search using sequence matching
        
        Args:
            query: Search term
            threshold: Similarity threshold (0-1)
        
        Returns:
            (Ingredient, similarity_score) or None
        """
        query = query.lower().strip()
        
        best_match = None
        best_score = 0
        
        # Search across all ingredient names and synonyms
        for ingredient_key, ingredient in self.ingredients.items():
            # Check name
            name_score = SequenceMatcher(None, query, ingredient.name.lower()).ratio()
            if name_score > best_score:
                best_score = name_score
                best_match = ingredient
            
            # Check synonyms
            for synonym in ingredient.synonyms:
                syn_score = SequenceMatcher(None, query, synonym.lower()).ratio()
                if syn_score > best_score:
                    best_score = syn_score
                    best_match = ingredient
        
        if best_score >= threshold:
            return (best_match, best_score)
        
        return None
    
    def get_all_ingredients(self) -> List[str]:
        """Get list of all ingredient names"""
        return list(self.ingredients.keys())


class IngredientDetector:
    """Main ingredient detection engine"""
    
    def __init__(self, db_path: str = 'ingredients_database.json'):
        """
        Initialize detector
        
        Args:
            db_path: Path to ingredients database
        """
        self.preprocessor = TextPreprocessor()
        self.database = IngredientDatabase(db_path)
    
    def detect_ingredients(self, ocr_text: str, enable_fuzzy: bool = True, 
                          fuzzy_threshold: float = 0.8) -> Dict:
        """
        Detect ingredients from OCR text
        
        Args:
            ocr_text: Raw OCR extracted text
            enable_fuzzy: Whether to use fuzzy matching
            fuzzy_threshold: Threshold for fuzzy matching (0-1)
        
        Returns:
            Dictionary with detected ingredients and metadata
        """
        # Preprocess text
        cleaned_text = self.preprocessor.preprocess(ocr_text)
        
        # Split into individual ingredients
        ingredient_items = self.preprocessor.split_ingredients(cleaned_text)
        
        detected = []
        unmatched = []
        
        for item in ingredient_items:
            # Clean ingredient
            clean_name = self.preprocessor.clean_ingredient(item)
            
            if not clean_name or len(clean_name) < 2:
                continue
            
            # Try exact match first
            ingredient = self.database.search_exact(clean_name)
            
            if ingredient:
                detected.append({
                    'original_text': item,
                    'cleaned_text': clean_name,
                    'matched_name': ingredient.name,
                    'database_key': ingredient.name.lower(),
                    'category': ingredient.category,
                    'allergen': ingredient.allergen,
                    'allergen_type': ingredient.allergen_type,
                    'description': ingredient.description,
                    'match_confidence': 1.0,
                    'match_type': 'exact'
                })
            elif enable_fuzzy:
                # Try fuzzy match
                result = self.database.search_fuzzy(clean_name, threshold=fuzzy_threshold)
                if result:
                    ingredient, score = result
                    detected.append({
                        'original_text': item,
                        'cleaned_text': clean_name,
                        'matched_name': ingredient.name,
                        'database_key': ingredient.name.lower(),
                        'category': ingredient.category,
                        'allergen': ingredient.allergen,
                        'allergen_type': ingredient.allergen_type,
                        'description': ingredient.description,
                        'match_confidence': score,
                        'match_type': 'fuzzy'
                    })
                else:
                    unmatched.append({
                        'text': clean_name,
                        'original_text': item
                    })
            else:
                unmatched.append({
                    'text': clean_name,
                    'original_text': item
                })
        
        # Extract allergen information
        allergens_found = [d for d in detected if d['allergen']]
        allergen_types = list(set([a['allergen_type'] for a in allergens_found if a['allergen_type']]))
        
        return {
            'total_detected': len(detected),
            'total_unmatched': len(unmatched),
            'detected_ingredients': detected,
            'unmatched_ingredients': unmatched,
            'allergens_found': len(allergens_found),
            'allergen_types': allergen_types,
            'categories': list(set([cat for d in detected for cat in d['category']])),
            'summary': {
                'total': len(ingredient_items),
                'matched': len(detected),
                'unmatched': len(unmatched),
                'match_rate': f"{(len(detected) / len(ingredient_items) * 100):.1f}%" if ingredient_items else "0%"
            }
        }
    
    def search_ingredient(self, query: str) -> Optional[Dict]:
        """
        Search for a specific ingredient in the database
        
        Args:
            query: Ingredient name or synonym
        
        Returns:
            Ingredient details or None
        """
        ingredient = self.database.search_exact(query)
        
        if not ingredient:
            result = self.database.search_fuzzy(query, threshold=0.7)
            if result:
                ingredient, score = result
        
        if ingredient:
            return ingredient.to_dict()
        
        return None


# Initialize global detector
try:
    ingredient_detector = IngredientDetector()
    INGREDIENT_DETECTOR_AVAILABLE = True
    print("✓ Ingredient detector initialized successfully")
except Exception as e:
    print(f"⚠ Ingredient detector initialization warning: {e}")
    ingredient_detector = None
    INGREDIENT_DETECTOR_AVAILABLE = False
