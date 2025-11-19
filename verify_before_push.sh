#!/bin/bash

# HeySalad Platform - Pre-Push Verification Script
# Run this before pushing to GitHub to ensure no secrets are leaked

echo "🔍 HeySalad Platform - Pre-Push Security Check"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Verify .env is not tracked
echo "📋 Check 1: Verifying .env is not tracked..."
if git ls-files | grep -q "^\.env$"; then
    echo -e "${RED}❌ FAIL: .env file is tracked by git!${NC}"
    echo "   Run: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ PASS: .env is not tracked${NC}"
fi
echo ""

# Check 2: Look for potential secrets in tracked files
echo "📋 Check 2: Scanning for potential secrets..."
SECRETS_FOUND=0

# Check for actual API keys (sk- followed by more than just package names)
if git grep -E "sk-[a-zA-Z0-9]{20,}" -- ':!.env' ':!.env.example' ':!verify_before_push.sh' ':!uv.lock' ':!*.lock' > /dev/null 2>&1; then
    echo -e "${RED}❌ WARNING: Found potential OpenAI/Stripe keys${NC}"
    git grep -n -E "sk-[a-zA-Z0-9]{20,}" -- ':!.env' ':!.env.example' ':!verify_before_push.sh' ':!uv.lock' ':!*.lock'
    SECRETS_FOUND=1
fi

if git grep -i "pk_live\|sk_live" -- ':!.env' ':!.env.example' > /dev/null 2>&1; then
    echo -e "${RED}❌ WARNING: Found Stripe live keys${NC}"
    git grep -n "pk_live\|sk_live" -- ':!.env' ':!.env.example'
    SECRETS_FOUND=1
fi

if git grep -i "SG\.[a-zA-Z0-9]" -- ':!.env' ':!.env.example' > /dev/null 2>&1; then
    echo -e "${RED}❌ WARNING: Found SendGrid API keys${NC}"
    git grep -n "SG\.[a-zA-Z0-9]" -- ':!.env' ':!.env.example'
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: No obvious secrets found${NC}"
else
    echo -e "${YELLOW}⚠️  Please review the findings above${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Verify .gitignore exists and contains key entries
echo "📋 Check 3: Verifying .gitignore..."
if [ ! -f .gitignore ]; then
    echo -e "${RED}❌ FAIL: .gitignore file not found!${NC}"
    ERRORS=$((ERRORS + 1))
else
    REQUIRED_ENTRIES=(".env" "*.db" "__pycache__" "*.log")
    MISSING=0
    
    for entry in "${REQUIRED_ENTRIES[@]}"; do
        if ! grep -q "$entry" .gitignore; then
            echo -e "${RED}❌ Missing in .gitignore: $entry${NC}"
            MISSING=1
        fi
    done
    
    if [ $MISSING -eq 0 ]; then
        echo -e "${GREEN}✅ PASS: .gitignore properly configured${NC}"
    else
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# Check 4: Verify .env.example exists
echo "📋 Check 4: Verifying .env.example exists..."
if [ ! -f .env.example ]; then
    echo -e "${YELLOW}⚠️  WARNING: .env.example not found${NC}"
    echo "   Consider creating one as a template"
else
    echo -e "${GREEN}✅ PASS: .env.example exists${NC}"
fi
echo ""

# Check 5: Check for large files
echo "📋 Check 5: Checking for large files (>10MB)..."
LARGE_FILES=$(find . -type f -size +10M -not -path "./.git/*" 2>/dev/null)
if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Large files found:${NC}"
    echo "$LARGE_FILES"
    echo "   Consider using Git LFS or excluding these files"
else
    echo -e "${GREEN}✅ PASS: No large files found${NC}"
fi
echo ""

# Check 6: Verify database files are not tracked
echo "📋 Check 6: Checking for database files..."
if git ls-files | grep -q "\.db$\|\.sqlite$"; then
    echo -e "${RED}❌ FAIL: Database files are tracked!${NC}"
    git ls-files | grep "\.db$\|\.sqlite$"
    echo "   Run: git rm --cached *.db"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ PASS: No database files tracked${NC}"
fi
echo ""

# Summary
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Safe to push.${NC}"
    echo ""
    echo "Next steps:"
    echo "  git add ."
    echo "  git commit -m 'feat: your commit message'"
    echo "  git push origin main"
    exit 0
else
    echo -e "${RED}❌ $ERRORS check(s) failed!${NC}"
    echo ""
    echo "Please fix the issues above before pushing."
    echo "See GITHUB_PREP.md for detailed instructions."
    exit 1
fi
