"""
OCR Pipeline Diagnostic Tool
Helps identify where the pipeline is failing and why
"""

import os
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import sys

# Set environment variables BEFORE PaddleOCR import
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

def diagnose_preprocessing(image_path):
    """
    Test image preprocessing and save intermediate stages for inspection
    """
    print("\n" + "="*80)
    print("OCR PIPELINE DIAGNOSTIC - PREPROCESSING ANALYSIS")
    print("="*80)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"✗ Failed to load image: {image_path}")
        return
    
    print(f"\n[1] Original Image")
    print(f"    Size: {image.shape}")
    cv2.imwrite("debug_01_original.jpg", image)
    print(f"    Saved: debug_01_original.jpg")
    
    # Stage 1: Resizing
    height, width = image.shape[:2]
    if height < 400 or width < 400:
        scale_factor = max(400 / height, 400 / width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        print(f"\n[2] After Upscaling")
    else:
        print(f"\n[2] Resizing (not needed, size OK)")
    
    print(f"    Size: {image.shape}")
    cv2.imwrite("debug_02_resized.jpg", image)
    
    if max(image.shape[0], image.shape[1]) > 1600:
        scale_factor = 1600 / max(image.shape[0], image.shape[1])
        image = cv2.resize(image, (int(image.shape[1] * scale_factor), 
                                   int(image.shape[0] * scale_factor)), 
                          interpolation=cv2.INTER_AREA)
        print(f"    Downscaled to: {image.shape}")
    
    # Stage 2: Bilateral Filter
    image_bilateral = cv2.bilateralFilter(image, 7, 50, 50)
    print(f"\n[3] After Bilateral Filter")
    print(f"    Size: {image_bilateral.shape}")
    cv2.imwrite("debug_03_bilateral.jpg", image_bilateral)
    
    # Stage 3: CLAHE
    lab = cv2.cvtColor(image_bilateral, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(12, 12))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    image_clahe = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    print(f"\n[4] After CLAHE Enhancement")
    print(f"    Size: {image_clahe.shape}")
    cv2.imwrite("debug_04_clahe.jpg", image_clahe)
    
    # Stage 4: Gaussian Blur
    image_blur = cv2.GaussianBlur(image_clahe, (3, 3), 0)
    print(f"\n[5] After Gaussian Blur")
    print(f"    Size: {image_blur.shape}")
    cv2.imwrite("debug_05_blur.jpg", image_blur)
    
    # Stage 5: Histogram Equalization
    image_hist = image_blur.copy()
    for i in range(3):
        image_hist[:,:,i] = cv2.equalizeHist(image_hist[:,:,i])
    print(f"\n[6] After Histogram Equalization")
    print(f"    Size: {image_hist.shape}")
    cv2.imwrite("debug_06_histogram.jpg", image_hist)
    
    # Stage 6: Morphological Closing
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image_morph = cv2.morphologyEx(image_hist, cv2.MORPH_CLOSE, kernel, iterations=1)
    print(f"\n[7] After Morphological Closing")
    print(f"    Size: {image_morph.shape}")
    cv2.imwrite("debug_07_morphology.jpg", image_morph)
    
    # Stage 7: Sharpening
    kernel_sharpen = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]]) / 1.0
    image_sharp = cv2.filter2D(image_morph, -1, kernel_sharpen)
    print(f"\n[8] After Sharpening")
    print(f"    Size: {image_sharp.shape}")
    cv2.imwrite("debug_08_sharpened.jpg", image_sharp)
    
    return image_sharp


def diagnose_ocr_extraction(image, test_name):
    """
    Test OCR extraction with different parameter combinations
    """
    print(f"\n" + "="*80)
    print(f"OCR EXTRACTION TEST: {test_name}")
    print("="*80)
    
    print("\nInitializing PaddleOCR...")
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang='en',
        enable_mkldnn=False,
        det_db_thresh=0.3,
        det_db_box_thresh=0.5,
        det_limit_side_len=960,
        rec_batch_num=10
    )
    print("✓ PaddleOCR initialized")
    
    print(f"\nProcessing image with shape: {image.shape}")
    results = ocr.ocr(image)
    
    if results and results[0]:
        print(f"✓ Found {len(results[0])} text boxes")
        
        # Show first 10 boxes
        print("\nFirst 10 text boxes:")
        for i, box in enumerate(results[0][:10]):
            coords = box[0]
            text_info = box[1]
            text = text_info[0] if isinstance(text_info, tuple) else str(text_info)
            conf = text_info[1] if isinstance(text_info, tuple) and len(text_info) > 1 else 0.0
            print(f"  Box {i+1}: '{text}' (confidence: {conf:.2f})")
        
        if len(results[0]) > 10:
            print(f"  ... and {len(results[0]) - 10} more boxes")
        
        return results
    else:
        print("✗ No text boxes detected!")
        return None


