"""
Advanced OCR Pipeline for Food Label Scanning
Comprehensive image preprocessing, text extraction, and ingredient detection
"""

import cv2
import numpy as np
import easyocr
import re
from typing import List, Dict, Tuple, Optional
from PIL import Image
import io
import base64
from skimage import transform, restoration, filters
import warnings


class ImagePreprocessor:
    """Advanced image preprocessing for food label OCR"""
    
    def __init__(self, target_size=(1200, 1600)):
        """
        Initialize preprocessor
        
        Args:
            target_size: Target image size for processing
        """
        self.target_size = target_size
    
    def load_image(self, image_input) -> np.ndarray:
        """
        Load image from various input formats
        
        Args:
            image_input: File path, numpy array, base64, or PIL Image
        
        Returns:
            numpy array in BGR format
        """
        if isinstance(image_input, str) and image_input.startswith('/'):
            # File path
            img = cv2.imread(image_input)
            if img is None:
                raise ValueError(f"Cannot read image from {image_input}")
            return img
        
        elif isinstance(image_input, str):
            # Base64 string
            try:
                if ',' in image_input:
                    image_input = image_input.split(',')[1]
                image_bytes = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise ValueError(f"Cannot decode base64 image: {e}")
        
        elif isinstance(image_input, Image.Image):
            # PIL Image
            if image_input.mode == 'RGBA':
                image_input = image_input.convert('RGB')
            return cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        
        elif isinstance(image_input, np.ndarray):
            # Numpy array (assume BGR)
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                return image_input.copy()
            raise ValueError("Invalid image array shape")
        
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
    
    def resize_image(self, image: np.ndarray, scale_factor: float = 1.5) -> np.ndarray:
        """
        Upscale image for better OCR accuracy
        
        Args:
            image: Input image
            scale_factor: Upscaling factor (1.5-2.0 recommended)
        
        Returns:
            Upscaled image
        """
        height, width = image.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Use INTER_CUBIC for upscaling
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        print(f"[Preprocessing] Upscaled image: {width}x{height} → {new_width}x{new_height}")
        return resized
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image
        
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("[Preprocessing] Converted to grayscale")
            return gray
        return image
    
    def denoise_image(self, image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Remove noise while preserving edges
        
        Args:
            image: Input image
            strength: Denoising strength (1-20)
        
        Returns:
            Denoised image
        """
        # Use bilateral filter to denoise while preserving edges
        denoised = cv2.bilateralFilter(image, 9, strength, strength)
        print(f"[Preprocessing] Applied bilateral denoising (strength={strength})")
        return denoised
    
    def apply_adaptive_thresholding(self, image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text extraction
        
        Args:
            image: Grayscale image
        
        Returns:
            Binary image
        """
        # Adaptive thresholding works better for varying lighting
        binary = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )
        print("[Preprocessing] Applied adaptive thresholding")
        return binary
    
    def sharpen_image(self, image: np.ndarray, strength: float = 1.5) -> np.ndarray:
        """
        Sharpen image to enhance text
        
        Args:
            image: Input image
            strength: Sharpening strength (1.0-2.0)
        
        Returns:
            Sharpened image
        """
        # Unsharp masking for controlled sharpening
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        morphed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Sharpen using kernel
        kernel_sharpen = np.array([
            [-1, -1, -1],
            [-1, 5 * strength, -1],
            [-1, -1, -1]
        ]) / (1 + 8 * (strength - 1))
        
        sharpened = cv2.filter2D(morphed, -1, kernel_sharpen)
        print(f"[Preprocessing] Applied sharpening (strength={strength})")
        return sharpened
    
    def correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct image rotation/skew
        
        Args:
            image: Input image
        
        Returns:
            Deskewed image
        """
        # Find contours to detect text orientation
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Detect edges
        edges = cv2.Canny(gray, 100, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0 and len(contours[0]) > 0:
            # Get angle of largest contour
            cnt = max(contours, key=cv2.contourArea)
            
            if len(cnt) >= 5:
                ellipse = cv2.fitEllipse(cnt)
                angle = ellipse[2]
                
                if abs(angle) > 2:  # Only rotate if angle significant
                    h, w = image.shape[:2]
                    center = (w // 2, h // 2)
                    
                    # Rotation matrix
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    
                    if len(image.shape) == 3:
                        rotated = cv2.warpAffine(image, M, (w, h), 
                                               borderMode=cv2.BORDER_REPLICATE)
                    else:
                        rotated = cv2.warpAffine(image, M, (w, h), 
                                               borderMode=cv2.BORDER_REPLICATE)
                    
                    print(f"[Preprocessing] Corrected skew (angle={angle:.1f}°)")
                    return rotated
        
        print("[Preprocessing] No significant skew detected")
        return image
    
    def detect_ingredients_region(self, image: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Detect and crop the ingredients section of the label
        
        Args:
            image: Input image
        
        Returns:
            Tuple of (cropped_region, region_info)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        h, w = gray.shape[:2]
        
        # Look for high text density areas (ingredients section typically has more text)
        # Divide image into regions and analyze text density
        regions = {
            'top': gray[0:h//3, :],
            'middle': gray[h//3:2*h//3, :],
            'bottom': gray[2*h//3:h, :]
        }
        
        # Extract text regions using morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        
        max_density_region = 'middle'
        max_density = 0
        region_bounds = {'top': (0, h//3), 'middle': (h//3, 2*h//3), 'bottom': (2*h//3, h)}
        
        for region_name, region_img in regions.items():
            # Apply morphology to find text regions
            morph = cv2.morphologyEx(region_img, cv2.MORPH_CLOSE, kernel)
            density = np.sum(morph > 128) / morph.size
            
            if density > max_density:
                max_density = density
                max_density_region = region_name
        
        # Crop to detected region with some margin
        start_y, end_y = region_bounds[max_density_region]
        margin_y = int((end_y - start_y) * 0.1)
        
        crop_y_start = max(0, start_y - margin_y)
        crop_y_end = min(h, end_y + margin_y)
        
        cropped = image[crop_y_start:crop_y_end, :]
        
        region_info = {
            'detected_region': max_density_region,
            'text_density': max_density,
            'original_bounds': (crop_y_start, crop_y_end, 0, w),
            'cropped_shape': cropped.shape
        }
        
        print(f"[Region Detection] Found ingredients in {max_density_region} "
              f"(density={max_density:.1%}), cropped: {cropped.shape}")
        
        return cropped, region_info
    
    def preprocess(self, image, 
                  upscale: float = 1.5,
                  denoise: bool = True,
                  sharpen: bool = True,
                  deskew: bool = True,
                  detect_region: bool = True) -> Tuple[np.ndarray, Dict]:
        """
        Complete preprocessing pipeline
        
        Args:
            image: Input image
            upscale: Upscaling factor (1.5-2.0)
            denoise: Apply denoising
            sharpen: Apply sharpening
            deskew: Correct skewed images
            detect_region: Detect ingredients region
        
        Returns:
            Tuple of (preprocessed_image, metadata)
        """
        print("\n[OCR Pipeline] Starting image preprocessing...")
        
        # Load image
        img = self.load_image(image)
        print(f"[Preprocessing] Loaded image: {img.shape}")
        
        # Upscale
        img = self.resize_image(img, upscale)
        
        # Detect region (before converting to grayscale for better detection)
        region_info = {}
        if detect_region:
            img, region_info = self.detect_ingredients_region(img)
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(img)
        
        # Denoise
        if denoise:
            gray = self.denoise_image(gray, strength=10)
        
        # Sharpen
        if sharpen:
            gray = self.sharpen_image(gray, strength=1.5)
        
        # Deskew
        if deskew:
            gray = self.correct_skew(gray)
        
        # Apply adaptive thresholding for OCR
        binary = self.apply_adaptive_thresholding(gray)
        
        # Convert back to BGR for OCR (some models work better with color)
        # For EasyOCR, we'll use the grayscale version
        
        metadata = {
            'original_shape': img.shape,
            'preprocessed_shape': binary.shape,
            'upscale_factor': upscale,
            'region_info': region_info
        }
        
        print("[Preprocessing] Complete preprocessing pipeline finished\n")
        
        return binary, metadata


class OptimizedEasyOCR:
    """Optimized EasyOCR engine for food labels"""
    
    def __init__(self, languages=['en'], gpu: bool = False, verbose: bool = False):
        """
        Initialize EasyOCR reader
        
        Args:
            languages: List of languages to detect
            gpu: Use GPU if available
            verbose: Print verbose output
        """
        print("[OCR Engine] Initializing EasyOCR...")
        
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.reader = easyocr.Reader(
                languages,
                gpu=gpu,
                verbose=verbose
            )
        
        print(f"[OCR Engine] EasyOCR initialized for {languages}")
    
    def extract_text(self, image: np.ndarray, 
                    detail: int = 1,
                    paragraph: bool = False,
                    batch_size: int = 1) -> List[Dict]:
        """
        Extract text from image with detailed information
        
        Args:
            image: Preprocessed image
            detail: Detail level (0=text only, 1=with confidence)
            paragraph: Group text by paragraphs
            batch_size: Batch size for processing
        
        Returns:
            List of detected text with metadata
        """
        print("[OCR] Extracting text...")
        
        try:
            results = self.reader.readtext(
                image,
                detail=detail,
                paragraph=paragraph,
                batch_size=batch_size
            )
            
            print(f"[OCR] Extracted {len(results)} text elements")
            
            # Convert to structured format
            extracted = []
            for detection in results:
                if len(detection) >= 2:
                    bbox = detection[0]  # Bounding box coordinates
                    text = detection[1]  # Detected text
                    confidence = detection[2] if len(detection) > 2 else 0.9
                    
                    extracted.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox,
                        'bbox_center': self._bbox_center(bbox)
                    })
            
            return extracted
        
        except Exception as e:
            print(f"[OCR] Error during text extraction: {e}")
            return []
    
    @staticmethod
    def _bbox_center(bbox) -> Tuple[float, float]:
        """Calculate center of bounding box"""
        points = np.array(bbox)
        center = points.mean(axis=0)
        return tuple(center)


class TextCleaner:
    """Advanced text cleaning and normalization"""
    
    def __init__(self):
        """Initialize text cleaner"""
        self.multi_word_patterns = [
            r'palm\s+oil', r'soy\s+lecithin', r'sunflower\s+oil',
            r'olive\s+oil', r'coconut\s+oil', r'corn\s+oil',
            r'canola\s+oil', r'soybean\s+oil', r'high\s+fructose',
            r'wheat\s+flour', r'whole\s+wheat', r'soy\s+protein',
            r'milk\s+protein', r'natural\s+flavors?', r'artificial\s+flavors?',
            r'sesame\s+seed', r'sesame\s+oil', r'tree\s+nuts?',
            r'peanut\s+oil', r'peanut\s+butter', r'caramel\s+color',
            r'citric\s+acid', r'sodium\s+benzoate', r'potassium\s+sorbate',
            r'baking\s+soda', r'baking\s+powder', r'xanthan\s+gum',
            r'guar\s+gum', r'vitamin\s+[a-z]', r'ferrous\s+sulfate'
        ]
    
    def clean_text(self, text: str) -> str:
        """
        Comprehensive text cleaning
        
        Args:
            text: Raw OCR text
        
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove common OCR artifacts
        artifacts = [
            r'™', r'®', r'©', r'℠',
            r'|\|', r'—', r'–', r'…', r'•'
        ]
        for artifact in artifacts:
            text = text.replace(artifact, '')
        
        # Remove leading/trailing punctuation
        text = re.sub(r'^[\W_]+|[\W_]+$', '', text)
        
        return text.strip()
    
    def extract_ingredients(self, text: str) -> List[str]:
        """
        Extract individual ingredients from text
        
        Args:
            text: Cleaned text
        
        Returns:
            List of ingredient strings
        """
        # Remove common section headers
        headers = [
            r'ingredients?:', r'contains?:', r'may\s+contain:',
            r'allergens?:', r'nutrition\s+facts', r'directions?:',
            r'storage:', r'manufactured'
        ]
        
        for header in headers:
            text = re.sub(header, '', text, flags=re.IGNORECASE)
        
        # Preserve multi-word ingredients temporarily
        placeholders = {}
        for i, pattern in enumerate(self.multi_word_patterns):
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                placeholder = f"__INGREDIENT_{i}__"
                text = re.sub(re.escape(match), placeholder, text, flags=re.IGNORECASE)
                placeholders[placeholder] = match
        
        # Split by common delimiters
        text = re.sub(r'[,;/\n]', '|', text)
        text = re.sub(r'\s+and\s+', '|', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+or\s+', '|', text, flags=re.IGNORECASE)
        
        ingredients = text.split('|')
        
        # Process each ingredient
        processed = []
        for ingredient in ingredients:
            ing = ingredient.strip()
            
            # Restore multi-word ingredients
            for placeholder, original in placeholders.items():
                ing = ing.replace(placeholder, original)
            
            # Remove parenthetical content (except allergen info)
            if '(' in ing and ')' in ing:
                # Keep if it contains allergen-related info
                if not any(allergen in ing.lower() for allergen in 
                          ['allergen', 'contains', 'may contain']):
                    ing = re.sub(r'\([^)]*\)', '', ing)
            
            # Clean up
            ing = self.clean_text(ing)
            
            # Filter out garbage
            if ing and len(ing) >= 2 and any(c.isalpha() for c in ing):
                processed.append(ing)
        
        return processed


class FuzzyMatcher:
    """Fuzzy matching for correcting OCR errors"""
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between strings"""
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # j+1 instead of j since previous_row and current_row are one character longer
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """Calculate similarity ratio (0-1)"""
        distance = FuzzyMatcher.levenshtein_distance(s1.lower(), s2.lower())
        return 1 - (distance / max(len(s1), len(s2)))
    
    @staticmethod
    def find_best_match(query: str, candidates: List[str], 
                       threshold: float = 0.75) -> Optional[Tuple[str, float]]:
        """
        Find best matching candidate for query
        
        Args:
            query: Query string
            candidates: List of candidate strings
            threshold: Minimum similarity threshold
        
        Returns:
            Tuple of (best_match, similarity) or None
        """
        best_match = None
        best_score = threshold
        
        for candidate in candidates:
            score = FuzzyMatcher.similarity_ratio(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return (best_match, best_score) if best_match else None


class AllergenDetector:
    """Detect and classify allergens"""
    
    ALLERGEN_DATABASE = {
        'gluten': ['wheat', 'barley', 'rye', 'gluten', 'spelt', 'kamut'],
        'dairy': ['milk', 'whey', 'casein', 'butter', 'cheese', 'yogurt', 'cream', 'lactose'],
        'egg': ['egg', 'eggs', 'egg white', 'egg yolk', 'mayonnaise', 'albumen'],
        'peanut': ['peanut', 'peanuts', 'arachis oil', 'monkey nuts'],
        'tree_nuts': ['almond', 'cashew', 'walnut', 'pecan', 'pistachio', 'macadamia',
                     'brazil nut', 'hazelnut', 'chestnut', 'tree nuts'],
        'soy': ['soy', 'soybean', 'soy lecithin', 'soy protein', 'soya', 'edamame'],
        'fish': ['fish', 'salmon', 'tuna', 'cod', 'anchovy', 'anchovy sauce'],
        'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster', 'clam', 'mussel', 'scallop'],
        'sesame': ['sesame', 'sesame seed', 'sesame oil', 'tahini'],
        'mustard': ['mustard', 'mustard seed'],
        'sulfites': ['sulfite', 'sulfur dioxide', 'metabisulfite', 'bisulfite']
    }
    
    @classmethod
    def detect_allergens(cls, ingredients: List[str]) -> Dict[str, List[str]]:
        """
        Detect allergens in ingredient list
        
        Args:
            ingredients: List of ingredient strings
        
        Returns:
            Dict mapping allergen type to detected ingredients
        """
        found_allergens = {}
        
        for allergen_type, allergen_list in cls.ALLERGEN_DATABASE.items():
            found_allergens[allergen_type] = []
            
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                
                for allergen_name in allergen_list:
                    if allergen_name in ingredient_lower:
                        if ingredient not in found_allergens[allergen_type]:
                            found_allergens[allergen_type].append(ingredient)
                        break
        
        # Clean up empty entries
        return {k: v for k, v in found_allergens.items() if v}


class OCRPipeline:
    """Complete OCR pipeline for food labels"""
    
    def __init__(self, use_gpu: bool = False, 
                 fuzzy_threshold: float = 0.75):
        """
        Initialize OCR pipeline
        
        Args:
            use_gpu: Use GPU for OCR if available
            fuzzy_threshold: Threshold for fuzzy matching
        """
        print("\n" + "="*60)
        print("INITIALIZING ADVANCED OCR PIPELINE FOR FOOD LABELS")
        print("="*60)
        
        self.preprocessor = ImagePreprocessor()
        self.ocr_engine = OptimizedEasyOCR(gpu=use_gpu)
        self.text_cleaner = TextCleaner()
        self.fuzzy_matcher = FuzzyMatcher()
        self.allergen_detector = AllergenDetector()
        self.fuzzy_threshold = fuzzy_threshold
        
        # Load ingredient database
        try:
            from ingredient_detector import IngredientDetector
            self.ingredient_detector = IngredientDetector()
            self.database_available = True
            print("[Pipeline] Ingredient database loaded successfully\n")
        except Exception as e:
            print(f"[Pipeline] Warning: Could not load ingredient database: {e}\n")
            self.ingredient_detector = None
            self.database_available = False
    
    def process_image(self, image_input, 
                     return_visualization: bool = False) -> Dict:
        """
        Process food label image end-to-end
        
        Args:
            image_input: Image file path, base64, PIL Image, or numpy array
            return_visualization: Return preprocessing visualization
        
        Returns:
            Comprehensive structured output
        """
        print("\n" + "="*60)
        print("STARTING FOOD LABEL ANALYSIS")
        print("="*60)
        
        result = {
            'success': False,
            'error': None,
            'preprocessing_info': {},
            'raw_text': '',
            'detected_text': [],
            'cleaned_ingredients': [],
            'matched_ingredients': [],
            'allergens': {},
            'confidence_score': 0.0
        }
        
        try:
            # Step 1: Image Preprocessing
            print("\n[STEP 1] IMAGE PREPROCESSING")
            print("-" * 40)
            preprocessed_img, preprocess_info = self.preprocessor.preprocess(image_input)
            result['preprocessing_info'] = preprocess_info
            
            # Step 2: OCR Text Extraction
            print("\n[STEP 2] OCR TEXT EXTRACTION")
            print("-" * 40)
            detected_text = self.ocr_engine.extract_text(preprocessed_img)
            result['detected_text'] = detected_text
            
            # Combine text
            raw_text = ' '.join([item['text'] for item in detected_text])
            result['raw_text'] = raw_text
            
            print(f"[OCR] Raw text extracted ({len(raw_text)} chars):\n{raw_text[:200]}...\n")
            
            if not raw_text.strip():
                result['error'] = 'No text detected in image'
                return result
            
            # Step 3: Text Cleaning
            print("[STEP 3] TEXT CLEANING & INGREDIENT EXTRACTION")
            print("-" * 40)
            cleaned_text = self.text_cleaner.clean_text(raw_text)
            ingredients = self.text_cleaner.extract_ingredients(cleaned_text)
            result['cleaned_ingredients'] = ingredients
            
            print(f"[Cleaning] Extracted {len(ingredients)} ingredients:")
            for i, ing in enumerate(ingredients[:10], 1):
                print(f"  {i}. {ing}")
            if len(ingredients) > 10:
                print(f"  ... and {len(ingredients) - 10} more")
            
            # Step 4: Database Matching
            print("\n[STEP 4] DATABASE MATCHING & FUZZY CORRECTION")
            print("-" * 40)
            matched_ingredients = self._match_ingredients_with_database(ingredients)
            result['matched_ingredients'] = matched_ingredients
            
            # Step 5: Allergen Detection
            print("\n[STEP 5] ALLERGEN DETECTION")
            print("-" * 40)
            matched_names = [m['matched_name'] for m in matched_ingredients]
            allergens = self.allergen_detector.detect_allergens(matched_names)
            result['allergens'] = allergens
            
            if allergens:
                print("[Allergens] Found allergens:")
                for allergen_type, ingredients_list in allergens.items():
                    print(f"  {allergen_type.upper()}: {', '.join(ingredients_list)}")
            else:
                print("[Allergens] No major allergens detected")
            
            # Calculate confidence
            total_detected = len(matched_ingredients)
            accurate_matches = sum(1 for m in matched_ingredients 
                                  if m['match_confidence'] >= 0.9)
            confidence = accurate_matches / total_detected if total_detected > 0 else 0.0
            result['confidence_score'] = confidence
            
            result['success'] = True
            
            print("\n" + "="*60)
            print(f"ANALYSIS COMPLETE - Confidence: {confidence:.1%}")
            print("="*60 + "\n")
            
            return result
        
        except Exception as e:
            print(f"\n[ERROR] Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            result['error'] = str(e)
            return result
    
    def _match_ingredients_with_database(self, ingredients: List[str]) -> List[Dict]:
        """
        Match ingredients with database using fuzzy matching
        
        Args:
            ingredients: List of ingredient strings
        
        Returns:
            List of matched ingredients with metadata
        """
        matched = []
        
        if not self.database_available or self.ingredient_detector is None:
            print("[Matching] Database not available, using basic matching")
            for ing in ingredients:
                matched.append({
                    'original': ing,
                    'matched_name': ing,
                    'category': ['unknown'],
                    'allergen': False,
                    'match_confidence': 0.5,
                    'match_type': 'no_database'
                })
            return matched
        
        for ingredient in ingredients:
            # Try exact match first
            exact_match = self.ingredient_detector.database.search_exact(ingredient)
            
            if exact_match:
                matched.append({
                    'original': ingredient,
                    'matched_name': exact_match.name,
                    'category': exact_match.category,
                    'allergen': exact_match.allergen,
                    'allergen_type': exact_match.allergen_type,
                    'description': exact_match.description,
                    'match_confidence': 1.0,
                    'match_type': 'exact'
                })
            else:
                # Try fuzzy match
                fuzzy_match = self.ingredient_detector.database.search_fuzzy(
                    ingredient,
                    threshold=self.fuzzy_threshold
                )
                
                if fuzzy_match:
                    match_obj, score = fuzzy_match
                    matched.append({
                        'original': ingredient,
                        'matched_name': match_obj.name,
                        'category': match_obj.category,
                        'allergen': match_obj.allergen,
                        'allergen_type': match_obj.allergen_type,
                        'description': match_obj.description,
                        'match_confidence': score,
                        'match_type': 'fuzzy'
                    })
                    print(f"  ✓ fuzzy: '{ingredient}' → '{match_obj.name}' ({score:.0%})")
                else:
                    matched.append({
                        'original': ingredient,
                        'matched_name': ingredient,
                        'category': ['unknown'],
                        'allergen': False,
                        'match_confidence': 0.0,
                        'match_type': 'unmatched'
                    })
        
        return matched
    
    def get_summary(self, result: Dict) -> Dict:
        """
        Generate user-friendly summary of analysis
        
        Args:
            result: Result from process_image
        
        Returns:
            Summary dictionary
        """
        if not result['success']:
            return {'error': result['error']}
        
        return {
            'total_ingredients': len(result['matched_ingredients']),
            'matched_ingredients': [m['matched_name'] for m in result['matched_ingredients']],
            'allergens_found': len(result['allergens']),
            'allergen_types': list(result['allergens'].keys()),
            'allergen_details': result['allergens'],
            'confidence': f"{result['confidence_score']:.0%}",
            'status': 'safe' if not result['allergens'] else 'caution'
        }


# Global pipeline instance
_ocr_pipeline = None

def get_ocr_pipeline(force_reinit: bool = False) -> Optional[OCRPipeline]:
    """Get or create global OCR pipeline"""
    global _ocr_pipeline
    
    if _ocr_pipeline is None or force_reinit:
        try:
            _ocr_pipeline = OCRPipeline()
        except Exception as e:
            print(f"Failed to initialize OCR pipeline: {e}")
            return None
    
    return _ocr_pipeline
