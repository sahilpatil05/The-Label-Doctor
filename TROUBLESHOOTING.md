# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### ❌ "HF_API_TOKEN not found" Error

**Symptom:** App crashes with `ValueError: Hugging Face API token not found`

**Solution:**

**Windows PowerShell:**
```powershell
$env:HF_API_TOKEN = "hf_your_token_here"
streamlit run app.py
```

Verify it's set:
```powershell
echo $env:HF_API_TOKEN  # Should print your token
```

**Mac/Linux:**
```bash
export HF_API_TOKEN="hf_your_token_here"
streamlit run app.py

# Verify
echo $HF_API_TOKEN
```

**Hugging Face Spaces:**
1. Go to your Space settings
2. Click "Repository secrets"
3. Add: `HF_API_TOKEN` = `hf_your_token`

---

### ❌ "App Not Loading on Mobile"

**Symptoms:**
- Blank screen on phone
- Camera permission not requested
- "Not Secure" error

**Solutions:**
- ✅ Use Hugging Face Spaces (always HTTPS)
- ✅ Use Railway/Heroku (auto-HTTPS)
- ✅ Don't use localhost/http on mobile
- Check browser console: Press F12 → Console tab

---

### ❌ "API Rate Limit Exceeded"

**Symptom:** `429 Too Many Requests` error

**Info:**
- Free tier: **50,000 OCR requests/month**
- That's ~1,600 requests/day

**Solutions:**
- 🔍 Check usage: https://huggingface.co/settings/billing
- 💡 Optimize: Cache results locally
- 🔄 Upgrade to paid plan if needed

---

### ❌ "Image Upload Fails"

**Symptoms:**
- "No image received"
- Empty upload field
- File type errors

**Solutions:**
- ✅ Use supported formats: `.jpg`, `.png`, `.gif`
- ✅ Keep image under 10MB
- ✅ Check browser console for errors
- 🔄 Try a different browser

---

### ❌ "OCR Extracts Gibberish Text"

**Symptoms:**
- Random characters instead of ingredient names
- Incomplete text extraction

**Causes:**
- Low image quality or blurry labels
- Poor lighting
- Rotated/angled images

**Solutions:**
- 📸 Take clear, straight-on photos
- 💡 Use good lighting
- ➡️ Position label horizontally
- 🖼️ Crop to just the ingredient list

---

### ❌ "Streamlit Error: Module Not Found"

**Symptom:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

### ❌ "Port 8501 Already in Use"

**Symptom:** `Address already in use`

**Solution:**
```bash
# Kill existing Streamlit process and restart
streamlit run app.py --server.port 8502
```

Or kill the process:
- **Mac/Linux:** `lsof -ti:8501 | xargs kill -9`
- **Windows:** `netstat -ano | findstr :8501`

---

### ❌ "Database Connection Error"

**Symptom:** `SQLAlchemy database error`

**Solution:**
1. Delete old database: `rm labeldoctor.db`
2. Run: `python populate_database.py`
3. Restart app: `streamlit run app.py`

---

## 💡 Performance Tips

### Speed Up OCR
- **Resize images:** Keep under 1920x1080px
- **JPEG compression:** Use 85% quality
- **Cache results:** Store extracted text locally

### Reduce API Calls
- ✅ Use browser cache (Streamlit auto-caches by default)
- ✅ Test locally before deploying
- ✅ Batch process multiple images

### Mobile Optimization
- ✅ Use Hugging Face Spaces (CDN-backed)
- ✅ Compress images before upload
- ✅ Disable auto-refresh (Streamlit setting)

---

## 🆘 Still Having Issues?

1. **Check logs:**
   - **Local:** Look at terminal output
   - **Spaces:** Go to Space settings → "Logs" tab
   - **Railway:** Dashboard → "Logs" section

2. **Common log locations:**
   - Hugging Face: https://huggingface.co/spaces/patilS012/ingredient-scanner
   - Railway: Your app dashboard
   - Heroku: `heroku logs --tail`

3. **Debug mode:**
   ```bash
   export DEBUG=True
   streamlit run app.py --logger.level=debug
   ```

4. **Test API directly:**
   ```bash
   python test_api.py
   ```

---

## 📞 Getting Help

- 🐛 **Bug Report:** Create issue with error message + steps to reproduce
- 💡 **Feature Request:** Create discussion with use case
- 📧 **Contact:** Check Space page for support links

**Always include:**
- Error message (full traceback)
- OS & browser version
- Steps to reproduce
- Screenshot if applicable
