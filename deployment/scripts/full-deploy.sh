#!/bin/bash
# Full Deployment Script for iHhashi
# This script automates the deployment to both Railway and Netlify
# Usage: ./full-deploy.sh [environment]
# Environment: development (default) | staging | production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# API Tokens (from user input)
RAILWAY_API_TOKEN="${RAILWAY_TOKEN:-91e3ad14-e35d-490d-9fa0-361ecc59822f}"
NETLIFY_AUTH_TOKEN="${NETLIFY_TOKEN:-nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b}"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║     🚀 iHhashi Full Deployment                            ║${NC}"
echo -e "${CYAN}║     Environment: ${YELLOW}$ENVIRONMENT${CYAN}                               ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# Helper Functions
# ============================================

print_step() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "─────────────────────────────────────────────"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ============================================
# Pre-flight Checks
# ============================================

print_step "Pre-flight Checks"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
NODE_VERSION=$(node -v)
print_success "Node.js version: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm version: $(npm -v)"

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed"
    exit 1
fi
print_success "Git available"

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi
print_success "Railway CLI available"

# Check Netlify CLI
if ! command -v netlify &> /dev/null; then
    print_warning "Netlify CLI not found. Installing..."
    npm install -g netlify-cli
fi
print_success "Netlify CLI available"

# ============================================
# Setup API Tokens
# ============================================

print_step "Configuring API Tokens"

export RAILWAY_API_TOKEN="$RAILWAY_API_TOKEN"
export NETLIFY_AUTH_TOKEN="$NETLIFY_AUTH_TOKEN"

print_success "Railway API token configured"
print_success "Netlify auth token configured"

# ============================================
# Backend Deployment (Railway)
# ============================================

print_step "Deploying Backend to Railway"

cd "$PROJECT_ROOT/backend"

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    print_warning "Logging in to Railway..."
    railway login --token "$RAILWAY_API_TOKEN" 2>/dev/null || true
fi

# Check if project is linked
if [ ! -f "$PROJECT_ROOT/.railway/config.json" ]; then
    print_warning "Railway project not linked"
    echo "Please link your Railway project manually:"
    echo "  cd backend && railway link"
    read -p "Press Enter when ready..."
fi

# Set basic environment variables
print_step "Setting Railway Environment Variables"

railway variables set ENVIRONMENT="$ENVIRONMENT" 2>/dev/null || true
railway variables set DEBUG="false" 2>/dev/null || true
railway variables set PYTHON_VERSION="3.11" 2>/dev/null || true

# Generate secret key if not exists
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
railway variables set SECRET_KEY="$SECRET_KEY" 2>/dev/null || true

# South Africa settings
railway variables set DEFAULT_CURRENCY="ZAR" 2>/dev/null || true
railway variables set VAT_RATE="0.15" 2>/dev/null || true
railway variables set DEFAULT_TIMEZONE="Africa/Johannesburg" 2>/dev/null || true

print_success "Basic environment variables set"

# Deploy backend
print_step "Building and Deploying Backend"

railway up --detach 2>/dev/null || railway up

print_success "Backend deployment initiated"

# Get backend URL
print_step "Getting Backend URL"

BACKEND_URL=$(railway domain 2>/dev/null || echo "")
if [ -z "$BACKEND_URL" ]; then
    # Try to get from status
    BACKEND_URL=$(railway status 2>/dev/null | grep -oP 'https://[^\s]+\.up\.railway\.app' || echo "")
fi

if [ -n "$BACKEND_URL" ]; then
    print_success "Backend URL: $BACKEND_URL"
else
    print_warning "Could not determine backend URL. You may need to check Railway Dashboard."
    BACKEND_URL="https://ihhashi-api.up.railway.app"
fi

# Wait a moment for deployment
sleep 5

# Check health
print_step "Checking Backend Health"

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" == "200" ]; then
    print_success "Backend is healthy!"
else
    print_warning "Backend health check returned: $HEALTH_STATUS"
    print_warning "The backend may still be starting up. Check Railway logs for details."
fi

# ============================================
# Frontend Deployment (Netlify)
# ============================================

print_step "Deploying Frontend to Netlify"

cd "$PROJECT_ROOT/frontend"

# Check if logged in to Netlify
if ! netlify status &> /dev/null; then
    print_warning "Logging in to Netlify..."
    export NETLIFY_AUTH_TOKEN="$NETLIFY_AUTH_TOKEN"
fi

# Install dependencies
print_step "Installing Frontend Dependencies"
npm ci
print_success "Dependencies installed"

# Set environment variables for build
print_step "Setting Frontend Environment Variables"

