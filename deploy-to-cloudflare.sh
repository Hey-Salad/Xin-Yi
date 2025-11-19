#!/bin/bash

# Quick Deploy to Cloudflare Pages
# This script helps you deploy the frontend to Cloudflare Pages

echo "🚀 Cloudflare Pages Deployment Helper"
echo "======================================"
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Wrangler not found. Installing..."
    npm install -g wrangler
fi

echo "✅ Wrangler is installed"
echo ""

# Check if logged in
echo "🔐 Checking Cloudflare authentication..."
if ! wrangler whoami &> /dev/null; then
    echo "Please login to Cloudflare:"
    wrangler login
else
    echo "✅ Already logged in to Cloudflare"
fi

echo ""
echo "📋 Your Cloudflare Account Info:"
wrangler whoami
echo ""

# Deploy
echo "🚀 Deploying frontend to Cloudflare Pages..."
echo ""

wrangler pages deploy frontend \
    --project-name=xinyi-heysalad \
    --branch=main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your site will be available at:"
echo "   • https://xinyi-heysalad.pages.dev"
echo "   • https://xinyi.heysalad.app (after custom domain setup)"
echo ""
echo "🔗 Next steps:"
echo "   1. Go to: https://dash.cloudflare.com"
echo "   2. Navigate to: Workers & Pages → xinyi-heysalad"
echo "   3. Add custom domain: xinyi.heysalad.app"
echo ""
echo "📚 For CI/CD setup, see: GET_CLOUDFLARE_CREDENTIALS.md"
echo ""
