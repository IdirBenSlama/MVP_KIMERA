#!/bin/bash
# Kimera SWM Backup Script
# Performs automated backups of PostgreSQL database and application data

# Configuration
BACKUP_DIR="/backup/kimera"
DB_CONTAINER="kimera-postgres"
DB_NAME="kimera_swm"
DB_USER="kimera"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}Starting Kimera SWM Backup - $TIMESTAMP${NC}"
echo "================================================"

# 1. Database Backup
echo -e "\n${YELLOW}1. Backing up PostgreSQL database...${NC}"
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME --verbose | gzip > "$BACKUP_DIR/kimera_db_$TIMESTAMP.sql.gz"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database backup completed${NC}"
    DB_SIZE=$(du -h "$BACKUP_DIR/kimera_db_$TIMESTAMP.sql.gz" | cut -f1)
    echo "  Size: $DB_SIZE"
else
    echo -e "${RED}✗ Database backup failed${NC}"
    exit 1
fi

# 2. Vector Data Backup (export vectors separately for safety)
echo -e "\n${YELLOW}2. Backing up vector data...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "\COPY (SELECT geoid_id, semantic_vector FROM geoids WHERE semantic_vector IS NOT NULL) TO STDOUT WITH CSV HEADER" | gzip > "$BACKUP_DIR/geoid_vectors_$TIMESTAMP.csv.gz"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "\COPY (SELECT scar_id, scar_vector FROM scars WHERE scar_vector IS NOT NULL) TO STDOUT WITH CSV HEADER" | gzip > "$BACKUP_DIR/scar_vectors_$TIMESTAMP.csv.gz"

echo -e "${GREEN}✓ Vector data backup completed${NC}"

# 3. Configuration Backup
echo -e "\n${YELLOW}3. Backing up configuration files...${NC}"
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" \
    .env \
    docker-compose.yml \
    requirements.txt \
    2>/dev/null

echo -e "${GREEN}✓ Configuration backup completed${NC}"

# 4. Neo4j Backup (if running)
echo -e "\n${YELLOW}4. Checking Neo4j backup...${NC}"
if docker ps | grep -q "kimera-neo4j"; then
    docker exec kimera-neo4j neo4j-admin dump --database=neo4j --to=/data/backup_$TIMESTAMP.dump
    docker cp kimera-neo4j:/data/backup_$TIMESTAMP.dump "$BACKUP_DIR/neo4j_$TIMESTAMP.dump"
    echo -e "${GREEN}✓ Neo4j backup completed${NC}"
else
    echo -e "${YELLOW}⚠ Neo4j not running, skipping backup${NC}"
fi

# 5. Create backup manifest
echo -e "\n${YELLOW}5. Creating backup manifest...${NC}"
cat > "$BACKUP_DIR/manifest_$TIMESTAMP.json" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "components": {
        "database": "kimera_db_$TIMESTAMP.sql.gz",
        "geoid_vectors": "geoid_vectors_$TIMESTAMP.csv.gz",
        "scar_vectors": "scar_vectors_$TIMESTAMP.csv.gz",
        "config": "config_$TIMESTAMP.tar.gz",
        "neo4j": "neo4j_$TIMESTAMP.dump"
    },
    "statistics": {
        "database_size": "$DB_SIZE",
        "total_files": 5
    }
}
EOF

echo -e "${GREEN}✓ Backup manifest created${NC}"

# 6. Cleanup old backups
echo -e "\n${YELLOW}6. Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "kimera_*" -type f -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "manifest_*" -type f -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}✓ Cleanup completed${NC}"

# 7. Verify backup integrity
echo -e "\n${YELLOW}7. Verifying backup integrity...${NC}"
if gzip -t "$BACKUP_DIR/kimera_db_$TIMESTAMP.sql.gz" 2>/dev/null; then
    echo -e "${GREEN}✓ Database backup verified${NC}"
else
    echo -e "${RED}✗ Database backup corrupted!${NC}"
    exit 1
fi

# 8. Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "Backup location: $BACKUP_DIR"
echo -e "Backup timestamp: $TIMESTAMP"
echo -e "Total backup size: $(du -sh $BACKUP_DIR | cut -f1)"
echo -e "${GREEN}================================================${NC}"

# Optional: Upload to cloud storage
# Uncomment and configure as needed
# echo -e "\n${YELLOW}Uploading to cloud storage...${NC}"
# aws s3 cp "$BACKUP_DIR/kimera_db_$TIMESTAMP.sql.gz" s3://your-bucket/kimera-backups/
# echo -e "${GREEN}✓ Cloud upload completed${NC}"