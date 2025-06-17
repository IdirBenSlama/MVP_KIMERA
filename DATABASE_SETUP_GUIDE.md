# KIMERA SWM Database Setup Guide

This guide explains how to build and configure the complete KIMERA SWM database system, which uses a hybrid architecture combining relational and graph databases.

## Database Architecture

KIMERA SWM uses a **dual-database architecture**:

### 🗄️ Relational Database (Primary Storage)
- **SQLite** (development) or **PostgreSQL** (production)
- Stores structured data: SCARs, Geoids, Insights
- Handles ACID transactions and complex queries
- Optimized with indexes for performance

### 🕸️ Graph Database (Semantic Storage)
- **Neo4j** for semantic relationships and causal chains
- Stores graph connections between concepts
- Enables complex relationship queries
- Supports semantic reasoning and pattern discovery

### 🔄 Dual-Write Pattern
- Data is written to both databases simultaneously
- SQL database remains the primary source of truth
- Neo4j provides enhanced semantic capabilities
- System gracefully degrades if Neo4j is unavailable

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
build_database.bat
```

**Linux/Mac:**
```bash
chmod +x build_database.sh
./build_database.sh
```

### Option 2: Manual Setup

```bash
# Basic setup (SQL only)
python build_database.py

# Full setup with Neo4j
python build_database.py --neo4j --enhanced --sample-data
```

## Prerequisites

### Required Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- `sqlalchemy>=2.0.41` - ORM and database abstraction
- `neo4j>=5.28.1` - Neo4j Python driver
- `psycopg2-binary>=2.9.10` - PostgreSQL adapter (optional)
- `pgvector>=0.4.1` - Vector operations (optional)

### Neo4j Setup (Optional but Recommended)

**Option 1: Docker (Easiest)**
```bash
docker run -d --name kimera-neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5
```

**Option 2: Local Installation**
1. Download Neo4j from https://neo4j.com/download/
2. Install and start the service
3. Set password via Neo4j Browser

**Environment Variables:**
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASS="your_password"
```

## Database Builder Options

The `build_database.py` script supports several options:

```bash
python build_database.py [OPTIONS]

Options:
  --neo4j         Initialize Neo4j graph database
  --enhanced      Create enhanced understanding tables
  --reset         Drop and recreate all tables
  --sample-data   Create sample data for testing
  --help          Show help message
```

### Examples

```bash
# Basic setup (development)
python build_database.py

# Full production setup
python build_database.py --neo4j --enhanced

# Reset and rebuild everything
python build_database.py --reset --neo4j --enhanced --sample-data

# SQL-only setup with enhanced tables
python build_database.py --enhanced --sample-data
```

## Database Schema

### Core Tables (Always Created)

#### `scars` - Semantic Contradiction and Resolution Records
```sql
CREATE TABLE scars (
    scar_id VARCHAR PRIMARY KEY,
    geoids JSON,                    -- Related geoid IDs
    reason VARCHAR,                 -- Contradiction reason
    timestamp DATETIME,             -- Creation time
    resolved_by VARCHAR,            -- Resolution method
    pre_entropy FLOAT,              -- Entropy before resolution
    post_entropy FLOAT,             -- Entropy after resolution
    delta_entropy FLOAT,            -- Entropy change
    cls_angle FLOAT,                -- Classification angle
    semantic_polarity FLOAT,        -- Semantic polarity
    mutation_frequency FLOAT,       -- Mutation rate
    weight FLOAT DEFAULT 1.0,       -- SCAR weight
    last_accessed DATETIME,         -- Last access time
    scar_vector JSON,               -- Embedding vector
    vault_id VARCHAR                -- Vault assignment (vault_a/vault_b)
);
```

#### `geoids` - Geometric Semantic Objects
```sql
CREATE TABLE geoids (
    geoid_id VARCHAR PRIMARY KEY,
    symbolic_state JSON,            -- Symbolic representation
    metadata_json JSON,             -- Metadata
    semantic_state_json JSON,       -- Semantic state
    semantic_vector JSON            -- Embedding vector
);
```