def test_preprocessing_aggressiveness():
    """
    Test different levels of preprocessing aggressiveness
    """
    print("\n" + "="*80)
    print("TESTING PREPROCESSING AGGRESSIVENESS LEVELS")
    print("="*80)
    
    image_path = "debug_01_original.jpg"
    if not os.path.exists(image_path):
        print(f"✗ {image_path} not found. Run diagnose_preprocessing() first.")
        return
    
    image = cv2.imread(image_path)
    
    # Level 1: Minimal preprocessing
    print("\n[LEVEL 1] Minimal Preprocessing")
    img1 = cv2.bilateralFilter(image, 5, 30, 30)
    img1 = cv2.GaussianBlur(img1, (3, 3), 0)
    cv2.imwrite("debug_aggressive_minimal.jpg", img1)
    print("  Saved: debug_aggressive_minimal.jpg")
    
    # Level 2: Medium preprocessing
    print("\n[LEVEL 2] Medium Preprocessing")
    img2 = cv2.bilateralFilter(image, 7, 50, 50)
    lab = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(10, 10))
    l = clahe.apply(l)
    img2 = cv2.merge([l, a, b])
    img2 = cv2.cvtColor(img2, cv2.COLOR_LAB2BGR)
    img2 = cv2.GaussianBlur(img2, (3, 3), 0)
    cv2.imwrite("debug_aggressive_medium.jpg", img2)
    print("  Saved: debug_aggressive_medium.jpg")
    
    # Level 3: Strong preprocessing (current default)
    print("\n[LEVEL 3] Strong Preprocessing (Current)")
    img3 = cv2.bilateralFilter(image, 7, 50, 50)
    lab = cv2.cvtColor(img3, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(12, 12))
    l = clahe.apply(l)
    img3 = cv2.merge([l, a, b])
    img3 = cv2.cvtColor(img3, cv2.COLOR_LAB2BGR)
    img3 = cv2.GaussianBlur(img3, (3, 3), 0)
    cv2.imwrite("debug_aggressive_strong.jpg", img3)
    print("  Saved: debug_aggressive_strong.jpg")
    
    print("\nNow test each with OCR to find the best aggressiveness level")


if __name__ == "__main__":
    
    # Test with actual label image
    test_image = "food_label.jpg"
    
    if not os.path.exists(test_image):
        print(f"✗ Test image not found: {test_image}")
        print("  Please provide a food label image named 'food_label.jpg'")
        sys.exit(1)
    
    # Step 1: Diagnose preprocessing
    preprocessed = diagnose_preprocessing(test_image)
    
    if preprocessed is None:
        print("✗ Preprocessing failed")
        sys.exit(1)
    
    # Step 2: Test OCR on preprocessed image
    results = diagnose_ocr_extraction(preprocessed, "Preprocessed Image (Full 8-Stage)")
    
    if results is None or not results[0]:
        print("\n" + "="*80)
        print("DIAGNOSIS: OCR NOT DETECTING TEXT")
        print("="*80)
        print("\nPossible causes:")
        print("1. Preprocessing is too aggressive (destroying text)")
        print("2. PaddleOCR parameters not optimal for this label type")
        print("3. Image quality issues (too small, low contrast, etc.)")
        print("\nTesting different aggressiveness levels...")
        test_preprocessing_aggressiveness()
        
        # Test minimal preprocessing
        print("\n" + "="*80)
        print("TESTING MINIMAL PREPROCESSING")
        print("="*80)
        
        original = cv2.imread(test_image)
        minimal = cv2.bilateralFilter(original, 5, 30, 30)
        minimal = cv2.GaussianBlur(minimal, (3, 3), 0)
        
        results_minimal = diagnose_ocr_extraction(minimal, "Minimal Preprocessing")
        
        if results_minimal and results_minimal[0]:
            print("\n✓ SUCCESS with minimal preprocessing!")
            print("  Recommendation: Reduce preprocessing aggressiveness")
        else:
            print("\n✗ Still no detection with minimal preprocessing")
            print("  Issue may be with PaddleOCR parameters or image format")
    else:
        print("\n✓ SUCCESS! OCR is detecting text properly")
        print("\nGenerating merged lines...")
        
        # Show line merging
        from app_api import merge_text_boxes_into_lines
        merged = merge_text_boxes_into_lines(results)
        
        if merged:
            print(f"\n✓ Merged into {len(merged)} lines")
            for i, line in enumerate(merged[:5]):
                print(f"  Line {i+1}: {line['text'][:60]}...")
        else:
            print("\n✗ Text box merging failed")
    
    print("\n" + "="*80)
    print("Debug images saved:")
    print("  - debug_01_original.jpg")
    print("  - debug_02_resized.jpg")
    print("  - debug_03_bilateral.jpg")
    print("  - debug_04_clahe.jpg")
    print("  - debug_05_blur.jpg")
    print("  - debug_06_histogram.jpg")
    print("  - debug_07_morphology.jpg")
    print("  - debug_08_sharpened.jpg")
    print("\nOpen these images to see where text is being lost")
    print("="*80)
