# Cloudflare Pages Deployment Guide

Complete guide to deploy Xin Yi frontend to Cloudflare Pages with automatic CI/CD.

---

## 🚀 Quick Deploy (Manual - First Time)

### Option 1: Using Wrangler CLI

```bash
# 1. Install Wrangler
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Deploy frontend
wrangler pages deploy frontend --project-name=xinyi-heysalad

# 4. Set custom domain in Cloudflare dashboard
# Go to: Workers & Pages → xinyi-heysalad → Custom domains
# Add: xinyi.heysalad.app
```

### Option 2: Using Cloudflare Dashboard

1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages**
3. Click **Create application** → **Pages** → **Connect to Git**
4. Select your GitHub repository: `Hey-Salad/Xin-Yi`
5. Configure build settings:
   - **Project name:** `xinyi-heysalad`
   - **Production branch:** `main`
   - **Build command:** (leave empty - static site)
   - **Build output directory:** `frontend`
6. Click **Save and Deploy**

---

## 🔄 Automatic CI/CD Setup

### Step 1: Get Cloudflare Credentials

1. **Get Account ID:**
   ```bash
   # Login first
   wrangler login
   
   # Get account ID
   wrangler whoami
   ```
   Or find it in Cloudflare Dashboard → Account Home (right sidebar)

