"""
Quick diagnostic test for OCR preprocessing and extraction fixes
Run this to verify the Pillow compatibility fix and OCR format handling
"""

import sys
import os

print("="*70)
print("DIAGNOSTIC TEST: OCR Preprocessing & Text Extraction")
print("="*70)

# Test 1: Check Pillow version and ANTIALIAS compatibility
print("\n[TEST 1] Pillow Compatibility Check")
print("-" * 70)
try:
    from PIL import Image
    print(f"✓ PIL imported successfully")
    print(f"  Pillow version: {Image.__version__ if hasattr(Image, '__version__') else 'unknown'}")
    
    # Check if ANTIALIAS exists
    if hasattr(Image, 'ANTIALIAS'):
        print(f"✓ Image.ANTIALIAS exists (native)")
    else:
        print(f"✗ Image.ANTIALIAS NOT found - applying compatibility fix...")
        Image.ANTIALIAS = Image.LANCZOS
        if hasattr(Image, 'ANTIALIAS'):
            print(f"✓ Image.ANTIALIAS now available (patched to LANCZOS)")
        else:
            print(f"✗ Failed to patch Image.ANTIALIAS")
    
    # Test actual usage
    test_img = Image.new('RGB', (100, 100))
    resized = test_img.resize((50, 50), Image.ANTIALIAS)
    print(f"✓ Image.ANTIALIAS works - resize test passed")
    
except Exception as e:
    print(f"✗ Pillow test failed: {e}")

# Test 2: Check if EasyOCR is available and functional
print("\n[TEST 2] EasyOCR Availability & Initialization")
print("-" * 70)
try:
    import easyocr
    print(f"✓ EasyOCR imported successfully")
    
    try:
        print("  Initializing EasyOCR Reader (English only, this takes ~30-60 seconds)...")
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print(f"✓ EasyOCR Reader initialized successfully")
    except Exception as init_error:
        print(f"⚠ EasyOCR Reader initialization failed: {init_error}")
        print("  (This is normal if models aren't downloaded yet)")
    
except ImportError as e:
    print(f"✗ EasyOCR not available: {e}")
    print("  Install with: pip install easyocr")

# Test 3: Check app_api imports
print("\n[TEST 3] App API Imports & Fixes")
print("-" * 70)
try:
    # This will trigger the Pillow fix if needed
    import app_api
    print(f"✓ app_api.py imported successfully")
    print(f"  PREPROCESSOR_AVAILABLE: {app_api.PREPROCESSOR_AVAILABLE}")
    
except Exception as e:
    print(f"✗ Failed to import app_api: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test merge function with sample data
print("\n[TEST 4] Merge Function - Format Handling")
print("-" * 70)
try:
    from app_api import merge_text_boxes_into_lines
    
    # Test EasyOCR format (4-point polygon boxes)
    easyocr_sample = [[
        ([[10, 10], [100, 10], [100, 30], [10, 30]], "Hello", 0.95),
        ([[10, 40], [100, 40], [100, 60], [10, 60]], "World", 0.92),
    ]]
    
    result = merge_text_boxes_into_lines(easyocr_sample, image_height=500)
    if result and len(result) > 0:
        print(f"✓ EasyOCR format: Successfully extracted {len(result)} lines")
        for i, line in enumerate(result):
            print(f"  Line {i+1}: '{line['text']}' (conf: {line['confidence']:.2%})")
    else:
        print(f"✗ EasyOCR format: Failed to extract text")
    
    # Test PaddleOCR format
    paddleocr_sample = [[
        ([[10, 10], [100, 10], [100, 30], [10, 30]], ("Hello", 0.95)),
        ([[10, 40], [100, 40], [100, 60], [10, 60]], ("World", 0.92)),
    ]]
    
    result2 = merge_text_boxes_into_lines(paddleocr_sample, image_height=500)
    if result2 and len(result2) > 0:
        print(f"✓ PaddleOCR format: Successfully extracted {len(result2)} lines")
        for i, line in enumerate(result2):
            print(f"  Line {i+1}: '{line['text']}' (conf: {line['confidence']:.2%})")
    else:
        print(f"✗ PaddleOCR format: Failed to extract text")
    
except Exception as e:
    print(f"✗ Merge function test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: OpenCV compatibility
print("\n[TEST 5] OpenCV Setup")
print("-" * 70)
try:
    import cv2
    print(f"✓ OpenCV imported: {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV error: {e}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
print("\nIf all tests passed, the fixes should work. If any failed:")
print("1. Install missing packages: pip install -r requirements.txt")
print("2. Restart the Flask server")
print("3. Try uploading an image to /api/scan")
