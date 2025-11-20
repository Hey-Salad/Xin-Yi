<img src="https://raw.githubusercontent.com/Hey-Salad/.github/refs/heads/main/HeySalad%20Logo%20%2B%20Tagline%20Black.svg" alt="HeySalad Logo" width="400"/>

# Xin Yi WMS® - Intelligent Food Warehouse Management 🥗

> **AI-powered warehouse management system designed for fresh food logistics with FEFO (First Expired, First Out) intelligence**

A comprehensive warehouse management platform built for HeySalad's fresh food operations, featuring real-time inventory tracking, expiration management, and AI-driven insights.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Pages-F38020.svg)](https://pages.cloudflare.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ **Key Features**

### 📊 **Real-Time Dashboard**
- Live inventory statistics and KPIs
- 7-day trend analysis with interactive charts
- Category distribution visualization
- Top 10 stock items tracking
- Auto-refresh every 30 seconds

### ⏰ **FEFO Intelligence**
- First Expired, First Out logic for stock-out operations
- Expiration alerts (configurable threshold)
- Lot-based inventory tracking
- Spoilage rate monitoring
- Temperature breach logging

### 🔍 **Product Management**
- Detailed product views with images
- Transaction history tracking
- Real-time stock levels
- Safety stock monitoring
- Multi-language support (English | 中文)

### 🤖 **AI Integration**
- Multi-provider AI chat (OpenAI, Anthropic, Gemini, DeepSeek)
- Natural language inventory queries
- Recipe suggestions for expiring ingredients
- Automated reporting

### 💳 **Payment & Communication**
- Stripe payment processing
- SendGrid email notifications
- Twilio SMS alerts
- Webhook handling

---

## 📱 **Screenshots**

| Dashboard | Product Details | Inventory List | FEFO Alerts |
|-----------|----------------|----------------|-------------|
| ![Dashboard](screenshots/dashboard.png) | ![Details](screenshots/product-detail.png) | ![Inventory](screenshots/inventory.png) | ![Alerts](screenshots/fefo-alerts.png) |

*Real-time warehouse management with beautiful, intuitive interface*

---

## 🛠 **Technical Stack**

### **Backend**
- **Framework:** Flask 3.1+ with modular blueprints
- **Database:** Supabase (PostgreSQL) with real-time subscriptions
- **API:** RESTful endpoints with CORS support
- **Authentication:** JWT tokens with role-based access
- **Deployment:** Raspberry Pi + Cloudflare Tunnel

