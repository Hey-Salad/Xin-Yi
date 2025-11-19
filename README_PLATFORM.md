# HeySalad Platform Backend

Comprehensive backend API platform for HeySalad services, featuring:
- 🥗 **Xin Yi**: Food inventory WMS with FEFO logic
- 🤖 **AI Services**: Multi-provider chat & image generation
- 💳 **Payments**: Stripe integration
- 📧 **Communication**: Email (SendGrid) & SMS (Twilio)

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the platform
uv run python backend/app_platform.py
```

Access at: `http://localhost:2124`

## 📚 API Documentation

### Platform Root
```
GET /
```
Returns overview of all available services and endpoints.

### Health Check
```
GET /health
```
Simple health check for monitoring.

### Service Status
```
GET /status
```
Detailed status of all integrated services.

---

## 🥗 WMS (Xin Yi) - Warehouse Management

**Base URL:** `/api/wms`

### Dashboard Statistics
```
GET /api/wms/dashboard/stats
```
Returns inventory totals, today's in/out, low stock alerts.

### FEFO Alerts
```
GET /api/wms/fefo-alerts?hours=48
```
Get items expiring within specified hours (default: 48).

**Response:**
```json
[
  {
    "lot_number": "LOT-2024-001",
    "material_name": "Organic Spinach",
    "quantity": 50,
    "expiration_date": "2024-01-20",
    "hours_until_expiry": 36.5,
    "urgency": "warning"
  }
]
```

### Spoilage Rate
```
GET /api/wms/spoilage-rate?days=30
```
Calculate waste percentage over specified period.

### Stock In (with Lot Tracking)
```
POST /api/wms/stock/in
Content-Type: application/json

{
  "material_id": "uuid",
  "quantity": 100,
  "lot_number": "LOT-2024-001",
  "expiration_date": "2024-02-15",
  "catch_weight": 45.5,
  "operator": "John Doe",
  "reason": "Purchase arrival"
}
```

### Stock Out (FEFO Logic)
```
POST /api/wms/stock/out
Content-Type: application/json

{
  "material_id": "uuid",
  "quantity": 50,
  "operator": "Jane Smith",
  "reason": "Sales order"
}
```

Automatically picks from earliest expiring lots.

---

## 🤖 AI Services

**Base URL:** `/api/ai`

### Universal Chat
```
POST /api/ai/chat
Content-Type: application/json

{
  "provider": "openai",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Supported Providers:**
- `openai` - GPT-4o-mini, GPT-4
- `anthropic` - Claude 3 Opus, Sonnet
- `gemini` - Gemini 1.5 Flash, Pro
- `deepseek` - DeepSeek Chat
- `huggingface` - Various open models

### Image Generation
```
POST /api/ai/image/generate
Content-Type: application/json

{
  "provider": "dalle",
  "prompt": "A fresh salad bowl with colorful vegetables",
  "size": "1024x1024"
}
```

### List Providers
```
GET /api/ai/providers
```
Returns available AI providers and their configuration status.

---

## 💳 Payment Processing

**Base URL:** `/api/payment`

### Create Payment Intent
```
POST /api/payment/create-payment-intent
Content-Type: application/json

{
  "amount": 2999,
  "currency": "usd",
  "customer_email": "customer@example.com",
  "metadata": {
    "order_id": "ORD-12345"
  }
}
```

**Response:**
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

### Create Subscription
```
POST /api/payment/create-subscription
Content-Type: application/json

{
  "customer_id": "cus_xxx",
  "price_id": "price_xxx",
  "trial_days": 14
}
```

### Webhook Handler
```
POST /api/payment/webhook
```
Handles Stripe webhook events (payment success, subscription changes, etc.)

### Get Config
```
GET /api/payment/config
```
Returns Stripe publishable key for frontend.

---

## 📧 Communication Services

**Base URL:** `/api/communication`

### Send Email
```
POST /api/communication/email/send
Content-Type: application/json

{
  "to": "customer@example.com",
  "subject": "Order Confirmation",
  "html_content": "<h1>Thank you!</h1>",
  "text_content": "Thank you for your order!"
}
```

### Send Template Email
```
POST /api/communication/email/template
Content-Type: application/json

{
  "to": "customer@example.com",
  "template_id": "d-xxx",
  "dynamic_data": {
    "customer_name": "John",
    "order_id": "12345"
  }
}
```

### Send SMS
```
POST /api/communication/sms/send
Content-Type: application/json

{
  "to": "+1234567890",
  "body": "Your verification code is 123456"
}
```

### Make Voice Call
```
POST /api/communication/voice/call
Content-Type: application/json

{
  "to": "+1234567890",
  "twiml_url": "https://example.com/twiml"
}
```

---

## 🔧 Configuration

### Required Environment Variables

```bash
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# AI Providers (at least one required)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GEMINI_API_KEY=xxx
DEEPSEEK_API_KEY=sk-xxx
HUGGINGFACE_API_KEY=hf_xxx
CLOUDFLARE_API_KEY=xxx

# Payment
STRIPE_PUBLIC_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Communication
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@heysalad.io
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 🚢 Deployment

### Cloudflare Workers / Pages Functions

1. **Install Wrangler:**
```bash
npm install -g wrangler
```

2. **Configure `wrangler.toml`:**
```toml
name = "heysalad-platform"
main = "backend/app_platform.py"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }
```

3. **Deploy:**
```bash
wrangler deploy
```

### Railway

1. **Connect GitHub repo**
2. **Set environment variables** in Railway dashboard
3. **Deploy automatically** on push to main

### Docker

```bash
docker build -t heysalad-platform .
docker run -p 2124:2124 --env-file .env heysalad-platform
```

---

## 🧪 Testing

```bash
# Run all tests
./test/run_all_tests.sh

# Test specific service
python3 test/test_wms.py
python3 test/test_ai.py
python3 test/test_payment.py
```

---

## 📦 Project Structure

```
heysalad-platform/
├── backend/
│   ├── app_platform.py          # Main application
│   ├── routes/
│   │   ├── wms_routes.py        # WMS/Inventory
│   │   ├── ai_routes.py         # AI services
│   │   ├── payment_routes.py    # Stripe
│   │   └── communication_routes.py  # Email/SMS
│   ├── database_supabase.py     # Database client
│   └── ...
├── frontend/                     # Frontend apps
├── mcp/                         # MCP integration
├── test/                        # Test suites
├── .env                         # Environment config (DO NOT COMMIT)
├── .gitignore                   # Git ignore rules
└── pyproject.toml              # Dependencies
```

---

## 🔐 Security

- **Never commit `.env` files** - Use `.env.example` as template
- **Use environment variables** for all secrets
- **Enable CORS** only for trusted domains
- **Validate all inputs** before processing
- **Use HTTPS** in production
- **Rotate API keys** regularly

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🆘 Support

- Documentation: [docs.heysalad.app](https://docs.heysalad.app)
- Issues: [GitHub Issues](https://github.com/heysalad/platform/issues)
- Email: support@heysalad.io

---

## 🗺️ Roadmap

- [ ] Add Stability AI image generation
- [ ] Implement rate limiting
- [ ] Add Redis caching
- [ ] WebSocket support for real-time updates
- [ ] GraphQL API
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app APIs

---

Built with ❤️ by the HeySalad team
