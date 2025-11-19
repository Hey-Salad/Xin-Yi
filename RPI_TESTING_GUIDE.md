# Raspberry Pi Testing Guide

## 📋 Prerequisites Check

```bash
# Check Python version (need 3.12+)
python3 --version

# Check if uv is installed
uv --version

# If not installed:
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

## 🔧 Setup

### 1. Navigate to project
```bash
cd ~/Xin-Yi  # or wherever you cloned it
```

### 2. Verify .env is in backend folder
```bash
ls -la backend/.env
# Should show your .env file
```

### 3. Install dependencies
```bash
uv sync
```

## 🧪 Testing Steps

### Test 1: Start the Platform Backend

```bash
# Start the main platform
uv run python backend/app_platform.py
```

**Expected output:**
```
============================================================
🚀 HeySalad Platform Backend Starting...
============================================================
📍 Port: 2124
🔧 Debug: True
🌍 Environment: development
============================================================

📦 Available Services:
  • WMS (Xin Yi): /api/wms/*
  • AI Services: /api/ai/*
  • Payments: /api/payment/*
  • Communication: /api/communication/*

🔗 Endpoints:
  • API Root: http://localhost:2124/
  • Health: http://localhost:2124/health
  • Status: http://localhost:2124/status
============================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:2124
 * Running on http://192.168.x.x:2124
```

**Keep this terminal open!**

---

### Test 2: Open New Terminal - Test API Endpoints

Open a **new SSH session** or terminal tab:

#### A. Test Platform Root
```bash
curl http://localhost:2124/
```

**Expected:** JSON with service overview

#### B. Test Health Check
```bash
curl http://localhost:2124/health
```

**Expected:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

#### C. Test Service Status
```bash
curl http://localhost:2124/status
```

**Expected:** Shows which services are configured (true/false)

---

### Test 3: WMS (Xin Yi) Endpoints

#### Get Dashboard Stats
```bash
curl http://localhost:2124/api/wms/dashboard/stats
```

**Expected:** Inventory statistics (total stock, today's in/out, etc.)

#### Get FEFO Alerts (Expiring Items)
```bash
curl http://localhost:2124/api/wms/fefo-alerts?hours=48
```

**Expected:** List of items expiring within 48 hours

#### Get Spoilage Rate
```bash
curl http://localhost:2124/api/wms/spoilage-rate?days=30
```

**Expected:** Waste percentage and statistics

---

### Test 4: AI Services

#### List Available AI Providers
```bash
curl http://localhost:2124/api/ai/providers
```

**Expected:** Shows which AI providers are configured

#### Test OpenAI Chat
```bash
curl -X POST http://localhost:2124/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "messages": [{"role": "user", "content": "Say hello in 5 words"}],
    "max_tokens": 50
  }'
```

**Expected:** AI response from OpenAI

#### Test Anthropic (Claude)
```bash
curl -X POST http://localhost:2124/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "anthropic",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "max_tokens": 50
  }'
```

#### Test Gemini
```bash
curl -X POST http://localhost:2124/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "messages": [{"role": "user", "content": "Name 3 fruits"}],
    "max_tokens": 50
  }'
```

---

### Test 5: Payment Services

#### Get Stripe Config
```bash
curl http://localhost:2124/api/payment/config
```

**Expected:** Returns Stripe publishable key

#### Create Payment Intent (Test)
```bash
curl -X POST http://localhost:2124/api/payment/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "currency": "usd",
    "customer_email": "test@example.com"
  }'
```

**Expected:** Payment intent with client_secret

---

### Test 6: Communication Services

#### Check Communication Status
```bash
curl http://localhost:2124/api/communication/status
```

**Expected:** Shows SendGrid and Twilio configuration status

#### Send Test Email
```bash
curl -X POST http://localhost:2124/api/communication/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your-email@example.com",
    "subject": "Test from HeySalad Platform",
    "html_content": "<h1>Hello from Raspberry Pi!</h1><p>Platform is working!</p>"
  }'
```

**Expected:** Email sent confirmation

#### Send Test SMS
```bash
curl -X POST http://localhost:2124/api/communication/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "body": "Test message from HeySalad Platform on RPi"
  }'
```

**Expected:** SMS sent confirmation

---

## 🌐 Test from Browser

If you want to access from your computer (not just RPi):

1. **Find RPi IP address:**
```bash
hostname -I
# Example output: 192.168.1.100
```

2. **Open browser on your computer:**
```
http://192.168.1.100:2124/
```

3. **Test endpoints in browser:**
- `http://192.168.1.100:2124/health`
- `http://192.168.1.100:2124/status`
- `http://192.168.1.100:2124/api/ai/providers`

---

## 🎯 Quick Test Script

Save this as `test_platform.sh`:

```bash
#!/bin/bash

echo "🧪 Testing HeySalad Platform..."
echo ""

BASE_URL="http://localhost:2124"

echo "1️⃣ Testing Health..."
curl -s $BASE_URL/health | jq '.'
echo ""

echo "2️⃣ Testing Status..."
curl -s $BASE_URL/status | jq '.'
echo ""

echo "3️⃣ Testing WMS Stats..."
curl -s $BASE_URL/api/wms/dashboard/stats | jq '.'
echo ""

echo "4️⃣ Testing AI Providers..."
curl -s $BASE_URL/api/ai/providers | jq '.'
echo ""

echo "5️⃣ Testing OpenAI Chat..."
curl -s -X POST $BASE_URL/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","messages":[{"role":"user","content":"Say hi"}],"max_tokens":20}' | jq '.'
echo ""

echo "✅ All tests complete!"
```

**Run it:**
```bash
chmod +x test_platform.sh
./test_platform.sh
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Reinstall dependencies
uv sync
```

### Issue: "Port already in use"
```bash
# Check what's using port 2124
sudo lsof -i :2124

# Kill the process
sudo kill -9 <PID>
```

### Issue: "Connection refused"
```bash
# Check if backend is running
ps aux | grep app_platform

# Check firewall (if applicable)
sudo ufw status
```

### Issue: Database connection errors
```bash
# Verify Supabase credentials in .env
cat backend/.env | grep SUPABASE

# Test connection
curl -H "apikey: YOUR_SUPABASE_KEY" \
  "https://YOUR_PROJECT.supabase.co/rest/v1/materials?select=*&limit=1"
```

### Issue: AI API errors
```bash
# Check which providers are configured
curl http://localhost:2124/api/ai/providers

# Verify API keys in .env
cat backend/.env | grep API_KEY
```

---

## 📊 Performance Monitoring

### Check CPU/Memory usage
```bash
# While platform is running
top -p $(pgrep -f app_platform)
```

### Check logs
```bash
# Run with verbose logging
FLASK_DEBUG=True uv run python backend/app_platform.py
```

---

## 🎉 Success Indicators

✅ Backend starts without errors
✅ Health endpoint returns `{"status": "healthy"}`
✅ Status shows configured services
✅ WMS endpoints return data from Supabase
✅ AI chat returns responses
✅ Payment config returns Stripe key
✅ Communication status shows configured services

---

## 🚀 Next Steps After Testing

1. **Set up as systemd service** (auto-start on boot)
2. **Configure nginx reverse proxy** (for HTTPS)
3. **Set up monitoring** (Prometheus/Grafana)
4. **Deploy frontend** to access via web UI
5. **Configure domain** (xinyi.heysalad.app)

See `DEPLOYMENT_GUIDE.md` for production setup!
