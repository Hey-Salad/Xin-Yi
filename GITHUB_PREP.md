# GitHub Preparation Checklist

## ✅ Pre-Push Security Checklist

### 1. Environment Variables
- [x] `.env` added to `.gitignore`
- [x] `.env.example` created with template values
- [ ] Verify no secrets in committed files

### 2. Sensitive Files Check
Run this command to check for potential secrets:
```bash
# Check for API keys in tracked files
git grep -i "api_key\|secret\|password\|token" -- ':!.env' ':!.env.example'

# Check what will be committed
git status
git diff --cached
```

### 3. Clean Up Before Push
```bash
# Remove any accidentally tracked files
git rm --cached .env
git rm --cached backend/warehouse.db
git rm --cached *.log

# Commit the cleanup
git add .gitignore
git commit -m "chore: update gitignore and remove sensitive files"
```

## 🚀 GitHub Repository Setup

### 1. Create Repository
```bash
# On GitHub, create new repository: heysalad-platform
# Then locally:

git init
git add .
git commit -m "feat: initial HeySalad platform backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/heysalad-platform.git
git push -u origin main
```

### 2. Repository Settings

#### Secrets (Settings → Secrets and variables → Actions)
Add these as GitHub Secrets for CI/CD:

**Database:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`

**AI Providers:**
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`
- `HUGGINGFACE_API_KEY`
- `CLOUDFLARE_API_KEY`

**Payment:**
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

**Communication:**
- `SENDGRID_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`

#### Branch Protection
- Enable branch protection for `main`
- Require pull request reviews
- Require status checks to pass

### 3. Add README Badges
Add to top of README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## 📝 Commit Message Convention

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/config changes

Examples:
```bash
git commit -m "feat: add FEFO alert endpoint"
git commit -m "fix: resolve Stripe webhook signature validation"
git commit -m "docs: update API documentation"
```

## 🔍 Pre-Push Verification

Run these checks before pushing:

```bash
# 1. Check for secrets
grep -r "sk-" . --exclude-dir=.git --exclude=.env --exclude=.env.example

# 2. Verify .gitignore is working
git status --ignored

# 3. Test the application
uv run python backend/app_platform.py

# 4. Run tests
./test/run_all_tests.sh

# 5. Check file sizes (avoid large files)
find . -type f -size +10M
```

## 🚨 Emergency: Leaked Secret

If you accidentally commit a secret:

```bash
# 1. Immediately rotate the compromised key/token
# 2. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (DANGEROUS - coordinate with team)
git push origin --force --all

# 4. Better: Use BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/
```

## 📦 Deployment Checklist

### Cloudflare Workers
- [ ] Install Wrangler CLI
- [ ] Configure `wrangler.toml`
- [ ] Set environment variables in Cloudflare dashboard
- [ ] Deploy: `wrangler deploy`

### Railway
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set up automatic deployments
- [ ] Configure custom domain

### Vercel/Netlify (Frontend)
- [ ] Connect repository
- [ ] Set build command
- [ ] Configure environment variables
- [ ] Set up custom domain

## 🎯 Post-Push Tasks

1. **Update Documentation**
   - [ ] Add API examples
   - [ ] Create architecture diagrams
   - [ ] Write deployment guide

2. **Set Up CI/CD**
   - [ ] GitHub Actions workflow
   - [ ] Automated testing
   - [ ] Deployment pipeline

3. **Monitoring**
   - [ ] Set up error tracking (Sentry)
   - [ ] Configure logging
   - [ ] Set up uptime monitoring

4. **Security**
   - [ ] Enable Dependabot
   - [ ] Set up security scanning
   - [ ] Configure CORS properly

## ✨ Ready to Push!

Once all checks pass:

```bash
git add .
git commit -m "feat: complete HeySalad platform backend with WMS, AI, payments, and communication"
git push origin main
```

## 🔗 Useful Links

- GitHub Docs: https://docs.github.com
- Conventional Commits: https://www.conventionalcommits.org
- Semantic Versioning: https://semver.org
- Keep a Changelog: https://keepachangelog.com
