# Image Display Troubleshooting

## ✅ What's Working

1. **Backend has image URLs** - Confirmed via API test
2. **Images are accessible** - Supabase storage returns 200 OK
3. **Frontend has image display code** - CSS and JavaScript are correct

## 🔍 Why Images Might Not Show

### Issue 1: Backend Not Restarted

The new `catalog_assets.py` module was added in the latest pull. Your local backend needs to be restarted to load it.

**Solution:**
```bash
# Stop the current backend process
# Find it:
ps aux | grep app_platform

# Kill it (replace PID):
kill -9 <PID>

# Or if using the process manager:
# Stop process ID 6 (from earlier)

# Restart:
uv run python backend/app_platform.py
```

### Issue 2: Image Index Not in Supabase

The images need an index file in Supabase Storage.

**Check if it exists:**
```bash
# Test the catalog endpoint
curl http://localhost:2124/api/wms/materials/all | grep storage_image_url | head -5
```

**If you see `"storage_image_url": null`, the index file is missing.**

### Issue 3: Browser Cache

**Solution:**
```bash
# Hard refresh in browser
# Mac: Cmd + Shift + R
# Windows: Ctrl + Shift + R

# Or open DevTools (F12) and disable cache
```

## 🧪 Quick Test

**1. Test API directly:**
```bash
curl -s http://localhost:2124/api/wms/materials/all | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data[:3]:
    print(f\"SKU: {item['sku']}\")
    print(f\"Name: {item['name']}\")
    print(f\"Image: {item.get('storage_image_url', 'NO IMAGE')}\")
    print('---')
"
```

**2. Test in browser console (F12):**
```javascript
// Check if images are in the data
fetch('http://localhost:2124/api/wms/materials/all')
  .then(r => r.json())
  .then(data => {
    console.log('First item:', data[0]);
    console.log('Has image?', !!data[0].storage_image_url);
  });
```

**3. Check if images render:**
```javascript
// In browser console
document.querySelectorAll('.material-thumb img').forEach(img => {
  console.log('Image src:', img.src);
  console.log('Image loaded:', img.complete);
});
```

## 🔧 Fix Steps

### Step 1: Restart Backend

```bash
# Kill old process
pkill -f app_platform

# Start new one
uv run python backend/app_platform.py
```

### Step 2: Refresh Frontend

```bash
# Hard refresh browser
# Cmd + Shift + R (Mac)
# Ctrl + Shift + R (Windows/Linux)
```

### Step 3: Check Browser Console

Open DevTools (F12) and look for:
- ❌ Red errors about images
- ⚠️ Yellow warnings about CORS
- ✅ Green network requests for images

## 📊 Expected Result

You should see:
- Small product thumbnails (56x56px) next to each product name
- Images load from: `https://ohbhwrpdxbrbxbdinmqr.supabase.co/storage/v1/object/public/catalog-images/products/...`
- Placeholder box if no image available

## 🆘 Still Not Working?

Run this diagnostic:

```bash
# Check backend is returning images
curl -s http://localhost:2124/api/wms/materials/all | \
  python3 -c "import sys, json; data = json.load(sys.stdin); \
  print(f'Total items: {len(data)}'); \
  with_images = sum(1 for item in data if item.get('storage_image_url')); \
  print(f'Items with images: {with_images}'); \
  print(f'Percentage: {with_images/len(data)*100:.1f}%')"
```

If percentage is 0%, the image index isn't loaded. Check:
1. Is `SUPABASE_URL` set in `.env`?
2. Does the Supabase bucket `catalog-images` exist?
3. Is the index file `catalog/longdan_image_index.json` in `catalog-cache` bucket?

---

**Most likely fix:** Just restart the backend! 🔄