#### `insights` - Generated Insights
```sql
CREATE TABLE insights (
    insight_id VARCHAR PRIMARY KEY,
    insight_type VARCHAR,           -- Type of insight
    source_resonance_id VARCHAR,    -- Source resonance
    echoform_repr JSON,             -- EchoForm representation
    application_domains JSON,       -- Application domains
    confidence FLOAT,               -- Confidence score
    entropy_reduction FLOAT,        -- Entropy reduction
    utility_score FLOAT DEFAULT 0.0, -- Utility score
    status VARCHAR DEFAULT 'provisional', -- Status
    created_at DATETIME,            -- Creation time
    last_reinforced_cycle VARCHAR   -- Last reinforcement
);
```

### Enhanced Tables (--enhanced flag)

When using `--enhanced`, additional tables are created for advanced understanding capabilities:

- `multimodal_groundings` - Multimodal semantic groundings
- `causal_relationships` - Causal relationship tracking
- `self_models` - System self-model storage
- `introspection_logs` - Introspective process logs
- `compositional_semantics` - Compositional understanding
- `conceptual_abstractions` - Abstract concept storage
- `value_systems` - Value and preference storage
- `genuine_opinions` - Opinion formation tracking
- `ethical_reasoning` - Ethical decision processes
- `understanding_tests` - Understanding validation
- `consciousness_indicators` - Consciousness measurements

### Neo4j Graph Schema

#### Node Types
- `:Geoid` - Semantic objects with properties
- `:Scar` - Contradiction resolution records

#### Relationship Types
- `(:Scar)-[:INVOLVES]->(:Geoid)` - SCAR involves specific geoids
- `(:Geoid)-[:RELATES_TO]->(:Geoid)` - Semantic relationships
- `(:Geoid)-[:CAUSES]->(:Geoid)` - Causal relationships

#### Constraints and Indexes
```cypher
-- Unique constraints
CREATE CONSTRAINT geoid_id_unique FOR (g:Geoid) REQUIRE g.geoid_id IS UNIQUE;
CREATE CONSTRAINT scar_id_unique FOR (s:Scar) REQUIRE s.scar_id IS UNIQUE;

-- Performance indexes
CREATE INDEX geoid_timestamp FOR (g:Geoid) ON (g.created_at);
CREATE INDEX scar_timestamp FOR (s:Scar) ON (s.timestamp);
CREATE INDEX scar_vault FOR (s:Scar) ON (s.vault_id);
```

## Performance Optimizations

### SQL Database Indexes

The builder creates optimized indexes for common query patterns:

```sql
-- SCAR indexes
CREATE INDEX idx_scars_vault_id ON scars(vault_id);
CREATE INDEX idx_scars_timestamp ON scars(timestamp DESC);
CREATE INDEX idx_scars_weight ON scars(weight);
CREATE INDEX idx_scars_vault_timestamp ON scars(vault_id, timestamp DESC);

-- Geoid indexes
CREATE INDEX idx_geoids_id ON geoids(geoid_id);
CREATE INDEX idx_geoids_created ON geoids(rowid);

-- Insight indexes
CREATE INDEX idx_insights_type ON insights(insight_type);
CREATE INDEX idx_insights_status ON insights(status);
CREATE INDEX idx_insights_created ON insights(created_at DESC);
```

### Database Configuration

For SQLite (development):
- WAL mode enabled for better concurrency
- Increased cache size for performance
- Foreign key constraints enabled

For PostgreSQL (production):
- Connection pooling configured
- Vector extension enabled (pgvector)
- Optimized for concurrent access

## Verification and Testing

### Database Health Check

After building, verify the setup:

```bash
# Check database status
python -c "
from backend.vault.database import SessionLocal, ScarDB
with SessionLocal() as db:
    count = db.query(ScarDB).count()
    print(f'SQL Database: {count} SCARs')
"

# Check Neo4j (if enabled)
python -c "
from backend.graph.session import get_session
with get_session() as s:
    result = s.run('MATCH (n) RETURN count(n) as count')
    print(f'Neo4j Database: {result.single()[\"count\"]} nodes')
"
```

### Running Tests

