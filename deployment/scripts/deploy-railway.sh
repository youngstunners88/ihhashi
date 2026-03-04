#!/bin/bash
# Railway Deployment Script for iHhashi Backend
# This script helps deploy the backend to Railway

set -e

echo "🚀 iHhashi Backend Deployment to Railway"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
fi

# Check if user is logged in
echo -e "${YELLOW}Checking Railway login status...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${RED}Not logged in to Railway. Please login:${NC}"
    railway login
fi

# Navigate to backend directory
cd "$(dirname "$0")/../../backend"

# Check if project is linked
if [ ! -f ../.railway/config.json ]; then
    echo -e "${YELLOW}No Railway project linked. Initializing...${NC}"
    railway init
fi

# Set up environment variables if not already set
echo -e "${YELLOW}Checking environment variables...${NC}"

# Required variables for production
REQUIRED_VARS=(
    "SECRET_KEY"
    "MONGODB_URL"
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "ENVIRONMENT"
)

echo -e "${YELLOW}Please ensure these environment variables are set in Railway Dashboard:${NC}"
for var in "${REQUIRED_VARS[@]}"; do
    echo "  - $var"
done

echo ""
echo -e "${GREEN}Current environment variables:${NC}"
railway variables

echo ""
read -p "Do you want to deploy now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Deploying to Railway...${NC}"
    railway up
    
    echo ""
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo ""
    echo "Your API should be available at:"
    railway status
else
    echo -e "${YELLOW}Deployment cancelled.${NC}"
fi