### **Frontend**
- **Core:** Vanilla JavaScript (ES6+)
- **Charts:** ECharts 5.4+ for data visualization
- **Styling:** Custom CSS with HeySalad® branding
- **Deployment:** Cloudflare Pages with CI/CD
- **Domain:** [xinyi.heysalad.app](https://xinyi.heysalad.app)

### **Architecture**
```
Frontend (Cloudflare Pages)
    ↓ HTTPS
Backend API (wms.heysalad.app)
    ↓ PostgreSQL
Database (Supabase)
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.12+
- uv package manager
- Supabase account
- Node.js 18+ (for frontend deployment)

### **Installation**

```bash
# Clone repository
git clone https://github.com/Hey-Salad/Xin-Yi.git
cd Xin-Yi

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
# Run the SQL migrations in backend/migrations/

# Start backend
uv run python backend/app_platform.py

# Start frontend (in new terminal)
cd frontend
python3 server.py
```

### **Access**
- **Frontend:** http://localhost:2125
- **Backend API:** http://localhost:2124
- **API Docs:** http://localhost:2124/

---

## 🌐 **API Endpoints**

### **Dashboard**
```http
GET /api/wms/dashboard/stats          # Dashboard statistics
GET /api/wms/dashboard/category-distribution  # Category pie chart
GET /api/wms/dashboard/weekly-trend   # 7-day trend data
GET /api/wms/dashboard/top-stock      # Top 10 items
```

### **Inventory Management**
```http
GET  /api/wms/materials/all           # All inventory items
GET  /api/wms/materials/info?name=X   # Single product details
GET  /api/wms/materials/product-stats?name=X  # Product statistics
GET  /api/wms/materials/product-trend?name=X  # 7-day trend
GET  /api/wms/materials/product-records?name=X # Transaction history
POST /api/wms/stock/in                # Stock-in operation
POST /api/wms/stock/out               # Stock-out (FEFO)
```

### **FEFO & Alerts**
```http
GET /api/wms/fefo-alerts?hours=48     # Expiring items
GET /api/wms/spoilage-rate?days=30    # Waste statistics
```

### **AI Services**
```http
POST /api/ai/chat                     # Multi-provider AI chat
POST /api/ai/image/generate           # Image generation
GET  /api/ai/providers                # Available AI providers
```

---

## 📊 **Database Schema**

### **Materials Table**
```sql
CREATE TABLE materials (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'unit',
    safe_stock INTEGER DEFAULT 20,
    location TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Inventory Lots Table** (FEFO Tracking)
```sql
CREATE TABLE inventory_lots (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    lot_number TEXT NOT NULL,
    expiration_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    catch_weight DECIMAL(10,2),
    status TEXT DEFAULT 'active',
    received_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Inventory Records Table**
```sql
CREATE TABLE inventory_records (
    id UUID PRIMARY KEY,
    material_id UUID REFERENCES materials(id),
    type TEXT CHECK (type IN ('in', 'out')),
    quantity INTEGER NOT NULL,
    operator TEXT DEFAULT 'System',
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔧 **Configuration**

### **Environment Variables**

```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Backend
BACKEND_PORT=2124
FRONTEND_PORT=2125
FLASK_ENV=production

# AI Providers (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Payment (optional)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...

# Communication (optional)
SENDGRID_API_KEY=SG....
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

---

## 🚢 **Deployment**

### **Frontend (Cloudflare Pages)**

```bash
# Install Wrangler
npm install -g wrangler

# Login
wrangler login

# Deploy
./deploy-to-cloudflare.sh
```

**Or use CI/CD:**
1. Add GitHub secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
2. Push to `main` branch
3. Automatic deployment via GitHub Actions

### **Backend (Raspberry Pi + Cloudflare Tunnel)**

```bash
# On Raspberry Pi
cd ~/Xin-Yi
git pull origin main

# Set up systemd service
sudo cp scripts/heysalad-backend.service /etc/systemd/system/
sudo systemctl enable heysalad-backend
sudo systemctl start heysalad-backend

# Configure Cloudflare Tunnel
cloudflared tunnel create xinyi-wms
cloudflared tunnel route dns xinyi-wms wms.heysalad.app
cloudflared tunnel run xinyi-wms
```

---

## 🧪 **Testing**

```bash
# Run all tests
./test/run_all_tests.sh

# Test specific components
python3 test/test_api.py          # API endpoints
python3 test/test_mcp.py           # MCP integration
python3 test/test_fefo.py          # FEFO logic

# Test platform
./test_platform.sh
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Development Guidelines**
- Follow PEP 8 for Python code
- Use TypeScript for new frontend features
- Add tests for new functionality
- Update documentation
- Maintain bilingual support (EN | 中文)

### **Get Help with Claude AI**

**Install the GitHub App:**
Run `/install-github-app` to add Claude to this repository for automated code reviews and PR assistance!

Once installed, tag [@claude](https://github.com/apps/claude-for-github) in issues and PRs for AI assistance!

---

## 📚 **Documentation**

- **[API Documentation](README_PLATFORM.md)** - Complete API reference
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Frontend Guide](FRONTEND_GUIDE.md)** - Frontend development
- **[Code Walkthrough](CODE_WALKTHROUGH.md)** - Architecture deep dive
- **[Testing Guide](test/README.md)** - Testing procedures
- **[Cloudflare Setup](CLOUDFLARE_PAGES_SETUP.md)** - CI/CD configuration

---

## 🎯 **Roadmap**

### **Phase 1: Core Features** ✅
- [x] Real-time dashboard
- [x] Inventory management
- [x] Product detail views
- [x] Multi-language support

### **Phase 2: FEFO Intelligence** 🚧
- [x] Lot-based tracking
- [x] Expiration alerts
- [x] FEFO stock-out logic
- [ ] Temperature monitoring
- [ ] Automated spoilage reports

### **Phase 3: AI Integration** 🔜
- [ ] Natural language queries
- [ ] Recipe suggestions
- [ ] Demand forecasting
- [ ] Automated reordering

### **Phase 4: Mobile App** 📱
- [ ] React Native app
- [ ] Barcode scanning
- [ ] Offline mode
- [ ] Push notifications

---

## ⚖️ **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**HeySalad®** (UK Trademark Registration No. **UK00004063403**) is a registered trademark of **SALADHR TECHNOLOGY LTD**.

---

## 🙏 **Acknowledgments**

- **Supabase** for excellent PostgreSQL hosting and real-time features
- **Cloudflare** for global CDN and Pages deployment
- **ECharts** for beautiful data visualization
- **Open Source Community** for countless libraries and inspiration

---

## 📞 **Contact & Support**

- **Issues:** [GitHub Issues](https://github.com/Hey-Salad/Xin-Yi/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Hey-Salad/Xin-Yi/discussions)
- **Email:** [peter@heysalad.io](mailto:peter@heysalad.io)
- **Website:** [heysalad.io](https://heysalad.io)

---

## ☕ **Support Us**

If you find Xin Yi WMS useful, consider supporting HeySalad!

<a href="https://www.buymeacoffee.com/heysalad"><img src="https://github.com/Hey-Salad/.github/blob/a4cbf4a12cca3477fdbfe55520b3fdfe0e0f35a4/bmc-button.png" alt="Buy Me A Coffee" width="200"/></a>

---

## ⚠️ **Disclaimer**

This software is provided "as is" without warranties. Always test thoroughly before using in production environments. For food safety compliance, consult with regulatory experts in your jurisdiction.

---

<div align="center">

**Built with ❤️ by HeySalad**

*Making food logistics smarter, one warehouse at a time*

[⭐ Star this repo](https://github.com/Hey-Salad/Xin-Yi) • [🐛 Report Issues](https://github.com/Hey-Salad/Xin-Yi/issues) • [💬 Discussions](https://github.com/Hey-Salad/Xin-Yi/discussions)

**Let's make every meal count! 🌱✨**

</div>
