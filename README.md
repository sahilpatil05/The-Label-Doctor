---
title: Ingredient Scanner
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🧠 Ingredient Scanner - Powered by Hugging Face

A mobile-friendly Flask web app for allergen detection and healthy food recommendations using cloud-based Hugging Face models with EasyOCR fallback.

---

## 🌍 Overview
The app scans ingredients from food products and identifies potential allergens for users with dietary restrictions.  
It also suggests safe and healthy **alternatives** for allergen-containing products.

**✨ New:** Cloud-based OCR using Hugging Face GLM-OCR model - no local installations needed!

---

## ⚙️ Tech Stack
- **Frontend:** HTML5 + CSS3 + JavaScript (mobile-responsive)
- **Backend:** Flask + SQLAlchemy
- **OCR Engine:** 
  - ⭐ **EasyOCR** (default, lightweight, no model downloads)
  - Fallback: PaddleOCR (if EasyOCR unavailable)
  - Cloud: Hugging Face GLM-OCR (optional, when `USE_HUGGINGFACE=True`)
- **Data:** JSON files (`allergens.json`, `alternatives.json`)
- **Database:** SQLite
- **Hosting:** Hugging Face Spaces (Docker)

---

## 🚀 Quick Start

### 1️⃣ Prerequisites
- Python 3.9+
- (Optional) Hugging Face Account for cloud models

### 2️⃣ Get Hugging Face API Token (Optional)
For cloud-based OCR, get a token:
1. Go to: **https://huggingface.co/settings/tokens**
2. Click **"New token"** with **Read** access
3. Copy token (starts with `hf_`)

**Note:** App works without Hugging Face token - uses EasyOCR by default!

### 3️⃣ Local Development Setup

**Clone & Install:**
```bash
git clone https://huggingface.co/spaces/patilS012/ingredient-scanner
cd ingredient-scanner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option A: Use EasyOCR (Default - No Token Needed)**
```powershell
# Windows PowerShell
python app_api.py
```

**Option B: Use Hugging Face Cloud Models**
```powershell
# Windows PowerShell
$env:HF_API_TOKEN = "hf_your_token_here"
$env:USE_HUGGINGFACE = "True"
python app_api.py
```

**Mac/Linux:**
```bash
# EasyOCR (default)
python app_api.py

# Or with Hugging Face
export HF_API_TOKEN="hf_your_token_here"
export USE_HUGGINGFACE="True"
python app_api.py
```

### 4️⃣ Test the App
- Open: **http://localhost:5000**
- Upload a food product image or take a photo
- App extracts ingredients and detects allergens

---

## 📋 Environment Variables

**Optional** - Set these to customize behavior:

```env
# ===== OCR Engine Configuration =====
# Use EasyOCR by default (no token needed)
# Set to True to use Hugging Face cloud models instead
USE_HUGGINGFACE=False

# Hugging Face API Token (only needed if USE_HUGGINGFACE=True)
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# ===== Flask Configuration =====
FLASK_ENV=production
DEBUG=False

# ===== Optional: Customize Hugging Face =====
# HF_OCR_MODEL=zai-org/GLM-OCR
# HF_API_TIMEOUT=30
```

**Note:** App works without any environment variables - EasyOCR is the default!

If using Hugging Face models, **never commit `.env` to git** - add to `.gitignore`.

---

## 🌐 Deployment Options

### ⭐ **Option A: Hugging Face Spaces (Recommended)**

**Easiest & Free!** Flask backend in Docker:
- ✅ Free hosting
- ✅ Auto HTTPS (required for mobile camera)
- ✅ Docker container ready
- ✅ Secret variables support

**Steps:**
1. Fork this Space: https://huggingface.co/spaces/patilS012/ingredient-scanner
2. (Optional) Add `HF_API_TOKEN` secret for cloud OCR
3. Space auto-builds & deploys! 🚀

**Your Space URL:** `https://huggingface.co/spaces/your-username/ingredient-scanner`

**Default Setup:**
- Uses EasyOCR (lightweight, no token needed)
- Works immediately after deployment

**Optional Enhancement:**
- Add `HF_API_TOKEN` secret → Flask will use Hugging Face models
- Set `USE_HUGGINGFACE=True` → Forces cloud models

### 🚂 **Option B: Railway.app**

```bash
railway login
railway init
railway up   # Deploy with Dockerfile
railway variables set USE_HUGGINGFACE=False  # Use EasyOCR (default)
```

### 🟣 **Option C: Docker (Local/Server)**

```bash
docker build -t ingredient-scanner -f Dockerfile.space .
docker run -p 5000:5000 \
  -e HF_API_TOKEN=hf_xxx \
  -e USE_HUGGINGFACE=False \
  ingredient-scanner
```

---

## 📱 Mobile Access

Your Flask app is fully mobile-responsive!

1. Deploy to Hugging Face Spaces (auto-HTTPS)
2. Open on any phone: `https://your-space-url.hf.space`
3. Grant camera permission when app loads
4. Start scanning product labels!

**Works with:**
- ✅ EasyOCR (default, instant)
- ✅ Hugging Face models (if token added)
- ✅ All modern browsers (Chrome, Safari, Firefox, Edge)
