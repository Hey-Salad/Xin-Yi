# Get Cloudflare Credentials for CI/CD

## Step 1: Get Account ID

1. Go to: https://dash.cloudflare.com
2. Click on any domain or go to **Workers & Pages**
3. Look at the URL or right sidebar
4. Your Account ID is visible there (format: `abc123def456...`)

**Or use Wrangler CLI:**
```bash
# Install if not already installed
npm install -g wrangler

# Login
wrangler login

# Get account ID
wrangler whoami
```

Copy your **Account ID** - you'll need it for GitHub Secrets.

---

## Step 2: Create API Token

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click **Create Token**
3. Click **Use template** next to **Edit Cloudflare Workers**
4. Or create custom token with these permissions:
   - **Account** → **Cloudflare Pages** → **Edit**
5. Click **Continue to summary**
6. Click **Create Token**
7. **COPY THE TOKEN NOW** (you won't see it again!)

---

## Step 3: Add Secrets to GitHub

1. Go to: https://github.com/Hey-Salad/Xin-Yi/settings/secrets/actions

2. Click **New repository secret**

3. Add Secret #1:
   ```
   Name: CLOUDFLARE_API_TOKEN
   Value: <paste-your-api-token-here>
   ```

4. Click **Add secret**

5. Add Secret #2:
   ```
   Name: CLOUDFLARE_ACCOUNT_ID
   Value: <paste-your-account-id-here>
   ```

6. Click **Add secret**

---

## Step 4: Verify Setup

Once secrets are added, the GitHub Actions workflow will automatically run on the next push to `main`.

**Check deployment status:**
- GitHub Actions: https://github.com/Hey-Salad/Xin-Yi/actions
- Cloudflare Dashboard: https://dash.cloudflare.com → Workers & Pages → xinyi-heysalad

---

## Step 5: Add Custom Domain

1. In Cloudflare Pages project, go to **Custom domains** tab
2. Click **Set up a custom domain**
3. Enter: `xinyi.heysalad.app`
4. Click **Continue**
5. Cloudflare will automatically configure DNS

---

## ✅ Done!

Your CI/CD pipeline is now active:
- ✅ Auto-deploy on push to `main`
- ✅ Preview deployments for pull requests
- ✅ Custom domain configured
- ✅ Free SSL certificate
- ✅ Global CDN

**Test it:**
```bash
# Make a small change
echo "<!-- CI/CD test -->" >> frontend/index.html

# Commit and push
git add .
git commit -m "test: trigger CI/CD"
git push origin main

# Watch it deploy
# GitHub: https://github.com/Hey-Salad/Xin-Yi/actions
# Cloudflare: https://dash.cloudflare.com
```
