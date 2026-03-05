#!/bin/bash
# Deploy iHhashi Frontend to Netlify

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== iHhashi Netlify Deployment ===${NC}"

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo -e "${YELLOW}⚠️  Warning: Node.js v22+ recommended for Capacitor${NC}"
    echo -e "${YELLOW}   Current version: $(node -v)${NC}"
    echo -e "${YELLOW}   Continuing anyway...${NC}"
    echo ""
fi

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo -e "${YELLOW}Installing Netlify CLI...${NC}"
    npm install -g netlify-cli
fi

cd /home/teacherchris37/frontend

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm ci --legacy-peer-deps || npm install --legacy-peer-deps
fi

# Check for required environment variables
check_env_var() {
    local var_name=$1
    local var_value=$(printenv "$var_name" 2>/dev/null || echo "")
    
    # Also check .env.local if it exists
    if [ -z "$var_value" ] && [ -f .env.local ]; then
        var_value=$(grep "^$var_name=" .env.local 2>/dev/null | cut -d'=' -f2- | sed 's/["'\''']//g' || echo "")
    fi
    
    # Also check .env.production if it exists
    if [ -z "$var_value" ] && [ -f .env.production ]; then
        var_value=$(grep "^$var_name=" .env.production 2>/dev/null | cut -d'=' -f2- | sed 's/["'\''']//g' || echo "")
    fi
    
    echo "$var_value"
}

VITE_API_URL=$(check_env_var "VITE_API_URL")
VITE_SUPABASE_URL=$(check_env_var "VITE_SUPABASE_URL")
VITE_SUPABASE_ANON_KEY=$(check_env_var "VITE_SUPABASE_ANON_KEY")

echo -e "${BLUE}Checking environment variables...${NC}"

MISSING_VARS=""

if [ -z "$VITE_API_URL" ] || [ "$VITE_API_URL" = "https://your-railway-app.up.railway.app" ]; then
    MISSING_VARS="$MISSING_VARS VITE_API_URL"
    echo -e "${RED}  ❌ VITE_API_URL not set${NC}"
else
    echo -e "${GREEN}  ✓ VITE_API_URL${NC}"
fi

if [ -z "$VITE_SUPABASE_URL" ]; then
    echo -e "${YELLOW}  ⚠️  VITE_SUPABASE_URL not set (optional for now)${NC}"
else
    echo -e "${GREEN}  ✓ VITE_SUPABASE_URL${NC}"
fi

if [ -z "$VITE_SUPABASE_ANON_KEY" ]; then
    echo -e "${YELLOW}  ⚠️  VITE_SUPABASE_ANON_KEY not set (optional for now)${NC}"
else
    echo -e "${GREEN}  ✓ VITE_SUPABASE_ANON_KEY${NC}"
fi

# If missing critical vars, create .env.local template
if [ -n "$MISSING_VARS" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Missing required environment variables:${NC}$MISSING_VARS"
    echo ""
    
    # Check if we should create template or use defaults for testing
    if [ ! -f .env.local ]; then
        echo -e "${YELLOW}Creating .env.local template...${NC}"
        cat > .env.local << 'EOF'
# Replace with your actual Railway backend URL
VITE_API_URL=https://your-railway-app.up.railway.app

# Supabase settings (replace with your actual values)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
EOF
        echo -e "${YELLOW}Template created at frontend/.env.local${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  1. Edit frontend/.env.local with your actual values"
    echo "  2. Set environment variables in Netlify Dashboard"
    echo "  3. Use defaults for testing (NOT RECOMMENDED for production)"
    echo ""
    
    read -p "Use placeholder values for testing? (y/N): " use_defaults
    if [[ $use_defaults =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Using placeholder values...${NC}"
        export VITE_API_URL="https://ihhashi-api.up.railway.app"
        export VITE_SUPABASE_URL=""
        export VITE_SUPABASE_ANON_KEY=""
    else
        echo -e "${RED}❌ Please set the required environment variables and try again${NC}"
        echo ""
        echo -e "${YELLOW}To set in Netlify Dashboard:${NC}"
        echo "  1. Go to https://app.netlify.com"
        echo "  2. Select your site"
        echo "  3. Go to Site Settings > Environment Variables"
        echo "  4. Add VITE_API_URL (your Railway backend URL)"
        echo ""
        exit 1
    fi
else
    # Export for build
    export VITE_API_URL
    export VITE_SUPABASE_URL
    export VITE_SUPABASE_ANON_KEY
fi

echo ""
echo -e "${GREEN}Building frontend...${NC}"
rm -rf dist
npm run build

if [ ! -d dist ]; then
    echo -e "${RED}❌ Build failed - dist directory not created${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build successful${NC}"
echo ""

# Check if site is linked
if [ ! -f .netlify/state.json ]; then
    echo -e "${YELLOW}Site not linked to Netlify${NC}"
    echo ""
    read -p "Link to existing Netlify site? (Y/n): " link_site
    if [[ ! $link_site =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}Running: netlify link${NC}"
        netlify link
    else
        read -p "Create new Netlify site? (y/N): " create_site
        if [[ $create_site =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Running: netlify sites:create${NC}"
            netlify sites:create
            netlify link
        else
            echo -e "${RED}❌ Cannot deploy without a linked site${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}Deploying to Netlify...${NC}"
netlify deploy --prod --dir=dist

echo ""
echo -e "${GREEN}✅ Frontend deployed!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Set environment variables in Netlify Dashboard if not already set"
echo "  2. Update CORS_ORIGINS in Railway with your Netlify URL"
echo "  3. Test your deployed app"
echo ""
echo -e "${BLUE}Dashboards:${NC}"
echo "  Netlify: https://app.netlify.com"
echo "  Railway: https://railway.app/dashboard"
