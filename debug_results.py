"""Debug PaddleOCR result format"""
import os
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_DISABLE_FAST_MATH'] = '1'
os.environ['FLAGS_use_new_ir'] = '0'
os.environ['CPU_NUM'] = '1'
os.environ['GLOG_minloglevel'] = '2'

import warnings
warnings.filterwarnings('ignore')

import cv2
import numpy as np
from paddleocr import PaddleOCR

test_img = np.ones((400, 800, 3), dtype=np.uint8) * 255
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(test_img, 'INGREDIENTS: Enriched', (20, 100), font, 0.7, (0, 0, 0), 2)

ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='en',
    enable_mkldnn=False
)

results = ocr.ocr(test_img)

print("=== PaddleOCR RESULT STRUCTURE ===\n")
print("results type:", type(results))
print("len(results):", len(results))
print("results[0] type:", type(results[0]))

# Try using it as a dict
ocr_result = results[0]

print("\nKeys in OCRResult:")
try:
    keys = list(ocr_result.keys())
    print("  Keys:", keys)
    
    for key in keys[:5]:
        val = ocr_result[key]
        print(f"    {key}: {val} (type: {type(val).__name__})")
except Exception as e:
    print("  Error:", e)

print("\nTrying iteration:")
try:
    items = list(ocr_result)
    print("  Items:", len(items))
    for i, item in enumerate(items[:3]):
        print(f"    [{i}]: {item}")
except Exception as e:
    print("  Error:", e)

print("\nTrying iteration with items():")
try:
    for key, val in list(ocr_result.items())[:3]:
        print(f"  {key}: {val}")
except Exception as e:
    print("  Error:", e)

print("\nJSON representation:")
try:
    if hasattr(ocr_result, 'json'):
        print("  Has json property")
        j = ocr_result.json
        print("  JSON:", j)
except Exception as e:
    print("  Error:", e)

print("\nString representation:")
print("  str():", str(ocr_result)[:200])


