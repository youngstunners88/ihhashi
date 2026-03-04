#!/bin/bash
# Setup Railway Environment Variables for iHhashi
# This script helps configure all necessary environment variables

set -e

echo "⚙️  Setting up Railway Environment Variables for iHhashi"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found. Please install it first:${NC}"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo -e "${RED}Not logged in. Please run: railway login${NC}"
    exit 1
fi

# Navigate to backend
cd "$(dirname "$0")/../../backend"

echo -e "${BLUE}Setting environment variables...${NC}"

# Core Application Settings
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set APP_NAME=iHhashi
railway variables set APP_VERSION=0.3.0

# Generate and set secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set SECRET_KEY="$SECRET_KEY"
echo -e "${GREEN}✓ Generated SECRET_KEY${NC}"

# JWT Configuration
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
railway variables set RATE_LIMIT_REQUESTS=100
railway variables set RATE_LIMIT_PERIOD=60
railway variables set AUTH_RATE_LIMIT=5/minute

# South Africa Settings
railway variables set DEFAULT_CURRENCY=ZAR
railway variables set VAT_RATE=0.15
railway variables set DEFAULT_TIMEZONE=Africa/Johannesburg
railway variables set SUPPORTED_LANGUAGES='["en","zu","st","af","tn","xh"]'

# Free Trial
railway variables set FREE_TRIAL_DAYS=45
railway variables set FREE_TRIAL_PLATFORM_FEE_PERCENT=0.0
railway variables set STANDARD_PLATFORM_FEE_PERCENT=15.0
railway variables set TIP_PLATFORM_FEE_PERCENT=0.0

# Payout Configuration
railway variables set PAYOUT_DAY_OF_WEEK=6
railway variables set PAYOUT_HOUR=11
railway variables set PAYOUT_MINUTE=11
railway variables set MINIMUM_PAYOUT_AMOUNT=100

# File Upload
railway variables set MAX_FILE_SIZE_MB=5
railway variables set ALLOWED_IMAGE_TYPES='["image/jpeg","image/png","image/webp"]'

# Delivery
railway variables set MAX_DELIVERY_RADIUS_KM=15
railway variables set ESTIMATED_DELIVERY_TIME_MINUTES=45

# MongoDB Atlas (Configured)
railway variables set MONGODB_URL="mongodb+srv://teacherchris37_db_user:iHhashil!!!@cluster0.ai5z7wq.mongodb.net/ihhashi?retryWrites=true&w=majority"
railway variables set DB_NAME=ihhashi
echo -e "${GREEN}✓ Configured MongoDB Atlas connection${NC}"

echo ""
echo -e "${YELLOW}⚠️  MANUAL CONFIGURATION REQUIRED${NC}"
echo "================================"
echo "The following variables need to be set manually in Railway Dashboard:"
echo ""
echo -e "${BLUE}🔐 Authentication (REQUIRED):${NC}"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_ANON_KEY"
echo "  - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo -e "${BLUE}🗄️  Database (REQUIRED):${NC}"
echo "  - MONGODB_URL (MongoDB Atlas - already configured)"
echo "  - REDIS_URL (Add Redis from Railway Addons)"
echo ""
echo -e "${BLUE}💳 Payments (REQUIRED for payments):${NC}"
echo "  - PAYSTACK_SECRET_KEY"
echo "  - PAYSTACK_PUBLIC_KEY"
echo "  - PAYSTACK_WEBHOOK_SECRET"
echo "  - YOCO_SECRET_KEY (alternative)"
echo ""
echo -e "${BLUE}🗺️  Maps & Location:${NC}"
echo "  - GOOGLE_MAPS_API_KEY"
echo ""
echo -e "${BLUE}🔔 Push Notifications:${NC}"
echo "  - FIREBASE_PROJECT_ID"
echo "  - FIREBASE_PRIVATE_KEY"
echo "  - FIREBASE_CLIENT_EMAIL"
echo ""
echo -e "${BLUE}📱 SMS:${NC}"
echo "  - TWILIO_ACCOUNT_SID"
echo "  - TWILIO_AUTH_TOKEN"
echo "  - TWILIO_PHONE_NUMBER"
echo ""
echo -e "${BLUE}📊 Analytics & Monitoring:${NC}"
echo "  - GLITCHTIP_DSN"
echo "  - POSTHOG_API_KEY"
echo ""
echo -e "${BLUE}🤖 Telegram:${NC}"
echo "  - TELEGRAM_BOT_TOKEN"
echo ""
echo "Set them at: https://railway.app/dashboard"
echo ""
echo -e "${GREEN}✅ Basic configuration complete!${NC}"