netlify env:set VITE_API_URL "$BACKEND_URL" 2>/dev/null || true
netlify env:set VITE_APP_ENV "$ENVIRONMENT" 2>/dev/null || true
netlify env:set VITE_APP_VERSION "0.3.0" 2>/dev/null || true
netlify env:set VITE_ENABLE_CHATBOT "true" 2>/dev/null || true
netlify env:set VITE_ENABLE_NOTIFICATIONS "true" 2>/dev/null || true
netlify env:set VITE_ENABLE_ANALYTICS "true" 2>/dev/null || true
netlify env:set VITE_CURRENCY_SYMBOL "R" 2>/dev/null || true
netlify env:set VITE_DEFAULT_LANGUAGE "en" 2>/dev/null || true

print_success "Frontend environment variables set"

# Build the project
print_step "Building Frontend"
npm run build
print_success "Frontend build complete"

# Deploy to Netlify
print_step "Deploying to Netlify"

# Check if site is linked
if [ ! -f "$PROJECT_ROOT/.netlify/state.json" ]; then
    print_warning "Netlify site not linked"
    echo "Would you like to create a new site or link an existing one?"
    select choice in "Create new site" "Link existing site" "Skip"; do
        case $choice in
            "Create new site")
                netlify init
                break
                ;;
            "Link existing site")
                netlify link
                break
                ;;
            "Skip")
                print_warning "Skipping Netlify deployment"
                break
                ;;
        esac
    done
fi

# Deploy
netlify deploy --prod --dir=dist --message "Deploy from script - $ENVIRONMENT"

print_success "Frontend deployed to Netlify"

# Get frontend URL
FRONTEND_URL=$(netlify status 2>/dev/null | grep "Website URL" | awk '{print $NF}' || echo "")

if [ -n "$FRONTEND_URL" ]; then
    print_success "Frontend URL: $FRONTEND_URL"
else
    print_warning "Could not determine frontend URL. Check Netlify Dashboard."
fi

# ============================================
# Post-Deployment Summary
# ============================================

print_step "Deployment Summary"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                   DEPLOYMENT COMPLETE                       ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Backend (Railway):${NC}"
echo "  URL: $BACKEND_URL"
echo "  Health: $BACKEND_URL/health"
echo ""
echo -e "${GREEN}Frontend (Netlify):${NC}"
echo "  URL: ${FRONTEND_URL:-"Check Netlify Dashboard"}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Set up Supabase authentication variables"
echo "  2. Configure payment gateway (Paystack/Yoco)"
echo "  3. Add MongoDB and Redis from Railway Addons"
echo "  4. Update CORS_ORIGINS in Railway with frontend URL"
echo "  5. Test the application"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Railway logs:    railway logs"
echo "  Netlify logs:    netlify logs"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# ============================================
# Environment Variables Checklist
# ============================================

echo ""
print_step "Required Environment Variables Checklist"

echo ""
echo -e "${YELLOW}Backend (Railway) - REQUIRED:${NC}"
echo "  [ ] MONGODB_URL - Add MongoDB from Railway Addons"
echo "  [ ] REDIS_URL - Add Redis from Railway Addons"
echo "  [ ] SUPABASE_URL - From Supabase project settings"
echo "  [ ] SUPABASE_ANON_KEY - From Supabase project settings"
echo "  [ ] CORS_ORIGINS - Should include: $FRONTEND_URL"
echo ""
echo -e "${YELLOW}Backend (Railway) - Optional:${NC}"
echo "  [ ] PAYSTACK_SECRET_KEY - For payments"
echo "  [ ] PAYSTACK_WEBHOOK_SECRET - For payment webhooks"
echo "  [ ] GOOGLE_MAPS_API_KEY - For maps"
echo "  [ ] FIREBASE_* - For push notifications"
echo "  [ ] GLITCHTIP_DSN - For error tracking"
echo "  [ ] POSTHOG_API_KEY - For analytics"
echo ""
echo -e "${YELLOW}Frontend (Netlify) - REQUIRED:${NC}"
echo "  [ ] VITE_SUPABASE_URL - From Supabase project settings"
echo "  [ ] VITE_SUPABASE_ANON_KEY - From Supabase project settings"
echo ""
echo -e "${YELLOW}Frontend (Netlify) - Optional:${NC}"
echo "  [ ] VITE_PAYSTACK_PUBLIC_KEY - For payments"
echo "  [ ] VITE_GOOGLE_MAPS_API_KEY - For maps"
echo "  [ ] VITE_POSTHOG_KEY - For analytics"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
