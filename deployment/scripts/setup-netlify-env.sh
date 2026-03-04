#!/bin/bash
# Setup Netlify Environment Variables for iHhashi Frontend
# This script helps configure all necessary environment variables

set -e

echo "⚙️  Setting up Netlify Environment Variables for iHhashi Frontend"
echo "================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo -e "${RED}Netlify CLI not found. Please install it first:${NC}"
    echo "npm install -g netlify-cli"
    exit 1
fi

# Check if logged in
if ! netlify status &> /dev/null; then
    echo -e "${RED}Not logged in. Please run: netlify login${NC}"
    exit 1
fi

cd "$(dirname "$0")/../.."

echo -e "${BLUE}Setting environment variables...${NC}"

# Core Application Settings
netlify env:set VITE_APP_ENV production
netlify env:set VITE_APP_VERSION 0.3.0
netlify env:set VITE_CURRENCY_SYMBOL R
netlify env:set VITE_DEFAULT_LANGUAGE en

# Feature Flags
netlify env:set VITE_ENABLE_CHATBOT true
netlify env:set VITE_ENABLE_NOTIFICATIONS true
netlify env:set VITE_ENABLE_ANALYTICS true

echo ""
echo -e "${YELLOW}⚠️  MANUAL CONFIGURATION REQUIRED${NC}"
echo "================================"
echo "The following variables need to be set manually:"
echo ""
echo -e "${BLUE}🔌 API Configuration (REQUIRED):${NC}"
echo "  VITE_API_URL=https://your-railway-app.up.railway.app"
echo "  (Update this after deploying to Railway)"
echo ""
echo -e "${BLUE}🔐 Supabase (REQUIRED for auth):${NC}"
echo "  VITE_SUPABASE_URL=https://your-project.supabase.co"
echo "  VITE_SUPABASE_ANON_KEY=your_anon_key"
echo ""
echo -e "${BLUE}💳 Payments (Optional):${NC}"
echo "  VITE_PAYSTACK_PUBLIC_KEY=pk_test_..."
echo ""
echo -e "${BLUE}🗺️  Maps (Optional):${NC}"
echo "  VITE_GOOGLE_MAPS_API_KEY=your_api_key"
echo ""
echo -e "${BLUE}📊 Analytics (Optional):${NC}"
echo "  VITE_POSTHOG_KEY=your_key"
echo "  VITE_POSTHOG_HOST=https://app.posthog.com"
echo ""
echo -e "${BLUE}🐛 Error Tracking (Optional):${NC}"
echo "  VITE_SENTRY_DSN=your_sentry_dsn"
echo ""
echo "Set them using:"
echo "  netlify env:set VARIABLE_NAME value"
echo ""
echo "Or in the Netlify Dashboard:"
echo "  Site settings > Environment variables"
echo ""
echo -e "${GREEN}✅ Basic configuration complete!${NC}"
