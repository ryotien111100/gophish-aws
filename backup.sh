#!/bin/bash

# ============================================
# GOPHISH BACKUP SCRIPT
# Creates a portable backup of the entire project
# ============================================

set -e

BACKUP_NAME="gophish-prod-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
BACKUP_DIR="$HOME/backups"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        GOPHISH PROJECT BACKUP                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}\n"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Stop containers (optional - safer for database consistency)
read -p "Stop containers before backup? (recommended) [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}Stopping containers...${NC}"
    docker compose down
fi

# Create backup
echo -e "${BLUE}Creating backup...${NC}"
cd ..
tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
    --exclude='gophish-prod/.git' \
    --exclude='gophish-prod/__pycache__' \
    gophish-prod/

# Show result
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
echo -e "\n${GREEN}✅ Backup created successfully!${NC}\n"
echo -e "${BLUE}File:${NC} $BACKUP_DIR/$BACKUP_NAME"
echo -e "${BLUE}Size:${NC} $BACKUP_SIZE"

echo -e "\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         RESTORE ON NEW HOST                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo -e "
1. Copy backup to new host:
   ${YELLOW}scp $BACKUP_DIR/$BACKUP_NAME user@newhost:~/${NC}

2. Extract on new host:
   ${YELLOW}tar -xzf $BACKUP_NAME${NC}
   ${YELLOW}cd gophish-prod${NC}

3. Start containers:
   ${YELLOW}docker compose up -d${NC}

4. Done! All data, configs, and SSL certs preserved.
"

# Ask to restart
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    read -p "Start containers again? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cd gophish-prod
        docker compose up -d
        echo -e "${GREEN}✅ Containers restarted${NC}"
    fi
fi
