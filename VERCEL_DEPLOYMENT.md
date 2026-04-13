# 🚀 Vercel Deployment Guide - Ingredient Scanner

## Overview
This guide walks you through deploying the Ingredient Scanner Flask app to Vercel.

---

## ⚠️ Important Considerations

### 1. **Database Limitation**
- Vercel's serverless functions use an **ephemeral filesystem** (files don't persist between deployments)
- SQLite database files will be lost after each deployment
- **Solution**: For production, migrate to PostgreSQL or another cloud database
- **For testing**: Accept that data won't persist, or use a managed database service

### 2. **Large Dependencies**
Your project has data-heavy packages (PaddleOCR, EasyOCR, OpenCV, Spacy) that may:
- Exceed Vercel's 250MB build size limit
- Slow down deployments
- **Solution**: The `.vercelignore` file provided reduces unnecessary files

### 3. **Function Timeout**
- Vercel's serverless functions timeout after **10-60 seconds** (depending on plan)
- OCR processing might be slow on large images
- **Solution**: Optimize image preprocessing or use the Hugging Face cloud option

---

## 📋 Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **Git Repository** - Push your code to GitHub, GitLab, or Bitbucket
3. **Environment Variables** - Prepare any API tokens or secrets

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Repository

**Push your code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

### Step 2: Log In to Vercel

Visit **https://vercel.com** and click "Sign In with GitHub" (or your preferred provider)

### Step 3: Import Project

1. Click **"New Project"** after logging in
2. Select your GitHub repository (`ingredient-scanner`)
3. Vercel will auto-detect Flask

### Step 4: Configure Deployment Settings

In the Vercel dashboard, you'll see project settings:

**Build & Development:**
- **Framework Preset:** Python
- **Build Command:** Leave empty (Vercel auto-detects `vercel.json`)
- **Output Directory:** `/`

**Environment Variables:**
Click "Environment Variables" and add:

```env
# Required
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this

# Optional (for Hugging Face cloud OCR)
USE_HUGGINGFACE=False  # Set to True if using cloud models
HF_API_TOKEN=hf_your_token_here  # Only if USE_HUGGINGFACE=True
```

### Step 5: Deploy

Click **"Deploy"** and watch the logs. Deployment usually takes 2-5 minutes.

---

## ✅ After Deployment

### Test Your App
Once deployment completes:
1. Copy your project URL (e.g., `https://ingredient-scanner.vercel.app`)
2. Test the app with an image upload
3. Check the Vercel logs if anything fails

### Common Issues & Fixes

#### ❌ Build Size Too Large
**Error:** `Function source code size (XXX MB) exceeds the 250 MB limit`

**Solution:**
```bash
# Remove unnecessary files locally
rm -r __pycache__
rm -r .git
rm -r venv
git push
# Then redeploy on Vercel
```

#### ❌ Timeout Errors
**Error:** `Task timed out after 60 seconds`

**Solution:**
- Reduce image upload size (frontend)
- Use Hugging Face cloud OCR (faster endpoint)
- Set `USE_HUGGINGFACE=True` in environment variables

#### ❌ Database Not Persisting
**Expected behavior:** Database is empty after each deployment

**Permanent Solution:**
Replace SQLite with PostgreSQL:
```python
# app_api.py
import os

if os.getenv('DATABASE_URL'):
    # Production: Use Vercel PostgreSQL or similar
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    # Development: Use SQLite
    db_path = os.path.join(os.path.dirname(__file__), 'labeldoctor.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
```

**To add PostgreSQL:**
1. Add **Vercel Postgres** integration (free tier available)
2. Set `DATABASE_URL` environment variable in Vercel
3. Update `app_api.py` code above
4. Redeploy

---

## 🔄 Continuous Deployment

After the initial setup:
- **Every push to `main` branch** automatically triggers a new deployment
- Vercel shows deployment status in GitHub
- Rollback to previous versions anytime

---

## 📊 Monitoring & Logs

### View Logs:
1. Go to your Vercel project dashboard
2. Click **"Deployments"** tab
3. Select latest deployment
4. Click **"Functions"** to see logs

### Real-time Monitoring:
```bash
# Install Vercel CLI
npm install -g vercel

# View live logs
vercel logs --tail
```

---

## 🛡️ Security Best Practices

1. **Change Secret Key**
   ```python
   # app_api.py - Change this!
   app.secret_key = 'labeldoctor_secret_key_2026'  # ← Make it unique
   ```

2. **Use Environment Variables for Secrets**
   - Store all API keys in Vercel dashboard
   - Never commit secrets to GitHub

3. **Enable HTTPS** (automatic with Vercel)

4. **API Rate Limiting** (optional)
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address
   
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/api/ocr', methods=['POST'])
   @limiter.limit("10 per minute")
   def ocr_route():
       # Your code
   ```

---

## 📦 Production Checklist

- [ ] Changed `app.secret_key` to a unique, secure value
- [ ] Set environment variables in Vercel dashboard
- [ ] Tested the deployed app with sample images
- [ ] Verified all API endpoints work
- [ ] Checked Vercel logs for errors
- [ ] (Optional) Set up custom domain
- [ ] (Optional) Configured PostgreSQL for data persistence

---

## 🔗 Useful Links

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
- [Vercel Python Runtime](https://vercel.com/docs/serverless-functions/python)
- [Vercel CLI](https://vercel.com/docs/cli)

---

## 💬 Troubleshooting

**Q: Why is my app slow?**
- OCR processing is CPU-intensive
- Consider using Hugging Face cloud models (faster)
- Optimize image preprocessing

**Q: Can I use a custom domain?**
- Yes! Go to Project Settings → Domains → Add custom domain

**Q: Can I see deployment history?**
- Yes! Click "Deployments" tab in Vercel dashboard

**Q: How do I rollback to a previous version?**
- Click the deployment you want and select "Promote to Production"

---

## Next Steps

1. ✅ Follow the deployment steps above
2. ✅ Test the live app
3. ✅ (Optional) Set up custom domain
4. ✅ (Optional) Migrate to PostgreSQL for production

Good luck! 🎉
