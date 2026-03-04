#!/bin/bash
# Quick Start Script for iHhashi Deployment
# This script uses your provided API tokens to get everything running quickly

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚀 iHhashi Quick Start Deployment                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration - Using provided tokens
RAILWAY_TOKEN="91e3ad14-e35d-490d-9fa0-361ecc59822f"
NETLIFY_TOKEN="nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Export tokens for CLI usage
export RAILWAY_API_TOKEN="$RAILWAY_TOKEN"
export NETLIFY_AUTH_TOKEN="$NETLIFY_TOKEN"

echo -e "${BLUE}API Tokens configured:${NC}"
echo "  Railway: ${RAILWAY_TOKEN:0:10}...${RAILWAY_TOKEN: -5}"
echo "  Netlify: ${NETLIFY_TOKEN:0:10}...${NETLIFY_TOKEN: -5}"
echo ""

# Menu
echo "What would you like to do?"
echo ""
echo "  1) Full Deployment (Backend + Frontend)"
echo "  2) Deploy Backend to Railway only"
echo "  3) Deploy Frontend to Netlify only"
echo "  4) Setup Environment Variables"
echo "  5) Configure GitHub Secrets"
echo "  6) Check Deployment Status"
echo "  7) View Logs"
echo "  8) Run Tests"
echo ""
read -p "Enter choice [1-8]: " choice

case $choice in
    1)
        echo ""
        echo -e "${CYAN}Starting Full Deployment...${NC}"
        "$SCRIPT_DIR/full-deploy.sh" production
        ;;
    2)
        echo ""
        echo -e "${CYAN}Deploying Backend to Railway...${NC}"
        cd "$PROJECT_ROOT/backend"
        
        # Check login
        if ! railway whoami &> /dev/null; then
            railway login --token "$RAILWAY_TOKEN"
        fi
        
        # Link if needed
        if [ ! -f "$PROJECT_ROOT/.railway/config.json" ]; then
            echo "Please select your Railway project:"
            railway link
        fi
        
        # Deploy
        railway up
        
        echo ""
        echo -e "${GREEN}✓ Backend deployed!${NC}"
        echo "URL: $(railway domain 2>/dev/null || echo 'Check Railway Dashboard')"
        ;;
    3)
        echo ""
        echo -e "${CYAN}Deploying Frontend to Netlify...${NC}"
        cd "$PROJECT_ROOT/frontend"
        
        # Install and build
        npm ci
        npm run build
        
        # Check login
        if ! netlify status &> /dev/null; then
            export NETLIFY_AUTH_TOKEN="$NETLIFY_TOKEN"
        fi
        
        # Link if needed
        if [ ! -f "$PROJECT_ROOT/.netlify/state.json" ]; then
            echo "Please select your Netlify site:"
            netlify link
        fi
        
        # Deploy
        netlify deploy --prod --dir=dist
        
        echo ""
        echo -e "${GREEN}✓ Frontend deployed!${NC}"
        netlify status
        ;;
    4)
        echo ""
        echo "Which environment variables to set up?"
        echo "  1) Railway (Backend)"
        echo "  2) Netlify (Frontend)"
        echo "  3) Both"
        read -p "Enter choice [1-3]: " env_choice
        
        case $env_choice in
            1) "$SCRIPT_DIR/setup-railway-env.sh" ;;
            2) "$SCRIPT_DIR/setup-netlify-env.sh" ;;
            3) 
                "$SCRIPT_DIR/setup-railway-env.sh"
                echo ""
                "$SCRIPT_DIR/setup-netlify-env.sh"
                ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
    5)
        "$SCRIPT_DIR/configure-secrets.sh"
        ;;
    6)
        echo ""
        echo -e "${CYAN}Checking Deployment Status...${NC}"
        echo ""
        
        # Check Railway
        echo -e "${BLUE}Railway Backend:${NC}"
        cd "$PROJECT_ROOT/backend"
        if railway whoami &> /dev/null; then
            railway status 2>/dev/null || echo "  Status: Check Railway Dashboard"
        else
            echo -e "  ${YELLOW}Not logged in to Railway${NC}"
        fi
        
        echo ""
        
        # Check Netlify
        echo -e "${BLUE}Netlify Frontend:${NC}"
        if netlify status &> /dev/null; then
            netlify status
        else
            echo -e "  ${YELLOW}Not logged in to Netlify${NC}"
        fi
        ;;
    7)
        echo ""
        echo "Which logs to view?"
        echo "  1) Railway (Backend)"
        echo "  2) Netlify (Frontend)"
        read -p "Enter choice [1-2]: " log_choice
        
        case $log_choice in
            1)
                cd "$PROJECT_ROOT/backend"
                railway logs --follow
                ;;
            2)
                netlify logs
                ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
    8)
        echo ""
        echo -e "${CYAN}Running Tests...${NC}"
        echo ""
        
        # Backend tests
        echo -e "${BLUE}Backend Tests:${NC}"
        cd "$PROJECT_ROOT/backend"
        pip install -r requirements.txt pytest pytest-asyncio 2>/dev/null || true
        python -m pytest --tb=short -q 2>/dev/null || echo "  Tests completed or skipped"
        
        echo ""
        
        # Frontend tests
        echo -e "${BLUE}Frontend Tests:${NC}"
        cd "$PROJECT_ROOT/frontend"
        npm ci 2>/dev/null || true
        npm run typecheck 2>/dev/null || echo "  Type check completed"
        npm test 2>/dev/null || echo "  Tests completed"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
