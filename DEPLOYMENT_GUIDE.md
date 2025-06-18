# Kimera SWM Production Deployment Guide

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Python 3.11+ with virtual environment
- [ ] PostgreSQL client tools (optional)
- [ ] 4GB+ RAM available
- [ ] 20GB+ disk space for data growth

### Configuration Verification
- [ ] `.env` file configured with production settings
- [ ] Docker containers healthy
- [ ] Database migrations completed
- [ ] Vector indexes optimized
- [ ] API endpoints responding

## 🚀 Deployment Steps

### 1. Environment Setup

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd "Kimera_SWM_Alpha_Prototype V0.1 140625"

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Production Configuration

Create production `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
SECRET_KEY=<generate-secure-key>
ALLOWED_ORIGINS=["https://your-domain.com"]

# Monitoring
ENABLE_MONITORING=true
LOG_LEVEL=INFO
```

### 3. Database Deployment

```bash
# Start database services
docker-compose up -d postgres neo4j redis

# Wait for services to be healthy
docker-compose ps

# Verify PostgreSQL extensions
docker exec -it kimera-postgres psql -U kimera -d kimera_swm -c "\dx"

# Run optimizations (if not already done)
python scripts/optimize_database.py
python scripts/vector_optimization.py
```

### 4. Data Migration (if needed)

```bash
# Backup existing data
docker exec kimera-postgres pg_dump -U kimera kimera_swm > backup_$(date +%Y%m%d).sql

# Run migration from SQLite (if applicable)
python scripts/migrate_sqlite_to_postgres.py
```

### 5. Application Deployment

```bash
# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Check logs
docker-compose logs -f --tail=100

# Start Kimera application
python run_kimera.py
```

### 6. Post-Deployment Verification

```bash
# Run system tests
python test_fixes.py

# Run performance benchmark
python scripts/performance_benchmark.py

# Check API health
curl http://localhost:8000/system/health
```

## 🔧 Production Optimization

### 1. PostgreSQL Tuning

Edit `postgresql.conf` or use ALTER SYSTEM:
```sql
-- Connection pooling
ALTER SYSTEM SET max_connections = 200;

-- Memory settings (adjust based on available RAM)
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET work_mem = '32MB';

-- Performance settings
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- Apply changes
SELECT pg_reload_conf();
```

### 2. Vector Index Optimization

```sql
-- Optimize vector indexes based on data size
DROP INDEX IF EXISTS idx_geoids_semantic_vector;
CREATE INDEX idx_geoids_semantic_vector 
ON geoids USING ivfflat (semantic_vector vector_cosine_ops) 
WITH (lists = 100);  -- Increase lists for larger datasets

DROP INDEX IF EXISTS idx_scars_vector;
CREATE INDEX idx_scars_vector 
ON scars USING ivfflat (scar_vector vector_cosine_ops) 
WITH (lists = 200);
```

### 3. Monitoring Setup

```bash
# Install monitoring stack (optional)
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring dashboards
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - pgAdmin: http://localhost:5050
```

## 📊 Monitoring & Maintenance

### Daily Tasks

```bash
# Check system health
python scripts/quick_analysis.py

# Update statistics
docker exec kimera-postgres psql -U kimera -d kimera_swm -c "ANALYZE;"

# Check logs for errors
docker-compose logs --since 24h | grep ERROR
```

### Weekly Tasks

```bash
# Refresh materialized views
docker exec kimera-postgres psql -U kimera -d kimera_swm -c "
REFRESH MATERIALIZED VIEW mv_scar_patterns;
REFRESH MATERIALIZED VIEW mv_geoid_complexity;
"

# Run maintenance script
python scripts/database_maintenance.py

# Backup database
docker exec kimera-postgres pg_dump -U kimera kimera_swm | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Monthly Tasks

```bash
# Full system analysis
python scripts/comprehensive_test.py

# Clean old data
python scripts/database_maintenance.py --cleanup-days=30

# Performance review
python scripts/performance_benchmark.py
```

## 🚨 Troubleshooting

### Common Issues

1. **High Vector Query Times**
   ```sql
   -- Check vector index usage
   EXPLAIN (ANALYZE, BUFFERS) 
   SELECT * FROM scars 
   ORDER BY scar_vector <=> '[...]'::vector 
   LIMIT 10;
   
   -- Rebuild index if needed
   REINDEX INDEX idx_scars_vector;
   ```

2. **Connection Pool Exhaustion**
   ```bash
   # Check active connections
   docker exec kimera-postgres psql -U kimera -d kimera_swm -c "
   SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
   "
   
   # Increase pool size in application config
   ```

3. **Slow Materialized Views**
   ```sql
   -- Check view refresh time
   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_scar_patterns;
   
   -- Consider partial refresh strategies
   ```

### Performance Monitoring Queries

```sql
-- Slow queries
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Table sizes
SELECT tablename, 
       pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## 🔒 Security Considerations

1. **Database Security**
   - Change default passwords
   - Use SSL/TLS connections
   - Implement row-level security if needed
   - Regular security updates

2. **API Security**
   - Enable CORS properly
   - Implement rate limiting
   - Use HTTPS in production
   - API key authentication

3. **Container Security**
   - Keep Docker images updated
   - Use non-root users in containers
   - Implement network segmentation
   - Regular vulnerability scanning

## 📈 Scaling Strategies

### Vertical Scaling
- Increase container resources
- Optimize PostgreSQL settings
- Add more CPU/RAM to host

### Horizontal Scaling
- Read replicas for PostgreSQL
- Load balancing for API
- Distributed vector search
- Neo4j clustering

### Caching Strategy
- Redis for frequently accessed data
- Materialized views for analytics
- Application-level caching
- CDN for static assets

## 🎯 Success Metrics

Monitor these KPIs:
- **Query Performance**: < 10ms for JSONB, < 2s for vector search
- **API Response Time**: < 100ms for 95th percentile
- **System Uptime**: > 99.9%
- **Concurrent Users**: Support 100+ simultaneous users
- **Data Growth**: Handle 10x current data volume

## 📞 Support

### Logs Location
- Application: `logs/kimera.log`
- PostgreSQL: `docker-compose logs postgres`
- Neo4j: `docker-compose logs neo4j`
- API: `docker-compose logs kimera-api`

### Health Checks
- Database: `http://localhost:8000/system/health`
- API Docs: `http://localhost:8000/docs`
- Monitoring: `http://localhost:8000/monitoring/status`

### Backup & Recovery
```bash
# Full backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backup_20240617.sql.gz
```

---

**Deployment Status**: Ready for production deployment
**Support Contact**: [Your contact information]
**Last Updated**: June 2024