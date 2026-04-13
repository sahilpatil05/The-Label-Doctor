"""
Named Entity Recognition (NER) Processor for Ingredient Extraction
Integrates spaCy for identifying ingredient entities, quantities, and attributes from OCR text
"""

import re
import warnings
from typing import List, Dict, Tuple, Optional

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
    # Try to load the English model
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy model 'en_core_web_sm' loaded successfully")
    except OSError:
        print("⚠ spaCy model 'en_core_web_sm' not found. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy model installed and loaded")
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠ spaCy not available. Install with: pip install spacy")
    nlp = None


class IngredientEntity:
    """Represents an identified ingredient entity with metadata"""
    
    def __init__(self, name: str, quantity: Optional[str] = None, unit: Optional[str] = None,
                 attributes: Optional[List[str]] = None, confidence: float = 1.0, entity_type: str = 'INGREDIENT'):
        """
        Args:
            name: Ingredient name
            quantity: Quantity value (e.g., "2.5")
            unit: Unit of measurement (e.g., "g", "ml", "tsp")
            attributes: List of modifiers/attributes (e.g., "organic", "raw", "roasted")
            confidence: Confidence score (0-1)
            entity_type: Type of entity (INGREDIENT, ALLERGEN, ADDITIVE, NUTRIENT, QUANTITY, PROCESSING)
        """
        self.name = name.strip()
        self.quantity = quantity
        self.unit = unit
        self.attributes = attributes or []
        self.confidence = confidence
        self.entity_type = entity_type
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'attributes': self.attributes,
            'confidence': self.confidence,
            'entity_type': self.entity_type,
            'full_name': self._build_full_name()
        }
    
    def _build_full_name(self) -> str:
        """Build full ingredient string with all components"""
        parts = []
        if self.attributes:
            parts.extend(self.attributes)
        if self.quantity and self.unit:
            parts.append(f"{self.quantity} {self.unit}")
        elif self.quantity:
            parts.append(self.quantity)
        parts.append(self.name)
        return ' '.join(parts)
    
    def __str__(self) -> str:
        return self._build_full_name()
    
    def __repr__(self) -> str:
        return f"IngredientEntity(name={self.name}, type={self.entity_type}, confidence={self.confidence})"


