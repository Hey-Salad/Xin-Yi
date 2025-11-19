#!/bin/bash

# HeySalad Platform Quick Test Script
# Run this after starting the backend to verify everything works

echo "🧪 Testing HeySalad Platform on Raspberry Pi..."
echo "================================================"
echo ""

BASE_URL="http://localhost:2124"

# Check if jq is installed for pretty JSON
if ! command -v jq &> /dev/null; then
    echo "💡 Tip: Install jq for prettier output: sudo apt install jq"
    JQ_CMD="cat"
else
    JQ_CMD="jq '.'"
fi

echo "1️⃣  Testing Health Check..."
echo "   GET $BASE_URL/health"
curl -s $BASE_URL/health | eval $JQ_CMD
echo ""
echo ""

echo "2️⃣  Testing Service Status..."
echo "   GET $BASE_URL/status"
curl -s $BASE_URL/status | eval $JQ_CMD
echo ""
echo ""

echo "3️⃣  Testing WMS Dashboard Stats..."
echo "   GET $BASE_URL/api/wms/dashboard/stats"
curl -s $BASE_URL/api/wms/dashboard/stats | eval $JQ_CMD
echo ""
echo ""

echo "4️⃣  Testing AI Providers List..."
echo "   GET $BASE_URL/api/ai/providers"
curl -s $BASE_URL/api/ai/providers | eval $JQ_CMD
echo ""
echo ""

echo "5️⃣  Testing OpenAI Chat..."
echo "   POST $BASE_URL/api/ai/chat"
curl -s -X POST $BASE_URL/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","messages":[{"role":"user","content":"Say hello in 3 words"}],"max_tokens":20}' | eval $JQ_CMD
echo ""
echo ""

echo "6️⃣  Testing Payment Config..."
echo "   GET $BASE_URL/api/payment/config"
curl -s $BASE_URL/api/payment/config | eval $JQ_CMD
echo ""
echo ""

echo "7️⃣  Testing Communication Status..."
echo "   GET $BASE_URL/api/communication/status"
curl -s $BASE_URL/api/communication/status | eval $JQ_CMD
echo ""
echo ""

echo "================================================"
echo "✅ All tests complete!"
echo ""
echo "📝 Next steps:"
echo "   • Check output above for any errors"
echo "   • Test specific endpoints you need"
echo "   • See RPI_TESTING_GUIDE.md for detailed tests"
echo ""