2. **Create API Token:**
   - Go to: https://dash.cloudflare.com/profile/api-tokens
   - Click **Create Token**
   - Use template: **Edit Cloudflare Workers**
   - Or create custom token with permissions:
     - Account → Cloudflare Pages → Edit
   - Copy the token (you'll only see it once!)

### Step 2: Add GitHub Secrets

1. Go to your GitHub repo: https://github.com/Hey-Salad/Xin-Yi
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

   **Secret 1:**
   - Name: `CLOUDFLARE_API_TOKEN`
   - Value: `<your-api-token-from-step-1>`

   **Secret 2:**
   - Name: `CLOUDFLARE_ACCOUNT_ID`
   - Value: `<your-account-id-from-step-1>`

### Step 3: Enable GitHub Actions

The workflow file is already created at `.github/workflows/deploy-frontend.yml`

**It will automatically deploy when:**
- You push changes to `main` branch
- Changes are in the `frontend/` directory
- Or you manually trigger it from Actions tab

### Step 4: Test the Workflow

```bash
# Make a small change to test
echo "<!-- Test deployment -->" >> frontend/index.html

# Commit and push
git add .
git commit -m "test: trigger CI/CD deployment"
git push origin main

# Watch deployment
# Go to: https://github.com/Hey-Salad/Xin-Yi/actions
```

---

## 🌐 Custom Domain Setup

### Add xinyi.heysalad.app

1. **In Cloudflare Pages:**
   - Go to your project: **xinyi-heysalad**
   - Click **Custom domains** tab
   - Click **Set up a custom domain**
   - Enter: `xinyi.heysalad.app`
   - Click **Continue**

2. **DNS Configuration:**
   - Cloudflare will automatically add a CNAME record
   - If manual setup needed:
     ```
     Type: CNAME
     Name: xinyi
     Target: xinyi-heysalad.pages.dev
     Proxy: Enabled (orange cloud)
     ```

3. **SSL/TLS:**
   - Go to **SSL/TLS** → **Overview**
   - Set to **Full** or **Full (strict)**
   - Certificate will be auto-provisioned

---

## 🔧 Environment Variables (Optional)

If you need environment variables in the frontend:

1. Go to **Workers & Pages** → **xinyi-heysalad** → **Settings** → **Environment variables**
2. Add variables for **Production** and **Preview** environments
3. Access in code:
   ```javascript
   // Note: Only available at build time for static sites
   const API_URL = process.env.API_URL || 'https://wms.heysalad.app/api/wms';
   ```

---

## 📊 Monitoring Deployments

### View Deployment Status

1. **GitHub Actions:**
   - https://github.com/Hey-Salad/Xin-Yi/actions
   - See build logs and status

2. **Cloudflare Dashboard:**
   - **Workers & Pages** → **xinyi-heysalad** → **Deployments**
   - See deployment history and logs

### Deployment URLs

- **Production:** https://xinyi.heysalad.app
- **Preview (auto):** https://[commit-hash].xinyi-heysalad.pages.dev
- **Direct:** https://xinyi-heysalad.pages.dev

---

## 🔄 Rollback

### Option 1: Via Cloudflare Dashboard

1. Go to **Deployments** tab
2. Find the previous working deployment
3. Click **⋯** → **Rollback to this deployment**

### Option 2: Via Git

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard <commit-hash>
git push origin main --force
```

---

## 🧪 Preview Deployments

Every pull request automatically gets a preview deployment:

1. Create a branch:
   ```bash
   git checkout -b feature/new-dashboard
   ```

2. Make changes and push:
   ```bash
   git add .
   git commit -m "feat: add new dashboard feature"
   git push origin feature/new-dashboard
   ```

3. Create Pull Request on GitHub

4. Cloudflare will comment with preview URL:
   ```
   ✅ Preview deployed to:
   https://abc123.xinyi-heysalad.pages.dev
   ```

---

## 🚨 Troubleshooting

### Issue: Deployment fails with "API token invalid"

**Solution:**
- Regenerate API token in Cloudflare
- Update `CLOUDFLARE_API_TOKEN` secret in GitHub

### Issue: Custom domain not working

**Solution:**
1. Check DNS propagation: https://dnschecker.org
2. Verify CNAME record points to `xinyi-heysalad.pages.dev`
3. Ensure SSL/TLS is set to **Full**
4. Wait up to 24 hours for DNS propagation

### Issue: 404 errors on page refresh

**Solution:**
Add `_redirects` file in frontend:
```bash
echo "/* /index.html 200" > frontend/_redirects
```

### Issue: CORS errors

**Solution:**
- Backend must allow origin: `https://xinyi.heysalad.app`
- Check backend CORS configuration
- Verify API_BASE_URL in frontend/app.js

---

## 📈 Performance Optimization

### Enable Caching

Create `frontend/_headers`:
```
/*
  Cache-Control: public, max-age=3600, must-revalidate

/*.css
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=31536000, immutable

/*.png
  Cache-Control: public, max-age=31536000, immutable

/*.svg
  Cache-Control: public, max-age=31536000, immutable
```

### Enable Compression

Cloudflare automatically compresses:
- HTML, CSS, JS
- SVG, JSON, XML

### Use Cloudflare CDN

- Automatic global CDN
- Edge caching
- DDoS protection
- Web Application Firewall (WAF)

---

## 🔐 Security Best Practices

### 1. Content Security Policy

Add to `frontend/_headers`:
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 2. HTTPS Only

- Cloudflare Pages enforces HTTPS by default
- HTTP automatically redirects to HTTPS

### 3. API Key Protection

- Never commit API keys to frontend code
- Use backend proxy for sensitive operations
- Implement rate limiting on backend

---

## 📝 Deployment Checklist

Before deploying to production:

- [ ] Test locally: `http://localhost:2125`
- [ ] Update API_BASE_URL to production backend
- [ ] Test with production backend
- [ ] Check all charts load correctly
- [ ] Verify mobile responsiveness
- [ ] Test in multiple browsers
- [ ] Check console for errors
- [ ] Verify CORS is working
- [ ] Test auto-refresh functionality
- [ ] Check search/filter works
- [ ] Verify product detail pages
- [ ] Test with slow network (throttling)
- [ ] Run Lighthouse audit
- [ ] Check accessibility (a11y)

---

## 🎯 Post-Deployment

### 1. Verify Deployment

```bash
# Check if site is live
curl -I https://xinyi.heysalad.app

# Test API connectivity
curl https://xinyi.heysalad.app/
```

### 2. Monitor Performance

- Use Cloudflare Analytics
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor error rates

### 3. Set Up Alerts

- Cloudflare Notifications for:
  - Deployment failures
  - High error rates
  - DDoS attacks

---

## 🔗 Useful Links

- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages
- **Wrangler Docs:** https://developers.cloudflare.com/workers/wrangler
- **GitHub Actions:** https://docs.github.com/en/actions
- **Your Dashboard:** https://dash.cloudflare.com
- **Your Repo:** https://github.com/Hey-Salad/Xin-Yi

---

## 💡 Tips

1. **Use Preview Deployments** for testing before merging to main
2. **Enable Branch Deployments** for staging environment
3. **Set up Slack/Discord notifications** for deployment status
4. **Use Cloudflare Analytics** to monitor traffic
5. **Enable Bot Fight Mode** for security

---

## 🆘 Need Help?

- Cloudflare Community: https://community.cloudflare.com
- GitHub Issues: https://github.com/Hey-Salad/Xin-Yi/issues
- Cloudflare Support: https://support.cloudflare.com

---

**Ready to deploy? Let's go! 🚀**

```bash
# Quick deploy command
wrangler pages deploy frontend --project-name=xinyi-heysalad
```
