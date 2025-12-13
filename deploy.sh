#!/bin/bash

# ============================================
# GOPHISH DEPLOYMENT SCRIPT
# Usage: ./deploy.sh [--restart]
# ============================================

set -e

DOMAIN_FILE=".env"
SCRIPT_FILE="setup.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GOPHISH PHISHING DOMAINS DEPLOYMENT       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}\n"

# Check if .env exists
if [ ! -f "$DOMAIN_FILE" ]; then
    echo -e "${YELLOW}❌ Error: $DOMAIN_FILE not found${NC}"
    exit 1
fi

# Step 1: Show configured domains
echo -e "${BLUE}[1/3] Phishing Domains in .env:${NC}"
grep "^PHISH_DOMAIN" "$DOMAIN_FILE" | grep -v "^#" || echo "  (none found)"
echo ""

# Step 2: Generate Traefik labels
echo -e "${BLUE}[2/3] Generating Traefik routes...${NC}"
python3 "$SCRIPT_FILE" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Routes generated in docker-compose.override.yml${NC}\n"
else
    echo -e "${YELLOW}⚠️  Warning: Script failed, but continuing...${NC}\n"
fi

# Step 3: Restart containers (optional)
if [ "$1" = "--restart" ]; then
    echo -e "${BLUE}[3/3] Restarting containers...${NC}"
    docker compose down 2>/dev/null || true
    docker compose up -d
    sleep 3
    echo -e "${GREEN}✅ Containers restarted${NC}\n"
else
    echo -e "${BLUE}[3/3] To apply changes, run:${NC}"
    echo -e "  ${YELLOW}docker compose down && docker compose up -d${NC}\n"
fi

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         DEPLOYMENT COMPLETE ✅                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}📌 QUICK REFERENCE:${NC}"
echo "  1. Edit domains:   nano .env"
echo "  2. Generate routes: python3 setup.py"
echo "  3. Restart:        docker compose down && docker compose up -d"
echo ""
echo "  Or use this shortcut: ./deploy.sh --restart"
echo ""
