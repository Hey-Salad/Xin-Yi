# Cloudflare Tunnel Deployment Guide

## Overview

This guide documents the deployment of the Xin Yi WMS backend using Cloudflare Tunnel, providing secure public access without exposing ports or configuring firewalls.

---

## Architecture

```
Internet
    ↓
Cloudflare CDN (wms.heysalad.app)
    ↓
Cloudflare Tunnel (heysalad-mcp)
    ↓
Local Backend (127.0.0.1:2124)
    ↓
Supabase Database
```

---

## What Was Deployed

### 1. Backend Service
- **URL**: https://wms.heysalad.app
- **Local Port**: 2124
- **Service**: Xin Yi WMS Platform Backend
- **Auto-start**: Enabled via systemd

### 2. Cloudflare Tunnel
- **Tunnel Name**: heysalad-mcp
- **Tunnel ID**: b496dc88-3b8a-458c-9ee1-70569684c3a9
- **DNS Record**: wms.heysalad.app → Cloudflare Tunnel
- **SSL**: Automatic via Cloudflare (free)

---

## Deployment Steps Completed

### Step 1: Cloudflare Tunnel Configuration

**File**: `/etc/cloudflared/config.yml`

```yaml
tunnel: heysalad-mcp
credentials-file: /home/admin/.cloudflared/heysalad-mcp.json

ingress:
  - hostname: wms.heysalad.app
    service: http://127.0.0.1:2124
  - hostname: vscode.heysalad.app
    service: http://127.0.0.1:8081
    originRequest:
      noTLSVerify: true
  - hostname: mcp.heysalad.app
    service: http://127.0.0.1:4141
  - service: http_status:404
```

### Step 2: DNS Configuration

Created CNAME record automatically:

```bash
cloudflared tunnel route dns heysalad-mcp wms.heysalad.app
```

**Result**: `wms.heysalad.app` → Cloudflare Tunnel IPs

### Step 3: Backend Systemd Service

**File**: `/etc/systemd/system/xinyi-backend.service`

```ini
[Unit]
Description=Xin Yi WMS Backend - HeySalad Platform
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/Xin-Yi
Environment="PATH=/home/admin/Xin-Yi/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/admin/.local/bin/uv run python backend/app_platform.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=xinyi-backend

[Install]
WantedBy=multi-user.target
```

**Commands executed**:
```bash
sudo systemctl enable xinyi-backend.service
sudo systemctl start xinyi-backend.service
```

### Step 4: Restart Cloudflared

```bash
sudo systemctl restart cloudflared
```

---

## Access URLs

### Public Access (via Cloudflare Tunnel)

- **Health Check**: https://wms.heysalad.app/health
- **API Root**: https://wms.heysalad.app/
- **WMS Dashboard Stats**: https://wms.heysalad.app/api/wms/dashboard/stats
- **WMS Materials**: https://wms.heysalad.app/api/wms/materials/all

### Local Access (on Raspberry Pi)

- **Health Check**: http://localhost:2124/health
- **API Root**: http://localhost:2124/
- **WMS Dashboard Stats**: http://localhost:2124/api/wms/dashboard/stats

---

## Service Management

### Backend Service

```bash
# Check status
sudo systemctl status xinyi-backend

# Start service
sudo systemctl start xinyi-backend

# Stop service
sudo systemctl stop xinyi-backend

# Restart service
sudo systemctl restart xinyi-backend

# View logs
sudo journalctl -u xinyi-backend -f

# View recent logs
sudo journalctl -u xinyi-backend -n 100 --no-pager
```

### Cloudflare Tunnel Service

```bash
# Check status
sudo systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# View logs
sudo journalctl -u cloudflared -f

# Check tunnel info
cloudflared tunnel info heysalad-mcp

# List all tunnels
cloudflared tunnel list

# Check tunnel connections
cloudflared tunnel info heysalad-mcp
```

---

## Testing Deployment

### 1. Test Health Endpoint

```bash
# Public
curl https://wms.heysalad.app/health

# Expected Response:
{
  "environment": "development",
  "status": "healthy"
}
```

### 2. Test API Endpoint

```bash
# Public
curl https://wms.heysalad.app/api/wms/dashboard/stats

# Expected Response:
{
  "in_change": -100.0,
  "low_stock_count": 0,
  "material_types": 36,
  "out_change": -100.0,
  "today_in": 0,
  "today_out": 0,
  "total_stock": 3337
}
```

### 3. Test DNS Resolution

```bash
nslookup wms.heysalad.app

# Expected:
# Name:	wms.heysalad.app
# Address: 104.21.70.254
# Address: 172.67.141.25
```

### 4. Check SSL Certificate

