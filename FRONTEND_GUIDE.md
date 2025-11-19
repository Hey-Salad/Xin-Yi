# Frontend Setup Guide - Xin Yi WMS Dashboard

## 🎨 Quick Start

### On Raspberry Pi

**1. Make sure backend is running first:**
```bash
# In one terminal
uv run python backend/app_platform.py
```

**2. Start the frontend (in a new terminal):**
```bash
./start_frontend.sh
```

**3. Access the dashboard:**
- On RPi browser: `http://localhost:2125`
- From your computer: `http://YOUR_RPI_IP:2125`

---

## 📱 Access Options

### Option 1: Local Access (on RPi)
```
http://localhost:2125
```

### Option 2: Network Access (from any device on same network)

**Find your RPi IP:**
```bash
hostname -I
# Example: 192.168.1.100
```

**Open in browser:**
```
http://192.168.1.100:2125
```

### Option 3: SSH Tunnel (secure remote access)

**From your computer:**
```bash
ssh -L 2125:localhost:2125 -L 2124:localhost:2124 pi@YOUR_RPI_IP
```

**Then access:**
```
http://localhost:2125
```

---

## 🎯 What You'll See

### Dashboard Features

1. **Statistics Cards**
   - 📦 Total Inventory
   - 📥 Today's Stock-In
   - 📤 Today's Stock-Out
   - ⚠️ Low Stock Alerts

2. **Charts**
   - 📈 7-Day In/Out Trend
   - 🥧 Category Distribution
   - 📊 Top 10 Stock Items

3. **Inventory Table**
   - Real-time stock levels
   - Search/filter functionality
   - Status indicators (Normal/Low/Critical)
   - Click any item for details

4. **Auto-Refresh**
   - Updates every 3 seconds
   - Countdown timer visible

---

## 🔧 Manual Frontend Start

If you prefer not to use the script:

```bash
cd frontend
python3 server.py
```

---

## 🌐 Configure for Production Domain

### Update API URL for Production

Edit `frontend/app.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'xinyi.heysalad.app'
    ? 'https://api.heysalad.app/api/wms'
    : `http://${window.location.hostname}:2124/api/wms`;
```

---

## 🐛 Troubleshooting

### Issue: "Failed to load data"

**Check backend is running:**
```bash
curl http://localhost:2124/health
```

**Check API endpoint:**
```bash
curl http://localhost:2124/api/wms/dashboard/stats
```

### Issue: "CORS error" in browser console

**Solution:** Backend already has CORS configured. If you still see errors:

1. Check `backend/app_platform.py` CORS settings
2. Make sure you're accessing via the correct URL
3. Try clearing browser cache

### Issue: Charts not displaying

**Check browser console** (F12) for errors

**Verify ECharts is loading:**
```javascript
// In browser console
typeof echarts
// Should return "object"
```

### Issue: Port 2125 already in use

**Find what's using it:**
```bash
sudo lsof -i :2125
```

**Kill the process:**
```bash
sudo kill -9 <PID>
```

**Or use a different port:**
```bash
# Edit frontend/server.py
PORT = 2126  # Change to any available port
```

---

## 📊 Testing Frontend

### Test 1: Open in Browser
```
http://localhost:2125
```

**Expected:** Dashboard loads with data

### Test 2: Check Network Tab (F12)
- Should see successful API calls to `/api/wms/*`
- Status codes should be 200
- Response should contain JSON data

### Test 3: Test Auto-Refresh
- Watch the countdown timer (top right)
- Data should refresh every 3 seconds
- No errors in console

### Test 4: Test Search
- Type in search box
- Table should filter in real-time
- Try searching by product name or SKU

### Test 5: Test Product Details
- Click any row in the inventory table
- Should navigate to product detail page
- Should show 7-day trend and transaction history

---

## 🎨 Customization

### Change Refresh Interval

Edit `frontend/app.js`:
```javascript
// Change from 3 seconds to 5 seconds
let countdownSeconds = 5;
```

### Change Theme Colors

Edit `frontend/style.css`:
```css
:root {
    --primary-color: #667eea;  /* Change to your brand color */
    --success-color: #48bb78;
    --warning-color: #ed8936;
    --danger-color: #f56565;
}
```

### Add Custom Logo

1. Add logo image to `frontend/` folder
2. Edit `frontend/index.html`:
```html
<header>
    <img src="logo.png" alt="Logo" style="height: 40px;">
    <h1>Xin Yi - 仓库管理系统</h1>
</header>
```

---

## 🚀 Production Deployment

### Option 1: Cloudflare Pages

```bash
# Install Wrangler
npm install -g wrangler

# Deploy
cd frontend
wrangler pages deploy . --project-name=xinyi-dashboard
```

### Option 2: Nginx (on RPi)

**Install Nginx:**
```bash
sudo apt install nginx
```

**Configure:**
```bash
sudo nano /etc/nginx/sites-available/xinyi
```

```nginx
server {
    listen 80;
    server_name xinyi.heysalad.app;
    
    root /home/pi/Xin-Yi/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /api/ {
        proxy_pass http://localhost:2124/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/xinyi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel
```

---

## 📱 Mobile Responsive

The dashboard is already mobile-responsive! Test on:
- 📱 Phone (portrait/landscape)
- 📱 Tablet
- 💻 Desktop

---

## 🔐 Add Authentication (Optional)

To add basic auth, edit `frontend/server.py`:

```python
import base64

class AuthHTTPRequestHandler(MyHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get('Authorization')
        if auth_header is None:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Xin Yi"')
            self.end_headers()
            return
        
        # Check credentials (username:password in base64)
        # Example: admin:password123
        expected = base64.b64encode(b'admin:password123').decode()
        if auth_header != f'Basic {expected}':
            self.send_response(401)
            self.end_headers()
            return
        
        super().do_GET()
```

---

## 📈 Performance Tips

### 1. Enable Caching
Already configured in `server.py` with cache control headers

### 2. Compress Assets
```bash
# Install gzip
sudo apt install gzip

# Compress CSS/JS
gzip -k frontend/style.css
gzip -k frontend/app.js
```

### 3. Use CDN for ECharts
Already using CDN in `index.html`

### 4. Optimize Images
```bash
# Install imagemagick
sudo apt install imagemagick

# Optimize images
convert logo.png -quality 85 logo-optimized.png
```

---

## 🎯 Next Steps

1. ✅ Frontend running locally
2. ⬜ Test all dashboard features
3. ⬜ Customize branding/colors
4. ⬜ Set up production domain
5. ⬜ Configure HTTPS with Let's Encrypt
6. ⬜ Set up monitoring/analytics

---

## 📞 Support

- Backend API docs: `README_PLATFORM.md`
- RPi testing: `RPI_TESTING_GUIDE.md`
- Deployment: `DEPLOYMENT_GUIDE.md`

---

Built with ❤️ for HeySalad
