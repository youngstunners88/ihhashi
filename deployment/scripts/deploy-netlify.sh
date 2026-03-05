#!/bin/bash
# Deploy iHhashi Frontend to Netlify

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== iHhashi Netlify Deployment ===${NC}"

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo -e "${YELLOW}Installing Netlify CLI...${NC}"
    npm install -g netlify-cli
fi

cd /home/teacherchris37/frontend

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm ci
fi

# Check if .env.local exists
if [ ! -f .env.local ] && [ ! -f .env.production ]; then
    echo -e "${YELLOW}⚠️  No environment file found. Creating .env.local template...${NC}"
    cat > .env.local << 'EOF'
# Replace with your actual Railway backend URL
VITE_API_URL=https://your-railway-app.up.railway.app

# Supabase settings (replace with your actual values)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
EOF
    echo -e "${RED}❌ Please edit .env.local with your actual values before deploying${NC}"
    exit 1
fi

echo -e "${GREEN}Building frontend...${NC}"
npm run build

# Check if site is linked
if [ ! -f .netlify/state.json ]; then
    echo -e "${YELLOW}Linking to Netlify site...${NC}"
    netlify link
fi

echo -e "${GREEN}Deploying to Netlify...${NC}"
netlify deploy --prod --dir=dist

echo ""
echo -e "${GREEN}✅ Frontend deployed!${NC}"
echo -e "${GREEN}Netlify Dashboard: https://app.netlify.com${NC}"