```bash
openssl s_client -connect wms.heysalad.app:443 -servername wms.heysalad.app < /dev/null 2>/dev/null | grep -A 2 "subject="

# Expected:
# subject=CN=heysalad.app
```

---

## Updating Frontend to Use Public API

Update `frontend/app.js` to use the public API:

```javascript
// API Base URL | API 基础 URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:2124/api/wms'
    : 'https://wms.heysalad.app/api/wms';  // Use public URL
```

Or for production deployment:

```javascript
const API_BASE_URL = window.location.hostname === 'xinyi.heysalad.app'
    ? 'https://wms.heysalad.app/api/wms'
    : `http://${window.location.hostname}:2124/api/wms`;
```

---

## Troubleshooting

### Issue: 404 Error when accessing public URL

**Symptoms**: `curl https://wms.heysalad.app/health` returns 404

**Solutions**:
1. Check if cloudflared service is running:
   ```bash
   sudo systemctl status cloudflared
   ```

2. Verify config file is correct:
   ```bash
   sudo cat /etc/cloudflared/config.yml
   ```

3. Check if DNS is resolving:
   ```bash
   nslookup wms.heysalad.app
   ```

4. Restart cloudflared:
   ```bash
   sudo systemctl restart cloudflared
   ```

5. Wait 1-2 minutes for config changes to propagate

### Issue: Backend not responding

**Symptoms**: Local requests fail with connection refused

**Solutions**:
1. Check if backend is running:
   ```bash
   sudo systemctl status xinyi-backend
   ```

2. Check backend logs:
   ```bash
   sudo journalctl -u xinyi-backend -n 50
   ```

3. Test backend locally:
   ```bash
   curl http://localhost:2124/health
   ```

4. Restart backend:
   ```bash
   sudo systemctl restart xinyi-backend
   ```

### Issue: Tunnel connections dropping

**Symptoms**: Cloudflared shows "Connection terminated"

**Solutions**:
1. Check cloudflared logs:
   ```bash
   sudo journalctl -u cloudflared -n 100
   ```

2. Verify credentials file exists:
   ```bash
   ls -la /home/admin/.cloudflared/heysalad-mcp.json
   ```

3. Restart cloudflared:
   ```bash
   sudo systemctl restart cloudflared
   ```

### Issue: CORS errors in browser

**Symptoms**: Frontend shows CORS errors in console

**Solutions**:
Already configured in `backend/app_platform.py`:

```python
CORS(app, origins=[
    "https://xinyi.heysalad.app",
    "https://heysalad.app",
    "https://*.heysalad.app",
    "http://localhost:*",
    "http://127.0.0.1:*"
])
```

If issues persist:
1. Verify the frontend is accessing the correct API URL
2. Check browser console for specific CORS error
3. Restart backend after CORS config changes

---

## Security Considerations

### 1. Cloudflare Protection

Cloudflare automatically provides:
- DDoS protection
- SSL/TLS encryption
- WAF (Web Application Firewall)
- Rate limiting
- Bot protection

### 2. No Exposed Ports

- Backend runs on localhost only
- No inbound firewall rules needed
- Tunnel connection is outbound only

### 3. Environment Variables

Sensitive data in `.env` file:
```bash
# Ensure .env is not committed
cat .gitignore | grep .env

# Check permissions
ls -la /home/admin/Xin-Yi/.env
```

### 4. Authentication

For production, consider adding authentication:
- JWT tokens
- API keys
- OAuth 2.0

Example in Flask:
```python
from flask import request, jsonify
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/wms/dashboard/stats')
@require_api_key
def get_stats():
    # Your code here
    pass
```

---

## Performance Optimization

### 1. Cloudflare Caching

Add cache headers for static endpoints:

```python
@app.route('/api/wms/dashboard/category-distribution')
def get_category_distribution():
    response = jsonify(data)
    response.headers['Cache-Control'] = 'public, max-age=60'  # Cache for 1 minute
    return response
```

### 2. Compression

Enable gzip compression in Flask:

```python
from flask_compress import Compress
compress = Compress(app)
```

### 3. Database Connection Pooling

Already configured in Supabase client.

---

## Monitoring

### 1. Check Backend Health

```bash
# Create a cron job to monitor health
crontab -e

# Add line:
*/5 * * * * curl -f https://wms.heysalad.app/health || echo "Backend down!" | mail -s "WMS Backend Alert" your@email.com
```

### 2. Cloudflare Analytics

Visit Cloudflare Dashboard:
- https://dash.cloudflare.com/
- Navigate to: heysalad.app → Analytics

### 3. System Monitoring

```bash
# Check system resources
htop

# Check disk space
df -h

# Check memory
free -h

# Check backend process
ps aux | grep "python backend/app_platform.py"
```

---

## Scaling

