#!/usr/bin/env python3
"""
QUICK REFERENCE: PaddleOCR Debugging Commands

Run this file to get quick diagnostic info:
    python check_paddle_status.py
"""

import os
import sys
import platform

print("\n" + "="*70)
print("PADDLEOCR STATUS CHECK")
print("="*70)

# 1. System Info
print("\n[1] SYSTEM INFORMATION")
print(f"    OS: {platform.system()} {platform.release()}")
print(f"    Python: {platform.python_version()}")
print(f"    Processor: {platform.processor()}")

# 2. Environment Variables
print("\n[2] PADDLEOCR ENVIRONMENT VARIABLES")
env_vars = [
    'PADDLE_CACHE_DIR', 'PADDLEOCR_MODEL_PATH', 
    'PADDLE_DISABLE_FAST_MATH', 'FLAGS_use_mkldnn', 
    'PADDLE_ENABLE_MKLDNN', 'CPU_NUM'
]
for var in env_vars:
    value = os.getenv(var, '[NOT SET]')
    print(f"    {var}: {value}")

# 3. Check Installed Packages
print("\n[3] OCR LIBRARIES INSTALLED")
try:
    import paddleocr
    print(f"    ✓ paddleocr: {paddleocr.__version__ if hasattr(paddleocr, '__version__') else 'installed'}")
except ImportError:
    print(f"    ✗ paddleocr: NOT INSTALLED")

try:
    import easyocr
    print(f"    ✓ easyocr: installed")
except ImportError:
    print(f"    ✗ easyocr: NOT INSTALLED")

try:
    import paddle
    print(f"    ✓ paddle: {paddle.__version__ if hasattr(paddle, '__version__') else 'installed'}")
except ImportError:
    print(f"    ✗ paddle: NOT INSTALLED")

try:
    import cv2
    print(f"    ✓ opencv: {cv2.__version__}")
except ImportError:
    print(f"    ✗ opencv: NOT INSTALLED")

# 4. Cache Directory
print("\n[4] CACHE DIRECTORY")
cache_dir = os.path.expanduser('~/.paddleocr')
if os.path.exists(cache_dir):
    size_mb = sum(os.path.getsize(os.path.join(dirpath,filename)) 
                  for dirpath, dirnames, filenames in os.walk(cache_dir) 
                  for filename in filenames) / 1024 / 1024
    print(f"    ✓ Exists: {cache_dir}")
    print(f"    Size: {size_mb:.1f} MB")
else:
    print(f"    ✗ Not found: {cache_dir}")

print("\n" + "="*70)
print("QUICK ACTION COMMANDS")
print("="*70)

print("""
To test PaddleOCR:
    python test_paddle_minimal.py

To run the Flask app:
    python app_api.py

To view the web UI:
    Open browser to: http://localhost:5000

To check detailed troubleshooting:
    Read: PADDLEOCR_TROUBLESHOOTING.md

To check session summary:
    Read: PADDLEOCR_SESSION_SUMMARY.md

To reinstall PaddleOCR:
    pip uninstall paddleocr paddlepaddle -y
    pip install paddleocr==2.7.0 paddlepaddle==2.5.0

To test ingredient extraction (if using test_api.py):
    python test_api.py

To check logs:
    Check Flask console output for [ERROR], [WARNING], ✓ messages
""")

print("="*70)
print("\nNOTE: If test_paddle_minimal.py passes, the issue is Flask-specific.")
print("      If it fails, implement solution from PADDLEOCR_TROUBLESHOOTING.md")
print("="*70 + "\n")