```bash
# Test database functionality
python -m pytest tests/test_vault_manager.py -v

# Test Neo4j integration
python test_neo4j_integration.py

# Full system test
python -m pytest tests/ -v
```

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL="sqlite:///./kimera_swm.db"  # or PostgreSQL URL
DATABASE_URL="postgresql://user:pass@localhost/kimera_swm"

# Neo4j Configuration
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="your_password"
NEO4J_ENCRYPTED="1"  # Enable encryption
NEO4J_POOL_SIZE="20"  # Connection pool size

# Vector Database (optional)
PGVECTOR_ENABLED="true"  # Enable vector operations
```

### Production Configuration

For production deployments:

1. **Use PostgreSQL** instead of SQLite
2. **Enable Neo4j** for full semantic capabilities
3. **Configure connection pooling** for high concurrency
4. **Set up monitoring** for database health
5. **Enable backups** for data protection

```bash
# Production example
export DATABASE_URL="postgresql://kimera:secure_password@db-server:5432/kimera_swm"
export NEO4J_URI="bolt://neo4j-server:7687"
export NEO4J_USER="kimera"
export NEO4J_PASS="secure_neo4j_password"

python build_database.py --neo4j --enhanced
```

## Troubleshooting

### Common Issues

**1. SQLAlchemy Import Error**
```
ImportError: No module named 'sqlalchemy'
```
Solution: `pip install -r requirements.txt`

**2. Neo4j Connection Failed**
```
Neo4j database is not responding
```
Solutions:
- Check if Neo4j is running: `docker ps | grep neo4j`
- Verify environment variables are set
- Check firewall settings for port 7687

**3. Permission Denied (Linux/Mac)**
```
Permission denied: ./build_database.sh
```
Solution: `chmod +x build_database.sh`

**4. Database Locked (SQLite)**
```
database is locked
```
Solutions:
- Close any open database connections
- Restart the application
- Check for zombie processes

**5. Table Already Exists**
```
Table 'scars' already exists
```
Solution: Use `--reset` flag to recreate tables

### Debug Mode

Enable debug logging:

```bash
export KIMERA_DEBUG=1
python build_database.py --neo4j --enhanced
```

### Manual Recovery

If the automated builder fails:

```python
# Manual table creation
from backend.vault.database import Base, engine
Base.metadata.create_all(bind=engine)

# Manual Neo4j setup
from backend.graph.session import get_session
with get_session() as s:
    s.run("CREATE CONSTRAINT geoid_id_unique FOR (g:Geoid) REQUIRE g.geoid_id IS UNIQUE")
```

## Maintenance

### Regular Maintenance Tasks

1. **Vacuum SQLite database** (monthly)
```bash
sqlite3 kimera_swm.db "VACUUM;"
```

2. **Analyze query performance** (weekly)
```bash
sqlite3 kimera_swm.db "ANALYZE;"
```

3. **Check Neo4j statistics** (weekly)
```cypher
CALL db.stats.retrieve('GRAPH COUNTS');
```

4. **Monitor database size** (daily)
```bash
du -h kimera_swm.db
```

### Backup and Recovery

**SQLite Backup:**
```bash
cp kimera_swm.db kimera_swm_backup_$(date +%Y%m%d).db
```

**Neo4j Backup:**
```bash
docker exec kimera-neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j_backup.dump
```

## Integration with KIMERA

The database system integrates seamlessly with KIMERA components:

- **VaultManager**: Handles dual-write operations
- **API Layer**: Provides database access via REST endpoints
- **Monitoring**: Tracks database performance and health
- **Testing**: Comprehensive test coverage for all operations

## Next Steps

After building the database:

1. **Start KIMERA**: `python run_kimera.py`
2. **Test API**: `curl http://localhost:8000/health`
3. **Explore Neo4j**: Visit http://localhost:7474
4. **Run comprehensive tests**: `python -m pytest tests/`
5. **Monitor performance**: Check dashboard at http://localhost:8000/dashboard

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the test output for specific errors
3. Check the KIMERA logs for detailed error messages
4. Consult the main README.md for system requirements

The database builder is designed to be robust and provide clear feedback about any issues encountered during setup.