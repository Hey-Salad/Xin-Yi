# Deployment Guide | 部署指南

Complete guide to deploy Xin Yi Warehouse Management System to production.

完整指南：将 Xin Yi 仓库管理系统部署到生产环境。

---

## Architecture Overview | 架构概览

```
Frontend: xinyi.heysalad.app (Cloudflare Pages)
Backend:  api.heysalad.app (Raspberry Pi + Cloudflare Tunnel)
Database: Supabase PostgreSQL
```

**Total Cost: $0/month** 🎉

---

## Prerequisites | 前置条件

- [x] Cloudflare account with `heysalad.app` domain
- [x] Supabase account with database created
- [x] Raspberry Pi with internet connection
- [x] GitHub account (for Cloudflare Pages)

---

## Part 1: Database Setup (Supabase) | 数据库设置

### 1.1 Create Supabase Project

1. Go to https://supabase.com
2. Create new project: `HeySalad_Xinyi`
3. Save credentials:
   - Project URL: `https://xxxxx.supabase.co`
   - anon key: `eyJ...`
   - service_role key: `eyJ...`

### 1.2 Create Database Schema

In Supabase SQL Editor, run:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Materials table
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT '个',
    safe_stock INTEGER DEFAULT 20,
    location TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inventory records table
CREATE TABLE inventory_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('in', 'out')),
    quantity INTEGER NOT NULL,
    operator TEXT DEFAULT '系统',
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_materials_sku ON materials(sku);
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_records_material_id ON inventory_records(material_id);
CREATE INDEX idx_records_created_at ON inventory_records(created_at);
CREATE INDEX idx_records_type ON inventory_records(type);
```

### 1.3 Insert Sample Data

Run the INSERT statements from the deployment guide (see SQL file).

---

## Part 2: Backend Setup (Raspberry Pi) | 后端设置

### 2.1 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Clone repository
cd ~
git clone <your-repo-url>
cd warehouse_system

# Install Python dependencies
uv sync
```

### 2.2 Configure Environment Variables

```bash
# Create .env file
nano .env
```

Paste your Supabase credentials:

```env
SUPABASE_URL=https://ohbhwrpdxbrbxbdinmqr.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
FLASK_ENV=production
FLASK_DEBUG=False
```

### 2.3 Test Backend

```bash
cd backend
uv run python database_supabase.py  # Test connection
uv run python app_supabase.py       # Start backend
```

Visit http://localhost:2124/api/dashboard/stats - should return JSON.

### 2.4 Create Systemd Service (Auto-start)

```bash
sudo nano /etc/systemd/system/warehouse-backend.service
```

```ini
[Unit]
Description=Warehouse Backend API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/warehouse_system/backend
Environment="PATH=/home/pi/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/.local/bin/uv run python app_supabase.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable warehouse-backend
sudo systemctl start warehouse-backend
sudo systemctl status warehouse-backend

# Check logs
sudo journalctl -u warehouse-backend -f
```

---

## Part 3: Cloudflare Tunnel Setup | Cloudflare 隧道设置

### 3.1 Install Cloudflared

```bash
# Download for Raspberry Pi (ARM64)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared

# Install
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

# Verify installation
cloudflared --version
```

### 3.2 Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser - select your `heysalad.app` domain.

### 3.3 Create Tunnel

```bash
cloudflared tunnel create xinyi-backend
```

Save the Tunnel ID shown (e.g., `abc123-def456-...`).

### 3.4 Configure Tunnel

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: api.heysalad.app
    service: http://localhost:2124
  - service: http_status:404
```

### 3.5 Create DNS Record

In Cloudflare Dashboard:
1. Go to **Zero Trust** → **Tunnels**
2. Click your tunnel → **Public Hostname**
3. Add hostname:
   - **Subdomain:** `api`
   - **Domain:** `heysalad.app`
   - **Service:** `HTTP://localhost:2124`

### 3.6 Install Tunnel as Service

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl status cloudflared

# Check logs
sudo journalctl -u cloudflared -f
```

### 3.7 Test Tunnel

```bash
# From your computer (not RPi)
curl https://api.heysalad.app/api/dashboard/stats
```

Should return JSON data!

---

## Part 4: Frontend Deployment (Cloudflare Pages) | 前端部署

### 4.1 Push to GitHub

```bash
cd ~/warehouse_system
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 4.2 Deploy to Cloudflare Pages

1. Go to https://dash.cloudflare.com
2. Click **Pages** → **Create a project**
3. Connect to GitHub → Select your repository
4. Configure build:
   - **Build command:** `cd frontend && mkdir -p dist && cp *.html *.css *.js dist/`
   - **Build output directory:** `frontend/dist`
5. Click **Save and Deploy**

