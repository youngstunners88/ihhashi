#!/bin/bash
# Complete iHhashi Deployment Script
# Run this after: railway login && netlify login

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   iHhashi Auto-Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check logins
echo -e "${BLUE}Checking authentication...${NC}"
if ! railway whoami &>/dev/null; then
    echo -e "${RED}❌ Not logged into Railway${NC}"
    echo "   Run: railway login"
    exit 1
fi
echo -e "${GREEN}✓ Railway authenticated${NC}"

if ! netlify whoami &>/dev/null; then
    echo -e "${RED}❌ Not logged into Netlify${NC}"
    echo "   Run: netlify login"
    exit 1
fi
echo -e "${GREEN}✓ Netlify authenticated${NC}"
echo ""

# ===============================
# BACKEND DEPLOYMENT
# ===============================
echo -e "${BLUE}>>> Deploying Backend to Railway...${NC}"
cd /home/teacherchris37/backend

# Check if linked to project
if [ ! -f .railway/config.json ] 2>/dev/null; then
    echo -e "${YELLOW}Linking to Railway project...${NC}"
    railway link
fi

# Deploy
echo -e "${YELLOW}Deploying...${NC}"
railway up

# Get domain
RAILWAY_URL=$(railway domain 2>/dev/null || echo "")
if [ -z "$RAILWAY_URL" ]; then
    echo -e "${RED}❌ Could not get Railway domain${NC}"
    echo "   Check dashboard: https://railway.app/dashboard"
    exit 1
fi

echo -e "${GREEN}✓ Backend deployed: https://$RAILWAY_URL${NC}"
echo ""

# ===============================
# FRONTEND DEPLOYMENT  
# ===============================
echo -e "${BLUE}>>> Deploying Frontend to Netlify...${NC}"
cd /home/teacherchris37/frontend

# Create env file with Railway URL
echo -e "${YELLOW}Creating .env.local with API URL...${NC}"
cat > .env.local << EOF
VITE_API_URL=https://$RAILWAY_URL
VITE_APP_ENV=production
EOF

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ ! -d node_modules ]; then
    npm ci --legacy-peer-deps
fi

# Build
echo -e "${YELLOW}Building frontend...${NC}"
rm -rf dist
npm run build

# Check if linked to site
if [ ! -f .netlify/state.json ] 2>/dev/null; then
    echo -e "${YELLOW}Linking to Netlify site...${NC}"
    netlify link
fi

# Deploy
echo -e "${YELLOW}Deploying to Netlify...${NC}"
DEPLOY_OUTPUT=$(netlify deploy --prod --dir=dist 2>&1)
echo "$DEPLOY_OUTPUT"

# Extract URL
NETLIFY_URL=$(echo "$DEPLOY_OUTPUT" | grep -oE 'https://[a-zA-Z0-9-]+\.netlify\.app' | head -1)

if [ -n "$NETLIFY_URL" ]; then
    echo ""
    echo -e "${GREEN}✓ Frontend deployed: $NETLIFY_URL${NC}"
else
    NETLIFY_URL="[Check Netlify dashboard]"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your URLs:${NC}"
echo -e "  Backend:  https://$RAILWAY_URL"
echo -e "  Frontend: $NETLIFY_URL"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Update CORS_ORIGINS in Railway!${NC}"
echo "   Go to: https://railway.app/dashboard"
echo "   Add CORS_ORIGINS=$NETLIFY_URL"
echo "   Then run: cd backend && railway up"
echo ""
echo -e "${BLUE}Test your deployment:${NC}"
echo "   curl https://$RAILWAY_URL/health"
echo ""