### Option 1: Deploy to Cloud

For higher traffic, consider:
- **Fly.io**: Automatic scaling, global edge
- **Railway**: Simple deployment, database included
- **Render**: Free tier, auto-deploy from Git
- **Digital Ocean App Platform**: Managed service

### Option 2: Multiple Instances

Run multiple backend instances:

```bash
# Instance 1 on port 2124
uv run python backend/app_platform.py

# Instance 2 on port 2125
PORT=2125 uv run python backend/app_platform.py
```

Update cloudflared config for load balancing:

```yaml
ingress:
  - hostname: wms.heysalad.app
    service: http_status:200
    originRequest:
      httpHostHeader: wms.heysalad.app
      loadBalancer:
        pool: wms-pool
```

---

## Backup and Recovery

### 1. Backup Configuration Files

```bash
# Create backup directory
mkdir -p ~/backups/xinyi-deployment

# Backup cloudflared config
sudo cp /etc/cloudflared/config.yml ~/backups/xinyi-deployment/
cp ~/.cloudflared/heysalad-mcp.json ~/backups/xinyi-deployment/

# Backup systemd service
sudo cp /etc/systemd/system/xinyi-backend.service ~/backups/xinyi-deployment/

# Backup environment variables
cp /home/admin/Xin-Yi/.env ~/backups/xinyi-deployment/env.backup
```

### 2. Database Backup

Supabase provides automatic backups, but you can also export:

```bash
# Export to SQL
pg_dump "postgresql://user:pass@db.xxx.supabase.co:5432/postgres" > backup.sql
```

### 3. Code Backup

Already backed up to GitHub:
- https://github.com/Hey-Salad/Xin-Yi

---

## Cost Analysis

### Current Setup (FREE)

- Cloudflare Tunnel: **$0/month** (Free tier)
- Cloudflare DNS: **$0/month** (Free tier)
- SSL Certificate: **$0/month** (Free via Cloudflare)
- Raspberry Pi: **~$5/month** (electricity)
- Supabase: **$0-25/month** (depends on usage)

**Total**: ~$5-30/month

### Cloud Alternative Costs

- Fly.io: $0-5/month (shared-cpu-1x)
- Railway: $5/month (starter)
- Render: $0-7/month (free tier + $7 for pro)
- Digital Ocean: $4-6/month (basic droplet)

---

## API Documentation

Full API documentation available at:
- Local: http://localhost:2124/
- Public: https://wms.heysalad.app/

### Available Services

1. **WMS (Warehouse Management)**
   - Prefix: `/api/wms`
   - Endpoints: Dashboard stats, materials, FEFO alerts, stock operations

2. **AI Services**
   - Prefix: `/api/ai`
   - Endpoints: Chat, image generation

3. **Payment Processing**
   - Prefix: `/api/payment`
   - Endpoints: Stripe integration

4. **Communication**
   - Prefix: `/api/communication`
   - Endpoints: Email, SMS

---

## Next Steps

### 1. Deploy Frontend

Options:
- **Cloudflare Pages**: Free, fast, auto-deploy from Git
- **Vercel**: Free tier, excellent performance
- **Netlify**: Free tier, simple deployment
- **Serve from RPi**: Use nginx or Apache

### 2. Add Monitoring

- Set up Sentry for error tracking
- Configure Grafana for metrics
- Enable Cloudflare Analytics

### 3. Add Authentication

- Implement JWT authentication
- Add API rate limiting
- Set up user roles/permissions

### 4. Enable HTTPS for Local Access

- Use Let's Encrypt
- Configure nginx reverse proxy
- Enable HTTP/2

---

## Support

### Documentation

- Backend: `/home/admin/Xin-Yi/README_PLATFORM.md`
- Frontend: `/home/admin/Xin-Yi/FRONTEND_GUIDE.md`
- Testing: `/home/admin/Xin-Yi/RPI_TESTING_GUIDE.md`

### Cloudflare Resources

- Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- Dashboard: https://dash.cloudflare.com/
- Support: https://support.cloudflare.com/

### GitHub Repository

- https://github.com/Hey-Salad/Xin-Yi

---

## Changelog

### 2025-11-19
- ✅ Configured Cloudflare Tunnel for wms.heysalad.app
- ✅ Created systemd service for backend auto-start
- ✅ Added missing API endpoints (category-distribution, weekly-trend, top-stock, materials/all)
- ✅ Made frontend bilingual (English | Chinese)
- ✅ Tested public access via Cloudflare Tunnel
- ✅ Created comprehensive deployment documentation

---

**Deployment Status**: ✅ LIVE

**Public URL**: https://wms.heysalad.app

**Last Updated**: November 19, 2025

---

Built with ❤️ for HeySalad
