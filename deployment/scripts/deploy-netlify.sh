#!/bin/bash
# Netlify Deployment Script for iHhashi Frontend
# This script helps deploy the frontend to Netlify

set -e

echo "🚀 iHhashi Frontend Deployment to Netlify"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo -e "${YELLOW}Netlify CLI not found. Installing...${NC}"
    npm install -g netlify-cli
fi

# Check if user is logged in
echo -e "${YELLOW}Checking Netlify login status...${NC}"
if ! netlify status &> /dev/null; then
    echo -e "${RED}Not logged in to Netlify. Please login:${NC}"
    netlify login
fi

# Navigate to frontend directory
cd "$(dirname "$0")/../../frontend"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm ci

# Build the project
echo -e "${YELLOW}Building project...${NC}"
npm run build

# Check if site is linked
if [ ! -f ../.netlify/state.json ]; then
    echo -e "${YELLOW}No Netlify site linked. Initializing...${NC}"
    netlify init
fi

# Deploy
echo -e "${GREEN}Deploying to Netlify...${NC}"
netlify deploy --prod --dir=dist

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Your site should be available at:"
netlify status
