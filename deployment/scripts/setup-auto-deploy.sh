#!/bin/bash
# Complete Auto-Deployment Setup for iHhashi
# This sets up GitHub Actions auto-deploy to Railway and Netlify

set -e

echo "🚀 Setting up Auto-Deployment for iHhashi"
echo "==========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO="youngstunners88/ihhashi"
RAILWAY_TOKEN="91e3ad14-e35d-490d-9fa0-361ecc59822f"
NETLIFY_TOKEN="nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b"

echo ""
echo -e "${CYAN}Repository:${NC} $REPO"
echo ""

# Check GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}Installing GitHub CLI...${NC}"
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update && sudo apt install gh -y
fi

# Check login status
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Please login to GitHub:${NC}"
    gh auth login
fi

echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"

# Install Railway CLI if needed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Installing Railway CLI...${NC}"
    npm install -g @railway/cli
fi

# Install Netlify CLI if needed
if ! command -v netlify &> /dev/null; then
    echo -e "${YELLOW}Installing Netlify CLI...${NC}"
    npm install -g netlify-cli
fi

echo ""
echo -e "${CYAN}Step 1: Configuring GitHub Secrets${NC}"
echo "====================================="

# Set Railway token
echo -e "${BLUE}Setting RAILWAY_TOKEN...${NC}"
echo "$RAILWAY_TOKEN" | gh secret set RAILWAY_TOKEN --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ RAILWAY_TOKEN set${NC}" || echo -e "${YELLOW}! Failed to set RAILWAY_TOKEN${NC}"

# Set Netlify auth token
echo -e "${BLUE}Setting NETLIFY_AUTH_TOKEN...${NC}"
echo "$NETLIFY_TOKEN" | gh secret set NETLIFY_AUTH_TOKEN --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ NETLIFY_AUTH_TOKEN set${NC}" || echo -e "${YELLOW}! Failed to set NETLIFY_AUTH_TOKEN${NC}"

# Get and set Netlify Site ID
echo ""
echo -e "${CYAN}Step 2: Getting Netlify Site ID${NC}"
echo "================================="

