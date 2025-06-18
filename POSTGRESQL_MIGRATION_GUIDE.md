# PostgreSQL Migration Guide for Kimera SWM

## 🎯 Benefits of PostgreSQL over SQLite

### Performance & Scalability
- **Concurrent Access**: PostgreSQL handles multiple connections efficiently
- **Better Performance**: Optimized for large datasets and complex queries
- **Vector Search**: Native pgvector extension for semantic similarity
- **Full-text Search**: Advanced text search capabilities
- **Parallel Query Execution**: Faster processing of complex operations

### Features
- **JSONB Support**: Efficient storage and querying of JSON data
- **Array Types**: Native array support for vector storage
- **Advanced Indexing**: B-tree, Hash, GiST, SP-GiST, GIN, and BRIN
- **Triggers & Functions**: Database-level logic for consistency
- **Materialized Views**: Pre-computed results for performance

### Reliability
- **ACID Compliance**: Full transactional integrity
- **Point-in-Time Recovery**: Restore to any moment
- **Replication**: Master-slave and multi-master options
- **Connection Pooling**: Better resource management

## 🚀 Quick Start

### 1. Start the PostgreSQL Container

```bash
# Start all services
docker-compose up -d

# Or just PostgreSQL and Neo4j
docker-compose up -d postgres neo4j

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 2. Update Environment Configuration

Create or update `.env` file:

```env
# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm

# Keep SQLite as fallback
SQLITE_DATABASE_URL=sqlite:///./kimera_swm.db

# Neo4j Configuration (unchanged)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=password
NEO4J_ENCRYPTED=0

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=localhost
API_PORT=8001
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### 3. Migrate Existing Data

```bash
# Run migration script
python scripts/migrate_sqlite_to_postgres.py

# Or manually export/import
python scripts/export_sqlite_data.py > data_export.json
python scripts/import_to_postgres.py < data_export.json
```

### 4. Update Application Code

The application should work with minimal changes thanks to SQLAlchemy abstraction. However, you may want to optimize certain queries:

```python
# In backend/vault/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Update engine creation for better performance
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for debugging
)
```

## 📊 Database Management

### Access pgAdmin

1. Open http://localhost:5050
2. Login: admin@kimera.local / admin
3. Add server:
   - Host: postgres (or localhost if from outside Docker)
   - Port: 5432
   - Database: kimera_swm
   - Username: kimera
   - Password: kimera_secure_pass_2025

### Direct PostgreSQL Access

```bash
# Connect via Docker
docker exec -it kimera-postgres psql -U kimera -d kimera_swm

# Connect from host (requires psql client)
psql -h localhost -p 5432 -U kimera -d kimera_swm

# Common commands
\dt                    # List tables
\d+ table_name        # Describe table
\l                    # List databases
\du                   # List users
\q                    # Quit
```

### Useful Queries

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Monitor active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start DESC;

-- Check vector similarity performance
EXPLAIN ANALYZE
SELECT geoid_id, semantic_vector <-> '[0.1, 0.2, ...]'::vector AS distance
FROM geoids
ORDER BY semantic_vector <-> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## 🔧 Performance Optimization

### 1. Create Indexes

```sql
-- Vector similarity index (after data is loaded)
CREATE INDEX idx_geoids_semantic_vector ON geoids 
USING ivfflat (semantic_vector vector_cosine_ops)
WITH (lists = 100);

-- Text search indexes
CREATE INDEX idx_geoids_symbolic_gin ON geoids 
USING gin (symbolic_state);

-- Timestamp indexes for time-based queries
CREATE INDEX idx_scars_timestamp ON scars (timestamp DESC);
CREATE INDEX idx_geoids_created ON geoids (created_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_scars_vault_timestamp ON scars (vault_id, timestamp DESC);
```

### 2. Vacuum and Analyze

```bash
# Run periodically for optimal performance
docker exec kimera-postgres psql -U kimera -d kimera_swm -c "VACUUM ANALYZE;"

# Or set up automatic vacuum in postgresql.conf
```

### 3. Connection Pooling

Consider using PgBouncer for production:

```yaml
# Add to docker-compose.yml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  container_name: kimera-pgbouncer
  environment:
    DATABASES_HOST: postgres
    DATABASES_PORT: 5432
    DATABASES_USER: kimera
    DATABASES_PASSWORD: kimera_secure_pass_2025
    DATABASES_DBNAME: kimera_swm
    POOL_MODE: transaction
    MAX_CLIENT_CONN: 1000
    DEFAULT_POOL_SIZE: 25
  ports:
    - "6432:6432"
  depends_on:
    - postgres
  networks:
    - kimera-network
```

## 🔒 Backup and Recovery

### Automated Backups

```bash
# Create backup script
cat > scripts/backup_postgres.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/kimera_swm_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

docker exec kimera-postgres pg_dump -U kimera -d kimera_swm > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
EOF

chmod +x scripts/backup_postgres.sh

# Add to crontab for daily backups
# 0 2 * * * /path/to/scripts/backup_postgres.sh
```

### Restore from Backup

```bash
# Restore from backup
gunzip < backup_file.sql.gz | docker exec -i kimera-postgres psql -U kimera -d kimera_swm
```

## 🚨 Monitoring

### PostgreSQL Metrics

```sql
-- Create monitoring views
CREATE VIEW kimera_stats AS
SELECT 
    (SELECT count(*) FROM geoids) as total_geoids,
    (SELECT count(*) FROM scars) as total_scars,
    (SELECT count(*) FROM scars WHERE vault_id = 'vault_a') as vault_a_scars,
    (SELECT count(*) FROM scars WHERE vault_id = 'vault_b') as vault_b_scars,
    (SELECT avg(delta_entropy) FROM scars) as avg_entropy_delta,
    (SELECT count(*) FROM multimodal_groundings) as multimodal_groundings,
    (SELECT count(*) FROM causal_relationships) as causal_relationships,
    pg_database_size('kimera_swm') as database_size;

-- Check it
SELECT * FROM kimera_stats;
```

### Set up Prometheus + Grafana (Optional)

```yaml
# Add to docker-compose.yml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter
  container_name: kimera-postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://kimera:kimera_secure_pass_2025@postgres:5432/kimera_swm?sslmode=disable"
  ports:
    - "9187:9187"
  depends_on:
    - postgres
  networks:
    - kimera-network
```

## 🎯 Migration Checklist

- [ ] Start PostgreSQL container
- [ ] Update .env file with PostgreSQL URL
- [ ] Run migration script to transfer data
- [ ] Update any custom SQL queries for PostgreSQL syntax
- [ ] Create performance indexes
- [ ] Set up backup strategy
- [ ] Test application with PostgreSQL
- [ ] Monitor performance improvements
- [ ] Document any PostgreSQL-specific optimizations

## 💡 Tips

1. **Keep SQLite for Development**: Use SQLite for quick local testing, PostgreSQL for production
2. **Use Transactions**: Wrap bulk operations in transactions for better performance
3. **Monitor Connections**: Watch connection pool usage and adjust settings
4. **Regular Maintenance**: Schedule VACUUM and ANALYZE operations
5. **Index Wisely**: Don't over-index; monitor query patterns first

The migration to PostgreSQL will provide significant performance improvements, especially as the Kimera system scales with more geoids and SCARs. The vector similarity search alone will be much faster with pgvector's optimized indexes.