"""
SIMPLIFIED OCR PIPELINE - Production Ready
No aggressive preprocessing, simpler logic, more robust
"""

import os
import cv2
import numpy as np

# CRITICAL: Set environment variables BEFORE importing Paddle
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_DISABLE_FAST_MATH'] = '1'
os.environ['FLAGS_use_new_ir'] = '0'
os.environ['CPU_NUM'] = '1'
os.environ['GLOG_minloglevel'] = '2'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'  # Skip connectivity check

import warnings
warnings.filterwarnings('ignore')

def simple_preprocess_image(image_np):
    """
    Minimal, non-aggressive preprocessing that doesn't destroy text
    """
    print("[PREPROCESS] Minimal preprocessing...")
    
    # Only resize if needed
    height, width = image_np.shape[:2]
    
    # Upscale if too small
    if height < 300:
        scale = 300 / height
        image_np = cv2.resize(image_np, (int(width * scale), int(height * scale)), 
                             interpolation=cv2.INTER_CUBIC)
    
    # Downscale if too large
    if max(image_np.shape[:2]) > 2500:
        scale = 2500 / max(image_np.shape[:2])
        new_h = int(image_np.shape[0] * scale)
        new_w = int(image_np.shape[1] * scale)
        image_np = cv2.resize(image_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Very light CLAHE - only if image seems low contrast
    lab = cv2.cvtColor(image_np, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Check contrast
    l_min, l_max = l.min(), l.max()
    if l_max - l_min < 120:  # Low contrast
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        l = clahe.apply(l)
    
    enhanced = cv2.merge([l, a, b])
    image_np = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    print(f"[PREPROCESS] ✓ Size: {image_np.shape}")
    return image_np


def initialize_paddleocr_safe():
    """Initialize PaddleOCR with new API, handling deprecations gracefully"""
    print("[OCR INIT] Initializing PaddleOCR (v2.7+)...")
    
    try:
        from paddleocr import PaddleOCR
        
        # Try new parameter names first
        ocr = PaddleOCR(
            use_textline_orientation=True,
            lang='en',
            enable_mkldnn=False,
            text_det_thresh=0.3,
            text_det_box_thresh=0.5,
            text_det_limit_side_len=960,
            text_recognition_batch_size=10
        )
    except TypeError:
        # Fall back to old parameter names if new ones fail
        print("[OCR INIT] Using legacy parameter names...")
        try:
            ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                enable_mkldnn=False,
                det_db_thresh=0.3,
                det_db_box_thresh=0.5,
                det_limit_side_len=960,
                rec_batch_num=10
            )
        except Exception as e:
            print(f"[OCR INIT] ✗ Failed: {e}")
            return None
    
    print("[OCR INIT] ✓ PaddleOCR initialized")
    return ocr


def extract_text_from_ocr_results(results):
    """
    Extract text from PaddleOCR results with proper handling
    Works with both old and new PaddleOCR versions
    """
    if not results or not results[0]:
        print("[EXTRACT] No OCR results")
        return "", [], 0.0
    
    print(f"[EXTRACT] Processing {len(results[0])} text boxes...")
    
    try:
        boxes = []
        
        # Extract all boxes with text and confidence
        for detection in results[0]:
            try:
                # Handle different result formats
                if isinstance(detection, (list, tuple)) and len(detection) >= 2:
                    coords = detection[0]  # Bounding box coordinates
                    text_info = detection[1]  # Text and confidence
                    
                    # Extract text and confidence
                    if isinstance(text_info, (list, tuple)):
                        text = str(text_info[0]) if text_info else ""
                        conf = float(text_info[1]) if len(text_info) > 1 else 0.5
                    else:
                        text = str(text_info)
                        conf = 0.5
                    
                    text = text.strip()
                    
                    # Skip very short text (likely noise)
                    if len(text) < 2:
                        continue
                    
                    # Calculate Y position (for line grouping)
                    if coords and len(coords) >= 2:
                        y_coords = [float(p[1]) if isinstance(p, (list, tuple)) else 0 for p in coords]
                        y_center = sum(y_coords) / len(y_coords) if y_coords else 0
                    else:
                        y_center = 0
                    
                    boxes.append({
                        'text': text,
                        'confidence': conf,
                        'y_center': y_center
                    })
            except Exception as e:
                print(f"[EXTRACT] Warning: Could not parse box: {e}")
                continue
        
        if not boxes:
            print("[EXTRACT] No valid text boxes extracted")
            return "", [], 0.0
        
        print(f"[EXTRACT] ✓ Extracted {len(boxes)} text boxes")
        
        # Sort by Y position (top to bottom), then group
        boxes.sort(key=lambda b: b['y_center'])
        
        # Group boxes into lines based on Y proximity
        lines = []
        current_line = [boxes[0]]
        y_threshold = 25  # pixels
        
        for i in range(1, len(boxes)):
            if abs(boxes[i]['y_center'] - current_line[-1]['y_center']) <= y_threshold:
                current_line.append(boxes[i])
            else:
                lines.append(current_line)
                current_line = [boxes[i]]
        
        if current_line:
            lines.append(current_line)
        
        print(f"[EXTRACT] Grouped into {len(lines)} lines")
        
        # Merge text within each line
        merged_lines = []
        for line in lines:
            line_text = ' '.join([box['text'] for box in line])
            avg_conf = sum([box['confidence'] for box in line]) / len(line)
            merged_lines.append({
                'text': line_text,
                'confidence': avg_conf
            })
        
        # Create full text
        full_text = '\n'.join([line['text'] for line in merged_lines])
        avg_confidence = sum([line['confidence'] for line in merged_lines]) / len(merged_lines) if merged_lines else 0.0
        
        print(f"[EXTRACT] ✓ Final text length: {len(full_text)}")
        print(f"[EXTRACT] ✓ Average confidence: {avg_confidence:.2%}")
        
        return full_text, merged_lines, avg_confidence
        
    except Exception as e:
        print(f"[EXTRACT] ✗ Error processing results: {e}")
        import traceback
        traceback.print_exc()
        return "", [], 0.0


def process_food_label_simple(image_path_or_array):
    """
    Simplified end-to-end OCR processing
    """
    print("\n" + "="*80)
    print("SIMPLIFIED OCR PIPELINE - PROCESSING LABEL")
    print("="*80)
    
    try:
        # Load image
        if isinstance(image_path_or_array, str):
            print(f"[LOAD] Loading image: {image_path_or_array}")
            image = cv2.imread(image_path_or_array)
            if image is None:
                raise FileNotFoundError(f"Cannot load: {image_path_or_array}")
        else:
            image = image_path_or_array
        
        print(f"[LOAD] ✓ Image size: {image.shape}")
        
        # Preprocess
        processed = simple_preprocess_image(image)
        
        # Initialize OCR
        ocr = initialize_paddleocr_safe()
        if ocr is None:
            raise RuntimeError("Failed to initialize PaddleOCR")
        
        # Extract
        print("[OCR] Running extraction...")
        results = ocr.ocr(processed)
        
        # Parse results
        full_text, lines, confidence = extract_text_from_ocr_results(results)
        
        if not full_text:
            print("[RESULT] ✗ No text extracted")
            return {
                'success': False,
                'error': 'No text detected in image',
                'text': '',
                'confidence': 0.0
            }
        
        print("\n[RESULT] ✓ SUCCESS!")
        print(f"  Lines: {len(lines)}")
        print(f"  Characters: {len(full_text)}")
        print(f"  Confidence: {confidence:.2%}")
        
        print("\n[SAMPLE] First 200 characters:")
        print(full_text[:200])
        
        return {
            'success': True,
            'text': full_text,
            'lines': lines,
            'confidence': confidence
        }
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'confidence': 0.0
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    else:
        image_file = "food_label.jpg"
    
    result = process_food_label_simple(image_file)
    
    if result['success']:
        print("\n" + "="*80)
        print("FULL EXTRACTED TEXT:")
        print("="*80)
        print(result['text'])
    else:
        print(f"\n✗ Processing failed: {result['error']}")
