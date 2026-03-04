#!/bin/bash
# Verify iHhashi Deployment Configuration
# This script checks that everything is properly configured

set -e

echo ""
echo "🔍 iHhashi Deployment Verification"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PASS=0
WARN=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++)) || true
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++)) || true
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++)) || true
}

echo -e "${BLUE}Project Structure:${NC}"
echo "─────────────────────────────────────────────"

# Check directories
[ -d "$PROJECT_ROOT/backend" ] && check_pass "Backend directory exists" || check_fail "Backend directory missing"
[ -d "$PROJECT_ROOT/frontend" ] && check_pass "Frontend directory exists" || check_fail "Frontend directory missing"
[ -d "$PROJECT_ROOT/deployment" ] && check_pass "Deployment directory exists" || check_fail "Deployment directory missing"

echo ""
echo -e "${BLUE}Backend Configuration:${NC}"
echo "─────────────────────────────────────────────"

# Backend files
cd "$PROJECT_ROOT/backend"
[ -f "requirements.txt" ] && check_pass "requirements.txt exists" || check_fail "requirements.txt missing"
[ -f "app/main.py" ] && check_pass "main.py exists" || check_fail "main.py missing"
[ -f "railway.json" ] && check_pass "railway.json exists" || check_fail "railway.json missing"
[ -f "railway.toml" ] && check_pass "railway.toml exists" || check_fail "railway.toml missing"
[ -f "Procfile" ] && check_pass "Procfile exists" || check_fail "Procfile missing"
[ -f "Dockerfile" ] && check_pass "Dockerfile exists" || check_fail "Dockerfile missing"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    check_pass "Python installed: $PYTHON_VERSION"
else
    check_fail "Python not installed"
fi

echo ""
echo -e "${BLUE}Frontend Configuration:${NC}"
echo "─────────────────────────────────────────────"

# Frontend files
cd "$PROJECT_ROOT/frontend"
[ -f "package.json" ] && check_pass "package.json exists" || check_fail "package.json missing"
[ -f "vite.config.ts" ] && check_pass "vite.config.ts exists" || check_fail "vite.config.ts missing"
[ -f "netlify.toml" ] && check_pass "netlify.toml exists" || check_fail "netlify.toml missing"
[ -f "dist/index.html" ] && check_pass "dist folder exists (built)" || check_warn "dist folder missing (run npm run build)"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js installed: $NODE_VERSION"
else
    check_fail "Node.js not installed"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    check_pass "npm installed: $NPM_VERSION"
else
    check_fail "npm not installed"
fi

echo ""
echo -e "${BLUE}CLI Tools:${NC}"
echo "─────────────────────────────────────────────"

# Railway CLI
if command -v railway &> /dev/null; then
    check_pass "Railway CLI installed"
else
    check_warn "Railway CLI not installed (npm install -g @railway/cli)"
fi

# Netlify CLI
if command -v netlify &> /dev/null; then
    check_pass "Netlify CLI installed"
else
    check_warn "Netlify CLI not installed (npm install -g netlify-cli)"
fi

# GitHub CLI
if command -v gh &> /dev/null; then
    check_pass "GitHub CLI installed"
else
    check_warn "GitHub CLI not installed (optional, for secret management)"
fi

echo ""
echo -e "${BLUE}Project Links:${NC}"
echo "─────────────────────────────────────────────"

# Check Railway link
if [ -f "$PROJECT_ROOT/.railway/config.json" ]; then
    check_pass "Railway project linked"
else
    check_warn "Railway project not linked (cd backend && railway link)"
fi

# Check Netlify link
if [ -f "$PROJECT_ROOT/.netlify/state.json" ]; then
    check_pass "Netlify site linked"
else
    check_warn "Netlify site not linked (netlify link)"
fi

echo ""
echo -e "${BLUE}GitHub Actions:${NC}"
echo "─────────────────────────────────────────────"

# Check GitHub Actions workflow
if [ -f "$PROJECT_ROOT/.github/workflows/deploy.yml" ]; then
    check_pass "GitHub Actions workflow exists"
else
    check_fail "GitHub Actions workflow missing"
fi

# Check if .github directory exists
if [ -d "$PROJECT_ROOT/.github" ]; then
    check_pass ".github directory exists"
else
    check_warn ".github directory missing (CI/CD not configured)"
fi

echo ""
echo -e "${BLUE}Environment Variables:${NC}"
echo "─────────────────────────────────────────────"

# Check for .env files
[ -f "$PROJECT_ROOT/backend/.env" ] && check_pass "Backend .env exists" || check_warn "Backend .env missing (copy from .env.example)"
[ -f "$PROJECT_ROOT/frontend/.env" ] && check_pass "Frontend .env exists" || check_warn "Frontend .env missing (copy from .env.example)"

# Check for example files
[ -f "$PROJECT_ROOT/backend/.env.example" ] && check_pass "Backend .env.example exists" || check_fail "Backend .env.example missing"
[ -f "$PROJECT_ROOT/frontend/.env.example" ] && check_pass "Frontend .env.example exists" || check_fail "Frontend .env.example missing"

echo ""
echo -e "${BLUE}Scripts:${NC}"
echo "─────────────────────────────────────────────"

# Check deployment scripts
[ -f "$PROJECT_ROOT/deployment/scripts/deploy-railway.sh" ] && check_pass "deploy-railway.sh exists" || check_fail "deploy-railway.sh missing"
[ -f "$PROJECT_ROOT/deployment/scripts/deploy-netlify.sh" ] && check_pass "deploy-netlify.sh exists" || check_fail "deploy-netlify.sh missing"
[ -f "$PROJECT_ROOT/deployment/scripts/full-deploy.sh" ] && check_pass "full-deploy.sh exists" || check_fail "full-deploy.sh missing"
[ -f "$PROJECT_ROOT/deployment/scripts/quick-start.sh" ] && check_pass "quick-start.sh exists" || check_fail "quick-start.sh missing"

# Check if scripts are executable
if [ -x "$PROJECT_ROOT/deployment/scripts/quick-start.sh" ]; then
    check_pass "Scripts are executable"
else
    check_warn "Scripts may not be executable (run: chmod +x deployment/scripts/*.sh)"
fi

echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "─────────────────────────────────────────────"

[ -f "$PROJECT_ROOT/deployment/README.md" ] && check_pass "Deployment README exists" || check_fail "Deployment README missing"
[ -f "$PROJECT_ROOT/README.md" ] && check_pass "Main README exists" || check_warn "Main README missing"

# Summary
echo ""
echo "═══════════════════════════════════════════════"
echo "            VERIFICATION SUMMARY"
echo "═══════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration looks good!${NC}"
    if [ $WARN -gt 0 ]; then
        echo -e "${YELLOW}⚠ Address the warnings above for best results.${NC}"
    fi
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./deployment/scripts/quick-start.sh"
    echo "  2. Or manually:"
    echo "     - cd backend && railway up"
    echo "     - cd frontend && npm run build && netlify deploy --prod"
else
    echo -e "${RED}✗ Please fix the failed checks above.${NC}"
    exit 1
fi

echo ""