### 4.3 Add Custom Domain

1. In Cloudflare Pages → Your project → **Custom domains**
2. Click **Set up a custom domain**
3. Enter: `xinyi.heysalad.app`
4. Click **Activate domain**

Wait 1-2 minutes for DNS propagation.

### 4.4 Test Frontend

Visit https://xinyi.heysalad.app

Should see your dashboard! 🎉

---

## Part 5: Verification Checklist | 验证清单

### Database
- [ ] Supabase project created
- [ ] Tables created (materials, inventory_records)
- [ ] Sample data inserted
- [ ] Connection tested from RPi

### Backend
- [ ] Backend running on RPi (port 2124)
- [ ] Systemd service enabled (auto-start)
- [ ] Environment variables configured
- [ ] Local test successful: `curl http://localhost:2124/api/dashboard/stats`

### Cloudflare Tunnel
- [ ] Cloudflared installed on RPi
- [ ] Tunnel created and configured
- [ ] DNS record created: `api.heysalad.app`
- [ ] Tunnel service running
- [ ] Remote test successful: `curl https://api.heysalad.app/api/dashboard/stats`

### Frontend
- [ ] Code pushed to GitHub
- [ ] Cloudflare Pages project created
- [ ] Build successful
- [ ] Custom domain added: `xinyi.heysalad.app`
- [ ] Website accessible: https://xinyi.heysalad.app
- [ ] API calls working (check browser console)

---

## Monitoring & Maintenance | 监控与维护

### Check Backend Status

```bash
# Service status
sudo systemctl status warehouse-backend

# View logs (last 50 lines)
sudo journalctl -u warehouse-backend -n 50

# Follow logs in real-time
sudo journalctl -u warehouse-backend -f
```

### Check Tunnel Status

```bash
# Service status
sudo systemctl status cloudflared

# View logs
sudo journalctl -u cloudflared -n 50
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart warehouse-backend

# Restart tunnel
sudo systemctl restart cloudflared

# Restart both
sudo systemctl restart warehouse-backend cloudflared
```

### Update Code

```bash
cd ~/warehouse_system
git pull origin main
sudo systemctl restart warehouse-backend
```

Frontend updates automatically via Cloudflare Pages on git push.

---

## Troubleshooting | 故障排除

### Backend not accessible

```bash
# Check if backend is running
curl http://localhost:2124/api/dashboard/stats

# If not working, check logs
sudo journalctl -u warehouse-backend -n 100

# Common issues:
# 1. Port already in use: sudo lsof -i :2124
# 2. Environment variables missing: cat .env
# 3. Supabase connection failed: check credentials
```

### Tunnel not working

```bash
# Check tunnel status
sudo systemctl status cloudflared

# Check logs
sudo journalctl -u cloudflared -n 100

# Test from outside
curl https://api.heysalad.app/api/dashboard/stats

# Common issues:
# 1. DNS not propagated: wait 5 minutes
# 2. Tunnel config wrong: check ~/.cloudflared/config.yml
# 3. Backend not running: check backend service
```

### Frontend not loading

1. Check Cloudflare Pages build logs
2. Verify custom domain is active
3. Check browser console for errors
4. Verify API_BASE_URL in app.js

---

## Security Best Practices | 安全最佳实践

### 1. Protect .env File

```bash
chmod 600 .env
```

Never commit `.env` to git (already in `.gitignore`).

### 2. Keep RPi Updated

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Monitor Logs

Check logs weekly for suspicious activity:

```bash
sudo journalctl -u warehouse-backend --since "1 week ago" | grep -i error
```

### 4. Backup Database

Supabase auto-backups, but you can also:

```bash
# Export data via Supabase dashboard
# Settings → Database → Backups
```

---

## Cost Summary | 成本总结

| Service | Cost | Notes |
|---------|------|-------|
| **Supabase** | $0/mo | Free tier: 500MB DB |
| **Cloudflare Pages** | $0/mo | Unlimited requests |
| **Cloudflare Tunnel** | $0/mo | Free forever |
| **Raspberry Pi** | $0/mo | You own it |
| **Domain** | ~$12/yr | heysalad.app |
| **Total** | **$1/mo** | Just domain cost! |

---

## Next Steps | 下一步

1. ✅ Deploy to production (follow this guide)
2. 🔄 Transform to food inventory (Xin Yi)
3. 👥 Add multi-tenancy (SaaS)
4. 💳 Add Stripe billing
5. 📱 Build mobile app

---

**Questions?** Check the other documentation:
- `README.md` - Project overview
- `CODE_WALKTHROUGH.md` - How the code works
- `DEVELOPMENT_PROMPTS.md` - Development history

**Status:** Ready for deployment! 🚀
