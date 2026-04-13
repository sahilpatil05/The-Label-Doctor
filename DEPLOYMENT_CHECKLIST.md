# ✅ Vercel Deployment Checklist

Use this checklist to guide your deployment process.

## Pre-Deployment Setup

- [ ] **Accounts Created**
  - [ ] GitHub account created and configured
  - [ ] Vercel account created (sign up at https://vercel.com)
  
- [ ] **Local Preparation**
  - [ ] Code committed to GitHub: `git push origin main`
  - [ ] Read VERCEL_QUICK_START.md
  - [ ] Read VERCEL_DEPLOYMENT.md for detailed guide

- [ ] **Files in Place**
  - [ ] `vercel.json` exists (auto-configured)
  - [ ] `.vercelignore` exists (for build optimization)
  - [ ] `requirements.txt` has all dependencies
  - [ ] `app_api.py` is the main Flask app

---

## Deployment Phase

- [ ] **GitHub Repository**
  - [ ] Repository is public or Vercel has access
  - [ ] Main branch has latest code
  - [ ] All files committed and pushed

- [ ] **Vercel Project Creation**
  - [ ] Go to https://vercel.com
  - [ ] Click "New Project"
  - [ ] Select your GitHub repository
  - [ ] Vercel auto-detects Flask/Python

- [ ] **Configuration**
  - [ ] Build Command: Leave empty (auto-detected)
  - [ ] Output Directory: Leave empty
  - [ ] Framework: Python (should be auto-selected)

- [ ] **Environment Variables** (Add these in Vercel Dashboard)
  - [ ] `FLASK_ENV` = `production`
  - [ ] `SECRET_KEY` = `unique-secure-random-string`
  - [ ] (Optional) `USE_HUGGINGFACE` = `False`
  - [ ] (Optional) `HF_API_TOKEN` = your token (if using cloud OCR)

- [ ] **Deploy**
  - [ ] Click "Deploy" button
  - [ ] Wait 2-5 minutes for deployment
  - [ ] Check for success message

---

## Post-Deployment Verification

- [ ] **Deployment Success**
  - [ ] Vercel shows "Success" status
  - [ ] Live URL is generated (e.g., https://ingredient-scanner.vercel.app)
  - [ ] No build errors in logs

- [ ] **App Testing**
  - [ ] Navigate to the live URL
  - [ ] App loads without errors
  - [ ] Can upload an image
  - [ ] OCR runs and returns results
  - [ ] Allergen detection works
  - [ ] Alternative products show

- [ ] **Monitoring**
  - [ ] Check Vercel logs for errors: `vercel logs --tail`
  - [ ] No 502 or timeout errors
  - [ ] Environment variables are set correctly

---

## Production Setup (Optional but Recommended)

- [ ] **Security Improvements**
  - [ ] Changed default SECRET_KEY to unique value
  - [ ] All API keys stored in environment variables
  - [ ] HTTPS is enabled (automatic with Vercel)

- [ ] **Database Solution**
  - [ ] Evaluated database persistence needs
  - [ ] (If needed) Added Vercel Postgres
  - [ ] (If needed) Updated DATABASE_URL environment variable
  - [ ] (If needed) Modified app_api.py to use DATABASE_URL

- [ ] **Custom Domain** (Optional)
  - [ ] Purchased domain name (if applicable)
  - [ ] Added domain in Vercel Settings → Domains
  - [ ] DNS records configured
  - [ ] HTTPS certificate auto-deployed

- [ ] **Continuous Deployment**
  - [ ] Tested that git push triggers auto-deployment
  - [ ] Verified new deploys show in Vercel dashboard
  - [ ] Can rollback to previous versions if needed

---

## Troubleshooting Checklist

If Something Goes Wrong:

- [ ] **Build Failed**
  - [ ] Check Vercel build logs
  - [ ] Verify `requirements.txt` is valid
  - [ ] Check `.vercelignore` isn't excluding needed files
  - [ ] Ensure `app_api.py` has no syntax errors

- [ ] **Function Timeout**
  - [ ] Reduce image upload size (frontend)
  - [ ] Enable Hugging Face cloud OCR
  - [ ] Optimize image preprocessing

- [ ] **Database Issues**
  - [ ] Understand SQLite doesn't persist on Vercel
  - [ ] Migrate to PostgreSQL for production data
  - [ ] Check DATABASE_URL environment variable

- [ ] **App Won't Load**
  - [ ] Check environment variables are set
  - [ ] Verify SECRET_KEY is set
  - [ ] Check logs: `vercel logs --tail`
  - [ ] Test locally: `python app_api.py`

---

## Ongoing Maintenance

- [ ] **Version Control**
  - [ ] Keep main branch clean
  - [ ] Use feature branches for development
  - [ ] Create git tags for releases

- [ ] **Monitoring**
  - [ ] Check analytics in Vercel dashboard monthly
  - [ ] Review logs for errors
  - [ ] Monitor function execution time

- [ ] **Updates**
  - [ ] Keep Python packages updated (`pip install --upgrade -r requirements.txt`)
  - [ ] Security patches applied promptly
  - [ ] Test locally before pushing to production

---

## Useful Commands Reference

```bash
# Check if Vercel CLI is installed
vercel --version

# List all Vercel projects
vercel projects list

# View live logs
vercel logs --tail

# Redeploy current code
vercel deploy --prod

# Check deployment status
vercel status
```

---

## Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **Flask & Vercel:** https://vercel.com/guides/deploying-flask-with-vercel
- **Python Runtime:** https://vercel.com/docs/serverless-functions/python
- **Troubleshooting:** See VERCEL_DEPLOYMENT.md section "Troubleshooting"

---

## Final Notes

✅ **You're all set!** Once you complete the checklist above, your app will be live and automatically deploying on every git push.

📞 **Need help?** 
- Check the detailed VERCEL_DEPLOYMENT.md
- Visit Vercel documentation
- Check Vercel build logs for specific errors

🎉 **Congratulations!** Your Ingredient Scanner is now deployed to the cloud!

---

**Last Updated:** April 2026  
**Status:** Verified & Ready to Deploy
