"""
COMPLETE CORRECTED OCR PIPELINE
================================

This file contains the exact Python code for:
1. Image preprocessing (8-stage pipeline)
2. PaddleOCR extraction with optimized parameters
3. Combining OCR text boxes into full lines
4. Extracting complete text properly

Copy-paste ready for integration into your Flask app!
"""

import os
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

# ===== CRITICAL: Set environment variables BEFORE PaddleOCR import =====
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_DISABLE_FAST_MATH'] = '1'
os.environ['PADDLE_ENABLE_MKLDNN'] = '0'
os.environ['FLAGS_use_new_ir'] = '0'
os.environ['FLAGS_pir_apply_shape_optimization'] = '0'
os.environ['FLAGS_pir_apply_cinn_pass'] = '0'
os.environ['CPU_NUM'] = '1'
os.environ['GLOG_minloglevel'] = '2'

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

# =============================================================================
# PART 1: IMAGE PREPROCESSING (8-STAGE PIPELINE)
# =============================================================================

def preprocess_image_for_ocr(image_np):
    """
    Comprehensive 8-stage image preprocessing for optimal OCR extraction.
    
    Args:
        image_np: NumPy array in BGR format
    
    Returns:
        Preprocessed image in BGR format
    
    Processing stages:
        1. Intelligent resizing (upscale if < 400px, downscale if > 1600px)
        2. Bilateral filtering (denoise while preserving edges)
        3. CLAHE contrast enhancement (in LAB color space)
        4. Gaussian blur (smooth remaining noise)
        5. Histogram equalization (enhance visibility per channel)
        6. Morphological closing (connect broken text strokes)
        7. Sharpening filter (enhance text edges)
        8. Ready for OCR
    """
    
    print("[PREPROCESSING] Starting 8-stage image enhancement...")
    
    # STAGE 1: Intelligent Resizing
    height, width = image_np.shape[:2]
    print(f"[STAGE 1] Original size: {width}x{height}")
    
    # Upscale small images to improve text clarity
    if height < 400 or width < 400:
        scale_factor = max(400 / height, 400 / width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        print(f"[STAGE 1] ✓ Upscaled to: {image_np.shape[1]}x{image_np.shape[0]}")
    
    # Limit maximum size (1600px) for OCR performance
    height, width = image_np.shape[:2]
    if max(height, width) > 1600:
        scale_factor = 1600 / max(height, width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_AREA)
        print(f"[STAGE 1] ✓ Downscaled to: {image_np.shape[1]}x{image_np.shape[0]}")
    
    # STAGE 2: Bilateral Filter (denoise while preserving edges)
    image_np = cv2.bilateralFilter(image_np, 7, 50, 50)
    print("[STAGE 2] ✓ Applied bilateral filtering (edge-preserving denoise)")
    
    # STAGE 3: CLAHE Contrast Enhancement (in LAB color space)
    # LAB space is better because L (luminance) is independent of color
    lab = cv2.cvtColor(image_np, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(
        clipLimit=4.0,          # Avoid over-enhancement (1-100, default 40)
        tileGridSize=(12, 12)   # Tile size for local contrast (8-64)
    )
    l = clahe.apply(l)
    
    enhanced = cv2.merge([l, a, b])
    image_np = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    print("[STAGE 3] ✓ Applied CLAHE contrast enhancement (LAB color space)")
    
    # STAGE 4: Gaussian Blur (smooth noise)
    image_np = cv2.GaussianBlur(image_np, (3, 3), 0)
    print("[STAGE 4] ✓ Applied Gaussian blur")
    
    # STAGE 5: Histogram Equalization (per-channel)
    # Spreads intensity values across full range
    for i in range(3):
        image_np[:,:,i] = cv2.equalizeHist(image_np[:,:,i])
    print("[STAGE 5] ✓ Applied histogram equalization (per-channel)")
    
    # STAGE 6: Morphological Closing (connect broken text)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image_np = cv2.morphologyEx(image_np, cv2.MORPH_CLOSE, kernel, iterations=1)
    print("[STAGE 6] ✓ Applied morphological closing")
    
    # STAGE 7: Sharpening Filter (enhance edges)
    kernel_sharpen = np.array([[-1, -1, -1],
                               [-1,  9, -1],
                               [-1, -1, -1]]) / 1.0
    image_np = cv2.filter2D(image_np, -1, kernel_sharpen)
    print("[STAGE 7] ✓ Applied sharpening filter")
    
    print(f"[PREPROCESSING] ✓ Complete! Final size: {image_np.shape[1]}x{image_np.shape[0]}")
    
    return image_np


# =============================================================================
# PART 2: OPTIMIZED PADDLEOCR INITIALIZATION
# =============================================================================

def initialize_optimized_paddleocr():
    """
    Initialize PaddleOCR with parameters optimized for dense ingredient labels.
    
    Returns:
        PaddleOCR instance
    
    Key parameters:
        - use_angle_cls=True: Detect rotated text (important for labels)
        - det_db_thresh=0.3: Lower detection threshold (default 0.3)
        - det_db_box_thresh=0.5: Box confidence threshold (default 0.5)
        - det_limit_side_len=960: Process larger images (default 960)
        - rec_batch_num=10: Recognition batch size (trade-off: speed vs memory)
    """
    
    print("[OCR INIT] Initializing PaddleOCR with optimized parameters...")
    
    import warnings
    from io import StringIO
    import sys
    
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        
        # Suppress verbose output
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            paddle_ocr = PaddleOCR(
                use_angle_cls=True,          # Detect rotated text
                lang='en',                   # English character set
                enable_mkldnn=False,         # CPU mode (Windows)
                det_db_thresh=0.3,           # Lower = detect more text
                det_db_box_thresh=0.5,       # Box detection threshold
                det_limit_side_len=960,      # Process larger images
                rec_batch_num=10             # Recognition batch size
            )
        finally:
            sys.stderr = old_stderr
    
    print("[OCR INIT] ✓ PaddleOCR initialized successfully")
    print("[OCR INIT]   - Angle detection: ENABLED")
    print("[OCR INIT]   - Language: English")
    print("[OCR INIT]   - MKL-DNN: Disabled (CPU mode)")
    print("[OCR INIT]   - Detection threshold: 0.3")
    print("[OCR INIT]   - Max image side: 960px")
    
    return paddle_ocr


# =============================================================================
# PART 3: TEXT BOX MERGING (FIXES CHARACTER-BY-CHARACTER EXTRACTION)
# =============================================================================

def merge_text_boxes_into_lines(ocr_results, y_threshold=20):
    """
    Merge OCR text boxes that belong to the same horizontal line.
    
    This is the KEY FIX for character-by-character extraction!
    
    Args:
        ocr_results: Output from PaddleOCR.ocr() method
        y_threshold: Maximum vertical distance (pixels) to consider boxes on same line
                    Default: 20 pixels
                    Adjust for different line spacing:
                    - 15: Tight line spacing
                    - 25-30: Loose line spacing
    
    Returns:
        List of merged lines with structure:
        [
            {'text': 'Enriched unbleached flour', 'confidence': 0.94},
            {'text': 'wheat flour, malted barley flour', 'confidence': 0.92},
            ...
        ]
    
    Algorithm:
        1. Extract bounding boxes with text and confidence
        2. Filter out single characters (noise)
        3. Calculate center Y coordinate for each box
        4. Sort by Y (top to bottom), then X (left to right)
        5. Group boxes with similar Y (within y_threshold)
        6. Merge text within each group (left-to-right order)
        7. Calculate average confidence per line
    """
    
    if not ocr_results or not ocr_results[0]:
        print("[MERGE] No OCR results to merge")
        return []
    
    detections = ocr_results[0]
    print(f"[MERGE] Processing {len(detections)} text boxes...")
    
    # Step 1: Extract boxes with their text and confidence
    boxes = []
    filtered_count = 0
    
    for detection in detections:
        if len(detection) >= 2:
            try:
                coords = detection[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = detection[1]  # (text, confidence)
                
                # Extract text and confidence
                if isinstance(text_info, tuple):
                    text = text_info[0]
                    confidence = text_info[1] if len(text_info) > 1 else 0.0
                else:
                    text = str(text_info)
                    confidence = 0.0
                
                # CRITICAL: Skip single characters (they cause fragmentation)
                if len(text.strip()) <= 1:
                    filtered_count += 1
                    continue
                
                # Calculate bounding box center Y coordinate (vertical position)
                y_coords = [point[1] for point in coords]
                center_y = sum(y_coords) / len(y_coords)
                
                # Calculate left X coordinate (horizontal position)
                x_coords = [point[0] for point in coords]
                left_x = min(x_coords)
                
                boxes.append({
                    'text': text.strip(),
                    'confidence': confidence,
                    'center_y': center_y,
                    'left_x': left_x
                })
            except (IndexError, TypeError, ValueError):
                continue
    
    print(f"[MERGE] Filtered out {filtered_count} single characters")
    print(f"[MERGE] Processing {len(boxes)} multi-character boxes")
    
    if not boxes:
        print("[MERGE] No boxes to merge")
        return []
    
    # Step 2: Sort boxes by Y coordinate (top to bottom), then X (left to right)
    boxes.sort(key=lambda b: (b['center_y'], b['left_x']))
    
    # Step 3: Group boxes into lines based on Y proximity
    lines = []
    current_line = [boxes[0]]
    
    for i in range(1, len(boxes)):
        current_y = boxes[i]['center_y']
        previous_y = current_line[-1]['center_y']
        
        # If Y difference is small, boxes belong to same line
        if abs(current_y - previous_y) <= y_threshold:
            current_line.append(boxes[i])
        else:
            # Y difference is large, start new line
            lines.append(current_line)
            current_line = [boxes[i]]
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    print(f"[MERGE] Merged into {len(lines)} lines")
    
    # Step 4: Merge text within each line (left to right)
    merged_lines = []
    for line_idx, line in enumerate(lines):
        # Sort by left_x to ensure proper reading order (left to right)
        line.sort(key=lambda b: b['left_x'])
        
        # Join text with spaces
        line_text = ' '.join([box['text'] for box in line])
        
        # Calculate average confidence for the line
        avg_confidence = sum([box['confidence'] for box in line]) / len(line)
        
        merged_lines.append({
            'text': line_text,
            'confidence': avg_confidence
        })
        
        print(f"[MERGE]   Line {line_idx + 1}: {line_text[:50]}... (conf: {avg_confidence:.1%})")
    
    return merged_lines


# =============================================================================
# PART 4: EXTRACT FULL TEXT FROM OCR RESULTS
# =============================================================================

def extract_full_text_from_ocr(ocr_results):
    """
    Extract complete text from OCR results with proper line handling.
    
    Args:
        ocr_results: Output from PaddleOCR.ocr() method
    
    Returns:
        Tuple of (full_text, merged_lines_list, average_confidence)
    
    Example:
        full_text, lines, confidence = extract_full_text_from_ocr(results)
        
        # full_text = "Enriched unbleached flour\nwheat flour..."
        # lines = [{'text': '...', 'confidence': 0.94}, ...]
        # confidence = 0.89
    """
    
    print("[EXTRACT] Starting text extraction...")
    
    # Step 1: Merge text boxes into complete lines
    merged_lines = merge_text_boxes_into_lines(ocr_results)
    
    if not merged_lines:
        print("[EXTRACT] No lines to extract")
        return "", [], 0.0
    
    # Step 2: Combine all lines into full text with newlines
    full_text = '\n'.join([line['text'] for line in merged_lines])
    
    # Step 3: Calculate average confidence
    avg_confidence = sum([line['confidence'] for line in merged_lines]) / len(merged_lines) if merged_lines else 0.0
    
    print(f"[EXTRACT] ✓ Extraction complete")
    print(f"[EXTRACT]   Total lines: {len(merged_lines)}")
    print(f"[EXTRACT]   Total characters: {len(full_text)}")
    print(f"[EXTRACT]   Average confidence: {avg_confidence:.2%}")
    
    return full_text, merged_lines, avg_confidence


# =============================================================================
# PART 5: COMPLETE PIPELINE (ALL PARTS TOGETHER)
# =============================================================================

def process_food_label_image(image_path_or_array, ocr_engine=None):
    """
    Complete pipeline: preprocess image → extract with PaddleOCR → merge boxes → return text.
    
    Args:
        image_path_or_array: Path to image file or NumPy array
        ocr_engine: PaddleOCR instance (will be initialized if None)
    
    Returns:
        Dictionary with results:
        {
            'success': bool,
            'full_text': str,          # Complete extracted text
            'lines': list,             # List of lines with confidence
            'confidence': float,       # Average OCR confidence (0-1)
            'line_count': int,
            'character_count': int,
            'error': str               # If error occurred
        }
    """
    
    print("="*80)
    print("PROCESSING FOOD LABEL IMAGE - COMPLETE PIPELINE")
    print("="*80)
    
    try:
        # Step 1: Load image
        print("\n[PIPELINE] Step 1: Loading image...")
        if isinstance(image_path_or_array, str):
            if not os.path.exists(image_path_or_array):
                raise FileNotFoundError(f"Image not found: {image_path_or_array}")
            image = cv2.imread(image_path_or_array)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path_or_array}")
            print(f"[PIPELINE] ✓ Loaded from file: {image_path_or_array}")
        else:
            image = image_path_or_array.copy()
            print("[PIPELINE] ✓ Using provided image array")
        
        print(f"[PIPELINE]   Image size: {image.shape}")
        
        # Step 2: Preprocess image (8-stage pipeline)
        print("\n[PIPELINE] Step 2: Preprocessing image...")
        processed_image = preprocess_image_for_ocr(image)
        
        # Step 3: Initialize PaddleOCR if needed
        print("\n[PIPELINE] Step 3: OCR initialization...")
        if ocr_engine is None:
            ocr_engine = initialize_optimized_paddleocr()
        else:
            print("[PIPELINE] ✓ Using provided OCR engine")
        
        # Step 4: Extract text with PaddleOCR
        print("\n[PIPELINE] Step 4: Running OCR extraction...")
        ocr_results = ocr_engine.ocr(processed_image)
        print(f"[PIPELINE] ✓ OCR extraction complete")
        
        # Step 5: Merge boxes and extract text
        print("\n[PIPELINE] Step 5: Merging text boxes and extracting full text...")
        full_text, merged_lines, avg_confidence = extract_full_text_from_ocr(ocr_results)
        
        if not full_text:
            raise ValueError("No text extracted from image")
        
        # Step 6: Return results
        print("\n[PIPELINE] Step 6: Preparing results...")
        results = {
            'success': True,
            'full_text': full_text,
            'lines': merged_lines,
            'confidence': avg_confidence,
            'line_count': len(merged_lines),
            'character_count': len(full_text)
        }
        
        print("\n" + "="*80)
        print("RESULT PREVIEW")
        print("="*80)
        print("\nExtracted text (first 500 chars):")
        print(full_text[:500])
        print("\n" + "="*80)
        
        return results
    
    except Exception as e:
        import traceback
        print(f"\n[PIPELINE] ✗ Error: {e}")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'full_text': "",
            'lines': [],
            'confidence': 0.0
        }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Example: Process a food label image
    """
    
    # Example 1: Process from file
    print("\nExample 1: Processing from file")
    print("-" * 40)
    result = process_food_label_image("food_label.jpg")
    
    if result['success']:
        print("\n✓ SUCCESS!")
        print(f"  Extracted {result['line_count']} lines, {result['character_count']} characters")
        print(f"  Average confidence: {result['confidence']:.2%}")
    else:
        print(f"\n✗ FAILED: {result['error']}")
    
    # Example 2: Process NumPy array from camera
    print("\n\nExample 2: Processing from camera frame")
    print("-" * 40)
    # frame = cv2.imread("label_frame.jpg")  # or from camera capture
    # result = process_food_label_image(frame)
    
    # Example 3: Just the preprocessing part
    print("\n\nExample 3: Just preprocessing (for inspection)")
    print("-" * 40)
    # image = cv2.imread("food_label.jpg")
    # preprocessed = preprocess_image_for_ocr(image)
    # cv2.imshow("Preprocessed", preprocessed)
    # cv2.waitKey(0)
    
    print("\n✓ Examples complete!")
