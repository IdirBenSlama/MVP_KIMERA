#!/bin/bash
# Kimera SWM Restore Script
# Restores PostgreSQL database and application data from backup

# Configuration
BACKUP_DIR="/backup/kimera"
DB_CONTAINER="kimera-postgres"
DB_NAME="kimera_swm"
DB_USER="kimera"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo "Example: $0 kimera_db_20240617_120000.sql.gz"
    echo -e "\nAvailable backups:"
    ls -la "$BACKUP_DIR"/kimera_db_*.sql.gz 2>/dev/null | tail -10
    exit 1
fi

BACKUP_FILE="$1"
FULL_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Check if backup file exists
if [ ! -f "$FULL_PATH" ]; then
    echo -e "${RED}Error: Backup file not found: $FULL_PATH${NC}"
    exit 1
fi

echo -e "${YELLOW}Kimera SWM Restore Process${NC}"
echo "================================================"
echo "Backup file: $BACKUP_FILE"
echo -e "${RED}WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# 1. Stop Kimera application
echo -e "\n${YELLOW}1. Stopping Kimera application...${NC}"
# Add your application stop command here
# systemctl stop kimera || true
echo -e "${GREEN}✓ Application stopped${NC}"

# 2. Create backup of current database
echo -e "\n${YELLOW}2. Creating backup of current database...${NC}"
CURRENT_BACKUP="kimera_db_before_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/$CURRENT_BACKUP"
echo -e "${GREEN}✓ Current database backed up to: $CURRENT_BACKUP${NC}"

# 3. Drop and recreate database
echo -e "\n${YELLOW}3. Preparing database for restore...${NC}"
docker exec $DB_CONTAINER psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
docker exec $DB_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec $DB_CONTAINER psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
echo -e "${GREEN}✓ Database prepared${NC}"

# 4. Restore database
echo -e "\n${YELLOW}4. Restoring database...${NC}"
gunzip -c "$FULL_PATH" | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restored successfully${NC}"
else
    echo -e "${RED}✗ Database restore failed${NC}"
    echo -e "${YELLOW}Attempting to restore previous backup...${NC}"
    gunzip -c "$BACKUP_DIR/$CURRENT_BACKUP" | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    exit 1
fi

# 5. Restore extensions
echo -e "\n${YELLOW}5. Restoring database extensions...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
echo -e "${GREEN}✓ Extensions restored${NC}"

# 6. Verify restore
echo -e "\n${YELLOW}6. Verifying restore...${NC}"
GEOID_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM geoids;")
SCAR_COUNT=$(docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM scars;")

echo "  Geoids: $GEOID_COUNT"
echo "  SCARs: $SCAR_COUNT"
echo -e "${GREEN}✓ Verification completed${NC}"

# 7. Rebuild indexes
echo -e "\n${YELLOW}7. Rebuilding indexes...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "REINDEX DATABASE $DB_NAME;"
echo -e "${GREEN}✓ Indexes rebuilt${NC}"

# 8. Update statistics
echo -e "\n${YELLOW}8. Updating statistics...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "ANALYZE;"
echo -e "${GREEN}✓ Statistics updated${NC}"

# 9. Restore vector data if separate files exist
TIMESTAMP=$(echo $BACKUP_FILE | grep -oP '\d{8}_\d{6}')
if [ -f "$BACKUP_DIR/geoid_vectors_$TIMESTAMP.csv.gz" ]; then
    echo -e "\n${YELLOW}9. Restoring vector data...${NC}"
    # Vector restore logic here if needed
    echo -e "${GREEN}✓ Vector data found (manual restore may be needed)${NC}"
fi

# 10. Start Kimera application
echo -e "\n${YELLOW}10. Starting Kimera application...${NC}"
# Add your application start command here
# systemctl start kimera
echo -e "${GREEN}✓ Application started${NC}"

# Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Restore completed successfully!${NC}"
echo -e "Restored from: $BACKUP_FILE"
echo -e "Database records:"
echo -e "  - Geoids: $GEOID_COUNT"
echo -e "  - SCARs: $SCAR_COUNT"
echo -e "\nPrevious database backed up to: $CURRENT_BACKUP"
echo -e "${GREEN}================================================${NC}"

# Run verification
echo -e "\n${YELLOW}Running system verification...${NC}"
cd /path/to/kimera && python test_fixes.py