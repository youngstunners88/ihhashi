#!/bin/bash
# iHhashi Google Play Store Deployment Script
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  iHhashi Play Store Deployment Tool    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

case "${1:-help}" in
    check)
        echo "Checking deployment readiness..."
        cd /home/teacherchris37
        git status --short
        echo ""
        ls -la frontend/dist 2>/dev/null || echo "Frontend dist/ not built"
        echo ""
        ls -la frontend/android/app/build/outputs/apk/ 2>/dev/null || echo "APK not built"
        ;;
    build)
        echo "Building Android APK..."
        cd /home/teacherchris37/frontend
        npm install
        npm run build
        npx cap sync android
        cd android
        ./gradlew assembleDebug
        echo "APK built at: frontend/android/app/build/outputs/apk/debug/"
        ;;
    verify)
        echo "Verifying Play Store readiness..."
        test -f /home/teacherchris37/docs/legal/PRIVACY_POLICY.md && echo "✓ Privacy Policy" || echo "✗ Privacy Policy missing"
        test -f /home/teacherchris37/frontend/android/app/build/outputs/apk/debug/app-debug.apk && echo "✓ APK built" || echo "✗ APK not built"
        test -f /home/teacherchris37/frontend/public/assets/splash.jpg && echo "✓ Assets present" || echo "✗ Assets missing"
        ;;
    help|*)
        echo "Usage: ./deploy-to-playstore.sh [command]"
        echo ""
        echo "Commands:"
        echo "  check   - Check deployment readiness"
        echo "  build   - Build Android APK"
        echo "  verify  - Verify Play Store readiness"
        echo ""
        ;;
esac
