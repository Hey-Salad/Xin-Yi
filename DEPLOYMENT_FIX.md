# Deployment Fix for Next.js Migration

## Problem
After migrating from `frontend/` to `frontend-next/`, GitHub Actions was still watching the old directory, so changes weren't being deployed.

## What Was Fixed

### 1. GitHub Actions Workflow (`.github/workflows/deploy-frontend.yml`)
**Changes:**
- ✅ Updated path trigger from `frontend/**` to `frontend-next/**`
- ✅ Added Node.js setup step
- ✅ Added npm install and build steps
- ✅ Changed deployment directory from `frontend` to `frontend-next/out`
- ✅ Added environment variables for build

### 2. Wrangler Configuration (`wrangler.toml`)
**Changes:**
- ✅ Updated `pages_build_output_dir` to `./frontend-next/out`
- ✅ Updated build command to build Next.js app
- ✅ Updated `watch_dirs` to `["frontend-next"]`
- ✅ Added environment variable placeholders

### 3. Next.js Configuration (`frontend-next/next.config.ts`)
**Changes:**
- ✅ Added `output: 'export'` for static site generation
- ✅ Added `images: { unoptimized: true }` for Cloudflare Pages compatibility

## What You Need to Do

### Step 1: Add GitHub Secrets
Go to your repo → Settings → Secrets and variables → Actions

Add these secrets if not already present:
```
CLOUDFLARE_API_TOKEN=your-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
NEXT_PUBLIC_API_URL=https://wms.heysalad.app/api
NEXT_PUBLIC_SUPABASE_URL=https://ohbhwrpdxbrbxbdinmqr.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your-supabase-key
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoiY2hpbHVtYmFwbSIsImEiOiJjbWdraTY1amswdWk3MmlxeXNhaGwyYzNjIn0.-Yv4ZPYvyxqYV_SBV9aJSA
```

### Step 2: Update Cloudflare Pages Settings (Optional)
If using Cloudflare Pages direct integration:

1. Go to Cloudflare Dashboard → Pages → xinyi-heysalad
2. Settings → Builds & deployments
3. Update:
   - **Build command:** `cd frontend-next && npm install && npm run build`
   - **Build output directory:** `frontend-next/out`
   - **Root directory:** `/`

4. Environment variables → Add:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_KEY`
   - `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN`

### Step 3: Test Deployment

**Option A: Push to GitHub (Automatic)**
```bash
git add .
git commit -m "Fix Next.js deployment configuration"
git push origin main
```

The GitHub Action will automatically trigger and deploy!

**Option B: Manual Deploy with Wrangler**
```bash
cd frontend-next
npm run build
npx wrangler pages deploy out --project-name=xinyi-heysalad
```

## Verification

After deployment, check:
1. ✅ GitHub Actions tab - workflow should complete successfully
2. ✅ Cloudflare Pages dashboard - new deployment should appear
3. ✅ Visit your site: https://xinyi-heysalad.pages.dev
4. ✅ Custom domain: https://xinyi.heysalad.app (if configured)

## Troubleshooting

### If build fails:
- Check GitHub Actions logs for specific errors
- Verify all secrets are set correctly
- Ensure `package-lock.json` is committed

### If site loads but features don't work:
- Check browser console for API errors
- Verify environment variables are set in Cloudflare
- Check that `NEXT_PUBLIC_API_URL` points to your backend

### If images don't load:
- This is expected with `unoptimized: true`
- Images will load but without Next.js optimization
- For better performance, consider using Cloudflare Images

## Notes

- **Static Export:** Next.js is now configured for static export (`output: 'export'`)
- **No Server-Side Rendering:** API routes and server components won't work in static export
- **Client-Side Only:** All data fetching happens client-side via your Flask backend
- **Environment Variables:** Must be prefixed with `NEXT_PUBLIC_` to be available in browser

## Next Steps

1. Commit and push these changes
2. Monitor GitHub Actions for successful deployment
3. Test the deployed site
4. Update DNS if needed for custom domain
