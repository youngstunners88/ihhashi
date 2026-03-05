#!/bin/bash
# Complete iHhashi Deployment Script
# Usage: ./DEPLOY_NOW.sh (after: railway login && netlify login)

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

read -p "Press Enter to start deployment..."
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
echo -e "${YELLOW}Deploying backend...${NC}"
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
echo -e "${YELLOW}Setting up frontend environment...${NC}"
cat > .env.local << EOF
VITE_API_URL=https://$RAILWAY_URL
VITE_APP_ENV=production
EOF

echo -e "${GREEN}✓ Created .env.local with API URL${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies (this may take a minute)...${NC}"
if [ ! -d node_modules ]; then
    npm ci --legacy-peer-deps 2>&1 | grep -v "npm warn" || true
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Build
echo -e "${YELLOW}Building frontend...${NC}"
rm -rf dist
npm run build 2>&1 | tail -20

if [ ! -d dist ]; then
    echo -e "${RED}❌ Build failed - dist folder not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build successful${NC}"

# Check if linked to site
if [ ! -f .netlify/state.json ] 2>/dev/null; then
    echo -e "${YELLOW}Linking to Netlify site...${NC}"
    netlify link
fi

# Deploy
echo -e "${YELLOW}Deploying to Netlify...${NC}"
netlify deploy --prod --dir=dist

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Your URLs:${NC}"
echo -e "  🚀 Backend:  https://$RAILWAY_URL"
echo ""
echo -e "  🌐 Frontend: $(netlify status --json 2>/dev/null | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || echo '[Check Netlify dashboard]')"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEP:${NC}"
echo "   Update CORS_ORIGINS in Railway with your Netlify URL!"
echo ""
echo "   1. Go to: https://railway.app/dashboard"
echo "   2. Select your project"
echo "   3. Go to Variables tab"
echo "   4. Add: CORS_ORIGINS=https://YOUR-NETLIFY-URL.netlify.app"
echo "   5. Redeploy: cd backend && railway up"
echo ""
echo -e "${BLUE}Test your deployment:${NC}"
echo "   curl https://$RAILWAY_URL/health"
echo ""
