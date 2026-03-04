#!/bin/bash
# Configure GitHub Secrets for CI/CD Deployment
# This script sets up the necessary secrets for GitHub Actions

set -e

echo "🔐 Configuring GitHub Secrets for iHhashi CI/CD"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# API Tokens from environment or user input
RAILWAY_TOKEN="${RAILWAY_TOKEN:-91e3ad14-e35d-490d-9fa0-361ecc59822f}"
NETLIFY_TOKEN="${NETLIFY_TOKEN:-nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b}"

echo ""
echo -e "${BLUE}This script will help you configure GitHub Secrets for automated deployments.${NC}"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI not found. Please install it first:${NC}"
    echo "  https://cli.github.com/"
    echo ""
    echo "Alternatively, you can manually add these secrets in GitHub:"
    echo "  Settings > Secrets and variables > Actions > New repository secret"
    echo ""
fi

# Check if logged in to GitHub
if command -v gh &> /dev/null && ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Please login to GitHub first:${NC}"
    gh auth login
fi

echo -e "${CYAN}Required Secrets:${NC}"
echo ""

# Function to set secret
set_secret() {
    local name=$1
    local value=$2
    
    if command -v gh &> /dev/null; then
        echo "$value" | gh secret set "$name" 2>/dev/null && echo -e "${GREEN}✓ $name set${NC}" || echo -e "${YELLOW}! Failed to set $name${NC}"
    else
        echo -e "${YELLOW}  - $name: $value${NC}"
    fi
}

echo "Setting deployment secrets..."
set_secret "RAILWAY_TOKEN" "$RAILWAY_TOKEN"
set_secret "NETLIFY_AUTH_TOKEN" "$NETLIFY_TOKEN"

echo ""
echo -e "${YELLOW}⚠️  The following secrets need to be set manually:${NC}"
echo ""

# Get Netlify Site ID
echo -e "${BLUE}Getting Netlify Site ID...${NC}"
if command -v netlify &> /dev/null; then
    NETLIFY_SITE_ID=$(netlify status --json 2>/dev/null | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    if [ -n "$NETLIFY_SITE_ID" ]; then
        set_secret "NETLIFY_SITE_ID" "$NETLIFY_SITE_ID"
    else
        echo -e "${YELLOW}  - NETLIFY_SITE_ID: Get from 'netlify status' or Netlify Dashboard${NC}"
    fi
else
    echo -e "${YELLOW}  - NETLIFY_SITE_ID: Get from Netlify Dashboard > Site settings > General${NC}"
fi

echo ""
echo -e "${CYAN}Manual Configuration Required:${NC}"
echo ""
echo "Add these secrets to GitHub (Settings > Secrets and variables > Actions):"
echo ""
echo -e "${BLUE}Required for Frontend:${NC}"
echo "  VITE_API_URL              - Your Railway backend URL (e.g., https://ihhashi-api.up.railway.app)"
echo "  VITE_SUPABASE_URL         - From Supabase project settings"
echo "  VITE_SUPABASE_ANON_KEY    - From Supabase project settings"
echo ""
echo -e "${BLUE}Optional for Payments:${NC}"
echo "  VITE_PAYSTACK_PUBLIC_KEY  - Paystack public key (pk_test_ or pk_live_)"
echo ""
echo -e "${BLUE}Optional for Maps:${NC}"
echo "  VITE_GOOGLE_MAPS_API_KEY  - Google Maps API key"
echo ""
echo -e "${BLUE}Optional for Analytics:${NC}"
echo "  VITE_POSTHOG_KEY          - PostHog API key"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Once secrets are configured, deployments will happen automatically"
echo "when you push to the main or master branch."
echo ""

# Create a secrets template file
cat > deployment/GITHUB_SECRETS.md << 'EOF'
# GitHub Secrets Configuration

This document lists all the secrets required for GitHub Actions CI/CD.

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret name and value

## Required Secrets

### Deployment

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `RAILWAY_TOKEN` | Railway API token | Railway Dashboard > Tokens |
| `NETLIFY_AUTH_TOKEN` | Netlify personal access token | Netlify Dashboard > User settings > Applications |
| `NETLIFY_SITE_ID` | Netlify site ID | `netlify status` or Site settings |

### Frontend Configuration

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `VITE_API_URL` | Backend API URL | After Railway deploy: `railway domain` |
| `VITE_SUPABASE_URL` | Supabase project URL | Supabase Dashboard > Settings > API > URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon/public key | Supabase Dashboard > Settings > API > anon public |

### Optional Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `VITE_PAYSTACK_PUBLIC_KEY` | Paystack public key | Paystack Dashboard > Settings > API Keys |
| `VITE_GOOGLE_MAPS_API_KEY` | Google Maps API key | Google Cloud Console > APIs & Services > Credentials |
| `VITE_POSTHOG_KEY` | PostHog project API key | PostHog Dashboard > Project settings > General |

## Backend Environment Variables (Railway)

These should be configured in Railway Dashboard, not GitHub:

### Required
- `MONGODB_URL` - Add MongoDB from Railway Addons
- `REDIS_URL` - Add Redis from Railway Addons  
- `SUPABASE_URL` - From Supabase Dashboard
- `SUPABASE_ANON_KEY` - From Supabase Dashboard
- `SUPABASE_SERVICE_ROLE_KEY` - From Supabase Dashboard
- `SECRET_KEY` - Auto-generated or use `openssl rand -base64 32`
- `CORS_ORIGINS` - Your Netlify frontend URL

### Optional
- `PAYSTACK_SECRET_KEY` - Paystack secret key
- `PAYSTACK_WEBHOOK_SECRET` - Paystack webhook secret
- `GOOGLE_MAPS_API_KEY` - Google Maps API key
- `FIREBASE_*` - Firebase service account credentials
- `GLITCHTIP_DSN` - GlitchTip/Sentry DSN
- `POSTHOG_API_KEY` - PostHog API key

## Testing Locally

You can test the GitHub Actions workflow locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act

# Run workflow
act push
```
EOF

echo -e "${GREEN}✓ Created deployment/GITHUB_SECRETS.md${NC}"
echo ""