NETLIFY_SITE_ID=$(netlify sites:list --json 2>/dev/null | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")

if [ -z "$NETLIFY_SITE_ID" ]; then
    echo -e "${YELLOW}Could not auto-detect Netlify Site ID.${NC}"
    echo -e "${BLUE}Please enter your Netlify Site ID manually:${NC}"
    echo "(Find it at: https://app.netlify.com/ > Your Site > Site settings > Site details > Site ID)"
    read -p "Site ID: " NETLIFY_SITE_ID
fi

if [ -n "$NETLIFY_SITE_ID" ]; then
    echo -e "${BLUE}Setting NETLIFY_SITE_ID...${NC}"
    echo "$NETLIFY_SITE_ID" | gh secret set NETLIFY_SITE_ID --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ NETLIFY_SITE_ID set${NC}" || echo -e "${YELLOW}! Failed to set NETLIFY_SITE_ID${NC}"
fi

echo ""
echo -e "${CYAN}Step 3: Frontend Environment Variables${NC}"
echo "========================================="
echo -e "${YELLOW}These are needed for the frontend build:${NC}"
echo ""

# Get Railway URL
RAILWAY_URL=$(cd backend && railway domain 2>/dev/null || echo "")
if [ -n "$RAILWAY_URL" ]; then
    VITE_API_URL="https://$RAILWAY_URL"
    echo -e "${GREEN}Detected Railway URL: $VITE_API_URL${NC}"
else
    echo -e "${YELLOW}Could not detect Railway URL.${NC}"
    read -p "Enter your Railway backend URL (e.g., https://ihhashi-api.up.railway.app): " VITE_API_URL
fi

echo -e "${BLUE}Setting VITE_API_URL...${NC}"
echo "$VITE_API_URL" | gh secret set VITE_API_URL --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ VITE_API_URL set${NC}" || echo -e "${YELLOW}! Failed to set VITE_API_URL${NC}"

echo ""
echo -e "${YELLOW}Please enter your Supabase credentials:${NC}"
read -p "VITE_SUPABASE_URL (e.g., https://xxxxx.supabase.co): " VITE_SUPABASE_URL
read -p "VITE_SUPABASE_ANON_KEY: " VITE_SUPABASE_ANON_KEY

echo -e "${BLUE}Setting Supabase secrets...${NC}"
echo "$VITE_SUPABASE_URL" | gh secret set VITE_SUPABASE_URL --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ VITE_SUPABASE_URL set${NC}" || echo -e "${YELLOW}! Failed${NC}"
echo "$VITE_SUPABASE_ANON_KEY" | gh secret set VITE_SUPABASE_ANON_KEY --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ VITE_SUPABASE_ANON_KEY set${NC}" || echo -e "${YELLOW}! Failed${NC}"

echo ""
echo -e "${CYAN}Optional: Payment & Maps Keys${NC}"
echo "==============================="
read -p "VITE_PAYSTACK_PUBLIC_KEY (optional, press Enter to skip): " VITE_PAYSTACK_PUBLIC_KEY
read -p "VITE_GOOGLE_MAPS_API_KEY (optional, press Enter to skip): " VITE_GOOGLE_MAPS_API_KEY

if [ -n "$VITE_PAYSTACK_PUBLIC_KEY" ]; then
    echo "$VITE_PAYSTACK_PUBLIC_KEY" | gh secret set VITE_PAYSTACK_PUBLIC_KEY --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ VITE_PAYSTACK_PUBLIC_KEY set${NC}"
fi

if [ -n "$VITE_GOOGLE_MAPS_API_KEY" ]; then
    echo "$VITE_GOOGLE_MAPS_API_KEY" | gh secret set VITE_GOOGLE_MAPS_API_KEY --repo "$REPO" 2>/dev/null && echo -e "${GREEN}✓ VITE_GOOGLE_MAPS_API_KEY set${NC}"
fi

echo ""
echo -e "${CYAN}Step 4: Setting Railway Environment Variables${NC}"
echo "================================================"

cd backend

# Login to Railway
export RAILWAY_TOKEN="$RAILWAY_TOKEN"
railway whoami 2>/dev/null || railway login

echo -e "${BLUE}Setting MongoDB URL on Railway...${NC}"
railway variables set MONGODB_URL="mongodb+srv://teacherchris37_db_user:iHhashil!!!@cluster0.ai5z7wq.mongodb.net/ihhashi?retryWrites=true&w=majority"
railway variables set DB_NAME=ihhashi
echo -e "${GREEN}✓ MongoDB configured on Railway${NC}"

echo -e "${BLUE}Setting other required variables...${NC}"
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set APP_NAME=iHhashi
railway variables set APP_VERSION=0.3.0
echo -e "${GREEN}✓ Basic settings configured${NC}"

echo ""
echo -e "${YELLOW}You still need to manually set these in Railway Dashboard:${NC}"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_ANON_KEY"
echo "  - SUPABASE_SERVICE_ROLE_KEY"
echo "  - REDIS_URL (add Redis from Railway Addons)"
echo "  - SECRET_KEY (generate with: openssl rand -base64 32)"
echo ""
echo "Visit: https://railway.app/dashboard"

cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Auto-Deployment Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}What happens now:${NC}"
echo "1. When you push to 'main' or 'master' branch, GitHub Actions will:"
echo "   - Run tests on your code"
echo "   - Deploy backend to Railway"
echo "   - Deploy frontend to Netlify"
echo ""
echo -e "${CYAN}To trigger a deployment now:${NC}"
echo "  git push origin main"
echo ""
echo -e "${CYAN}To check deployment status:${NC}"
echo "  gh workflow view deploy.yml"
echo ""
