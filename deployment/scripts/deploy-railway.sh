#!/bin/bash
# Deploy iHhashi Backend to Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== iHhashi Railway Deployment ===${NC}"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Installing Railway CLI...${NC}"
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Please login to Railway:${NC}"
    railway login
fi

cd /home/teacherchris37/backend

# Check if project is linked
if [ ! -f .railway/config.json ]; then
    echo -e "${YELLOW}Linking to Railway project...${NC}"
    railway link
fi

echo -e "${GREEN}Deploying to Railway...${NC}"
railway up

# Get the deployed URL
SERVICE_URL=$(railway domain 2>/dev/null || echo "")
if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅ Deployed successfully!${NC}"
    echo -e "${GREEN}URL: https://$SERVICE_URL${NC}"
    echo ""
    echo -e "${YELLOW}Set this URL as VITE_API_URL in your frontend environment${NC}"
else
    echo -e "${YELLOW}⚠️  Deployment status unknown. Check Railway dashboard.${NC}"
fi

echo ""
echo -e "${GREEN}Railway Dashboard: https://railway.app/dashboard${NC}"
