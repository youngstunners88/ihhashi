#!/bin/bash
# Full deployment script for iHhashi (Backend + Frontend)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   iHhashi Full Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Parse arguments
SKIP_BACKEND=false
SKIP_FRONTEND=false
SETUP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-backend    Skip backend deployment"
            echo "  --skip-frontend   Skip frontend deployment"
            echo "  --setup-only      Only show setup instructions"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run setup if requested
if [ "$SETUP_ONLY" = true ]; then
    bash "$(dirname "$0")/setup-env.sh"
    exit 0
fi

# Deploy Backend
if [ "$SKIP_BACKEND" = false ]; then
    echo -e "${BLUE}>>> Deploying Backend to Railway...${NC}"
    bash "$(dirname "$0")/deploy-railway.sh"
    echo ""
fi

# Deploy Frontend
if [ "$SKIP_FRONTEND" = false ]; then
    echo -e "${BLUE}>>> Deploying Frontend to Netlify...${NC}"
    bash "$(dirname "$0")/deploy-netlify.sh"
    echo ""
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Test your backend health endpoint: curl https://your-railway-url.up.railway.app/health"
echo "  2. Visit your frontend URL and verify everything works"
echo "  3. Check logs if anything is not working:"
echo "     - Railway: https://railway.app/dashboard"
echo "     - Netlify: https://app.netlify.com"
echo ""
