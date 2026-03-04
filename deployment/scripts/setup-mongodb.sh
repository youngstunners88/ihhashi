#!/bin/bash
# MongoDB Atlas Configuration Script for iHhashi
# This script configures MongoDB Atlas connection for Railway

set -e

echo ""
echo "🗄️  Configuring MongoDB Atlas for iHhashi"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# MongoDB Connection String
MONGODB_URI="mongodb+srv://teacherchris37_db_user:iHhashi1!!!@cluster0.ai5z7wq.mongodb.net/ihhashi?retryWrites=true&w=majority"

echo -e "${BLUE}MongoDB Atlas Connection Details:${NC}"
echo "  Cluster: cluster0.ai5z7wq.mongodb.net"
echo "  Database: ihhashi"
echo "  Username: teacherchris37_db_user"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
fi

# Check login
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Please login to Railway:${NC}"
    railway login
fi

cd "$(dirname "$0")/../../backend"

echo -e "${CYAN}Setting MongoDB environment variables in Railway...${NC}"
echo ""

# Set the MongoDB URI in Railway
railway variables set MONGODB_URL="$MONGODB_URI"
railway variables set MONGODB_URI="$MONGODB_URI"
railway variables set DB_NAME="ihhashi"

echo -e "${GREEN}✓ MongoDB variables set in Railway${NC}"
echo ""

# Verify
echo -e "${BLUE}Current Railway environment variables:${NC}"
railway variables | grep -E "(MONGODB|DB_NAME)" || echo "  (Variables will be visible after deployment)"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ MongoDB Atlas configuration complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Deploy to Railway: railway up"
echo "  2. Verify connection: railway logs"
echo "  3. Test API: curl https://your-app.up.railway.app/health"
echo ""
echo -e "${YELLOW}Note: Make sure your MongoDB Atlas cluster allows connections from Railway.${NC}"
echo "  Go to MongoDB Atlas → Network Access → Add IP Address → Allow from anywhere (0.0.0.0/0)"
echo "  OR add Railway's specific IP ranges"
echo ""
