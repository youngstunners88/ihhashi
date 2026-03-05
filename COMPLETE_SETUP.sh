#!/bin/bash
# Complete iHhashi Deployment Setup
# Run this script to set up everything

set -e

echo "🚀 iHhashi Complete Deployment Setup"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

REPO="youngstunners88/ihhashi"

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 installed${NC}"
        return 0
    fi
}

echo "Checking required tools..."
check_command git
check_command gh || { echo "Installing GitHub CLI..."; curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && sudo apt update && sudo apt install gh -y; }
check_command npm || { echo "Please install Node.js/npm first"; exit 1; }

echo ""
echo "Installing Railway and Netlify CLIs..."
npm install -g @railway/cli netlify-cli

echo ""
echo -e "${BLUE}Step 1: GitHub Login${NC}"
echo "====================="
if ! gh auth status &> /dev/null; then
    echo "Please login to GitHub:"
    gh auth login
fi

echo ""
echo -e "${BLUE}Step 2: Setting GitHub Secrets${NC}"
echo "==============================="

# Secrets
RAILWAY_TOKEN="91e3ad14-e35d-490d-9fa0-361ecc59822f"
NETLIFY_TOKEN="nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b"

echo "$RAILWAY_TOKEN" | gh secret set RAILWAY_TOKEN --repo "$REPO" && echo -e "${GREEN}✓ RAILWAY_TOKEN set${NC}" || echo -e "${RED}✗ RAILWAY_TOKEN failed${NC}"
echo "$NETLIFY_TOKEN" | gh secret set NETLIFY_AUTH_TOKEN --repo "$REPO" && echo -e "${GREEN}✓ NETLIFY_AUTH_TOKEN set${NC}" || echo -e "${RED}✗ NETLIFY_AUTH_TOKEN failed${NC}"

# Get Netlify Site ID
echo ""
echo -e "${YELLOW}Getting Netlify Site ID...${NC}"
export NETLIFY_AUTH_TOKEN="$NETLIFY_TOKEN"
NETLIFY_SITE_ID=$(netlify sites:list --json 2>/dev/null | python3 -c "import json,sys; sites=json.load(sys.stdin); print(sites[0]['id']) if sites else ''" || echo "")

if [ -z "$NETLIFY_SITE_ID" ]; then
    echo -e "${YELLOW}Please create a Netlify site first:${NC}"
    cd frontend
    netlify init --manual
    NETLIFY_SITE_ID=$(netlify status --json 2>/dev/null | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    cd ..
fi

if [ -n "$NETLIFY_SITE_ID" ]; then
    echo "$NETLIFY_SITE_ID" | gh secret set NETLIFY_SITE_ID --repo "$REPO" && echo -e "${GREEN}✓ NETLIFY_SITE_ID set${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Railway Setup${NC}"
echo "======================"

export RAILWAY_TOKEN="$RAILWAY_TOKEN"
cd backend

# Check if already linked
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}Creating new Railway project...${NC}"
    railway login
    railway init --name ihhashi-api
fi

# Set environment variables
echo "Setting Railway environment variables..."
railway variables set MONGODB_URL="mongodb+srv://teacherchris37_db_user:iHhashil!!!@cluster0.ai5z7wq.mongodb.net/ihhashi?retryWrites=true&w=majority"
railway variables set DB_NAME=ihhashi
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set APP_NAME=iHhashi
railway variables set APP_VERSION=0.3.0
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set REFRESH_TOKEN_EXPIRE_DAYS=7
railway variables set DEFAULT_CURRENCY=ZAR
railway variables set VAT_RATE=0.15
railway variables set DEFAULT_TIMEZONE=Africa/Johannesburg
echo -e "${GREEN}✓ Railway variables set${NC}"

# Get Railway URL
RAILWAY_URL=$(railway domain 2>/dev/null || echo "")
if [ -n "$RAILWAY_URL" ]; then
    RAILWAY_URL="https://$RAILWAY_URL"
else
    echo -e "${YELLOW}Railway URL not available yet. Will be available after first deploy.${NC}"
    RAILWAY_URL="https://ihhashi-api.up.railway.app"
fi

cd ..

echo ""
echo -e "${BLUE}Step 4: Frontend Environment Variables${NC}"
echo "========================================="

echo "$RAILWAY_URL" | gh secret set VITE_API_URL --repo "$REPO" && echo -e "${GREEN}✓ VITE_API_URL set to $RAILWAY_URL${NC}"

echo ""
echo -e "${YELLOW}Please enter your Supabase credentials:${NC}"
read -p "VITE_SUPABASE_URL (e.g., https://xxxxx.supabase.co): " VITE_SUPABASE_URL
read -p "VITE_SUPABASE_ANON_KEY: " VITE_SUPABASE_ANON_KEY

echo "$VITE_SUPABASE_URL" | gh secret set VITE_SUPABASE_URL --repo "$REPO"
echo "$VITE_SUPABASE_ANON_KEY" | gh secret set VITE_SUPABASE_ANON_KEY --repo "$REPO"
echo -e "${GREEN}✓ Supabase secrets set${NC}"

echo ""
echo -e "${BLUE}Step 5: Deploy!${NC}"
echo "=================="

# Merge work to main and push
git checkout main 2>/dev/null || git checkout -b main
git merge work --no-edit
git push origin main

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${CYAN}What's Next:${NC}"
echo "1. The GitHub Actions workflow will run automatically"
echo "2. Check deployment status at: https://github.com/$REPO/actions"
echo "3. Your backend will be at: $RAILWAY_URL"
echo ""
echo -e "${YELLOW}Manual Steps Remaining:${NC}"
echo "1. Add Redis to your Railway project (Railway Dashboard > New > Redis)"
echo "2. Add Supabase credentials to Railway variables:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo "3. Add SECRET_KEY to Railway: openssl rand -base64 32"
echo ""
echo -e "${BLUE}Railway Dashboard:${NC} https://railway.app/dashboard"
echo -e "${BLUE}Netlify Dashboard:${NC} https://app.netlify.com"
echo ""
