"""
Enhanced Image Preprocessing for OCR
Balanced approach: stable but effective text enhancement
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Dict, Optional


class OCRImagePreprocessor:
    """Enhanced image preprocessing optimized for food label OCR"""
    
    def __init__(self, target_min_size: int = 500, target_max_size: int = 2000, 
                 use_clahe: bool = True, use_denoise: bool = False):
        """
        Initialize preprocessor
        
        Args:
            target_min_size: Minimum dimension (upscale if smaller)
            target_max_size: Maximum dimension (downscale if larger)
            use_clahe: Apply CLAHE contrast enhancement (recommended)
            use_denoise: Apply bilateral denoising (slower, for very noisy images)
        """
        self.target_min_size = target_min_size
        self.target_max_size = target_max_size
        self.use_clahe = use_clahe
        self.use_denoise = use_denoise
    
    def load_image(self, image_input) -> np.ndarray:
        """
        Load image from various input formats
        
        Args:
            image_input: File path, numpy array, base64, or PIL Image
        
        Returns:
            numpy array in BGR format
        """
        if isinstance(image_input, str) and (image_input.startswith('/') or 
                                              image_input.startswith('\\') or 
                                              ':' in image_input[:2]):
            # File path
            img = cv2.imread(image_input)
            if img is None:
                raise ValueError(f"Cannot read image from {image_input}")
            return img
        
        elif isinstance(image_input, str):
            # Base64 string or short string
            try:
                if ',' in image_input:
                    image_input = image_input.split(',')[1]
                image_bytes = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise ValueError(f"Cannot decode image: {e}")
        
        elif isinstance(image_input, Image.Image):
            # PIL Image
            if image_input.mode == 'RGBA':
                image_input = image_input.convert('RGB')
            return cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        
        elif isinstance(image_input, np.ndarray):
            # Numpy array (assume BGR)
            if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                return image_input.copy()
            elif len(image_input.shape) == 3 and image_input.shape[2] == 4:
                # RGBA to BGR
                return cv2.cvtColor(image_input, cv2.COLOR_RGBA2BGR)
            else:
                raise ValueError(f"Invalid image array shape: {image_input.shape}")
        
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
    
    def resize_image(self, image: np.ndarray, target_min: int, target_max: int) -> Tuple[np.ndarray, Dict]:
        """
        Resize image to optimal size for OCR
        
        Args:
            image: Input BGR image
            target_min: Minimum dimension threshold
            target_max: Maximum dimension threshold
        
        Returns:
            Tuple of (resized_image, resize_info)
        """
        height, width = image.shape[:2]
        original_size = (width, height)
        
        scaling_info = {
            'original_size': original_size,
            'target_min': target_min,
            'target_max': target_max,
            'scaling_applied': False,
            'scale_factor': 1.0,
            'final_size': original_size
        }
        
        # Upscale if too small
        if height < target_min or width < target_min:
            scale_factor = max(target_min / height, target_min / width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            scaling_info['scale_factor'] = scale_factor
            scaling_info['scaling_applied'] = True
            scaling_info['final_size'] = (new_width, new_height)
            print(f"[PREPROCESS] Upscaled: {original_size} → {(new_width, new_height)}")
            height, width = image.shape[:2]
        
        # Downscale if too large
        if height > target_max or width > target_max:
            scale_factor = target_max / max(height, width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            scaling_info['scale_factor'] = scale_factor
            scaling_info['scaling_applied'] = True
            scaling_info['final_size'] = (new_width, new_height)
            print(f"[PREPROCESS] Downscaled: {original_size} → {(new_width, new_height)}")
        
        return image, scaling_info
    
    def enhance_contrast_clahe(self, image: np.ndarray, clip_limit: float = 2.0, 
                                tile_size: int = 8) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        Improves local contrast without creating artifacts
        
        Args:
            image: Input BGR image
            clip_limit: Contrast limit (1.0-4.0 recommended)
            tile_size: Tile grid size (typical: 8-16)
        
        Returns:
            Enhanced BGR image
        """
        try:
            # Convert to LAB color space (better for enhancement)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE only to L channel
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
            l = clahe.apply(l)
            
            # Merge and convert back
            enhanced_lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            print(f"[PREPROCESS] Applied CLAHE (clip_limit={clip_limit})")
            return result
        except Exception as e:
            print(f"[PREPROCESS] CLAHE failed ({e}), skipping")
            return image
    
    def denoise_bilateral(self, image: np.ndarray, strength: int = 9) -> np.ndarray:
        """
        Apply bilateral filtering (preserves edges while removing noise)
        
        Args:
            image: Input BGR image
            strength: Filter diameter (5-15 recommended)
        
        Returns:
            Denoised BGR image
        """
        try:
            denoised = cv2.bilateralFilter(image, strength, 50, 50)
            print(f"[PREPROCESS] Applied bilateral denoising")
            return denoised
        except Exception as e:
            print(f"[PREPROCESS] Denoise failed ({e}), skipping")
            return image
    
    def sharpen_text(self, image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply sharpening to enhance text edges
        
        Args:
            image: Input BGR image
            kernel_size: Kernel size for morphology
        
        Returns:
            Sharpened BGR image
        """
        try:
            # Use morphological sharpening (more stable than unsharp mask)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            
            # Apply morphological close to fill small gaps
            closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Apply slight sharpening via kernel
            sharpening_kernel = np.array([
                [-1, -1, -1],
                [-1, 9, -1],
                [-1, -1, -1]
            ]) / 1.0
            
            sharpened = cv2.filter2D(closed, -1, sharpening_kernel / 9.0)
            print(f"[PREPROCESS] Applied text sharpening")
            return sharpened
        except Exception as e:
            print(f"[PREPROCESS] Sharpening failed ({e}), skipping")
            return image
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert BGR to grayscale for better OCR
        
        Args:
            image: Input BGR image
        
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print(f"[PREPROCESS] Converted to grayscale")
            return gray
        return image
    
    def preprocess(self, image_input) -> Tuple[np.ndarray, Dict]:
        """
        Complete preprocessing pipeline for OCR
        
        Args:
            image_input: Various image input formats
        
        Returns:
            Tuple of (preprocessed_image, preprocessing_info)
        """
        preprocessing_info = {
            'steps_applied': [],
            'dimensions': {},
            'enhancements': {}
        }
        
        try:
            # Step 1: Load image
            print("[PREPROCESS] ===== Starting Image Preprocessing =====")
            image = self.load_image(image_input)
            preprocessing_info['steps_applied'].append('load')
            print(f"[PREPROCESS] Loaded image: {image.shape}")
            
            # Step 2: Resize to optimal dimensions
            image, resize_info = self.resize_image(image, self.target_min_size, self.target_max_size)
            preprocessing_info['steps_applied'].append('resize')
            preprocessing_info['dimensions'] = resize_info
            
            # Step 3: Optional denoising (only if requested - slower)
            if self.use_denoise:
                image = self.denoise_bilateral(image, strength=9)
                preprocessing_info['steps_applied'].append('denoise')
                preprocessing_info['enhancements']['denoise'] = {'strength': 9}
            
            # Step 4: Contrast enhancement (CLAHE) - main improvement
            if self.use_clahe:
                # Try different CLAHE strengths based on image brightness
                image = self.enhance_contrast_clahe(image, clip_limit=2.0, tile_size=8)
                preprocessing_info['steps_applied'].append('clahe')
                preprocessing_info['enhancements']['clahe'] = {'clip_limit': 2.0, 'tile_size': 8}
            
            # Step 5: Sharpening for better text detection
            image = self.sharpen_text(image, kernel_size=5)
            preprocessing_info['steps_applied'].append('sharpen')
            
            # Step 6: Convert to grayscale (helps with OCR)
            image = self.convert_to_grayscale(image)
            preprocessing_info['steps_applied'].append('grayscale')
            
            print(f"[PREPROCESS] ✓ Complete! Final size: {image.shape}")
            print(f"[PREPROCESS] Steps applied: {' → '.join(preprocessing_info['steps_applied'])}")
            
            return image, preprocessing_info
            
        except Exception as e:
            print(f"[PREPROCESS] ✗ Preprocessing failed: {e}")
            print(f"[PREPROCESS] Falling back to minimal preprocessing")
            
            try:
                # Minimal fallback
                image = self.load_image(image_input)
                image, _ = self.resize_image(image, self.target_min_size, self.target_max_size)
                image = self.convert_to_grayscale(image)
                preprocessing_info['fallback_used'] = True
                preprocessing_info['steps_applied'] = ['load', 'resize', 'grayscale']
                return image, preprocessing_info
            except Exception as fallback_error:
                raise RuntimeError(f"Even fallback preprocessing failed: {fallback_error}")


class AdaptiveLineThresholdCalculator:
    """Calculate adaptive y_threshold for text line merging based on image characteristics"""
    
    @staticmethod
    def calculate_threshold(image: np.ndarray, image_height: int) -> int:
        """
        Calculate optimal y_threshold for line merging based on image resolution
        
        Args:
            image: Preprocessed image (can be grayscale or BGR)
            image_height: Height of the image in pixels
        
        Returns:
            Recommended y_threshold in pixels
        """
        # Base threshold: ~2-3% of image height
        # This adapts to image resolution
        base_threshold = max(10, int(image_height * 0.025))
        
        # Adjust based on text line spacing patterns
        # (typically food labels have moderate spacing)
        
        # For typical food labels:
        # - Small images (< 600px): threshold ~15px
        # - Medium images (600-1200px): threshold ~20-25px  
        # - Large images (> 1200px): threshold ~30px
        
        if image_height < 600:
            return 15
        elif image_height < 1200:
            return 20
        else:
            return min(30, base_threshold)
    
    @staticmethod
    def get_recommended_settings(image_height: int) -> Dict:
        """Get recommended preprocessing and merging settings based on image size"""
        settings = {
            'y_threshold': AdaptiveLineThresholdCalculator.calculate_threshold(None, image_height),
            'clahe_clip_limit': 2.0,
            'denoise': False
        }
        
        # Special handling for very small/large images
        if image_height < 400:
            settings['clahe_clip_limit'] = 2.5  # Stronger enhancement for small images
        elif image_height > 1500:
            settings['denoise'] = True  # Denoise large images for clarity
            settings['clahe_clip_limit'] = 1.5  # Lighter enhancement to avoid artifacts
        
        return settings


# Example usage
if __name__ == "__main__":
    print("Image Preprocessor Module Loaded")
    print("Usage:")
    print("  from image_preprocessor import OCRImagePreprocessor")
    print("  pp = OCRImagePreprocessor()")
    print("  preprocessed, info = pp.preprocess(image_input)")
