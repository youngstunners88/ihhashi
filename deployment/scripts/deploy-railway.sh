#!/bin/bash
# Deploy iHhashi Backend to Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== iHhashi Railway Deployment ===${NC}"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Installing Railway CLI...${NC}"
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null 2>&1; then
    echo -e "${YELLOW}Please login to Railway:${NC}"
    railway login
fi

cd /home/teacherchris37/backend

# Check if project is linked
if [ ! -f .railway/config.json ] 2>/dev/null || ! railway status &> /dev/null 2>&1; then
    echo -e "${YELLOW}Project not linked to Railway${NC}"
    echo ""
    read -p "Link to existing Railway project? (Y/n): " link_project
    if [[ ! $link_project =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}Running: railway link${NC}"
        railway link
    else
        read -p "Create new Railway project? (y/N): " create_project
        if [[ $create_project =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Creating new project...${NC}"
            railway init
        else
            echo -e "${RED}❌ Cannot deploy without a linked project${NC}"
            exit 1
        fi
    fi
fi

# Check environment variables
echo ""
echo -e "${BLUE}Checking Railway environment variables...${NC}"

# Try to get env vars from Railway
RAILWAY_ENV=$(railway variables --json 2>/dev/null || echo "{}")

if [ "$RAILWAY_ENV" = "{}" ] || [ -z "$RAILWAY_ENV" ]; then
    echo -e "${YELLOW}⚠️  No environment variables set in Railway${NC}"
    echo ""
    echo -e "${YELLOW}Required variables:${NC}"
    echo "  - MONGODB_URL (your MongoDB connection string)"
    echo "  - SECRET_KEY (generate: openssl rand -base64 32)"
    echo "  - SUPABASE_URL (from Supabase project)"
    echo "  - SUPABASE_ANON_KEY (from Supabase project)"
    echo "  - CORS_ORIGINS (your Netlify frontend URL)"
    echo ""
    echo -e "${YELLOW}Set them at: https://railway.app/dashboard${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Deploying to Railway...${NC}"
railway up

# Get the deployed URL
SERVICE_URL=$(railway domain 2>/dev/null || echo "")
if [ -n "$SERVICE_URL" ]; then
    echo ""
    echo -e "${GREEN}✅ Deployed successfully!${NC}"
    echo -e "${GREEN}URL: https://$SERVICE_URL${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Test health endpoint:"
    echo "     curl https://$SERVICE_URL/health"
    echo ""
    echo "  2. Set this URL as VITE_API_URL in your frontend:"
    echo "     export VITE_API_URL=https://$SERVICE_URL"
    echo ""
else
    echo ""
    echo -e "${YELLOW}⚠️  Deployment status unknown. Check Railway dashboard.${NC}"
fi

echo -e "${BLUE}Railway Dashboard: https://railway.app/dashboard${NC}"