class IngredientNERProcessor:
    """Named Entity Recognition processor for ingredient extraction"""
    
    # Common units of measurement
    VALID_UNITS = {
        'weight': ['kg', 'g', 'mg', 'oz', 'lb', 'lbs', 'ounce', 'ounces', 'gram', 'grams',
                   'milligram', 'milligrams', 'kilogram', 'kilograms', 'pound', 'pounds'],
        'volume': ['ml', 'l', 'ul', 'dl', 'fl oz', 'cup', 'cups', 'gallon', 'gallons',
                   'liter', 'liters', 'milliliter', 'milliliters', 'pint', 'pints',
                   'tablespoon', 'tablespoons', 'tbsp', 'tsp', 'teaspoon', 'teaspoons'],
        'count': ['%', 'pcs', 'pieces', 'item', 'items', 'each', 'unit', 'units'],
        'abbreviations': ['ml', 'l', 'g', 'kg', 'oz', 'lb', 'tsp', 'tbsp', 'cup', 'fl']
    }
    
    # Common ingredient qualifiers and processing methods
    INGREDIENT_ATTRIBUTES = {
        'processing': ['roasted', 'baked', 'fried', 'dried', 'fermented', 'pasteurized',
                      'hydrolyzed', 'emulsified', 'powder', 'powdered', 'liquid', 'gel',
                      'extract', 'concentrate', 'refined', 'bleached', 'malted'],
        'origin': ['maltose', 'dextrose', 'sucrose', 'fructose', 'lactose', 'glucose',
                  'organic', 'non-gmo', 'genetically', 'wild', 'farm', 'free-range'],
        'quality': ['premium', 'high', 'pure', 'natural', 'artificial', 'synthetic',
                   'organic', 'raw', 'cooked', 'fresh', 'frozen', 'canned', 'aged'],
        'allergen_indicators': ['may contain', 'contains trace', 'processed in',
                               'manufactured', 'facility', 'cross-contamination']
    }
    
    # Common allergen-related keywords
    ALLERGEN_KEYWORDS = [
        'wheat', 'soy', 'soybean', 'milk', 'dairy', 'egg', 'nuts', 'peanut', 'sesame',
        'fish', 'shellfish', 'crustacean', 'tree nuts', 'gluten', 'sulfite', 'sulfites',
        'mustard', 'celery', 'lupin', 'mollusks', 'sulfur', 'preservative'
    ]
    
    # Food additive types
    ADDITIVE_KEYWORDS = {
        'colors': ['color', 'coloring', 'dye', 'red', 'yellow', 'blue', 'green', 'class'],
        'preservatives': ['preservative', 'e200', 'e300', 'benzoate', 'sorbate', 'nitrite', 'nitrate'],
        'emulsifiers': ['emulsifier', 'lecithin', 'e322', 'mono', 'diglyceride'],
        'thickeners': ['thickener', 'starch', 'gum', 'pectin', 'gelatin', 'agar'],
        'sweeteners': ['sweetener', 'aspartame', 'sucralose', 'saccharin', 'sorbitol', 'xylitol']
    }
    
    def __init__(self):
        """Initialize the NER processor"""
        self.nlp = nlp  # Use global spaCy model
        self.spacy_available = SPACY_AVAILABLE
    
    def process_ingredient_text(self, text: str) -> List[IngredientEntity]:
        """
        Process ingredient text using NER and pattern matching
        
        Args:
            text: Raw ingredient text from OCR
        
        Returns:
            List of IngredientEntity objects
        """
        if not text or not text.strip():
            return []
        
        ingredients = []
        
        # Split into individual ingredient items by common delimiters
        ingredient_items = self._split_ingredients(text)
        
        for item in ingredient_items:
            if not item.strip() or len(item.strip()) < 2:
                continue
            
            # Extract entity from item
            entity = self._extract_entity_from_item(item)
            if entity:
                ingredients.append(entity)
        
        return ingredients
    
    def _split_ingredients(self, text: str) -> List[str]:
        """
        Split ingredient text into individual ingredient items
        Respects parentheses and handles multiple delimiters
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        items = []
        current = ''
        paren_depth = 0
        
        for char in text:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
            elif char in (',', ';', '\n') and paren_depth == 0:
                if current.strip():
                    items.append(current.strip())
                current = ''
            else:
                current += char
        
        if current.strip():
            items.append(current.strip())
        
        return items
    
    def _extract_entity_from_item(self, item: str) -> Optional[IngredientEntity]:
        """
        Extract entity information from a single ingredient item
        Identifies: ingredient name, quantity, unit, attributes, and entity type
        """
        item = item.strip()
        if not item or len(item) < 2:
            return None
        
        # Extract quantity and unit
        quantity, unit, remaining = self._extract_quantity_and_unit(item)
        
        # Use spaCy for NER if available
        if self.spacy_available and self.nlp:
            return self._extract_with_spacy_ner(remaining, quantity, unit)
        else:
            return self._extract_with_pattern_matching(remaining, quantity, unit)
    
    def _extract_quantity_and_unit(self, text: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extract quantity and unit from ingredient text
        
        Returns:
            Tuple of (quantity, unit, remaining_text)
        """
        # Pattern for quantity and unit extraction
        # Matches: "2.5 ml", "50g", "1/2 cup", etc.
        quantity_pattern = r'^([0-9]+(?:[.,/][0-9]+)*)\s*([a-zA-Z%]+)?[\s\-]*(.*)$'
        
        match = re.match(quantity_pattern, text)
        if match:
            quantity = match.group(1).replace(',', '.')
            unit = match.group(2) if match.group(2) else None
            remaining = match.group(3) if match.group(3) else text
            
            # Normalize units
            if unit:
                unit = unit.lower()
                # Check if it's a valid unit abbreviation
                all_units = []
                for unit_list in self.VALID_UNITS.values():
                    all_units.extend(unit_list)
                if unit not in all_units:
                    unit = None
            
            return quantity, unit, remaining.strip()
        
        return None, None, text
    
    def _extract_with_spacy_ner(self, text: str, quantity: Optional[str],
                               unit: Optional[str]) -> Optional[IngredientEntity]:
        """
        Extract entity using spaCy NER
        """
        try:
            doc = self.nlp(text)
            
            # Extract entities
            ingredient_name = text  # Default to full text
            entity_type = 'INGREDIENT'
            confidence = 1.0
            attributes = []
            
            # Look for named entities
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'FOOD']:
                    ingredient_name = ent.text
                    confidence = 0.95
                    break
            
            # Extract attributes
            for token in doc:
                if token.pos_ == 'ADJ':  # Adjectives often describe ingredients
                    if token.text.lower() in [attr for attrs in self.INGREDIENT_ATTRIBUTES.values() for attr in attrs]:
                        attributes.append(token.text.lower())
            
            # Classify entity type
            ingredient_lower = ingredient_name.lower()
            if any(allergen in ingredient_lower for allergen in self.ALLERGEN_KEYWORDS):
                entity_type = 'ALLERGEN'
            elif any(additive in ingredient_lower for additive_list in self.ADDITIVE_KEYWORDS.values() for additive in additive_list):
                entity_type = 'ADDITIVE'
            
            # Create ingredient entity
            return IngredientEntity(
                name=ingredient_name,
                quantity=quantity,
                unit=unit,
                attributes=attributes,
                confidence=confidence,
                entity_type=entity_type
            )
        except Exception as e:
            print(f"spaCy NER error: {e}")
            return self._extract_with_pattern_matching(text, quantity, unit)
    
    def _extract_with_pattern_matching(self, text: str, quantity: Optional[str],
                                      unit: Optional[str]) -> Optional[IngredientEntity]:
        """
        Extract entity using pattern matching (fallback)
        """
        text = text.strip()
        if not text:
            return None
        
        attributes = []
        entity_type = 'INGREDIENT'
        
        # Extract attributes (qualifiers before ingredient name)
        text_lower = text.lower()
        for attr_category, attr_list in self.INGREDIENT_ATTRIBUTES.items():
            for attr in attr_list:
                if attr in text_lower:
                    attributes.append(attr)
                    text = re.sub(r'\b' + attr + r'\b', '', text, flags=re.IGNORECASE).strip()
        
        # Remove parenthetical content for cleaner ingredient name
        ingredient_name = re.sub(r'\([^)]*\)', '', text).strip()
        if not ingredient_name:
            ingredient_name = text
        
        # Classify entity type
        if any(allergen in ingredient_name.lower() for allergen in self.ALLERGEN_KEYWORDS):
            entity_type = 'ALLERGEN'
        elif any(additive in ingredient_name.lower() for additive_list in self.ADDITIVE_KEYWORDS.values() for additive in additive_list):
            entity_type = 'ADDITIVE'
        
        return IngredientEntity(
            name=ingredient_name,
            quantity=quantity,
            unit=unit,
            attributes=attributes,
            confidence=0.8,
            entity_type=entity_type
        )
    
    def extract_allergen_statements(self, text: str) -> Dict[str, List[str]]:
        """
        Extract allergen-related statements from text
        
        Returns:
            Dictionary with categories of allergen information
        """
        allergen_info = {
            'contains': [],
            'may_contain': [],
            'processed_in': [],
            'not_suitable_for': []
        }
        
        text_lower = text.lower()
        
        # Look for allergen statements
        contains_pattern = r'(?:contains?|made with)\s*:?\s*([^.;,\n]*)'
        may_contain_pattern = r'(?:may contain|may include|trace|traces?)\s*:?\s*([^.;,\n]*)'
        processed_pattern = r'(?:processed|manufactured|produced)\s+(?:in|on|with)\s*:?\s*([^.;,\n]*)'
        
        # Extract statements
        for match in re.finditer(contains_pattern, text_lower, re.IGNORECASE):
            allergen_info['contains'].append(match.group(1).strip())
        
        for match in re.finditer(may_contain_pattern, text_lower, re.IGNORECASE):
            allergen_info['may_contain'].append(match.group(1).strip())
        
        for match in re.finditer(processed_pattern, text_lower, re.IGNORECASE):
            allergen_info['processed_in'].append(match.group(1).strip())
        
        return allergen_info
    
    def get_entity_type_label(self, entity_type: str) -> Dict[str, object]:
        """
        Get a human-readable label and risk level for entity type
        """
        type_info = {
            'INGREDIENT': {'label': 'Active Ingredient', 'risk': 'high', 'color': 'red'},
            'ALLERGEN': {'label': 'Allergen', 'risk': 'critical', 'color': 'red'},
            'ADDITIVE': {'label': 'Food Additive', 'risk': 'medium', 'color': 'orange'},
            'NUTRIENT': {'label': 'Nutrient', 'risk': 'low', 'color': 'green'},
            'QUANTITY': {'label': 'Quantity Marker', 'risk': 'none', 'color': 'gray'},
            'PROCESSING': {'label': 'Processing Method', 'risk': 'low', 'color': 'yellow'}
        }
        return type_info.get(entity_type, {'label': 'Unknown', 'risk': 'unknown', 'color': 'gray'})


def initialize_ner_processor() -> IngredientNERProcessor:
    """
    Initialize and return NER processor
    Handles warnings if spaCy is not available
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return IngredientNERProcessor()


# Initialize global NER processor
try:
    ner_processor = initialize_ner_processor()
    NER_AVAILABLE = ner_processor.spacy_available
    print(f"✓ NER Processor initialized - spaCy available: {NER_AVAILABLE}")
except Exception as e:
    print(f"⚠ NER Processor initialization warning: {e}")
    ner_processor = None
    NER_AVAILABLE = False
